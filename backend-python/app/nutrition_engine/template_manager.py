import yaml
import logging
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class TemplateManager:
    """
    Loads and validates semantic constraint templates.
    """
    def __init__(self, template_path: str):
        self.template_path = template_path
        self._templates = {}
        self._load_templates()

    def _load_templates(self):
        if not os.path.exists(self.template_path):
            logger.error(f"Template file not found: {self.template_path}")
            return
            
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self._templates = yaml.safe_load(f) or {}
                
            # Basic validation
            if "regions" not in self._templates:
                logger.warning(f"Templates file {self.template_path} missing 'regions' root key.")
                
        except Exception as e:
            logger.error(f"Failed to load templates from {self.template_path}: {e}")
            raise

    def get_templates_for_meal(self, meal_type: str, region: str = "pan_indian") -> List[Dict[str, Any]]:
        """
        Retrieves templates for a specific meal type.
        Falls back to pan_indian if regional templates don't exist for that meal.
        """
        regions = self._templates.get("regions", {})
        
        # Start with regional templates
        region_data = regions.get(region, {})
        templates = region_data.get(meal_type, [])
        
        # Fallback to pan_indian if no regional templates exist
        if not templates and region != "pan_indian":
            pan_indian_data = regions.get("pan_indian", {})
            templates = pan_indian_data.get(meal_type, [])
            
        # Sort by priority descending
        return sorted(templates, key=lambda x: x.get('priority', 0), reverse=True)

    def filter_feasible_templates(self, templates: List[Dict[str, Any]], target_macros: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Phase 4.9: Template Feasibility Checker
        Filters out templates that cannot realistically hit the required macros.
        """
        feasible = []
        target_pro = target_macros.get("protein", 0)
        target_cal = target_macros.get("calories", 0)
        
        for t in templates:
            capacity = t.get("nutrition", {}).get("capacity", {})
            pro_cap = capacity.get("protein", {})
            cal_cap = capacity.get("calories", {})
            
            # Default to very loose bounds if not explicitly defined
            min_pro, max_pro = pro_cap.get("min", 0), pro_cap.get("max", 999)
            min_cal, max_cal = cal_cap.get("min", 0), cal_cap.get("max", 5000)
            
            if not (min_pro <= target_pro <= max_pro):
                logger.debug(f"Template {t.get('id')} rejected: protein {target_pro} outside {min_pro}-{max_pro}")
                continue
            if not (min_cal <= target_cal <= max_cal):
                logger.debug(f"Template {t.get('id')} rejected: cals {target_cal} outside {min_cal}-{max_cal}")
                continue
                
            feasible.append(t)
        return feasible

    def validate_template_schema(self, template: Dict[str, Any]) -> bool:
        """
        Checks if a template conforms to the structural constraint schema.
        """
        required_keys = ['id', 'anchor', 'required']
        for key in required_keys:
            if key not in template:
                return False
                
        if 'role' not in template['anchor']:
            return False
            
        return True
