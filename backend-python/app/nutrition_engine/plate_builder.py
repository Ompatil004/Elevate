import logging
from typing import Dict, List, Any
import random

logger = logging.getLogger(__name__)

class PlateBuilder:
    """
    Phase 4.9: Explicit Plate Builder
    Strictly builds a plate based on an Anchor and Template constraints.
    Rejects any plate that cannot satisfy all structural requirements.
    """
    def __init__(self, food_graph):
        self.food_graph = food_graph

    def build_plate(self, anchor: Dict, template: Dict[str, Any], valid_nodes: List[Dict], meal_type: str) -> List[Dict]:
        """
        Builds a single candidate plate. Returns an empty list if the plate fails the completeness check.
        """
        plate = [anchor]
        anchor_role = template.get('anchor', {}).get('role')
        roles_fulfilled = {anchor_role: 1}
        
        # Fill Required Roles
        required_rules = template.get('required', [])
        plate_valid = True
        
        for req in required_rules:
            role = req.get('role')
            if role == anchor_role:
                continue 
                
            target_count = req.get('count', 1)
            for _ in range(target_count):
                best_match = self._find_best_match_for_role(role, valid_nodes, plate, anchor, meal_type)
                if best_match:
                    plate.append(best_match)
                    roles_fulfilled[role] = roles_fulfilled.get(role, 0) + 1
                else:
                    logger.debug(f"Plate Completeness Check Failed: Could not find required role '{role}' for anchor '{anchor['food_id']}'")
                    plate_valid = False
                    break
            if not plate_valid:
                break
                
        # Phase 4.9: Plate Completeness Check
        # The optimizer should *never* repair an incomplete plate.
        if not plate_valid:
            return [] # Reject immediately
            
        # Fill Optional Roles
        optional_rules = template.get('optional', [])
        realism_max_items = template.get('realism', {}).get('max_total_items', 5)
        
        for opt in optional_rules:
            if len(plate) >= realism_max_items:
                break
                
            role = opt.get('role')
            max_count = opt.get('max', 1)
            
            # Check anchor's structural_rules
            preferred_roles = [p['role'] for p in anchor.get('structural_rules', {}).get('preferred', [])]
            
            # Add if preferred, or 50% chance for variety if not
            if role in preferred_roles or random.random() > 0.5:
                best_match = self._find_best_match_for_role(role, valid_nodes, plate, anchor, meal_type)
                if best_match:
                    plate.append(best_match)
                    
        return plate

    def _find_best_match_for_role(self, role: str, valid_nodes: List[Dict], current_plate: List[Dict], anchor: Dict, meal_type: str) -> Dict:
        candidates = []
        current_fids = {n['food_id'] for n in current_plate}
        
        for node in valid_nodes:
            if node['food_id'] in current_fids:
                continue
            if node['semantics'].get('meal_role') != role:
                continue
            if node['meal_suitability'].get(meal_type.lower(), 0) < 30:
                continue
                
            # Phase 4.9: Must not be forbidden by anchor's structural rules
            forbidden_roles = [f['role'] for f in anchor.get('structural_rules', {}).get('forbidden', [])]
            if role in forbidden_roles:
                continue

            # Must not have exact 0 compatibility
            comp_score = anchor.get('compatibility', {}).get(role, 50)
            if comp_score == 0:
                continue
                
            candidates.append((node, comp_score))
            
        if not candidates:
            return None
            
        # Sort by compatibility
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Pick from top 3 to ensure some variety
        top_candidates = candidates[:3]
        return random.choice(top_candidates)[0]
