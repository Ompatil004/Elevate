from typing import List, Dict, Any, Tuple
import time
from app.detectors.base_detector import BaseDetector

class PlankDetector(BaseDetector):
    """
    Detector for plank movements (isometric holds).
    Tracks hip angle and detects hold stability.
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
        # Planks are isometric, we count the hold time (represented as reps / hold duration)
        kps = self.get_keypoints(landmarks)
        if not kps:
            return state_data.get('counter', 0), state_data.get('stage', 'rest')
            
        l_shoulder = kps.get('l_shoulder')
        l_hip = kps.get('l_hip')
        l_knee = kps.get('l_knee')
        
        if not (l_shoulder and l_hip and l_knee):
            return state_data.get('counter', 0), state_data.get('stage', 'rest')
            
        hip_angle = self.calculate_angle(l_shoulder[:2], l_hip[:2], l_knee[:2])
        
        down_threshold = self.config.get('down_angle', 130.0)
        up_threshold = self.config.get('up_angle', 185.0)
        
        counter = state_data.get('counter', 0)
        stage = state_data.get('stage', 'rest')
        
        is_in_position = down_threshold <= hip_angle <= up_threshold
        
        now = time.time()
        hold_start = state_data.get('hold_start_time', 0.0)
        
        if is_in_position:
            if hold_start == 0.0:
                hold_start = now
                stage = 'holding'
            else:
                elapsed = now - hold_start
                # Increment counter every 5 seconds of plank hold
                if elapsed >= 5.0:
                    counter += 1
                    hold_start = now  # Reset hold start to track next 5s block
        else:
            hold_start = 0.0
            stage = 'rest'
            
        state_data['hold_start_time'] = hold_start
        return counter, stage

    def check_form(self, landmarks) -> List[str]:
        self.feedback = []
        kps = self.get_keypoints(landmarks)
        if not kps:
            return self.feedback
            
        l_shoulder = kps.get('l_shoulder')
        l_hip = kps.get('l_hip')
        l_knee = kps.get('l_knee')
        
        if l_shoulder and l_hip and l_knee:
            hip_angle = self.calculate_angle(l_shoulder[:2], l_hip[:2], l_knee[:2])
            if hip_angle < 130:
                self.feedback.append("Engage your core - don't let your hips sag")
                self.form_score = max(50, self.form_score - 15)
            elif hip_angle > 185:
                self.feedback.append("Lower your hips to stay parallel to the floor")
                self.form_score = max(50, self.form_score - 10)
                
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        self.form_score = 100
        self.check_form(landmarks)
        return self.form_score
