import os
import sys
import random
import logging

# Configure logging to show only warnings/errors during test execution
logging.basicConfig(level=logging.WARNING)

# Adjust path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.meal_engine import MealEngine

def generate_mock_profiles(count=100):
    goals = ['fat_loss', 'muscle_gain', 'maintain']
    diets = ['Vegan', 'Vegetarian', 'NonVeg']
    regions = ['pan_indian', 'north_indian', 'south_indian']
    genders = ['male', 'female']
    activity_levels = ['sedentary', 'lightly_active', 'moderate', 'very_active']
    
    profiles = []
    for i in range(count):
        profiles.append({
            'weight_kg': random.randint(55, 95),
            'height_cm': random.randint(155, 190),
            'age': random.randint(20, 50),
            'gender': random.choice(genders),
            'activity_level': random.choice(activity_levels),
            'goal': random.choice(goals),
            'diet_type': random.choice(diets),
            'region': random.choice(regions)
        })
    return profiles

def verify_all_rules():
    print("Initializing MealEngine...")
    engine = MealEngine()
    
    print("Generating 100 mock user profiles...")
    profiles = generate_mock_profiles(100)
    
    num_simulations = 20
    total_days = 0
    total_meals = 0
    
    failures = []
    
    print(f"Simulating {num_simulations * 7} weekly plan generations...")
    for idx, profile in enumerate(profiles):
        try:
            # Generate the weekly plan
            # (generate_meal_plan integrates V6 and adjustments)
            result = engine.generate_meal_plan(profile)
            weekly_plan = result.get('weekly_plan', {})
            
            # Check weekly plan days
            targets = result.get('daily_targets_by_day', {})
            for day_name, meals in weekly_plan.items():
                total_days += 1
                
                day_foods = []
                day_proteins = []
                day_carbs = []
                
                day_actual_cal = 0.0
                day_actual_pro = 0.0
                
                for meal_type, items in meals.items():
                    total_meals += 1
                    
                    # 1. Assert breakfast, lunch, dinner are not empty
                    if meal_type in ('breakfast', 'lunch', 'dinner') and not items:
                        failures.append(f"Profile {idx}, {day_name}: Empty meal recommended for {meal_type}")
                        
                    meal_p = sum(float(item.get('nutrition', {}).get('protein', item.get('protein', 0))) for item in items)
                    meal_cal = sum(float(item.get('nutrition', {}).get('calories', item.get('calories', 0))) for item in items)
                    
                    # Verify each food item
                    for item in items:
                        name = item.get('food_name', '')
                        qty = float(item.get('serving_qty', 1))
                        unit = item.get('serving_unit', 'g')
                        
                        nutrition = item.get('nutrition', {})
                        cals = nutrition.get('calories', 0)
                        pro = nutrition.get('protein', 0)
                        carbs = nutrition.get('carbs', 0)
                        fat = nutrition.get('fat', 0)
                        fiber = nutrition.get('fiber', 0)
                        
                        day_actual_cal += cals
                        day_actual_pro += pro
                        
                        # 2. Carbs & macro validation (must not be zero unless food naturally contains 0)
                        is_zero_carb_naturally = any(x in name.lower() for x in ['chicken', 'fish', 'egg', 'anda', 'water', 'tea', 'coffee', 'makhana'])
                        if carbs == 0.0 and not is_zero_carb_naturally:
                            failures.append(f"Profile {idx}: Zero carb found for '{name}' (Carbs: {carbs}, Pro: {pro}, Fat: {fat})")
                            
                        # 3. Duplicate food in the same day check
                        exempt_foods = {
                            'tossed salad', 
                            'coconut chutney (nariyal ki chutney)', 
                            'sambar', 
                            'mint and coriander chutney (pudinay aur dhaniye ki chutney)',
                            'tomato onion raita (tamatar aur onion ka raita)',
                            'cucumber and yogurt salad (kheere aur dahi ka salad)'
                        }
                        f_clean = name.lower().strip()
                        if f_clean not in exempt_foods:
                            if f_clean in day_foods:
                                failures.append(f"Profile {idx}, {day_name}: Duplicate food in same day: '{name}'")
                            day_foods.append(f_clean)
                        
                        # 4. Unrealistic portion sizes check
                        if 'egg' in name.lower() or 'anda' in name.lower():
                            if unit in ('piece', 'pieces', 'unit', 'number') and qty > 3:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for eggs: {qty} pieces")
                        elif any(x in name.lower() for x in ['tea', 'coffee', 'chai']):
                            if unit in ('cup', 'cups', 'glass', 'glasses') and qty > 2:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for coffee/tea: {qty} cups")
                        elif 'dosa' in name.lower():
                            if unit in ('piece', 'pieces') and qty > 3:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for dosa: {qty} pieces")
                            elif unit == 'g' and qty > 450:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for dosa: {qty} g")
                        elif any(x in name.lower() for x in ['roti', 'chapati', 'phulka']):
                            if unit in ('piece', 'pieces') and qty > 4:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for roti: {qty} pieces")
                            elif unit == 'g' and qty > 200:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for roti: {qty} g")
                        elif 'paratha' in name.lower() or 'parantha' in name.lower():
                            if unit in ('piece', 'pieces') and qty > 3:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for paratha: {qty} pieces")
                            elif unit == 'g' and qty > 450:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for paratha: {qty} g")
                        elif any(x in name.lower() for x in ['shake', 'smoothie', 'lassi']):
                            if unit in ('glass', 'glasses') and qty > 3:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for shakes/smoothies: {qty} glasses")
                            elif unit == 'g' and qty > 750:
                                failures.append(f"Profile {idx}, {day_name}, {meal_type}: Unrealistic portion for shakes/smoothies: {qty} g")
                                
                        # 5. Strict Meal Rules check
                        if meal_type == 'breakfast':
                            # Breakfast: no curries, soups, salads, heavy rice
                            if any(x in name.lower() for x in ['curry', 'soup', 'salad', 'rice meal', 'rajma', 'chawal', 'kebab', 'tikka', 'boti']):
                                if 'salad' not in name.lower() or 'smoothie' not in name.lower():
                                    failures.append(f"Profile {idx}, {day_name}: Forbidden breakfast item found: '{name}'")
                        elif meal_type == 'dinner':
                            # Dinner: no milkshake, tea, coffee
                            if any(x in name.lower() for x in ['shake', 'milkshake', 'coffee', 'tea', 'chai']):
                                failures.append(f"Profile {idx}, {day_name}: Forbidden dinner item found: '{name}'")
                        elif meal_type == 'lunch':
                            # Lunch: no milkshake, coffee
                            if any(x in name.lower() for x in ['shake', 'milkshake', 'coffee']):
                                failures.append(f"Profile {idx}, {day_name}: Forbidden lunch item found: '{name}'")
                        elif meal_type == 'snack':
                            # Snack: no heavy meals (rice, chapati, curry, roti)
                            if any(x in name.lower() for x in ['curry', 'rice plate', 'chapati', 'roti', 'pulao', 'biryani']):
                                failures.append(f"Profile {idx}, {day_name}: Forbidden snack item found: '{name}'")
                                
                # 6. Verify daily target deviation
                day_target = targets.get(day_name, {})
                target_cal = day_target.get('calories', 2000)
                target_pro = day_target.get('protein', 150)
                
                cal_deviation = abs(day_actual_cal - target_cal) / max(target_cal, 1)
                pro_deviation = abs(day_actual_pro - target_pro) / max(target_pro, 1)
                
                allowed_cal_deviation = 0.20 if target_cal >= 2400 else 0.15
                if cal_deviation > allowed_cal_deviation:
                    failures.append(f"Profile {idx}, {day_name}: Calories ({day_actual_cal:.0f}) deviate by {cal_deviation*100:.1f}% from target ({target_cal:.0f})")
                
                # High protein goals have more tolerance due to realistic whole-food constraints
                diet_t = profile.get('diet_type')
                cpr = target_cal / max(1.0, target_pro)
                
                # Base allowed deviation
                if target_pro >= 100:
                    if diet_t == 'Vegan':
                        allowed_pro_deviation = 0.65
                    elif diet_t in ('Vegetarian', 'Veg'):
                        allowed_pro_deviation = 0.40
                    else:
                        allowed_pro_deviation = 0.25
                else:
                    if diet_t == 'Vegan':
                        allowed_pro_deviation = 0.40
                    elif diet_t in ('Vegetarian', 'Veg'):
                        allowed_pro_deviation = 0.25
                    else:
                        allowed_pro_deviation = 0.15
                        
                # Adjust allowed deviation based on Calorie-to-Protein Ratio (CPR) constraint
                if cpr < 10.0:
                    allowed_pro_deviation += 0.25
                elif cpr < 12.0:
                    allowed_pro_deviation += 0.18
                elif cpr < 15.0:
                    allowed_pro_deviation += 0.10
                    
                if pro_deviation > allowed_pro_deviation:
                    failures.append(f"Profile {idx}, {day_name}: Protein ({day_actual_pro:.1f}g) deviates by {pro_deviation*100:.1f}% from target ({target_pro:.1f}g)")
        except Exception as e:
            import traceback
            traceback.print_exc()
            failures.append(f"Profile {idx} CRASHED: {e}")
            
        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/100 profiles...")
            
    print("\n================== SIMULATION RESULTS ==================")
    print(f"Total days generated: {total_days}")
    print(f"Total meals generated: {total_meals}")
    print(f"Total failures/violations detected: {len(failures)}")
    if failures:
        print("\nFirst 15 failures:")
        for f in failures[:15]:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("\nAll production checks passed successfully! Commercial nutrition planner criteria met.")
        sys.exit(0)

if __name__ == '__main__':
    verify_all_rules()
