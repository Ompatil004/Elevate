from typing import List, Dict, Any, Tuple
from app.detectors.base_detector import BaseDetector

class CurlDetector(BaseDetector):
    """
    Detector for curl movements (bicep curls).
    Tracks elbow angle and shoulder stability.
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
        kps = self.get_keypoints(landmarks)
        if not kps:
            return state_data.get('counter', 0), state_data.get('stage', 'down')
            
        l_shoulder = kps.get('l_shoulder')
        l_elbow = kps.get('l_elbow')
        l_wrist = kps.get('l_wrist')
        
        if not (l_shoulder and l_elbow and l_wrist):
            return state_data.get('counter', 0), state_data.get('stage', 'down')
            
        elbow_angle = self.calculate_angle(l_shoulder[:2], l_elbow[:2], l_wrist[:2])
        
        down_threshold = self.config.get('down_angle', 45.0)  # contracted
        up_threshold = self.config.get('up_angle', 150.0)    # extended
        rom_min = self.config.get('rom_min', 90.0)
        
        counter = state_data.get('counter', 0)
        stage = state_data.get('stage', 'down')  # 'down' means extended / rest for curls
        if stage is None:
            stage = 'down'
            
        max_angle = state_data.get('max_angle', 0.0)
        min_angle = state_data.get('min_angle', 180.0)
        
        # State machine: down (extended) -> up (contracted) -> down (extended)
        if stage == 'down':
            max_angle = max(max_angle, elbow_angle)
            if elbow_angle < down_threshold:
                stage = 'up'
                min_angle = elbow_angle
        elif stage == 'up':
            min_angle = min(min_angle, elbow_angle)
            if elbow_angle > up_threshold:
                rom = max_angle - min_angle
                if rom >= rom_min:
                    counter += 1
                stage = 'down'
                max_angle = elbow_angle
                min_angle = 180.0
                
        state_data['max_angle'] = max_angle
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
        
        if l_shoulder and l_elbow and l_hip:
            # Check shoulder stability (avoid swinging)
            shoulder_angle = self.calculate_angle(l_hip[:2], l_shoulder[:2], l_elbow[:2])
            if shoulder_angle > 35:
                self.feedback.append("Keep elbows close to your sides - avoid shoulder swing")
                self.form_score = max(50, self.form_score - 15)
                
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        self.form_score = 100
        self.check_form(landmarks)
        return self.form_score
