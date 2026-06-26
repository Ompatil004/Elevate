import os
import yaml

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "nutrition_rules.yaml")

def load_nutrition_rules():
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load nutrition_rules.yaml: {e}")
        return {
            "variety": {
                "same_food_max_frequency_days": 2,
                "meal_identity_max_frequency_days": 3,
                "protein_source_consecutive_max": 2,
                "cuisine_daily_max": 2,
                "cooking_style_consecutive_max": 2
            },
            "portions": {
                "chutney_pickle_max_tbsp": 2.0,
                "salad_raita_max_bowl": 1.0,
                "condiment_max_calories_percent": 5.0,
                "side_dish_max_calories_percent": 20.0,
                "side_dish_multiplier_max": 1.0
            },
            "retry_limits": {
                "candidate": 20,
                "meal": 10,
                "day": 5,
                "week": 2
            },
            "validation_thresholds": {
                "warning_protein_deviation_percent": 5.0,
                "warning_calorie_deviation_percent": 5.0,
                "critical_protein_deviation_percent": 15.0,
                "critical_calorie_deviation_percent": 15.0
            }
        }

NUTRITION_RULES = load_nutrition_rules()
