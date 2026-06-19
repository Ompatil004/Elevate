from typing import List, Dict, Any, Tuple
from app.detectors.base_detector import BaseDetector

class RaiseDetector(BaseDetector):
    """
    Detector for raise movements (lateral raise, front raise).
    Tracks shoulder abduction angle.
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
        kps = self.get_keypoints(landmarks)
        if not kps:
            return state_data.get('counter', 0), state_data.get('stage', 'down')
            
        l_hip = kps.get('l_hip')
        l_shoulder = kps.get('l_shoulder')
        l_elbow = kps.get('l_elbow')
        
        if not (l_hip and l_shoulder and l_elbow):
            return state_data.get('counter', 0), state_data.get('stage', 'down')
            
        shoulder_angle = self.calculate_angle(l_hip[:2], l_shoulder[:2], l_elbow[:2])
        
        down_threshold = self.config.get('down_angle', 30.0)
        up_threshold = self.config.get('up_angle', 80.0)
        rom_min = self.config.get('rom_min', 45.0)
        
        counter = state_data.get('counter', 0)
        stage = state_data.get('stage', 'down')
        if stage is None:
            stage = 'down'
            
        max_angle = state_data.get('max_angle', 0.0)
        
        if stage == 'down':
            if shoulder_angle > up_threshold:
                stage = 'up'
                max_angle = shoulder_angle
        elif stage == 'up':
            max_angle = max(max_angle, shoulder_angle)
            if shoulder_angle < down_threshold:
                rom = max_angle - down_threshold
                if rom >= rom_min:
                    counter += 1
                stage = 'down'
                max_angle = 0.0
                
        state_data['max_angle'] = max_angle
        return counter, stage

    def check_form(self, landmarks) -> List[str]:
        self.feedback = []
        kps = self.get_keypoints(landmarks)
        if not kps:
            return self.feedback
            
        l_hip = kps.get('l_hip')
        l_shoulder = kps.get('l_shoulder')
        l_elbow = kps.get('l_elbow')
        
        if l_hip and l_shoulder and l_elbow:
            shoulder_angle = self.calculate_angle(l_hip[:2], l_shoulder[:2], l_elbow[:2])
            # Check if raising arms too high above head (usually lateral raises stop near 90 deg)
            if shoulder_angle > 110:
                self.feedback.append("Lower your hands slightly - stay in the target raise range")
                self.form_score = max(50, self.form_score - 10)
                
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        self.form_score = 100
        self.check_form(landmarks)
        return self.form_score
