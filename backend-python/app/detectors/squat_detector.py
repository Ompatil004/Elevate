from typing import List, Dict, Any, Tuple
import time
from app.detectors.base_detector import BaseDetector

class SquatDetector(BaseDetector):
    """
    Detector for squat movements.
    Tracks knee angle and validates hip/shoulder alignment.
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
        kps = self.get_keypoints(landmarks)
        if not kps:
            return state_data.get('counter', 0), state_data.get('stage', 'up')
            
        l_hip, r_hip = kps.get('l_hip'), kps.get('r_hip')
        l_knee, r_knee = kps.get('l_knee'), kps.get('r_knee')
        l_ankle, r_ankle = kps.get('l_ankle'), kps.get('r_ankle')
        
        if not (l_hip and l_knee and l_ankle):
            return state_data.get('counter', 0), state_data.get('stage', 'up')
            
        # Knee angle (left side primarily, or average if confident)
        knee_angle = self.calculate_angle(l_hip[:2], l_knee[:2], l_ankle[:2])
        
        down_threshold = self.config.get('down_angle', 90.0)
        up_threshold = self.config.get('up_angle', 160.0)
        rom_min = self.config.get('rom_min', 60.0)
        
        counter = state_data.get('counter', 0)
        stage = state_data.get('stage', 'up')
        if stage is None:
            stage = 'up'
            
        min_angle = state_data.get('min_angle', 180.0)
        
        # State machine: UP -> DOWN -> UP
        if stage == 'up':
            if knee_angle < down_threshold:
                stage = 'down'
                min_angle = knee_angle
        elif stage == 'down':
            min_angle = min(min_angle, knee_angle)
            if knee_angle > up_threshold:
                rom = up_threshold - min_angle
                if rom >= rom_min:
                    counter += 1
                stage = 'up'
                min_angle = 180.0
                
        state_data['min_angle'] = min_angle
        return counter, stage

    def check_form(self, landmarks) -> List[str]:
        self.feedback = []
        kps = self.get_keypoints(landmarks)
        if not kps:
            return self.feedback
            
        l_hip, r_hip = kps.get('l_hip'), kps.get('r_hip')
        l_knee, r_knee = kps.get('l_knee'), kps.get('r_knee')
        l_ankle, r_ankle = kps.get('l_ankle'), kps.get('r_ankle')
        l_shoulder = kps.get('l_shoulder')
        
        if l_knee and r_knee and l_ankle and r_ankle:
            # Check knee alignment (knees collapsing inward)
            knee_dist = abs(l_knee[0] - r_knee[0])
            ankle_dist = abs(l_ankle[0] - r_ankle[0])
            if knee_dist < ankle_dist * 0.7:
                self.feedback.append("Avoid knee collapse - push knees out")
                self.form_score = max(50, self.form_score - 15)
                
        if l_hip and l_shoulder and l_knee:
            # Check if torso is leaning too far forward
            torso_angle = self.calculate_angle(l_shoulder[:2], l_hip[:2], l_knee[:2])
            if torso_angle < 65:
                self.feedback.append("Keep chest up - avoid leaning too far forward")
                self.form_score = max(50, self.form_score - 10)
                
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        self.form_score = 100
        self.check_form(landmarks)
        return self.form_score
