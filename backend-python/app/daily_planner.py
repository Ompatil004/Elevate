"""
Daily Meal Planner Module

Generates complete daily meal plans using the MealBuilder system.
Produces 4 meal slots: breakfast, lunch, snack, and dinner.
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
    Generate a complete daily meal plan with breakfast, lunch, snack, and dinner.
    
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

    # ── Snack slot (Section 4.1 of plan) ───────────────────────────────────
    # Calorie targets by goal:
    #   weight_loss  → 150–250 kcal  (1–2 light items)
    #   maintain     → 200–300 kcal  (2–3 items)
    #   weight_gain  → 300–450 kcal  (3–4 items)
    snack = _generate_snack(builder, goal, used_items, seed + 300)
    if snack:
        for item in snack.get('items', []):
            used_items.add(item['name'])

    dinner = _generate_meal_with_retry(builder, "dinner", goal, used_items, seed + 200)
    if dinner:
        for item in dinner.get('items', []):
            used_items.add(item['name'])
    
    # Calculate total daily calories
    total_calories = 0
    total_protein = 0
    
    for meal in [breakfast, lunch, snack, dinner]:
        if meal:
            total_calories += meal.get('total_calories', 0)
            total_protein += meal.get('total_protein', 0)
    
    return {
        "day_plan": {
            "breakfast": breakfast,
            "lunch": lunch,
            "snack": snack,
            "dinner": dinner
        },
        "total_calories": round(total_calories, 1),
        "total_protein": round(total_protein, 1),
        "goal": goal,
        "seed": seed,
        "meals_generated": sum(1 for m in [breakfast, lunch, snack, dinner] if m is not None)
    }


def _get_snack_calorie_range(goal: str):
    """Return (min_cal, max_cal) for snack slot based on goal."""
    goal_key = str(goal).strip().lower().replace(' ', '_').replace('muscle_gain', 'weight_gain')
    return {
        'weight_loss': (150, 250),
        'maintain':    (200, 300),
        'weight_gain': (300, 450),
    }.get(goal_key, (200, 300))


def _generate_snack(builder, goal: str, used_items: Set[str], seed: int) -> Optional[Dict]:
    """
    Generate a snack with a lighter calorie target than full meals.

    Snacks are generated from the protein and side pools to favour:
    - High-protein options (chana, boiled egg, paneer)
    - Light carbs (fruit, poha)
    - Sides (raita, buttermilk)
    """
    cal_min, cal_max = _get_snack_calorie_range(goal)
    rng = random.Random(seed)

    if not builder.food_items:
        return None

    if not builder.tagged_items:
        builder._tag_all_items()

    # Snack pool: protein + carb + side items, avoid heavy mains
    snack_pool = (
        builder.get_items_by_tag('protein') +
        builder.get_items_by_tag('side') +
        [i for i in builder.get_items_by_tag('carb') if i.get('calories', 999) < 250]
    )

    # Prefer items not already used today
    fresh_pool = [i for i in snack_pool if i.get('name') not in used_items]
    pool = fresh_pool if fresh_pool else snack_pool

    if not pool:
        return None

    best_snack = None
    best_penalty = float('inf')

    for _ in range(40):
        # Pick 1–3 items depending on goal
        count = 1 if cal_max <= 250 else (2 if cal_max <= 350 else 3)
        count = min(count, len(pool))
        items_raw = rng.sample(pool, count)

        items = [
            {
                'name': item.get('name', ''),
                'tag': builder.assign_food_tag(item.get('name', '')),
                'calories': round(float(item.get('calories', 0) or 0), 1),
                'protein': round(float(item.get('protein', 0) or 0), 1),
                'carbs': round(float(item.get('carbs', 0) or 0), 1),
                'fat': round(float(item.get('fat', 0) or 0), 1),
            }
            for item in items_raw
        ]

        total_cal = sum(i['calories'] for i in items)
        total_prot = sum(i['protein'] for i in items)

        in_range = cal_min <= total_cal <= cal_max
        penalty = 0 if in_range else min(
            abs(total_cal - cal_min),
            abs(total_cal - cal_max)
        )

        if penalty < best_penalty and total_cal >= 80:  # minimum viable snack
            best_penalty = penalty
            best_snack = {
                'meal_type': 'snack',
                'items': items,
                'total_calories': round(total_cal, 1),
                'calories': round(total_cal, 1),
                'protein': round(total_prot, 1),
                'total_protein': round(total_prot, 1),
                'carbs': round(sum(i['carbs'] for i in items), 1),
                'fat': round(sum(i['fat'] for i in items), 1),
                'score': 2,
                'explanation': f'Light snack ({int(total_cal)} kcal) — keeps energy stable between meals.',
            }
            if in_range:
                break

    return best_snack


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
    Includes the snack slot alongside the three main meals.
    
    Args:
        day_plan: Raw day plan dictionary
        
    Returns:
        Formatted day plan dictionary with breakfast, lunch, snack, dinner
    """
    dp = day_plan.get("day_plan", {})
    return {
        "day_plan": {
            "breakfast": format_meal_for_api(dp.get("breakfast")),
            "lunch":     format_meal_for_api(dp.get("lunch")),
            "snack":     format_meal_for_api(dp.get("snack")),
            "dinner":    format_meal_for_api(dp.get("dinner")),
        },
        "total_calories":  day_plan.get("total_calories"),
        "total_protein":   day_plan.get("total_protein"),
        "goal":            day_plan.get("goal"),
        "meals_generated": day_plan.get("meals_generated")
    }
