import pandas as pd
import os

# Define the paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "nutrition.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "nutrition_processed.csv")

# Unhealthy patterns to remove
UNHEALTHY_PATTERNS = [
    "shahi", "kofta", "keema", "tandoori chicken", "butter chicken",
    "bhatura", "poori", "puri", "samosa", "pakora", "fried", "kachori",
    "jalebi", "gulab jamun", "malai", "korma", "bhujia", "chips", "namkeen",
    "cookie", "biscuit", "pickle", "preserve", "achaar", "achar", "murabba",
    "cake", "pastry", "ice cream", "chocolate", "sweet", "laddu", "laddoo",
    "barfi", "peda", "halwa", "candy", "fudge", "brownie", "tart", "pie",
    "pizza", "burger", "fries", "donut", "doughnut", "muffin", "croissant"
]

# New healthy dataset additions
HEALTHY_NEW_ITEMS = [
    # Breakfast
    ["Moong Dal Chilla", "Breakfast", 180, 10.0, 25.0, 4.0, "Veg", "None", "Veg_Breakfast"],
    ["Oats Idli", "Breakfast", 140, 6.0, 24.0, 2.0, "Veg", "None", "Veg_Breakfast"],
    ["Ragi Dosa", "Breakfast", 160, 5.0, 30.0, 2.5, "Veg", "None", "Veg_Breakfast"],
    ["Vegetable Poha", "Breakfast", 190, 4.0, 35.0, 4.0, "Veg", "None", "Veg_Breakfast"],
    ["Vegetable Dalia (Broken Wheat)", "Breakfast", 170, 6.0, 32.0, 3.0, "Veg", "Wheat", "Veg_Breakfast"],
    ["Sprouts Salad (Moong)", "Breakfast", 120, 8.0, 20.0, 1.0, "Veg", "None", "Veg_Breakfast"],
    ["Besan Chilla", "Breakfast", 175, 9.0, 22.0, 5.0, "Veg", "None", "Veg_Breakfast"],
    ["Quinoa Upma", "Breakfast", 210, 7.0, 34.0, 5.0, "Veg", "None", "Veg_Breakfast"],
    ["Methi Thepla (Low Oil)", "Breakfast", 140, 4.0, 22.0, 4.0, "Veg", "Wheat", "Veg_Breakfast"],
    ["Egg White Scramble with Spinach", "Breakfast", 110, 18.0, 3.0, 2.0, "Non-Veg", "Egg", "Non-Veg_Breakfast"],
    
    # Lunch Main
    ["Soya Chunks Curry (Low Oil)", "Lunch", 220, 25.0, 18.0, 5.0, "Veg", "Soy", "Veg_Lunch"],
    ["Palak Paneer (Low Fat)", "Lunch", 240, 14.0, 10.0, 16.0, "Veg", "Milk", "Veg_Lunch"],
    ["Chicken Tikka (Air Fried)", "Lunch", 210, 30.0, 4.0, 8.0, "Non-Veg", "None", "Non-Veg_Lunch"],
    ["Grilled Fish (Rohu/Surmai)", "Lunch", 190, 25.0, 2.0, 8.0, "Non-Veg", "Fish", "Non-Veg_Lunch"],
    ["Rajma Curry (Low Oil)", "Lunch", 230, 14.0, 35.0, 4.0, "Veg", "None", "Veg_Lunch"],
    ["Chana Masala (Low Oil)", "Lunch", 220, 12.0, 35.0, 5.0, "Veg", "None", "Veg_Lunch"],
    ["Dal Tadka (Less Ghee)", "Lunch", 180, 11.0, 28.0, 4.0, "Veg", "None", "Veg_Lunch"],
    ["Tofu Bhurji", "Lunch", 190, 18.0, 8.0, 10.0, "Veg", "Soy", "Veg_Lunch"],
    ["Mushroom Matar (Low Oil)", "Lunch", 160, 8.0, 20.0, 5.0, "Veg", "None", "Veg_Lunch"],
    ["Chicken Stew with Veggies", "Lunch", 250, 28.0, 15.0, 8.0, "Non-Veg", "None", "Non-Veg_Lunch"],
    
    # Dinner Main
    ["Paneer Bhurji (Low Oil)", "Dinner", 210, 15.0, 8.0, 14.0, "Veg", "Milk", "Veg_Dinner"],
    ["Lauki Chana Dal", "Dinner", 150, 9.0, 22.0, 3.0, "Veg", "None", "Veg_Dinner"],
    ["Mixed Vegetable Stew", "Dinner", 130, 4.0, 20.0, 3.0, "Veg", "None", "Veg_Dinner"],
    ["Grilled Chicken Breast (Indian Spices)", "Dinner", 180, 35.0, 2.0, 4.0, "Non-Veg", "None", "Non-Veg_Dinner"],
    ["Masoor Dal (Light)", "Dinner", 160, 10.0, 26.0, 2.0, "Veg", "None", "Veg_Dinner"],
    ["Baingan Bharta (Low Oil)", "Dinner", 110, 3.0, 15.0, 4.0, "Veg", "None", "Veg_Dinner"],
    ["Fish Curry (Kerala Style - Low Coconut)", "Dinner", 220, 22.0, 6.0, 11.0, "Non-Veg", "Fish", "Non-Veg_Dinner"],
    ["Soya Kheema (Dry)", "Dinner", 200, 24.0, 15.0, 5.0, "Veg", "Soy", "Veg_Dinner"],
    ["Moong Dal Tadka", "Dinner", 170, 11.0, 26.0, 3.0, "Veg", "None", "Veg_Dinner"],
    ["Egg Curry (Tomato Base, 2 Eggs)", "Dinner", 200, 14.0, 10.0, 12.0, "Non-Veg", "Egg", "Non-Veg_Dinner"],
    
    # Sides (can be attached to lunch/dinner)
    ["Multigrain Roti", "Lunch", 110, 4.0, 20.0, 1.5, "Veg", "Wheat", "Veg_Side"],
    ["Multigrain Roti", "Dinner", 110, 4.0, 20.0, 1.5, "Veg", "Wheat", "Veg_Side"],
    ["Jowar Roti", "Lunch", 100, 3.0, 21.0, 1.0, "Veg", "None", "Veg_Side"],
    ["Jowar Roti", "Dinner", 100, 3.0, 21.0, 1.0, "Veg", "None", "Veg_Side"],
    ["Bajra Roti", "Lunch", 115, 3.5, 22.0, 1.5, "Veg", "None", "Veg_Side"],
    ["Bajra Roti", "Dinner", 115, 3.5, 22.0, 1.5, "Veg", "None", "Veg_Side"],
    ["Brown Rice (1 cup boiled)", "Lunch", 215, 5.0, 45.0, 1.8, "Veg", "None", "Veg_Side"],
    ["Brown Rice (1 cup boiled)", "Dinner", 215, 5.0, 45.0, 1.8, "Veg", "None", "Veg_Side"],
    ["Cucumber Tomato Salad", "Lunch", 40, 1.0, 8.0, 0.5, "Veg", "None", "Veg_Side"],
    ["Cucumber Tomato Salad", "Dinner", 40, 1.0, 8.0, 0.5, "Veg", "None", "Veg_Side"],
    
    # Snacks
    ["Roasted Makhana (Fox Nuts)", "Snack", 120, 3.0, 18.0, 4.0, "Veg", "None", "Veg_Snack"],
    ["Roasted Chana", "Snack", 140, 7.0, 20.0, 3.0, "Veg", "None", "Veg_Snack"],
    ["Boiled Peanuts", "Snack", 160, 6.0, 12.0, 10.0, "Veg", "Peanut", "Veg_Snack"],
    ["Sprouts Chaat", "Snack", 110, 7.0, 18.0, 1.0, "Veg", "None", "Veg_Snack"],
    ["Greek Yogurt with Berries", "Snack", 130, 12.0, 14.0, 3.0, "Veg", "Milk", "Veg_Snack"],
    ["Apple with Almonds", "Snack", 150, 3.0, 22.0, 7.0, "Veg", "Nut", "Veg_Snack"],
    ["Boiled Eggs (2)", "Snack", 140, 12.0, 1.0, 10.0, "Non-Veg", "Egg", "Non-Veg_Snack"],
    ["Whey Protein Shake", "Snack", 120, 24.0, 3.0, 1.5, "Veg", "Milk", "Veg_Snack"],
    ["Roasted Pumpkin Seeds", "Snack", 160, 8.0, 4.0, 13.0, "Veg", "None", "Veg_Snack"],
    ["Masala Oats (Small Bowl)", "Snack", 130, 5.0, 22.0, 3.0, "Veg", "None", "Veg_Snack"]
]

# Ensure we have the same columns as the target dataframe
columns = ["Name", "Type", "Calories", "Protein", "Carbs", "Fats", "Tags", "Allergens", "Swap_Group"]

def process_data():
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH)
        except Exception as e:
            print(f"Error reading dataset: {e}")
            return
            
        initial_len = len(df)
        print(f"Initial rows in {DATA_PATH}: {initial_len}")

        # Rename to consistent capitalized columns if they have variants
        col_map = {c: c.capitalize() if c.lower() != "swap_group" else "Swap_Group" for c in df.columns}
        if "name" in col_map: col_map["name"] = "Name"
        if "meal_type" in col_map: col_map["meal_type"] = "Type"
        if "fat" in col_map: col_map["fat"] = "Fats"
        df.rename(columns=col_map, inplace=True)

        if "Name" not in df.columns:
            print(f"Dataset columns: {df.columns.tolist()}")
            return

        # 1. Filter out unhealthy items based on name matching
        mask = pd.Series([True] * len(df))
        for pattern in UNHEALTHY_PATTERNS:
            mask = mask & (~df['Name'].str.lower().str.contains(pattern, na=False))
        
        df_clean = df[mask].copy()
        print(f"Removed {initial_len - len(df_clean)} unhealthy rows.")

        # 3. Add new healthy items
        new_df = pd.DataFrame(HEALTHY_NEW_ITEMS, columns=columns)
        
        # If dataset has extra columns (like food_category or goal_tag), handle them
        for col in df_clean.columns:
            if col not in new_df.columns:
                if col == "goal_tag":
                    new_df[col] = "Maintain" # default
                elif col == "food_category":
                    # Assign food_category based on meal type or name
                    def get_cat(row):
                        if row["Type"] == "Snack": return "snack"
                        elif "Side" in row["Swap_Group"]: return "side_dish"
                        elif "Roti" in row["Name"] or "Rice" in row["Name"] or "Salad" in row["Name"]: return "side_dish"
                        else: return "main_meal"
                    new_df[col] = new_df.apply(get_cat, axis=1)
                else:
                    new_df[col] = ""
                    
        df_final = pd.concat([df_clean, new_df], ignore_index=True)
        
        # Drop duplicates to prevent stacking the 50 healthy items on repeated runs
        df_final = df_final.drop_duplicates(subset=['Name'], keep='first')
        
        print(f"Added {len(new_df)} healthy rows. Final row count: {len(df_final)}")
        
        # Save to both locations
        df_final.to_csv(DATA_PATH, index=False)
        print(f"Saved to {DATA_PATH}")
        
        # In processed CSV we also save
        if os.path.exists(PROCESSED_DATA_PATH):
            df_final.to_csv(PROCESSED_DATA_PATH, index=False)
            print(f"Saved to {PROCESSED_DATA_PATH}")
        else:
            print(f"{PROCESSED_DATA_PATH} not found, only saved {DATA_PATH}")

if __name__ == "__main__":
    process_data()
