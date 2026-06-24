import pandas as pd
import re

def main():
    print("Loading datasets...")
    nutr = pd.read_csv('../data/nutrition_production_final_v4.csv')
    meta = pd.read_csv('../data/meal_metadata.csv')

    # Merge to get food_name and category
    df = pd.merge(meta, nutr[['food_id', 'food_name', 'category']], on='food_id', how='left')

    print("Initial items:", len(df))

    # Add new columns
    df['food_category'] = df['category']
    df['can_be_primary_meal'] = False
    df['max_serving_multiplier'] = 2.0  # default to 2x max

    # Define regex patterns
    condiment_pattern = re.compile(r'\b(chutney|sauce|powder|masala|dressing|pickle|achaar|dip|syrup|paste|podi|preserve|spice|blend|relish|chutneys|powders|masalas)\b', re.IGNORECASE)
    beverage_pattern = re.compile(r'\b(milkshake|drink|juice|tea|coffee|smoothie|water|squash|cordial|shake)\b', re.IGNORECASE)
    dessert_pattern = re.compile(r'\b(burfi|halwa|ladoo|kheer|payasam|sweet|dessert|mithai|cake|ice cream|brownie|jalebi|rasgulla|gulab jamun|chikki|peda|barfi|pudding)\b', re.IGNORECASE)

    # 1. Update Condiments
    cond_mask = df['food_name'].str.contains(condiment_pattern, regex=True, na=False)
    
    # Exceptions (e.g., Masala Dosa)
    main_dish_keywords = r'\b(dosa|chicken|paneer|meat|mutton|fish|egg|eggs|rice|roti|dal|sabzi|chops|curry|gravy|biryani|pulao|khichdi|idli|vada|upma|poha)\b'
    cond_exception_mask = df['food_name'].str.contains(main_dish_keywords, regex=True, na=False, flags=re.IGNORECASE)
    
    true_cond_mask = cond_mask & ~cond_exception_mask
    
    df.loc[true_cond_mask, 'food_category'] = 'Condiment'
    df.loc[true_cond_mask, 'meal_role'] = 'condiment'
    df.loc[true_cond_mask, 'can_be_primary_meal'] = False
    df.loc[true_cond_mask, 'portion_max'] = 30.0

    # 2. Update Beverages
    bev_mask = df['food_name'].str.contains(beverage_pattern, regex=True, na=False)
    df.loc[bev_mask, 'food_category'] = 'Beverage'
    df.loc[bev_mask, 'meal_role'] = 'beverage'
    df.loc[bev_mask, 'can_be_primary_meal'] = False
    df.loc[bev_mask, 'serving_unit'] = 'ml'

    # 3. Update Desserts
    des_mask = df['food_name'].str.contains(dessert_pattern, regex=True, na=False)
    df.loc[des_mask, 'food_category'] = 'Dessert'
    df.loc[des_mask, 'meal_role'] = 'dessert'
    df.loc[des_mask, 'can_be_primary_meal'] = False

    # 4. Mark Primary Meals
    primary_roles = ['combo_meal', 'protein_main', 'carb_base']
    df.loc[df['meal_role'].isin(primary_roles), 'can_be_primary_meal'] = True

    # Save to CSV
    cols_to_save = [
        'food_id', 'serving_unit', 'serving_quantity', 'serving_weight_g', 
        'meal_role', 'swap_group', 'meal_pair_group', 
        'portion_min', 'portion_max', 'portion_step', 
        'budget_level', 'availability',
        'food_category', 'can_be_primary_meal', 'max_serving_multiplier'
    ]
    
    meta_new = df[cols_to_save]
    meta_new.to_csv('../data/meal_metadata.csv', index=False)
    print("Updated meal_metadata.csv")

if __name__ == '__main__':
    main()
