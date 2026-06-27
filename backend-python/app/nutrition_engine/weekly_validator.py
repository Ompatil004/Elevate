import logging
from app.nutrition_engine.config import NUTRITION_RULES
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WeeklyValidator:
    """
    Phase 4.8: Weekly Validator
    Checks the holistic outputs of the weekly meal plan to ensure it meets dietary goals.
    """
    def __init__(self):
        pass
        
    def validate_plan(self, weekly_plan: Dict[str, Any], user_profile: Dict[str, Any], daily_targets: Dict[str, float]) -> Dict[str, Any]:
        """
        Validates the weekly plan. Returns a report containing metrics and validation status.
        """
        report = {
            "is_valid": True,
            "warnings": [],
            "metrics": {
                "avg_daily_calories": 0,
                "avg_daily_protein": 0,
                "avg_daily_carbs": 0,
                "avg_daily_fat": 0
            }
        }
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        days_counted = len(weekly_plan)
        
        if days_counted == 0:
            report["is_valid"] = False
            report["warnings"].append("Weekly plan is empty.")
            return report
            
        for day, meals in weekly_plan.items():
            for meal_name, items in meals.items():
                for item in items:
                    nut = item.get('nutrition', {})
                    total_calories += nut.get('calories', 0)
                    total_protein += nut.get('protein', 0)
                    total_carbs += nut.get('carbs', 0)
                    total_fat += nut.get('fat', 0)
                    
        avg_cal = total_calories / days_counted
        avg_pro = total_protein / days_counted
        
        report["metrics"]["avg_daily_calories"] = round(avg_cal, 2)
        report["metrics"]["avg_daily_protein"] = round(avg_pro, 2)
        report["metrics"]["avg_daily_carbs"] = round(total_carbs / days_counted, 2)
        report["metrics"]["avg_daily_fat"] = round(total_fat / days_counted, 2)
        
        # Check holistic limits
        if daily_targets and any(k.startswith('Day_') for k in daily_targets):
            target_cal = sum(d.get('calories', 0) for d in daily_targets.values()) / len(daily_targets)
            target_pro = sum(d.get('protein', 0) for d in daily_targets.values()) / len(daily_targets)
        else:
            target_cal = daily_targets.get('calories', 0)
            target_pro = daily_targets.get('protein', 0)
        
        if target_cal > 0:
            cal_diff = abs(avg_cal - target_cal) / target_cal
            if cal_diff > 0.15:
                report["is_valid"] = False
                report["warnings"].append(f"Average calories ({avg_cal}) deviate more than 15% from target ({target_cal})")
                
        if target_pro > 0:
            pro_diff = abs(avg_pro - target_pro) / target_pro
            if pro_diff > 0.20:
                report["warnings"].append(f"Average protein ({avg_pro}) deviates significantly from target ({target_pro})")
                
        # Phase 5: The "Indian Family Test"
        self._indian_family_test(weekly_plan, report)
                
        return report

    def _indian_family_test(self, weekly_plan: Dict[str, Any], report: Dict[str, Any]):
        """
        Heuristic-based check to see if the plates actually look like Indian meals.
        """
        for day, meals in weekly_plan.items():
            for meal_name, items in meals.items():
                if meal_name.lower() == 'snack':
                    continue
                    
                food_names_lower = [str(item.get('food_name', '')).lower() for item in items]
                
                # Curry needs a carb
                has_curry = any('curry' in fn or 'dal' in fn or 'gravy' in fn for fn in food_names_lower)
                has_carb = any('rice' in fn or 'roti' in fn or 'chapati' in fn or 'paratha' in fn or 'bread' in fn or 'pulao' in fn or 'biryani' in fn for fn in food_names_lower)
                
                if has_curry and not has_carb:
                    # Could be eating just dal or just chicken curry
                    # Exempt if it's soup or stew
                    if not any('soup' in fn or 'shorba' in fn for fn in food_names_lower):
                        report["warnings"].append(f"Indian Family Test Failed on {day} {meal_name}: Curry served without roti or rice.")
                        
                # Excessive dryness
                has_dry = sum(1 for fn in food_names_lower if 'dry' in fn or 'tikka' in fn)
                has_wet = any('curry' in fn or 'dal' in fn or 'raita' in fn or 'chutney' in fn for fn in food_names_lower)
                if has_dry >= 2 and not has_wet:
                    report["warnings"].append(f"Indian Family Test Failed on {day} {meal_name}: Very dry meal (multiple dry dishes) without any dal, raita, or chutney.")
                    
                # Double heavy proteins
                has_heavy_pro = sum(1 for fn in food_names_lower if 'chicken' in fn or 'paneer' in fn or 'mutton' in fn or 'fish' in fn)
                if has_heavy_pro >= 2:
                    report["warnings"].append(f"Indian Family Test Failed on {day} {meal_name}: Multiple heavy protein sources (e.g. Chicken AND Paneer).")

    def _map_food_to_blueprint_role(self, food: Dict, template_role: str = "") -> str:
        sem = food.get("semantics", {})
        category = sem.get("category", "") or ""
        dish_family = sem.get("dish_family", "") or ""
        food_name = food.get("food_name", "")
        food_name_lower = food_name.lower().strip()
        role = template_role or sem.get("meal_role", "") or ""
        
        _PROTEIN_GROUPS = {
            "Dal & Pulses", "Chicken/Meat", "Paneer", "Eggs", "Fish/Seafood",
            "Meat & Chicken", "Paneer & Tofu", "Seafood", "Soya & Tofu", "protein", "protein_main"
        }
        _CARB_GROUPS = {
            "Rice", "Whole Grains", "Millets & Whole Grains", "Breads & Roti", "Oats & Cereals", "carb", "carb_base"
        }

        # Priority 0: Hard name/dish_family overrides — must come before category checks
        # Raita/pachadi is always a side dish regardless of category or food_group
        if any(w in food_name_lower for w in ("raita", "pachadi")) or dish_family in ("raita",):
            return "raita"
        # Carb-based bases (sandwich, wrap, roll, toast, roti, paratha, chapati, naan, dosa, idli, poha, upma, oats, rice, bread, pasta, etc.)
        _CARB_KEYWORDS = (
            "sandwich", "wrap", "toast", "roll", "paratha", "parantha", 
            "roti", "chapati", "naan", "dosa", "idli", "poha", "upma", 
            "uttapam", "cereal", "oats", "rice", "bread", "pancake", "waffle", "cheela",
            "chilla", "paniyaram", "appam", "koozh", "bhel", "khichdi", "bath", "sweet potato", "mudde",
            "spaghetti", "pasta", "noodles", "macaroni"
        )
        _CARB_FAMILIES = (
            "sandwich", "roll", "wrap", "toast", "roti", "paratha", 
            "bread", "naan", "dosa", "idli", "uttapam", "poha", "upma", "rice", "pasta", "noodles",
            "chilla", "paniyaram", "appam", "koozh", "bhel", "khichdi", "bath", "mudde"
        )
        if dish_family in _CARB_FAMILIES or any(w in food_name_lower for w in _CARB_KEYWORDS):
            # If it is a carb base but contains a major protein keyword, it behaves as the protein main
            if any(p in food_name_lower for p in ("chicken", "egg", "paneer", "tofu", "fish", "mutton", "soya", "turkey")):
                return "protein"
            return "carb"
        # Soup/shorba is always a side/soup
        if dish_family == "soup" or any(w in food_name_lower for w in ("soup", "shorba")):
            return "soup"
        # Chutney/pickle
        if any(w in food_name_lower for w in ("chutney", "pickle", "achar")) or dish_family in ("chutney",):
            return "chutney"
        # Salad/kachumber - sprouted salads or salads with meat/dairy function as protein sources
        if any(w in food_name_lower for w in ("salad", "kachumber", "kosambari")) or dish_family in ("salad",):
            if any(p in food_name_lower for p in ("chicken", "egg", "paneer", "tofu", "fish", "mutton", "soya", "moong", "chana", "peanut")):
                return "protein"
            return "salad"

        # 1. food_group/category + template_role
        food_group = sem.get("food_group", "") or category
        food_group_lower = food_group.lower().strip()
        _PROTEIN_GROUPS_LOWER = {g.lower() for g in _PROTEIN_GROUPS}
        _CARB_GROUPS_LOWER = {g.lower() for g in _CARB_GROUPS}
        if role in ("protein_main", "curry") or food_group_lower in _PROTEIN_GROUPS_LOWER:
            return "protein"
        if role == "carb_base" or food_group_lower in _CARB_GROUPS_LOWER:
            return "carb"
            
        # 2. dish_family
        if dish_family in ("rice", "plain_rice", "fried_rice", "pulao", "biryani", "roti", "paratha", "bread", "naan", "dosa", "idli", "uttapam", "poha", "upma", "chilla", "paniyaram", "appam", "koozh", "bhel", "khichdi", "bath", "mudde"):
            if any(p in food_name_lower for p in ("chicken", "egg", "paneer", "tofu", "fish", "mutton", "soya", "turkey")):
                return "protein"
            return "carb"
        if dish_family in ("curry", "korma", "dal", "sambar", "egg_dish", "omelette"):
            return "protein"
        if dish_family == "soup":
            return "soup"
            
        # 3. Normalized category field from dataset (case-insensitive and plural-robust)
        category_lower = category.lower().strip()
        if category_lower in ("fruits", "fruit"):
            return "fruit"
        if category_lower in ("salad", "salads"):
            if any(p in food_name_lower for p in ("chicken", "egg", "paneer", "tofu", "fish", "mutton", "soya", "moong", "chana", "peanut")):
                return "protein"
            return "salad"
        if category_lower in ("dairy", "dairy & eggs", "curd & yogurt"):
            return "dairy"
        if category_lower in ("vegetables", "vegetable", "leafy greens", "leafy green"):
            return "vegetable"
            
        # 4. Configuration-driven pattern map in nutrition_rules.yaml
        starch_patterns = NUTRITION_RULES.get("compatibility", {}).get("starch_patterns", [])
        sandwich_patterns = NUTRITION_RULES.get("compatibility", {}).get("sandwich_patterns", [])
        if any(p in food_name_lower for p in starch_patterns):
            if any(p in food_name_lower for p in ("chicken", "egg", "paneer", "tofu", "fish", "mutton", "soya", "turkey")):
                return "protein"
            return "carb"
        if any(p in food_name_lower for p in sandwich_patterns):
            if any(p in food_name_lower for p in ("chicken", "egg", "paneer", "tofu", "fish", "mutton", "soya", "turkey")):
                return "protein"
            return "carb"
            
        # 5. Food name matching as absolute last resort
        if any(w in food_name_lower for w in ("salad", "kachumber")):
            if any(p in food_name_lower for p in ("chicken", "egg", "paneer", "tofu", "fish", "mutton", "soya", "moong", "chana", "peanut")):
                return "protein"
            return "salad"
        if any(w in food_name_lower for w in ("raita", "pachadi")):
            return "raita"
        if any(w in food_name_lower for w in ("chutney", "pickle", "achar")):
            return "chutney"
        if "papad" in food_name_lower:
            return "papad"
        if any(w in food_name_lower for w in ("soup", "shorba")):
            return "soup"
        if any(w in food_name_lower for w in ("rice", "roti", "chapati", "paratha", "parantha", "naan", "bread", "oats", "poha", "upma", "dosa", "idli", "cereal", "chilla", "cheela", "paniyaram", "appam", "koozh", "bhel", "khichdi", "bath", "sweet potato", "mudde")):
            if any(p in food_name_lower for p in ("chicken", "egg", "paneer", "tofu", "fish", "mutton", "soya", "turkey")):
                return "protein"
            return "carb"
        if any(w in food_name_lower for w in ("egg", "chicken", "fish", "paneer", "tofu", "soya", "mutton", "prawn", "dal", "chana", "rajma", "sambar", "kadhi", "korma", "curry", "bhurji", "kebab", "tikka", "peanut", "peanuts", "moong", "mung", "lentil", "lentils", "bean", "beans", "chole", "gram", "almond", "almonds")):
            return "protein"
        if any(w in food_name_lower for w in ("curd", "yogurt", "dahi", "milk", "cheese", "lassi", "buttermilk", "chaas")):
            return "dairy"
        if any(w in food_name_lower for w in ("fruit", "apple", "banana", "orange", "mango", "papaya", "grapes", "melon", "guava", "pomegranate")):
            return "fruit"
            
        return "other"

    def validate_serialized_plan(self, serialized_plan: Dict[str, Any], daily_targets: Dict[str, float], user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        report = {
            "is_valid": True,
            "critical_errors": [],
            "warnings": [],
            "stats": {}
        }
        
        warn_cal = 0.10
        crit_cal = 0.15
        warn_pro = 0.10
        crit_pro = 0.15

        if not serialized_plan:
            report["is_valid"] = False
            report["critical_errors"].append("Weekly plan is empty.")
            return report

        # Allergy checking setup
        allergies = []
        if user_profile:
            allergies = [a.lower().strip() for a in user_profile.get("allergies", []) or user_profile.get("allergens", []) or []]

        for day, meals in serialized_plan.items():
            day_cal = 0.0
            day_pro = 0.0
            day_foods = []
            exempt_foods = {'sambar', 'boiled rice (uble chawal)'}
            
            for meal_name, items in meals.items():
                if not items:
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Missing meal: {meal_name} on {day}")
                    continue

                foods_in_meal = []
                meal_cal = 0.0
                meal_pro = 0.0
                has_side_dish = False
                side_dish_cal = 0.0
                condiment_cal = 0.0

                for item in items:
                    fname = item.get('food_name', '').lower().strip()
                    unit = item.get('serving_unit', '').lower().strip()
                    qty = item.get('serving_qty', 0)
                    
                    foods_in_meal.append(fname)
                    
                    # Allergy check
                    food_allergens = str(item.get("allergens", "")).lower().strip()
                    for allergy in allergies:
                        if allergy in food_allergens:
                            report["is_valid"] = False
                            report["critical_errors"].append(f"Allergy violation: '{allergy}' found in '{item.get('food_name')}' on {day} {meal_name}")

                    # Same-day food duplicate check
                    if fname and fname not in exempt_foods:
                        if fname in day_foods:
                            report["is_valid"] = False
                            report["critical_errors"].append(f"Same-day duplicate food: '{fname}' on {day}")
                        day_foods.append(fname)
                    
                    # Nutrition
                    nut = item.get('nutrition', {})
                    c = nut.get('calories', 0)
                    p = nut.get('protein', 0)
                    meal_cal += c
                    meal_pro += p
                    
                    # Unit sanity
                    if 'rice' in fname and unit in ['tsp', 'tbsp']:
                        report["is_valid"] = False
                        report["critical_errors"].append(f"Impossible unit for {fname}: {unit} on {day} {meal_name}")
                        
                    if 'chutney' in fname or 'pickle' in fname:
                        condiment_cal += c
                        if qty > float(NUTRITION_RULES["portions"]["chutney_pickle_max_tbsp"]):
                            report["is_valid"] = False
                            report["critical_errors"].append(f"Portion exceeded for {fname}: {qty} {unit} on {day} {meal_name}")

                    if 'salad' in fname or 'raita' in fname:
                        side_dish_cal += c
                        if unit in ['bowl', 'plate'] and qty > float(NUTRITION_RULES["portions"]["salad_raita_max_bowl"]):
                            report["is_valid"] = False
                            report["critical_errors"].append(f"Portion exceeded for {fname}: {qty} {unit} on {day} {meal_name}")

                if len(set(foods_in_meal)) != len(foods_in_meal):
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Duplicate food in same meal: {foods_in_meal} on {day} {meal_name}")

                # Blueprint validation check — aligned with generator rules (relaxed)
                # Hard requirements: Protein + Carb (prevents truly broken meals)
                # Soft requirements: Vegetable, Side, Fruit/Dairy (warnings only)
                blueprint_roles = [self._map_food_to_blueprint_role(item, item.get("template_role")) for item in items]
                mt_lower = meal_name.lower()

                if mt_lower == "breakfast":
                    has_protein = "protein" in blueprint_roles
                    has_carb = "carb" in blueprint_roles
                    has_dairy = "dairy" in blueprint_roles or "raita" in blueprint_roles
                    has_fruit = "fruit" in blueprint_roles
                    # Dairy/raita counts as protein at breakfast (curd/yogurt IS a protein source)
                    has_protein_or_dairy = has_protein or has_dairy
                    if not (has_protein_or_dairy and has_carb):
                        report["is_valid"] = False
                        report["critical_errors"].append(f"Breakfast missing protein/dairy+carb on {day}: {blueprint_roles}")
                    elif not (has_fruit or has_dairy):
                        report["warnings"].append(f"Breakfast on {day} missing fruit/dairy component: {blueprint_roles}")
                elif mt_lower in ("lunch", "dinner"):
                    has_protein = "protein" in blueprint_roles
                    has_carb = "carb" in blueprint_roles
                    has_veg = "vegetable" in blueprint_roles
                    if mt_lower == "lunch":
                        has_side = any(r in blueprint_roles for r in ("salad", "raita", "chutney", "papad"))
                    else:
                        has_side = any(r in blueprint_roles for r in ("soup", "salad", "raita"))
                    if not (has_protein and has_carb):
                        report["is_valid"] = False
                        report["critical_errors"].append(f"{meal_name} missing protein or carb on {day}: {blueprint_roles}")
                    else:
                        if not has_veg:
                            report["warnings"].append(f"{meal_name} on {day} missing vegetable component: {blueprint_roles}")
                        if not has_side:
                            report["warnings"].append(f"{meal_name} on {day} missing side dish (salad/raita/soup): {blueprint_roles}")
                elif mt_lower == "snack":
                    has_snack_item = any(r in blueprint_roles for r in ("protein", "dairy", "fruit"))
                    if not has_snack_item:
                        report["is_valid"] = False
                        report["critical_errors"].append(f"Snack on {day} has no protein/dairy/fruit: {blueprint_roles}")

                # ── V6 Meal Realism Warnings (observability only) ─────────────────
                _SIZE_LIMITS = {"breakfast": 3, "lunch": 4, "dinner": 4, "snack": 2}
                size_limit = _SIZE_LIMITS.get(mt_lower, 4)
                non_water = [it for it in items if "water" not in it.get("food_name", "").lower()]
                if len(non_water) > size_limit:
                    report["warnings"].append(
                        f"{meal_name} on {day} has {len(non_water)} items (V6 limit: {size_limit})"
                    )

                _SIDE_ROLES = {"salad", "raita", "soup", "chutney", "papad", "pickle"}
                side_roles_in_meal = [r for r in blueprint_roles if r in _SIDE_ROLES]
                if len(side_roles_in_meal) > 1:
                    report["warnings"].append(
                        f"{meal_name} on {day} has multiple sides: {side_roles_in_meal}"
                    )

                if meal_cal == 0:
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Zero calories for meal {meal_name} on {day}")

                if meal_cal > 0:
                    if (condiment_cal / meal_cal) * 100 > float(NUTRITION_RULES["portions"]["condiment_max_calories_percent"]):
                        report["warnings"].append(f"Condiments exceed % cal limit on {day} {meal_name}")
                    if (side_dish_cal / meal_cal) * 100 > float(NUTRITION_RULES["portions"]["side_dish_max_calories_percent"]):
                        report["warnings"].append(f"Side dishes exceed % cal limit on {day} {meal_name}")

                day_cal += meal_cal
                day_pro += meal_pro

            target_cal = daily_targets.get(day, daily_targets).get('calories', 0)
            target_pro = daily_targets.get(day, daily_targets).get('protein', 0)

            if target_cal > 0:
                cal_diff = abs(day_cal - target_cal) / target_cal
                if cal_diff > crit_cal:
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Day {day} calories ({day_cal}) deviate critically from target ({target_cal})")
                elif cal_diff > warn_cal:
                    report["warnings"].append(f"Day {day} calories ({day_cal}) deviate from target ({target_cal})")

            if target_pro > 0:
                pro_diff = abs(day_pro - target_pro) / target_pro
                if pro_diff > crit_pro:
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Day {day} protein ({day_pro}) deviates critically from target ({target_pro})")
                elif pro_diff > warn_pro:
                    report["warnings"].append(f"Day {day} protein ({day_pro}) deviates from target ({target_pro})")

        return report
