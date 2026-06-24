import pandas as pd
nutr = pd.read_csv('../data/nutrition_production_final_v4.csv')
for name in ['Masala Dosa', 'Gooseberry Chutney', 'Rasam Powder', 'Curd Dressing', 'Pineapple Milkshake']:
    res = nutr[nutr['food_name'].str.contains(name, case=False, na=False)]
    for _, r in res.iterrows():
        print(f"{r['food_name']} | Cat: {r['category']} | MealType: {r['meal_type']}")
