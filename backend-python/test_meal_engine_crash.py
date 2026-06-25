import sys
import os

sys.path.insert(0, r"D:\Final Year Project\githubclone 22 mor\githubclone\ELEVATE_GITHUB\Elevate\backend-python")

from app.workout_engine import WorkoutEngine
from app.meal_engine import get_meal_engine

def test():
    w = WorkoutEngine()
    e = get_meal_engine()
    
    profile = {
        'user_id': '123',
        'age': 30,
        'weight': 70,
        'height': 175,
        'gender': 'Male',
        'goal': 'Weight Loss',
        'dietary_preference': 'Vegetarian',
        'allergies': [],
        'activity_level': 'Moderate',
        'weekly_workout_plan': []
    }
    
    print("Testing generate_weekly_plan...")
    try:
        w_plan = w.generate_weekly_plan(profile)
        print("Success! Got workout plan.")
    except Exception as ex:
        import traceback
        traceback.print_exc()

    print("Testing generate_meal_plan...")
    try:
        plan = e.generate_meal_plan(profile)
        weekly = plan.get("weekly_plan", {})
        print("Success! Got meal plan.")
        
        # --- Variety Check ---
        print("\n" + "="*60)
        print(" MEAL VARIETY CHECK (max 2 repeats = PASS)")
        print("="*60)
        meal_id_counts = {}
        for day, meals in weekly.items():
            print(f"\n  {day}:")
            for meal_type, items in meals.items():
                if items:
                    name = items[0].get("food_name", "?")
                    meal_id = items[0].get("semantics", {}).get("meal_name", name)
                    print(f"    {meal_type:12s}: {meal_id}")
                    meal_id_counts[meal_id] = meal_id_counts.get(meal_id, 0) + 1

        print("\n  === Repeat Count ===")
        max_repeats = 0
        for mid, cnt in sorted(meal_id_counts.items(), key=lambda x: -x[1]):
            flag = "REPEAT" if cnt > 2 else "OK"
            if cnt > 1:
                print(f"  [{flag}]  '{mid}': {cnt}x")
            max_repeats = max(max_repeats, cnt)
        print(f"\n  Max repeats: {max_repeats}  {'PASS' if max_repeats <= 2 else 'NEEDS REVIEW'}")

        # --- Swap Options Quality Test ---
        print("\n" + "="*60)
        print(" SWAP OPTIONS QUALITY TEST")
        print("="*60)
        monday = weekly.get("Monday", weekly.get("Day_1", {}))
        breakfast_items = monday.get("breakfast", [])
        if breakfast_items:
            item = breakfast_items[0]
            food_name = item.get("food_name", "")
            cal = float(item.get("calories", 0))
            prot = float(item.get("protein", 0))
            print(f"\n  Original: {food_name}  |  {cal:.1f} kcal  |  {prot:.1f}g protein")
            
            swaps = e.get_swap_options(food_name, "breakfast", profile,
                                       target_calories=cal, target_protein=prot)
            if swaps:
                for s in swaps:
                    cal_diff_pct = abs(s['calories'] - cal) / max(cal, 1) * 100
                    flag = "CLOSE" if cal_diff_pct <= 25 else "FAR"
                    print(f"  [{flag}]  {s['food_name']:35s}  {s['calories']:6.1f} kcal ({cal_diff_pct:4.0f}% diff)  {s['protein']:5.1f}g prot  |  {s['serving']}")
            else:
                print("  No swaps found (food may not have similar family members).")

    except Exception as ex:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
