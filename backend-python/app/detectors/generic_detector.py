from typing import List, Dict, Any, Tuple
from app.detectors.base_detector import BaseDetector

class GenericDetector(BaseDetector):
    """
    Fallback detector for general movement tracking.
    Uses default average joint angles for simple rep counting.
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
        kps = self.get_keypoints(landmarks)
        if not kps:
            return state_data.get('counter', 0), state_data.get('stage', 'up')
            
        l_shoulder = kps.get('l_shoulder')
        l_elbow = kps.get('l_elbow')
        l_wrist = kps.get('l_wrist')
        l_hip = kps.get('l_hip')
        l_knee = kps.get('l_knee')
        l_ankle = kps.get('l_ankle')
        
        # Calculate a general metric based on average change in major joint angles
        angle = 120.0
        if l_shoulder and l_elbow and l_wrist:
            angle = self.calculate_angle(l_shoulder[:2], l_elbow[:2], l_wrist[:2])
        elif l_hip and l_knee and l_ankle:
            angle = self.calculate_angle(l_hip[:2], l_knee[:2], l_ankle[:2])
            
        down_threshold = self.config.get('down_angle', 100.0)
        up_threshold = self.config.get('up_angle', 140.0)
        rom_min = self.config.get('rom_min', 40.0)
        
        counter = state_data.get('counter', 0)
        stage = state_data.get('stage', 'up')
        if stage is None:
            stage = 'up'
            
        min_angle = state_data.get('min_angle', 180.0)
        
        if stage == 'up':
            if angle < down_threshold:
                stage = 'down'
                min_angle = angle
        elif stage == 'down':
            min_angle = min(min_angle, angle)
            if angle > up_threshold:
                rom = up_threshold - min_angle
                if rom >= rom_min:
                    counter += 1
                stage = 'up'
                min_angle = 180.0
                
        state_data['min_angle'] = min_angle
        return counter, stage

    def check_form(self, landmarks) -> List[str]:
        self.feedback = []
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        return 100
