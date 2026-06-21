"""
Hybrid Volume Optimizer for Sets/Reps
======================================
Combines rule-based logic with user-specific adaptation.
ML models can be plugged in when available.

Author: Elevate Team
"""
# -*- coding: utf-8 -*-

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json


class HybridVolumeOptimizer:
    """
    Smart hybrid system for calculating optimal sets/reps.
    
    Phases:
    1. Rule-based starting point (safe, proven defaults)
    2. User-specific adaptation (learns from THEIR workouts)
    3. ML enhancement (when models available)
    """
    
    def __init__(self):
        # ML models (optional - will use rules if not available)
        self.sets_model = None
        self.reps_model = None
        self.volume_model = None
        
        # Try to load ML models
        self._try_load_ml_models()
        
        # Progression engine for multi-factor overload
        try:
            from .progression_engine import get_progression_engine
            self.progression_engine = get_progression_engine()
        except Exception:
            self.progression_engine = None
        
        # Rule-based configuration
        self.base_sets = {
            'Beginner': 3,
            'Intermediate': 4,
            'Advanced': 5
        }
        
        self.base_reps = {
            'Strength': '4-6',
            'Muscle Gain': '8-12',
            'Hypertrophy': '8-12',
            'Endurance': '15-20',
            'Fat Loss': '12-15',
            'Maintenance': '10-12'
        }
        
        print("[HYBRID] HybridVolumeOptimizer initialized")
        if self.sets_model:
            print("   [ML] ML models loaded - will use hybrid predictions")
        else:
            print("   [RULES] Using smart rule-based system (ML models not found)")
        if self.progression_engine:
            print("   [PROG] ProgressionEngine loaded — multi-factor overload active")
    
    def _try_load_ml_models(self):
        """Try to load ML models, gracefully degrade if not available"""
        try:
            import joblib
            import os
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'models')
            
            sets_path = os.path.join(model_dir, 'xgboost_sets.pkl')
            reps_path = os.path.join(model_dir, 'xgboost_reps.pkl')
            volume_path = os.path.join(model_dir, 'xgboost_volume.pkl')
            
            if os.path.exists(sets_path):
                self.sets_model = joblib.load(sets_path)
            if os.path.exists(reps_path):
                self.reps_model = joblib.load(reps_path)
            if os.path.exists(volume_path):
                self.volume_model = joblib.load(volume_path)
                
        except Exception as e:
            # Silently fail - will use rules
            pass
    
    def calculate_optimal_sets(
        self,
        user_profile: Dict,
        workout_history: List[Dict] = None,
        exercise_type: str = 'compound'
    ) -> int:
        """
        Calculate optimal sets using hybrid approach.
        
        Args:
            user_profile: User's current profile
            workout_history: List of completed workouts (for adaptation)
            exercise_type: 'compound' or 'isolation'
        
        Returns:
            Optimal number of sets
        """
        # Phase 1: Rule-based starting point
        base_sets = self._get_rule_based_sets(user_profile, exercise_type)
        
        # Phase 2: User-specific adaptation (if history available)
        if workout_history and len(workout_history) > 0:
            adapted_sets = self._adapt_based_on_history(base_sets, workout_history, user_profile)
        else:
            adapted_sets = base_sets
        
        # Phase 3: ML adjustment (if model available)
        if self.sets_model is not None:
            ml_sets = self._predict_with_ml_model(user_profile, 'sets')
            # Blend ML prediction with rule-based (weight depends on data confidence)
            confidence = min(len(workout_history) / 20.0, 1.0) if workout_history else 0.0
            final_sets = int(round((1 - confidence) * adapted_sets + confidence * ml_sets))
        else:
            final_sets = adapted_sets
        
        # Apply safety caps
        final_sets = self._apply_safety_caps(final_sets, user_profile)
        
        return final_sets
    
    def calculate_optimal_reps(
        self,
        user_profile: Dict,
        workout_history: List[Dict] = None,
        intensity: float = 0.75
    ) -> str:
        """
        Calculate optimal rep range using hybrid approach.
        
        Args:
            user_profile: User's current profile
            workout_history: List of completed workouts
            intensity: Target intensity (0.0-1.0)
        
        Returns:
            Rep range string (e.g., "8-12")
        """
        # Phase 1: Rule-based starting point
        base_reps = self._get_rule_based_reps(user_profile, intensity)
        
        # Phase 2: User-specific adaptation
        if workout_history and len(workout_history) > 2:
            adapted_reps = self._adapt_reps_based_on_history(base_reps, workout_history, user_profile)
        else:
            adapted_reps = base_reps
        
        # Phase 3: ML adjustment
        if self.reps_model is not None:
            ml_reps = self._predict_with_ml_model(user_profile, 'reps')
            confidence = min(len(workout_history) / 20.0, 1.0) if workout_history else 0.0
            # Blend rep ranges
            final_reps = self._blend_rep_ranges(adapted_reps, ml_reps, confidence)
        else:
            final_reps = adapted_reps
        
        # Apply age-based safety adjustments
        final_reps = self._apply_age_based_rep_adjustments(final_reps, user_profile)
        
        return final_reps
    
    def _get_rule_based_sets(self, user_profile: Dict, exercise_type: str) -> int:
        """Phase 1: Get rule-based starting sets"""
        experience = user_profile.get('experience', 'Beginner')
        goal = user_profile.get('goal', 'Muscle Gain')
        age = user_profile.get('age', 25)
        
        # Base sets from experience
        sets = self.base_sets.get(experience, 3)
        
        # Adjust for goal
        if goal in ['Strength', 'Power']:
            sets += 1  # Strength needs more sets at lower reps
        elif goal in ['Endurance']:
            sets -= 1  # Endurance needs fewer sets at higher reps
        
        # Adjust for exercise type
        if exercise_type == 'isolation':
            sets = max(2, sets - 1)  # Less volume for isolation
        
        # Age adjustment (safety)
        if age > 50:
            sets = max(2, sets - 1)
        elif age < 18:
            sets = max(2, min(sets, 3))  # Cap for younger users
        
        return sets
    
    def _get_rule_based_reps(self, user_profile: Dict, intensity: float) -> str:
        """Phase 1: Get rule-based starting reps"""
        goal = user_profile.get('goal', 'Muscle Gain')
        experience = user_profile.get('experience', 'Beginner')
        
        # Base reps from goal
        base_range = self.base_reps.get(goal, '8-12')
        
        # Adjust for experience
        if experience == 'Beginner':
            # Beginners benefit from higher reps (practice, lighter weight)
            base_range = self._shift_rep_range(base_range, +2)
        elif experience == 'Advanced':
            # Advanced can handle lower reps with heavier weight
            base_range = self._shift_rep_range(base_range, -1)
        
        # Adjust for intensity
        if intensity > 0.85:
            base_range = self._shift_rep_range(base_range, -2)  # Higher intensity = lower reps
        elif intensity < 0.65:
            base_range = self._shift_rep_range(base_range, +3)  # Lower intensity = higher reps
        
        return base_range
    
    def _adapt_based_on_history(
        self,
        base_sets: int,
        workout_history: List[Dict],
        user_profile: Dict
    ) -> int:
        """Phase 2: Adapt sets based on user's workout history — uses ProgressionEngine when available"""
        if not workout_history or len(workout_history) == 0:
            return base_sets
        
        # ── Use ProgressionEngine if available ──
        if self.progression_engine is not None:
            try:
                # Build current params from base
                goal = user_profile.get('goal', 'Muscle Gain')
                rep_range = self.base_reps.get(goal, '8-12')
                low, high = map(int, rep_range.split('-'))
                
                current_params = {
                    'sets': base_sets,
                    'reps_low': low,
                    'reps_high': high,
                    'intensity': 0.75,
                    'rest_seconds': 90,
                }
                
                # Estimate completion from recent history
                recent = workout_history[-5:]
                completion_rates = []
                for w in recent:
                    for ex in w.get('exercises', []):
                        target = ex.get('target_reps', 10)
                        done   = ex.get('completed_reps', target)
                        if isinstance(target, str):
                            try:
                                lo, hi = map(int, target.split('-'))
                                target = (lo + hi) / 2
                            except Exception:
                                target = 10
                        if target > 0:
                            completion_rates.append(done / target)
                
                completion_pct = float(np.mean(completion_rates)) if completion_rates else 0.7
                
                result = self.progression_engine.compute_progression(
                    user_profile=user_profile,
                    current_params=current_params,
                    workout_stats={'completion_pct': completion_pct, 'fatigue_level': 5.0},
                )
                
                adapted = result['sets']
                method  = result['progression_method']
                print(f"    ProgressionEngine → {adapted} sets ({method})")
                return adapted
                
            except Exception as e:
                print(f"    ProgressionEngine failed ({e}), falling back to heuristic")
        
        # ── Fallback: original heuristic ──
        recent = workout_history[-5:]
        
        completion_rates = []
        for workout in recent:
            exercises = workout.get('exercises', [])
            for ex in exercises:
                target_reps = ex.get('target_reps', 10)
                completed_reps = ex.get('completed_reps', target_reps)
                if isinstance(target_reps, str):
                    try:
                        low, high = map(int, target_reps.split('-'))
                        target_reps = (low + high) / 2
                    except:
                        target_reps = 10
                if target_reps > 0:
                    rate = completed_reps / target_reps
                    completion_rates.append(rate)
        
        if not completion_rates:
            return base_sets
        
        avg_completion = np.mean(completion_rates)
        
        if avg_completion > 1.1:
            adjustment = +1
        elif avg_completion < 0.8:
            adjustment = -1
        elif avg_completion > 1.0:
            adjustment = +0.5
        else:
            adjustment = 0
        
        if len(recent) >= 3:
            first_half = completion_rates[:len(completion_rates)//2]
            second_half = completion_rates[len(completion_rates)//2:]
            if np.mean(second_half) < np.mean(first_half) - 0.1:
                adjustment -= 1
        
        return int(max(2, min(6, base_sets + adjustment)))
    
    def _adapt_reps_based_on_history(
        self,
        base_reps: str,
        workout_history: List[Dict],
        user_profile: Dict
    ) -> str:
        """Phase 2: Adapt rep range based on user's history"""
        if not workout_history or len(workout_history) < 3:
            return base_reps
        
        # Analyze recent performance
        recent = workout_history[-5:]
        
        # Check if user consistently hits top of rep range
        top_range_hits = 0
        total_sets = 0
        
        for workout in recent:
            exercises = workout.get('exercises', [])
            for ex in exercises:
                target_reps = ex.get('target_reps', base_reps)
                completed_reps = ex.get('completed_reps', 0)
                
                if isinstance(target_reps, str):
                    try:
                        low, high = map(int, target_reps.split('-'))
                        total_sets += 1
                        if completed_reps >= high:
                            top_range_hits += 1
                    except:
                        pass
        
        if total_sets == 0:
            return base_reps
        
        hit_rate = top_range_hits / total_sets
        
        # Adjust rep range based on performance
        if hit_rate > 0.7:
            # User consistently hits top  increase difficulty
            new_range = self._shift_rep_range(base_reps, -1)
            print(f"    User hitting top of range ({hit_rate:.1%})  harder rep range: {new_range}")
            return new_range
        elif hit_rate < 0.3:
            # User struggling  decrease difficulty
            new_range = self._shift_rep_range(base_reps, +2)
            print(f"    User struggling ({hit_rate:.1%})  easier rep range: {new_range}")
            return new_range
        
        return base_reps
    
    def _predict_with_ml_model(self, user_profile: Dict, target: str) -> float:
        """Phase 3: Predict using ML model if available"""
        # This would use the loaded ML models
        # For now, return rule-based fallback
        if target == 'sets':
            return self.base_sets.get(user_profile.get('experience', 'Beginner'), 3)
        elif target == 'reps':
            goal = user_profile.get('goal', 'Muscle Gain')
            rep_range = self.base_reps.get(goal, '8-12')
            low, high = map(int, rep_range.split('-'))
            return (low + high) / 2
        return 3.0
    
    def _apply_safety_caps(self, sets: int, user_profile: Dict) -> int:
        """Apply safety caps based on user characteristics"""
        age = user_profile.get('age', 25)
        experience = user_profile.get('experience', 'Beginner')
        body_issues = user_profile.get('body_issues', [])
        
        # Age caps
        if age > 60:
            sets = min(sets, 3)
        elif age > 50:
            sets = min(sets, 4)
        
        # Experience caps
        if experience == 'Beginner':
            sets = min(sets, 4)  # Prevent overtraining
        
        # Injury considerations
        if body_issues and len(body_issues) > 0:
            sets = min(sets, 3)  # Reduce volume with injuries
        
        # Absolute bounds
        sets = max(2, min(sets, 6))
        
        return sets
    
    def _apply_age_based_rep_adjustments(self, rep_range: str, user_profile: Dict) -> str:
        """Apply age-based safety adjustments to rep range"""
        age = user_profile.get('age', 25)
        
        if age > 55:
            # Older adults: higher reps, lighter weight
            rep_range = self._shift_rep_range(rep_range, +2)
            # Ensure minimum rep of 8 for safety
            try:
                low, high = map(int, rep_range.split('-'))
                low = max(low, 8)
                rep_range = f"{low}-{high}"
            except:
                rep_range = "10-15"
        elif age < 18:
            # Younger users: moderate reps, focus on form
            rep_range = self._shift_rep_range(rep_range, +1)
            try:
                low, high = map(int, rep_range.split('-'))
                high = min(high, 15)  # Cap to prevent max effort
                rep_range = f"{low}-{high}"
            except:
                rep_range = "10-15"
        
        return rep_range
    
    def _shift_rep_range(self, rep_range: str, shift: int) -> str:
        """Shift rep range up or down"""
        try:
            low, high = map(int, rep_range.split('-'))
            new_low = max(1, low + shift)
            new_high = max(2, high + shift)
            return f"{new_low}-{new_high}"
        except:
            return rep_range
    
    def _blend_rep_ranges(self, range1: str, range2: str, weight: float) -> str:
        """Blend two rep ranges based on confidence weight"""
        try:
            low1, high1 = map(int, range1.split('-'))
            low2, high2 = map(int, range2.split('-'))
            
            blended_low = int(round((1 - weight) * low1 + weight * low2))
            blended_high = int(round((1 - weight) * high1 + weight * high2))
            
            return f"{blended_low}-{blended_high}"
        except:
            return range1
    
    def get_volume_recommendation(
        self,
        user_profile: Dict,
        workout_history: List[Dict] = None,
        exercise_name: str = '',
        exercise_type: str = 'compound'
    ) -> Dict:
        """
        Get complete volume recommendation (sets, reps, rest) for an exercise.
        
        Returns:
            Dict with sets, reps, rest_time, and reasoning
        """
        # Calculate intensity based on goal
        goal = user_profile.get('goal', 'Muscle Gain')
        intensity_map = {
            'Strength': 0.85,
            'Muscle Gain': 0.75,
            'Hypertrophy': 0.75,
            'Fat Loss': 0.70,
            'Endurance': 0.60,
            'Maintenance': 0.70
        }
        intensity = intensity_map.get(goal, 0.75)
        
        # Calculate optimal sets and reps
        sets = self.calculate_optimal_sets(user_profile, workout_history, exercise_type)
        reps = self.calculate_optimal_reps(user_profile, workout_history, intensity)
        
        # Calculate rest time
        rest_time = self._calculate_rest_time(intensity, user_profile)
        
        # Build reasoning
        reasoning = self._build_reasoning(sets, reps, user_profile, workout_history)
        
        return {
            'sets': sets,
            'reps': reps,
            'rest_time_seconds': rest_time,
            'intensity': intensity,
            'exercise_type': exercise_type,
            'reasoning': reasoning,
            'method': 'hybrid' if workout_history else 'rule_based',
            'ml_enhanced': self.sets_model is not None
        }
    
    def _calculate_rest_time(self, intensity: float, user_profile: Dict) -> int:
        """Calculate rest time based on intensity and goal"""
        goal = user_profile.get('goal', 'Muscle Gain')
        age = user_profile.get('age', 25)
        
        # Base rest from intensity
        if intensity >= 0.85:
            rest = 180  # 3 min for strength
        elif intensity >= 0.75:
            rest = 90  # 90 sec for hypertrophy
        elif intensity >= 0.65:
            rest = 60  # 60 sec for fat loss
        else:
            rest = 45  # 45 sec for endurance
        
        # Age adjustment
        if age > 50:
            rest = min(rest + 30, 240)  # More rest for older adults
        
        # Goal adjustment
        if goal == 'Strength':
            rest = max(rest, 120)
        elif goal == 'Fat Loss':
            rest = min(rest, 60)  # Keep heart rate up
        
        return rest
    
    def _build_reasoning(
        self,
        sets: int,
        reps: str,
        user_profile: Dict,
        workout_history: List[Dict] = None
    ) -> str:
        """Build human-readable reasoning for recommendations"""
        experience = user_profile.get('experience', 'Beginner')
        goal = user_profile.get('goal', 'Muscle Gain')
        age = user_profile.get('age', 25)
        
        reasons = []
        
        # Experience reason
        reasons.append(f"{experience} level: {sets} sets base")
        
        # Goal reason
        reasons.append(f"Goal: {goal}  {reps} reps")
        
        # Age reason
        if age > 50:
            reasons.append(f"Age {age}: reduced volume for recovery")
        elif age < 18:
            reasons.append(f"Age {age}: moderate volume for safety")
        
        # History-based reason
        if workout_history and len(workout_history) > 2:
            reasons.append("Adjusted based on your recent performance")
        
        return "; ".join(reasons)


# Singleton pattern
_optimizer = None

def get_hybrid_optimizer():
    """Get or create hybrid optimizer instance"""
    global _optimizer
    if _optimizer is None:
        _optimizer = HybridVolumeOptimizer()
    return _optimizer
