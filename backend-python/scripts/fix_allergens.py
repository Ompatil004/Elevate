import pandas as pd
import numpy as np
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# We will read from the V2 file and overwrite it to keep all the 3-tier nutrition updates
CSV_PATH = os.path.join(BASE_DIR, 'data', 'nutrition_production_final_v2.csv')

def run_allergen_fix():
    print("Starting Deep Allergen Fix...")
    df = pd.read_csv(CSV_PATH)
    
    # Dictionary of robust keywords for Indian and global foods
    allergen_rules = {
        "Milk": [
            'milk', 'cheese', 'dairy', 'paneer', 'curd', 'yogurt', 'yoghurt', 'ghee', 'butter', 'lassi', 
            'buttermilk', 'malai', 'cream', 'whey', 'chai', 'cappuccino', 'latte', 'macchiato', 'kheer', 
            'rabri', 'kulfi', 'mawa', 'khoya', 'chaas', 'raita', 'sandesh', 'rasgulla', 'gulab jamun', 
            'rasmalai', 'peda', 'barfi', 'shrikhand', 'payasam', 'makhani', 'kofta', 'malai', 'milkshake', 
            'chhaas', 'dahi'
        ],
        "Egg": [
            'egg', 'anda', 'bhurji', 'omelet', 'omelette', 'mayonnaise', 'meringue', 'frittata', 'shakshuka',
            'egg roll', 'baida'
        ],
        "Fish": [
            'fish', 'macha', 'machher', 'macchi', 'rohu', 'katla', 'hilsa', 'surmai', 'pomfret', 'basa', 
            'salmon', 'tuna', 'bombay duck', 'moilee', 'mach', 'meen'
        ],
        "Shellfish": [
            'prawn', 'shrimp', 'crab', 'lobster', 'mussel', 'oyster', 'squid', 'calamari', 'jhinga', 'chingri', 'era', 'Royyalu'
        ],
        "Peanuts": [
            'peanut', 'groundnut', 'moongfali', 'mungfali', 'singdana', 'chikki'
        ],
        "Tree Nuts": [
            'almond', 'cashew', 'walnut', 'pecan', 'pistachio', 'hazelnut', 'macadamia', 'pine nut', 
            'badam', 'kaju', 'pista', 'akhrot', 'chironji', 'nut', 'marzipan', 'praline'
        ],
        "Soy": [
            'soy', 'soya', 'tofu', 'tempeh', 'edamame', 'soyabean', 'nutrela', 'miso', 'soy sauce', 'tamari', 'textured vegetable protein', 'tvp'
        ],
        "Gluten": [
            'wheat', 'gluten', 'bread', 'pasta', 'roti', 'chapati', 'paratha', 'naan', 'kulcha', 'puri', 
            'bhatura', 'oat', 'barley', 'rye', 'maida', 'sooji', 'suji', 'rava', 'semolina', 'seitan', 
            'dalia', 'bulgur', 'couscous', 'noodle', 'macaroni', 'spaghetti', 'pizza', 'burger', 'bun', 
            'pav', 'rusk', 'biscuit', 'cake', 'pastry', 'samosa', 'kachori', 'mathri', 'wrap', 'roll',
            'spelt', 'farro', 'pita', 'bagel', 'muffin', 'pancake', 'waffle', 'puri', 'luchi', 'churma',
            'halwa', 'upma', 'bhature', 'thepla', 'khakhra', 'noodles', 'momos', 'momo', 'vermicelli', 'seviyan'
        ],
        "Sesame": [
            'sesame', 'til', 'tahini', 'tilgul', 'gajak', 'rewri'
        ]
    }
    
    # Exceptions that might match but shouldn't (e.g., coconut is not a tree nut for FDA strictly but sometimes is, water chestnut is not)
    # Actually, we will just use regex word boundaries
    
    compiled_rules = {}
    for allergen, words in allergen_rules.items():
        # Match whole words or substrings properly. For instance, 'nut' matches 'nutrela' if we aren't careful, but soy takes precedence.
        # We'll use word boundaries where appropriate or just direct substring if it's safe.
        pattern = r'\b(?:' + '|'.join(map(re.escape, words)) + r')\b'
        compiled_rules[allergen] = re.compile(pattern)
        
    counts = {
        'total_updated': 0,
        'None': 0,
        'Milk': 0,
        'Egg': 0,
        'Fish': 0,
        'Shellfish': 0,
        'Peanuts': 0,
        'Tree Nuts': 0,
        'Soy': 0,
        'Gluten': 0,
        'Sesame': 0
    }
    
    for i, row in df.iterrows():
        name = str(row['food_name']).lower()
        
        found_allergens = set()
        
        for allergen, pattern in compiled_rules.items():
            if pattern.search(name):
                found_allergens.add(allergen)
                
        # Special overrides for "coconut" -> Not a tree nut for our strict definition, unless specifically requested
        # Special overrides: if 'peanut' is found, it's not a 'tree nut', but the word 'nut' might trigger 'tree nut'.
        if 'peanut' in name or 'groundnut' in name:
            found_allergens.add('Peanuts')
            
        # If 'nutrela' is found, it has 'nut' but it's soy.
        if 'nutrela' in name:
            if 'Tree Nuts' in found_allergens:
                found_allergens.remove('Tree Nuts')
                
        # Black coffee / Green tea -> no milk!
        if any(x in name for x in ['black coffee', 'green tea', 'black tea', 'herbal tea', 'lemon tea', 'iced tea', 'espresso', 'americano']):
            if 'Milk' in found_allergens:
                found_allergens.remove('Milk')
                
        # Plain oats are technically GF in some places, but user specifically said "Oats -> Gluten (only if not certified gluten-free)"
        # So we keep Gluten for oats.
        
        # Vegan foods shouldn't have dairy/egg/meat
        if row.get('is_vegan') == True:
            if 'Milk' in found_allergens: found_allergens.remove('Milk')
            if 'Egg' in found_allergens: found_allergens.remove('Egg')
            if 'Fish' in found_allergens: found_allergens.remove('Fish')
            if 'Shellfish' in found_allergens: found_allergens.remove('Shellfish')
            
        if len(found_allergens) > 0:
            # Sort to make it deterministic
            allergen_str = ", ".join(sorted(list(found_allergens)))
        else:
            allergen_str = "None"
            
        df.at[i, 'allergens'] = allergen_str
        counts['total_updated'] += 1
        
        if allergen_str == "None":
            counts['None'] += 1
        else:
            for a in found_allergens:
                counts[a] += 1
                
    df.to_csv(CSV_PATH, index=False)
    
    print("=" * 50)
    print("ALLERGEN VALIDATION REPORT")
    print("=" * 50)
    print(f"Total allergen fields updated : {counts['total_updated']}")
    print(f"Total foods with 'None'       : {counts['None']}")
    print(f"Total foods containing Milk   : {counts['Milk']}")
    print(f"Total foods containing Egg    : {counts['Egg']}")
    print(f"Total foods containing Fish   : {counts['Fish']}")
    print(f"Total foods containing Shellfish: {counts['Shellfish']}")
    print(f"Total foods containing Peanuts: {counts['Peanuts']}")
    print(f"Total foods containing Tree Nuts: {counts['Tree Nuts']}")
    print(f"Total foods containing Soy    : {counts['Soy']}")
    print(f"Total foods containing Gluten : {counts['Gluten']}")
    print(f"Total foods containing Sesame : {counts['Sesame']}")
    print("=" * 50)
    print(f"Successfully updated: {CSV_PATH}")

if __name__ == '__main__':
    run_allergen_fix()
