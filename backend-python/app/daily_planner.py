"""
Daily Meal Planner Module

Generates complete daily meal plans using the MealBuilder system.
"""

import random
from typing import Dict, List, Optional, Set


def _generate_meal_with_retry(builder, meal_type: str, goal: str,
                              used_items: Set[str], base_seed: int,
                              retries: int = 4):
    """Generate one meal with a few fallback attempts for robustness."""
    for attempt in range(retries):
        meal = builder.generate_meal(
            meal_type=meal_type,
            include_side=True,
            goal=goal,
            used_items=used_items,
            seed=base_seed + attempt
        )
        if meal:
            return meal
    return None


def generate_day_plan(builder, goal: str = "maintain", seed: Optional[int] = None) -> Dict:
    """
    Generate a complete daily meal plan with breakfast, lunch, and dinner.
    
    Args:
        builder: MealBuilder instance with food items
        goal: Fitness goal (weight_loss, muscle_gain, maintain)
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with day plan and total calories
    """
    if seed is None:
        seed = random.randint(1, 10000)
    
    # Track used items across meals for diversity
    used_items: Set[str] = set()
    
    # Generate each meal
    breakfast = _generate_meal_with_retry(builder, "breakfast", goal, used_items, seed)
    if breakfast:
        for item in breakfast.get('items', []):
            used_items.add(item['name'])
    
    lunch = _generate_meal_with_retry(builder, "lunch", goal, used_items, seed + 100)
    if lunch:
        for item in lunch.get('items', []):
            used_items.add(item['name'])
    
    dinner = _generate_meal_with_retry(builder, "dinner", goal, used_items, seed + 200)
    if dinner:
        for item in dinner.get('items', []):
            used_items.add(item['name'])
    
    # Calculate total daily calories
    total_calories = 0
    total_protein = 0
    
    for meal in [breakfast, lunch, dinner]:
        if meal:
            total_calories += meal.get('total_calories', 0)
            total_protein += meal.get('total_protein', 0)
    
    return {
        "day_plan": {
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner
        },
        "total_calories": round(total_calories, 1),
        "total_protein": round(total_protein, 1),
        "goal": goal,
        "seed": seed,
        "meals_generated": sum(1 for m in [breakfast, lunch, dinner] if m is not None)
    }


def generate_weekly_plan(builder, goal: str = "maintain") -> Dict:
    """
    Generate a complete 7-day meal plan.
    
    Args:
        builder: MealBuilder instance with food items
        goal: Fitness goal
        
    Returns:
        Dictionary with 7-day plan
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_plan = {}
    
    for i, day in enumerate(days):
        day_plan = generate_day_plan(builder, goal=goal, seed=random.randint(1, 10000))
        weekly_plan[day] = day_plan
    
    # Calculate weekly totals
    total_calories = sum(day["total_calories"] for day in weekly_plan.values())
    avg_daily_calories = total_calories / 7
    
    return {
        "weekly_plan": weekly_plan,
        "total_weekly_calories": round(total_calories, 1),
        "avg_daily_calories": round(avg_daily_calories, 1),
        "goal": goal
    }


def format_meal_for_api(meal: Dict) -> Dict:
    """
    Format a single meal for API response.
    
    Args:
        meal: Raw meal dictionary
        
    Returns:
        Formatted meal dictionary
    """
    if not meal:
        return None
    
    return {
        "meal_type": meal.get("meal_type"),
        "items": [
            {
                "name": item.get("name"),
                "tag": item.get("tag"),
                "calories": item.get("calories"),
                "protein": item.get("protein")
            }
            for item in meal.get("items", [])
        ],
        "total_calories": meal.get("total_calories"),
        "total_protein": meal.get("total_protein"),
        "score": meal.get("score"),
        "explanation": meal.get("explanation"),
        "valid": meal.get("score", 0) >= 2
    }


def format_day_plan_for_api(day_plan: Dict) -> Dict:
    """
    Format a complete day plan for API response.
    
    Args:
        day_plan: Raw day plan dictionary
        
    Returns:
        Formatted day plan dictionary
    """
    return {
        "day_plan": {
            "breakfast": format_meal_for_api(day_plan["day_plan"]["breakfast"]),
            "lunch": format_meal_for_api(day_plan["day_plan"]["lunch"]),
            "dinner": format_meal_for_api(day_plan["day_plan"]["dinner"])
        },
        "total_calories": day_plan.get("total_calories"),
        "total_protein": day_plan.get("total_protein"),
        "goal": day_plan.get("goal"),
        "meals_generated": day_plan.get("meals_generated")
    }
