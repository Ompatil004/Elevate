import pandas as pd
nutr = pd.read_csv('../data/nutrition_production_final_v4.csv')
meta = pd.read_csv('../data/meal_metadata.csv')
df = pd.merge(nutr, meta, on='food_id', how='left')

print('Total foods:', len(df))

def search(name):
    res = df[df['food_name'].str.contains(name, case=False, na=False)]
    for _, r in res.iterrows():
        print(f"{r['food_name']} | Role: {r['meal_role']} | Unit: {r['serving_unit']} | Qty: {r['serving_quantity']} | Min: {r.get('portion_min')} | Max: {r.get('portion_max')}")

search('Masala Dosa')
search('Gooseberry Chutney')
search('Rasam Powder')
search('Curd Dressing')
search('Pineapple Milkshake')
