def get_food_family(name: str, swap_group: str) -> str:
    n = str(name).lower()
    sg = str(swap_group).lower()
    
    if 'sandwich' in n: return 'Sandwich'
    if 'salad' in n or 'kosambari' in n: return 'Salad'
    if 'raita' in n or 'pachadi' in n: return 'Raita'
    if 'soup' in n or 'shorba' in n or 'broth' in n: return 'Soup'
    if 'milkshake' in n or 'smoothie' in n or 'lassi' in n or 'drink' in n or 'juice' in n: return 'Drink'
    if 'fruit' in n or sg == 'fruits': return 'Fruit'
    if sg == 'yogurt/curd' or 'curd' in n or 'yogurt' in n: return 'Yogurt'
    if 'oats' in n or 'oatmeal' in n or 'porridge' in n or 'muesli' in n: return 'Oats'
    if 'dosa' in n or 'idli' in n or 'uttapam' in n or 'paniyaram' in n: return 'South Indian Breakfast'
    if 'paratha' in n or 'thepla' in n or 'cheela' in n or 'chilla' in n: return 'Paratha'
    # ── Granular families for swap-option matching ──────────────────────────
    # Rice-based staples
    if 'biryani' in n or 'pulao' in n: return 'Rice'
    if 'khichdi' in n or 'bisi bele' in n: return 'Rice'
    if 'rice' in n: return 'Rice'
    # Roti / Bread family — so swaps for roti only return other breads
    if 'roti' in n or 'chapati' in n or 'phulka' in n or 'naan' in n: return 'Roti'
    if 'bread' in n or 'toast' in n: return 'Roti'
    # Dal & Lentils
    if 'dal' in n or 'lentil' in n or 'sambar' in n or 'rasam' in n: return 'Dal'
    # Animal proteins — separate families for better swaps
    if 'chicken' in n or sg == 'chicken/meat': return 'Chicken'
    if 'mutton' in n or 'lamb' in n or 'pork' in n or 'beef' in n: return 'Meat'
    if 'fish' in n or 'prawn' in n or 'seafood' in n or sg == 'fish & seafood': return 'Fish'
    if 'egg' in n or sg == 'eggs': return 'Eggs'
    # Paneer / Tofu
    if 'paneer' in n or sg == 'paneer': return 'Paneer'
    if 'tofu' in n or sg == 'tofu & soy' or 'soya' in n or 'soy' in n: return 'Tofu'
    # Vegetables / Curry / Sabzi
    if 'sabzi' in n or 'curry' in n or 'masala' in n: return 'Curry'
    if 'pasta' in n or 'noodles' in n or 'thukpa' in n: return 'Pasta'
    
    return sg.title() if sg else 'Other'

def get_primary_unit(food_name: str) -> str:
    """
    Centralized Serving Unit Registry (Phase 5).
    Returns the strict household unit for a given food.
    Returns None if no specific unit is found.
    """
    n = str(food_name).lower()
    
    # Precise overrides first
    if 'bhel' in n: return 'bowl'
    if 'poha' in n: return 'bowl'
    if 'upma' in n: return 'bowl'
    if 'idli' in n: return 'piece'
    if 'dosa' in n or 'cheela' in n or 'chilla' in n or 'pancake' in n: return 'piece'
    if 'roti' in n or 'chapati' in n or 'phulka' in n or 'naan' in n or 'paratha' in n or 'thepla' in n: return 'piece'
    if 'bread' in n or 'toast' in n: return 'slice'
    if 'sandwich' in n: return 'sandwich'
    if 'egg' in n and not any(x in n for x in ['curry', 'bhurji', 'salad', 'nog', 'soup']): return 'piece'
    if 'chutney' in n: return 'tbsp'
    if 'pickle' in n or 'achar' in n: return 'tbsp'
    if n in ['butter', 'oil', 'ghee', 'olive oil', 'mustard oil', 'coconut oil', 'sesame oil', 'peanut oil', 'sunflower oil', 'canola oil']: return 'tsp'
    if 'whey' in n or 'protein powder' in n: return 'scoop'
    if 'tea' in n or 'coffee' in n: return 'cup'
    if 'buttermilk' in n or 'chaas' in n or 'lassi' in n or 'drink' in n or 'juice' in n: return 'glass'
    if 'milk' in n and 'shake' not in n: return 'glass'
    if 'shake' in n or 'smoothie' in n: return 'glass'
    if 'banana' in n or 'apple' in n or 'orange' in n or 'guava' in n: return 'medium fruit'
    if 'salad' in n or 'kosambari' in n or 'kachumber' in n or 'tossed' in n: return 'bowl'
    if 'raita' in n or 'pachadi' in n: return 'bowl'
    if 'dal' in n or 'lentil' in n or 'sambar' in n or 'rasam' in n: return 'bowl'
    if 'soup' in n or 'shorba' in n or 'broth' in n: return 'bowl'
    if 'oats' in n or 'oatmeal' in n or 'porridge' in n: return 'bowl'
    if 'yogurt' in n or 'curd' in n or 'dahi' in n: return 'bowl'
    if 'curry' in n or 'gravy' in n or 'sabzi' in n or 'chole' in n or 'rajma' in n: return 'bowl'
    if 'paneer' in n and not any(x in n for x in ['curry', 'bhurji', 'gravy', 'tikka', 'sandwich', 'salad']): return 'g'
    if 'rice' in n and not any(x in n for x in ['rice cake', 'rice flour']): return 'plate'
    if 'khichdi' in n or 'biryani' in n or 'pulao' in n: return 'plate'
    
    return None

def get_meal_suitability(food_name: str, meal_type: str) -> int:
    """
    Returns a score from 0-100 indicating how suitable a food is for a given meal.
    """
    n = str(food_name).lower()
    m = meal_type.lower()
    
    if m == 'breakfast':
        if 'egg' in n and 'curry' not in n: return 100
        if 'poha' in n or 'upma' in n or 'oats' in n or 'porridge' in n or 'muesli' in n: return 100
        if 'idli' in n or 'dosa' in n or 'cheela' in n or 'chilla' in n or 'pancake' in n: return 100
        if 'bread' in n or 'toast' in n or 'sandwich' in n: return 100
        if 'smoothie' in n or 'shake' in n or 'whey' in n: return 100
        if 'curd rice' in n: return 40
        if 'fish' in n or 'chicken' in n or 'mutton' in n or 'pork' in n: return 0
        if 'rajma' in n or 'chole' in n or 'dal makhani' in n: return 5
        if 'sabzi' in n or 'curry' in n or 'gravy' in n: return 20
        if 'salad' in n and 'fruit' not in n: return 25
        if 'khichdi' in n or 'pulao' in n or 'biryani' in n: return 10
        return 60  # Lowered default: only clearly breakfast-appropriate foods get 80+
        
    elif m == 'lunch':
        if 'fish' in n or 'chicken' in n or 'paneer' in n or 'dal' in n or 'rajma' in n or 'chole' in n: return 100
        if 'rice' in n or 'roti' in n or 'chapati' in n or 'paratha' in n: return 100
        if 'salad' in n or 'raita' in n: return 100
        if 'curry' in n or 'sabzi' in n: return 100
        if 'poha' in n or 'upma' in n or 'oats' in n: return 0
        return 80
        
    elif m == 'dinner':
        if 'fish' in n or 'chicken' in n or 'paneer' in n or 'dal' in n: return 100
        if 'soup' in n or 'shorba' in n or 'broth' in n: return 100
        if 'rice' in n or 'roti' in n or 'chapati' in n: return 90
        if 'salad' in n or 'raita' in n: return 90
        if 'rajma' in n or 'chole' in n or 'dal makhani' in n: return 40 # A bit heavy for dinner
        if 'biryani' in n or 'paratha' in n or 'fried' in n: return 30 # Heavy
        if 'poha' in n or 'upma' in n: return 0
        return 80
        
    elif m == 'snack':
        if 'yogurt' in n or 'curd' in n or 'fruit' in n or 'apple' in n or 'banana' in n: return 100
        if 'whey' in n or 'protein powder' in n or 'shake' in n or 'smoothie' in n: return 100
        if 'chana' in n or 'makhana' in n or 'nuts' in n or 'almond' in n or 'sprouts' in n: return 100
        if 'paneer' in n and 'curry' not in n and 'gravy' not in n: return 90
        if 'egg' in n and 'curry' not in n: return 90
        if 'fish' in n or 'chicken curry' in n or 'rajma' in n or 'dal' in n: return 0
        if 'rice' in n or 'roti' in n or 'chapati' in n: return 0
        return 55  # Lowered snack default to stay below threshold of 60
        
    return 100
