import pandas as pd
import json
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    def __init__(self, data_path: str, output_path: str):
        self.data_path = data_path
        self.output_path = output_path

    def build_graph(self):
        logger.info(f"Loading data from {self.data_path}")
        df = pd.read_csv(self.data_path)
        
        graph = {
            "metadata": {
                "version": "2.1",
                "total_items": len(df)
            },
            "nodes": {},
            "compatibility_matrix": {} # Populated offline ideally via LLM rules or heuristics
        }

        # Build nodes
        for _, row in df.iterrows():
            food_id = str(row['food_id'])
            
            # Simulated basic recipe metadata that would be built offline
            prep_time = 15 if row['category'] in ['Healthy Beverage', 'Fruits', 'Snack', 'Salad'] else 30
            difficulty = "Easy" if prep_time <= 15 else "Medium"
            estimated_cost = 40 if row['category'] in ['Whole Grains', 'Rice', 'Dal & Pulses'] else 80

            graph["nodes"][food_id] = {
                "name": row['food_name'],
                "category": row['category'],
                "meal_type": str(row['meal_type']).split(','), # Might be list
                "calories": float(row['calories_kcal']),
                "macros": {
                    "protein": float(row['protein_g']),
                    "carbs": float(row['carbohydrates_g']),
                    "fat": float(row['fat_g'])
                },
                "tags": {
                    "is_vegan": bool(row['is_vegan']),
                    "is_vegetarian": bool(row['is_vegetarian']),
                    "is_high_protein": bool(row['is_high_protein'])
                },
                "recipe_metadata": {
                    "preparation_time_min": prep_time,
                    "difficulty": difficulty,
                    "estimated_cost_inr": estimated_cost
                }
            }

        # Simulated Compatibility Matrix Builder
        # In a real run, this parses the separate food_metadata.csv or runs LLM rules
        logger.info("Building dummy compatibility matrix...")
        for food_id, node in graph["nodes"].items():
            if "Idli" in node["name"]:
                # Find sambar
                sambar = df[df['food_name'].str.contains("Sambar", case=False, na=False)]
                if not sambar.empty:
                    sambar_id = str(sambar.iloc[0]['food_id'])
                    if food_id not in graph["compatibility_matrix"]:
                        graph["compatibility_matrix"][food_id] = {}
                    graph["compatibility_matrix"][food_id][sambar_id] = 100

        with open(self.output_path, 'w') as f:
            json.dump(graph, f, indent=2)
            
        logger.info(f"Successfully compiled knowledge graph to {self.output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, '..', 'data', 'nutrition_production_final_v4.csv')
    output_path = os.path.join(base_dir, '..', 'data', 'compiled_nutrition_graph_v2.json')
    
    if os.path.exists(data_path):
        builder = KnowledgeGraphBuilder(data_path, output_path)
        builder.build_graph()
    else:
        logger.error("Source CSV not found.")
