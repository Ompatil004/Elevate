from typing import List, Dict, Any, Tuple
from app.detectors.base_detector import BaseDetector

class LungeDetector(BaseDetector):
    """
    Detector for lunge movements.
    Tracks knee angle.
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
        kps = self.get_keypoints(landmarks)
        if not kps:
            return state_data.get('counter', 0), state_data.get('stage', 'up')
            
        l_hip = kps.get('l_hip')
        l_knee = kps.get('l_knee')
        l_ankle = kps.get('l_ankle')
        
        if not (l_hip and l_knee and l_ankle):
            return state_data.get('counter', 0), state_data.get('stage', 'up')
            
        knee_angle = self.calculate_angle(l_hip[:2], l_knee[:2], l_ankle[:2])
        
        down_threshold = self.config.get('down_angle', 100.0)
        up_threshold = self.config.get('up_angle', 160.0)
        rom_min = self.config.get('rom_min', 50.0)
        
        counter = state_data.get('counter', 0)
        stage = state_data.get('stage', 'up')
        if stage is None:
            stage = 'up'
            
        min_angle = state_data.get('min_angle', 180.0)
        
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
            
        l_knee = kps.get('l_knee')
        l_ankle = kps.get('l_ankle')
        
        if l_knee and l_ankle:
            # Check knee alignment relative to ankle (e.g. knee collapsing inward or outward too far)
            alignment = abs(l_knee[0] - l_ankle[0])
            if alignment > 0.15:
                self.feedback.append("Align your front knee with your ankle")
                self.form_score = max(50, self.form_score - 10)
                
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        self.form_score = 100
        self.check_form(landmarks)
        return self.form_score
