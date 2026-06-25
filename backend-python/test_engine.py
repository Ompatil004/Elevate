import asyncio
import os
import sys

# Ensure backend-python is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.nutrition_engine.engine import NutritionEngineV6

async def run_test():
    engine = NutritionEngineV6()
    profile = {
        "age": 32,
        "gender": "male",
        "weight_kg": 60,
        "height_cm": 170,
        "activity_level": "moderate",
        "goal": "muscle_gain",
        "diet_type": "NonVeg",
        "cuisine_preferences": ["North Indian", "South Indian", "Pan Indian"]
    }
    
    print("Generating weekly plan...")
    plan = engine.generate_plan(profile)
    
    print("\nGeneration Stats:")
    print(plan.get("stats", {}))
    
    print("\nSample Day 1:")
    day1 = plan.get("plan", {}).get("Day_1", {})
    for meal_type, items in day1.items():
        print(f"  {meal_type.upper()}:")
        for item in items:
            name = item.get("food_name", "")
            qty = item.get("serving_qty", "")
            unit = item.get("serving_unit", "")
            cal = item.get("nutrition", {}).get("calories", 0)
            pro = item.get("nutrition", {}).get("protein", 0)
            print(f"    - {qty} {unit} {name} (Cal: {cal:.0f}, Pro: {pro:.1f}g)")

if __name__ == "__main__":
    asyncio.run(run_test())
