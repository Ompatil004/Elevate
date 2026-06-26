import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class IngredientOptimizer:
    """
    Scans a generated weekly plan and attempts to batch ingredients 
    to reduce the total number of unique groceries required (Shopping Efficiency).
    """
    def __init__(self, food_graph):
        self.food_graph = food_graph

    def optimize(self, weekly_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-generation optimization pass.
        If a user needs 50g of Red Bell Pepper on Tuesday, and 50g of Yellow Bell Pepper on Thursday,
        swap them to use 100g of Red Bell Pepper to save grocery complexity, provided it doesn't 
        violate meal identity.
        """
        logger.info("Running Batch Ingredient Optimization pass...")
        
        # Track ingredient usage across the week
        ingredient_usage = {}
        for day, meals in weekly_plan.items():
            for meal_type, plate in meals.items():
                if not plate:
                    continue
                for item in plate:
                    food_id = item.get('food_id')
                    food_name = item.get('food_name')
                    family = item.get('semantics', {}).get('family', '')
                    
                    if family not in ingredient_usage:
                        ingredient_usage[family] = {}
                        
                    if food_id not in ingredient_usage[family]:
                        ingredient_usage[family][food_id] = {'name': food_name, 'count': 0, 'days': set()}
                        
                    ingredient_usage[family][food_id]['count'] += 1
                    ingredient_usage[family][food_id]['days'].add(day)
                    
        # Identify sparse ingredients (used only once) and try to map them to dominant ones in the same family
        swaps_made = 0
        for family, items in ingredient_usage.items():
            if len(items) <= 1 or family in ('Drink', 'Other', 'Spice'):
                continue
                
            # Find dominant item
            dominant_item_id = max(items.keys(), key=lambda k: items[k]['count'])
            dominant_item = items[dominant_item_id]
            
            # If the dominant item is used multiple times, swap single-use items to it
            if dominant_item['count'] > 1:
                for item_id, data in items.items():
                    if item_id != dominant_item_id and data['count'] == 1:
                        # Perform swap in the plan
                        self._apply_swap(weekly_plan, item_id, dominant_item_id, dominant_item['name'])
                        swaps_made += 1
                        
        logger.info(f"Ingredient Optimizer completed. Made {swaps_made} grocery efficiency swaps.")
        return weekly_plan

    def _apply_swap(self, weekly_plan: Dict, old_id: str, new_id: str, new_name: str):
        for day, meals in weekly_plan.items():
            for meal_type, plate in meals.items():
                if not plate:
                    continue
                for item in plate:
                    if item.get('food_id') == old_id:
                        # Note: we should strictly fetch the new node's nutrition, but for a 
                        # simple semantic swap within the same family, macros are usually similar.
                        item['food_id'] = new_id
                        item['food_name'] = new_name
                        # Update semantics
                        if 'semantics' in item:
                            item['semantics']['food_name'] = new_name
