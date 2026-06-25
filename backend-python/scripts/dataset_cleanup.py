import json
import os

def clean_dataset():
    filepath = 'data/food_knowledge_base.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Cleanups
    for food_id, item in data.items():
        name = item.get("food_name", "").lower()
        diet_type = item.get("diet_type", "")
        
        # 1. Eggitarian fix
        if diet_type == "Vegetarian" and any(x in name for x in ["egg ", " eggs", "anda", "omelette", "omelet", "egg nog"]):
            item["diet_type"] = "Eggitarian"
            
        # 2. Vegan fix
        if diet_type in ["Vegetarian", "Eggitarian"] and any(x in name for x in ["tofu", "soya chunks", "tempeh"]) and not any(x in name for x in ["paneer", "milk", "cheese", "curd", "yogurt", "egg"]):
            item["diet_type"] = "Vegan"

        # 3. Russian Salad usage penalty
        if "russian salad" in name:
            if "meal_priority" in item:
                # Lower the score across all meals to make it a fallback, not a favorite
                for m in item["meal_priority"]:
                    val = item["meal_priority"][m]
                    if isinstance(val, dict):
                        item["meal_priority"][m]["score"] = min(0.3, val.get("score", 0.3))
                    else:
                        item["meal_priority"][m] = min(0.3, float(val))

        # 4. Murmura (Puffed rice) shouldn't be a primary dinner side. 
        if "murmura" in name or "puffed rice" in name:
            if "meal_priority" in item:
                for m in ["lunch", "dinner", "snack"]:
                    if m in item["meal_priority"] and isinstance(item["meal_priority"][m], dict):
                        item["meal_priority"][m]["score"] = 0.4 if m == "lunch" else 0.1 if m == "dinner" else 0.9
                    else:
                        item["meal_priority"][m] = 0.4 if m == "lunch" else 0.1 if m == "dinner" else 0.9

        # 5. Deviled eggs and heavy eggs shouldn't naturally accompany Pulao as a side.
        if "deviled egg" in name:
            if "meal_priority" in item:
                for m, score in [("dinner", 0.2), ("lunch", 0.4), ("breakfast", 0.9)]:
                    if m in item["meal_priority"] and isinstance(item["meal_priority"][m], dict):
                        item["meal_priority"][m]["score"] = score
                    else:
                        item["meal_priority"][m] = score
                
        # Make paneer pulao highly prioritized for lunch/dinner so it doesn't just randomly appear in odd combos
        if "paneer pulao" in name:
             if "meal_priority" in item:
                for m, score in [("dinner", 0.9), ("lunch", 0.9), ("breakfast", 0.0)]:
                    if m in item["meal_priority"] and isinstance(item["meal_priority"][m], dict):
                        item["meal_priority"][m]["score"] = score
                    else:
                        item["meal_priority"][m] = score

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("Dataset cleanup complete. Eggs classified to Eggitarian, meal suitability adjusted for Russian Salad, Murmura, and Deviled Egg.")

if __name__ == "__main__":
    clean_dataset()
