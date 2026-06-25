import json
import csv
import os
import random

# Ensure reproducible generation
random.seed(42)

def generate_meal_kb():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "data", "nutrition_production_final_v4.csv")
    
    # Simple list of realistic foods extracted from typical Indian/Global diet profiles
    # (These must exactly match the `food_name` in the CSV, but for safety we use known generic names
    # since candidate_generator does a lowercase strip match)
    
    # 1. Carbs
    rotis = [
        ("Multigrain Roti", "piece"), ("Chapati (Roti)", "piece"), ("Phulka", "piece"),
        ("Jowar Roti", "piece"), ("Bajra Roti", "piece"), ("Missi Roti", "piece")
    ]
    rices = [
        ("Boiled Rice (Uble Chawal)", "plate"), ("Brown Rice", "plate"), 
        ("Jeera Rice", "plate"), ("Vegetable Pulao", "plate")
    ]
    breads = [
        ("Brown Bread", "slice"), ("Whole Wheat Bread", "slice"), ("Multigrain Bread", "slice")
    ]
    breakfast_carbs = [
        ("Oatmeal (Oats Porridge)", "bowl"), ("Poha", "bowl"), ("Semolina Upma (Suji/Rava Upma)", "bowl"),
        ("Idli", "serving"), ("Plain Dosa", "piece"), ("Masala Dosa", "piece"), ("Besan Chilla", "piece"),
        ("Moong Dal Chilla", "piece")
    ]
    
    # 2. Proteins
    veg_proteins = [
        ("Dal Makhani", "bowl"), ("Yellow Moong Dal", "bowl"), ("Toor Dal", "bowl"), 
        ("Masoor Dal", "bowl"), ("Chana Dal", "bowl"), ("Rajma Curry", "bowl"), 
        ("Chole (Chickpea Curry)", "bowl"), ("Lobia Curry", "bowl"), ("Soya Bean Curry", "bowl"),
        ("Soya Chunks Curry", "bowl"), ("Paneer Butter Masala", "bowl"), ("Palak Paneer", "bowl"),
        ("Kadhai Paneer", "bowl"), ("Matar Paneer", "bowl"), ("Tofu Curry", "bowl")
    ]
    nonveg_proteins = [
        ("Chicken Curry", "bowl"), ("Butter Chicken", "bowl"), ("Kadhai Chicken", "bowl"),
        ("Chicken Tikka Masala", "bowl"), ("Fish Curry", "bowl"), ("Mutton Curry", "bowl"),
        ("Egg Curry", "bowl"), ("Boiled Egg", "piece"), ("Scrambled Eggs", "bowl"),
        ("Chicken Breast (Grilled)", "piece")
    ]
    
    # 3. Sides & Veggies
    dry_veggies = [
        ("Aloo Gobi", "bowl"), ("Bhindi Masala", "bowl"), ("Baingan Bharta", "bowl"),
        ("Cabbage Sabzi", "bowl"), ("Capsicum Besan Sabzi", "bowl"), ("Mixed Vegetable Curry", "bowl"),
        ("Mushroom Matar", "bowl"), ("Aloo Matar", "bowl"), ("Lauki Sabzi", "bowl"), ("Tori Sabzi", "bowl")
    ]
    salads = [
        ("Tossed Salad", "bowl"), ("Cucumber Salad", "bowl"), ("Kachumber Salad", "bowl"),
        ("Sprout Salad", "bowl"), ("Lettuce Salad", "bowl")
    ]
    yogurts = [
        ("Plain Yogurt (Curd)", "bowl"), ("Tomato Onion Raita (Tamatar Aur Onion Ka Raita)", "bowl"),
        ("Cucumber Raita", "bowl"), ("Boondi Raita", "bowl"), ("Greek Yogurt", "bowl")
    ]
    chutneys = [
        ("Mint and Coriander Chutney (Pudinay Aur Dhaniye Ki Chutney)", "tbsp"),
        ("Coconut Chutney (Nariyal Ki Chutney)", "tbsp"),
        ("Tomato Chutney", "tbsp")
    ]

    meal_kb = []
    
    def add_meal(m_id, name, m_type, diet, anchor, foods_with_ratios, p_src, c_src, vegs, diff="medium", time=20):
        # Build strict internal ratios and food lists
        foods = []
        portion_rules = {}
        internal_ratio = {}
        
        for f_name, unit, ratio, min_q, max_q in foods_with_ratios:
            foods.append(f_name)
            internal_ratio[f_name] = ratio
            portion_rules[f_name] = {"min_qty": min_q, "max_qty": max_q, "unit": unit}
            
        meal_kb.append({
            "meal_id": m_id,
            "meal_name": name,
            "meal_type": m_type,
            "diet_type": diet,
            "anchor_role": anchor,
            "foods": foods,
            "protein_source": p_src,
            "carb_source": c_src,
            "vegetables": vegs,
            "difficulty": diff,
            "prep_time": time,
            "version": "2.0",
            "cuisine": "South Indian" if "Dosa" in name or "Idli" in name or "Sambar" in name else "North Indian" if "Paneer" in name or "Chicken" in name else "Pan Indian",
            "cooking_style": "Curry" if "Curry" in name or "Masala" in name or "Sambar" in name else "Dry" if "Salad" in name or "Dry" in name else "Boiled" if "Boiled" in name else "Grilled" if "Grilled" in name else "Mixed",
            "internal_ratio": internal_ratio,
            "portion_rules": portion_rules,
            "rules": []
        })

    # GENERATE LUNCH/DINNER MEALS (Roti + Curry + Veggie + Salad + Yogurt)
    # Permute over Carbs (Roti/Rice) and Proteins
    def gen_main_meals(meal_type="lunch"):
        # VEGETARIAN (Dal/Paneer/Rajma)
        for carb, c_unit in rotis + rices:
            for pro, p_unit in veg_proteins:
                for veg, v_unit in dry_veggies:
                    # Sample a salad and a yogurt
                    salad, s_unit = random.choice(salads)
                    yogurt, y_unit = random.choice(yogurts)
                    
                    c_src = "roti" if "roti" in carb.lower() or "chapati" in carb.lower() or "phulka" in carb.lower() else "rice"
                    p_src = "paneer" if "paneer" in pro.lower() else "dal & pulses" if "dal" in pro.lower() or "rajma" in pro.lower() or "chole" in pro.lower() else "tofu & soy"
                    diet = "Vegetarian" if p_src == "paneer" or "yogurt" in yogurt.lower() or "raita" in yogurt.lower() else "Vegan"
                    
                    # Setup base ratio (e.g., 2 rotis : 1 bowl curry : 0.5 bowl veg : 1 bowl salad : 0.5 bowl yogurt)
                    carb_ratio = 2.0 if c_src == "roti" else 1.0
                    carb_max = 5.0 if c_src == "roti" else 3.0
                    
                    m_id = f"{carb.replace(' ', '_').lower()}_{pro.replace(' ', '_').lower()}_{meal_type}"
                    
                    # 1 in 10 chance to actually add this specific combo to avoid 1000s of meals, target ~300
                    if random.random() < 0.15:
                        add_meal(
                            m_id=m_id,
                            name=f"{pro.split('(')[0].strip()} with {carb.split('(')[0].strip()}",
                            m_type=meal_type,
                            diet=diet,
                            anchor="combo_meal",
                            foods_with_ratios=[
                                (carb, c_unit, carb_ratio, 1.0, carb_max),
                                (pro, p_unit, 1.0, 0.5, 3.0),
                                (veg, v_unit, 0.5, 0.5, 2.0),
                                (salad, s_unit, 1.0, 0.5, 2.0),
                                (yogurt, y_unit, 0.5, 0.5, 2.0)
                            ],
                            p_src=p_src,
                            c_src=c_src,
                            vegs=[veg.split(' ')[0].lower(), "cucumber", "tomato"]
                        )
                        
        # NON-VEG (Chicken/Fish/Mutton/Egg)
        for carb, c_unit in rotis + rices:
            for pro, p_unit in nonveg_proteins:
                for veg, v_unit in dry_veggies:
                    salad, s_unit = random.choice(salads)
                    
                    c_src = "roti" if "roti" in carb.lower() or "chapati" in carb.lower() or "phulka" in carb.lower() else "rice"
                    p_src = "chicken/meat" if "chicken" in pro.lower() or "mutton" in pro.lower() else "fish & seafood" if "fish" in pro.lower() else "eggs"
                    
                    carb_ratio = 2.0 if c_src == "roti" else 1.0
                    carb_max = 5.0 if c_src == "roti" else 3.0
                    
                    m_id = f"{carb.replace(' ', '_').lower()}_{pro.replace(' ', '_').lower()}_{meal_type}"
                    
                    if random.random() < 0.2:
                        add_meal(
                            m_id=m_id,
                            name=f"{pro.split('(')[0].strip()} with {carb.split('(')[0].strip()}",
                            m_type=meal_type,
                            diet="NonVeg",
                            anchor="combo_meal",
                            foods_with_ratios=[
                                (carb, c_unit, carb_ratio, 1.0, carb_max),
                                (pro, p_unit, 1.0, 0.5, 3.0),
                                (veg, v_unit, 0.5, 0.5, 2.0),
                                (salad, s_unit, 1.0, 0.5, 2.0)
                            ],
                            p_src=p_src,
                            c_src=c_src,
                            vegs=[veg.split(' ')[0].lower(), "onion"]
                        )

    gen_main_meals("lunch")
    gen_main_meals("dinner")

    # GENERATE BREAKFASTS
    for carb, c_unit in breakfast_carbs:
        if "Dosa" in carb or "Idli" in carb:
            add_meal(
                m_id=f"{carb.replace(' ', '_').lower()}_breakfast",
                name=f"{carb} Breakfast",
                m_type="breakfast",
                diet="Vegan",
                anchor="combo_meal",
                foods_with_ratios=[
                    (carb, c_unit, 2.0 if "Idli" in carb else 1.0, 1.0, 4.0),
                    ("Sambar", "bowl", 1.0, 0.5, 3.0),
                    ("Coconut Chutney (Nariyal Ki Chutney)", "tbsp", 2.0, 1.0, 5.0)
                ],
                p_src="dal & pulses",
                c_src="dosa" if "Dosa" in carb else "idli",
                vegs=["coconut", "tomato"]
            )
        elif "Chilla" in carb:
            add_meal(
                m_id=f"{carb.replace(' ', '_').lower()}_breakfast",
                name=f"{carb} Breakfast",
                m_type="breakfast",
                diet="Vegetarian",
                anchor="combo_meal",
                foods_with_ratios=[
                    (carb, c_unit, 2.0, 1.0, 4.0),
                    ("Mint and Coriander Chutney (Pudinay Aur Dhaniye Ki Chutney)", "tbsp", 2.0, 1.0, 5.0),
                    ("Plain Yogurt (Curd)", "bowl", 0.5, 0.5, 2.0)
                ],
                p_src="dal & pulses",
                c_src="chilla",
                vegs=["mint", "coriander"]
            )
        elif "Poha" in carb or "Upma" in carb:
            add_meal(
                m_id=f"{carb.replace(' ', '_').lower()}_breakfast",
                name=f"{carb} Breakfast",
                m_type="breakfast",
                diet="Vegan",
                anchor="combo_meal",
                foods_with_ratios=[
                    (carb, c_unit, 1.0, 0.5, 3.0),
                    ("Sprout Salad", "bowl", 0.5, 0.5, 2.0)
                ],
                p_src="dal & pulses",
                c_src="poha" if "Poha" in carb else "upma",
                vegs=["onion", "tomato"]
            )
        elif "Oats" in carb:
            add_meal(
                m_id=f"{carb.replace(' ', '_').lower()}_breakfast",
                name=f"{carb} Breakfast",
                m_type="breakfast",
                diet="Vegetarian",
                anchor="combo_meal",
                foods_with_ratios=[
                    (carb, c_unit, 1.0, 0.5, 3.0),
                    ("Banana", "piece", 1.0, 1.0, 2.0),
                    ("Almonds", "piece", 10.0, 5.0, 20.0)
                ],
                p_src="milk",
                c_src="oats",
                vegs=[]
            )

    # Sandwich/Egg Breakfasts
    for egg_style, e_unit in [("Boiled Egg", "piece"), ("Scrambled Eggs", "bowl"), ("Omelette", "piece")]:
        for bread, b_unit in breads:
            add_meal(
                m_id=f"{egg_style.replace(' ', '_').lower()}_{bread.replace(' ', '_').lower()}_breakfast",
                name=f"{egg_style} with {bread}",
                m_type="breakfast",
                diet="NonVeg",
                anchor="combo_meal",
                foods_with_ratios=[
                    (bread, b_unit, 2.0, 1.0, 4.0),
                    (egg_style, e_unit, 2.0 if e_unit == "piece" else 1.0, 1.0, 4.0 if e_unit == "piece" else 2.0),
                    ("Tomato", "piece", 0.5, 0.5, 1.0) # Veggie on side
                ],
                p_src="eggs",
                c_src="bread & roti",
                vegs=["tomato"]
            )
            
    # GENERATE SNACKS
    snacks = [
        ("Roasted Chana", "bowl", "Vegetarian", "chana"),
        ("Makhana (Fox Nuts)", "bowl", "Vegetarian", "makhana"),
        ("Mixed Nuts", "bowl", "Vegetarian", "nuts"),
        ("Boiled Egg", "piece", "NonVeg", "eggs"),
        ("Sprout Salad", "bowl", "Vegan", "dal & pulses"),
        ("Greek Yogurt", "bowl", "Vegetarian", "yogurt"),
        ("Banana", "piece", "Vegan", "fruit"),
        ("Apple", "piece", "Vegan", "fruit"),
        ("Protein Shake", "glass", "Vegetarian", "supplement")
    ]
    for s_name, s_unit, s_diet, s_psrc in snacks:
        add_meal(
            m_id=f"{s_name.replace(' ', '_').lower()}_snack",
            name=f"{s_name} Snack",
            m_type="snack",
            diet=s_diet,
            anchor="snack",
            foods_with_ratios=[
                (s_name, s_unit, 1.0, 0.5, 3.0)
            ],
            p_src=s_psrc,
            c_src="fruit" if s_psrc == "fruit" else "none",
            vegs=[]
        )

    # Save to file
    out_path = os.path.join(base_dir, "data", "meal_knowledge_base.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(meal_kb, f, indent=2)
        
    print(f"Generated {len(meal_kb)} structured meals with internal scaling ratios to {out_path}.")

if __name__ == "__main__":
    generate_meal_kb()
