from typing import List, Dict, Any, Tuple
from app.detectors.base_detector import BaseDetector

class PushDetector(BaseDetector):
    """
    Detector for push movements (horizontal_push, vertical_push).
    Tracks elbow angle and checks for body alignment / flaring elbows.
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
        kps = self.get_keypoints(landmarks)
        if not kps:
            return state_data.get('counter', 0), state_data.get('stage', 'up')
            
        l_shoulder = kps.get('l_shoulder')
        l_elbow = kps.get('l_elbow')
        l_wrist = kps.get('l_wrist')
        
        if not (l_shoulder and l_elbow and l_wrist):
            return state_data.get('counter', 0), state_data.get('stage', 'up')
            
        elbow_angle = self.calculate_angle(l_shoulder[:2], l_elbow[:2], l_wrist[:2])
        
        down_threshold = self.config.get('down_angle', 90.0)
        up_threshold = self.config.get('up_angle', 160.0)
        rom_min = self.config.get('rom_min', 60.0)
        
        counter = state_data.get('counter', 0)
        stage = state_data.get('stage', 'up')
        if stage is None:
            stage = 'up'
            
        min_angle = state_data.get('min_angle', 180.0)
        
        if stage == 'up':
            if elbow_angle < down_threshold:
                stage = 'down'
                min_angle = elbow_angle
        elif stage == 'down':
            min_angle = min(min_angle, elbow_angle)
            if elbow_angle > up_threshold:
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
            
        l_shoulder = kps.get('l_shoulder')
        l_elbow = kps.get('l_elbow')
        l_wrist = kps.get('l_wrist')
        l_hip = kps.get('l_hip')
        l_ankle = kps.get('l_ankle')
        
        # Check body alignment (e.g. saggy hips in pushups)
        if l_shoulder and l_hip and l_ankle:
            alignment = abs((l_shoulder[1] - l_hip[1]) - (l_hip[1] - l_ankle[1]))
            if alignment > 0.15:
                self.feedback.append("Keep your body in a straight line")
                self.form_score = max(50, self.form_score - 15)
                
        # Check if elbows are flaring too wide
        if l_shoulder and l_elbow and l_wrist:
            shoulder_angle = self.calculate_angle(l_hip[:2] if l_hip else [l_shoulder[0], l_shoulder[1] + 0.5], l_shoulder[:2], l_elbow[:2])
            if shoulder_angle > 85:
                self.feedback.append("Avoid flaring elbows too wide")
                self.form_score = max(50, self.form_score - 10)
                
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        self.form_score = 100
        self.check_form(landmarks)
        return self.form_score
