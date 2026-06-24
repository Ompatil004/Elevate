import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'nutrition_production_final_v2.csv')
CLEAN_CSV_PATH = os.path.join(BASE_DIR, 'data', 'nutrition_production_v3_clean.csv')

def is_unhealthy(name):
    name = str(name).lower()
    
    # 1. Desserts, Sweets, High Sugar
    sweets = ['ladoo', 'kheer', 'barfi', 'halwa', 'chocolate', 'butterscotch', 'squash', 'putharekulu', 
              'jalebi', 'gulab jamun', 'rasgulla', 'rasmalai', 'peda', 'sandesh', 'pastry', 'cake', 
              'biscuit', 'rusk', 'candy', 'toffee', 'custard', 'choux', 'swan', 'sweet', 'shrikhand', 'payasam']
    
    # 2. Deep Fried / Greasy / High Glycemic
    fried = ['samosa', 'kachori', 'puri', 'bhatura', 'bhature', 'luchi', 'mathri', 'vada', 'pakora', 
             'bhajiya', 'cutlet', 'fries', 'chips', 'churma', 'bonda', 'bhajji']
             
    # 3. Processed Fast Food
    fast_food = ['macaroni', 'mayonnaise', 'burger', 'pizza', 'hot dog', 'frankie']
    
    # 4. Ultra-Rich / Heavy Cream Curries
    rich_curries = ['shahi', 'makhani', 'malai']
    
    # Check if name contains any unhealthy keywords
    for word in sweets + fried + fast_food + rich_curries:
        if word in name.split() or f" {word} " in f" {name} ":
            # Handle some exceptions like "sweet potato" which is healthy
            if word == 'sweet' and 'sweet potato' in name:
                continue
            return True
            
    # Explicit full string matches for specific bad items observed
    if 'with squashes' in name: return True
    if 'lemonade' in name: return True
    if 'fruit punch' in name: return True # Just liquid sugar
    
    return False

def run_purge():
    print("Starting Unhealthy Foods Purge...")
    df = pd.read_csv(CSV_PATH)
    initial_count = len(df)
    
    # 1. Purge Unhealthy Foods
    df['is_unhealthy'] = df['food_name'].apply(is_unhealthy)
    
    # Keep track of what we delete for the report
    deleted_df = df[df['is_unhealthy'] == True]
    deleted_foods = deleted_df['food_name'].tolist()
    
    # Filter the dataset
    df = df[df['is_unhealthy'] == False]
    df = df.drop(columns=['is_unhealthy'])
    
    final_count = len(df)
    deleted_count = initial_count - final_count
    
    # 2. Fix Meal Timings (Move heavy proteins to Lunch/Dinner)
    shifted_count = 0
    shifted_foods = []
    
    for i, row in df.iterrows():
        meal = str(row.get('meal_type', ''))
        is_heavy_protein = row.get('contains_meat') == True or row.get('contains_fish') == True
        name = str(row['food_name']).lower()
        
        # Heavy curries or meat shouldn't be breakfast
        is_heavy_curry = 'curry' in name or 'kofta' in name or 'roghan josh' in name or 'korma' in name or 'tikka' in name
        
        if (is_heavy_protein or is_heavy_curry):
            if meal.lower() in ['breakfast', 'snack', 'pre workout', 'post workout']:
                df.at[i, 'meal_type'] = 'Dinner' # Default to dinner
                shifted_count += 1
                shifted_foods.append(row['food_name'])
                
    df.to_csv(CLEAN_CSV_PATH, index=False)
    
    print("=" * 60)
    print("UNHEALTHY FOODS PURGE REPORT")
    print("=" * 60)
    print(f"Initial Foods       : {initial_count}")
    print(f"Foods Deleted       : {deleted_count}")
    print(f"Final Foods Remaining : {final_count}")
    print(f"Meal Timings Shifted: {shifted_count}")
    print("-" * 60)
    print("Sample of Deleted Foods:")
    for f in deleted_foods[:10]:
        print(f"  - {f}")
    print("-" * 60)
    print("Sample of Shifted Meal Timings (To Lunch/Dinner):")
    for f in shifted_foods[:10]:
        print(f"  - {f}")
    print("=" * 60)
    print(f"Clean dataset successfully saved to: {CLEAN_CSV_PATH}")

if __name__ == '__main__':
    run_purge()
