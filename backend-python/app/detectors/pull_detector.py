from typing import List, Dict, Any, Tuple
from app.detectors.base_detector import BaseDetector

class PullDetector(BaseDetector):
    """
    Detector for pull movements (horizontal_pull, vertical_pull, row, dip).
    Tracks elbow angle and shoulder positioning.
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
        
        # Pull exercises have contraction at the bottom or top depending on geometry
        # Let's support standard state machine where 'down' means contracted (elbow angle is small)
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
        l_hip = kps.get('l_hip')
        
        # Check posture/leaning angle
        if l_shoulder and l_hip:
            # We want to check torso stability
            if l_shoulder[1] > l_hip[1] + 0.1:
                self.feedback.append("Keep your spine neutral - don't round your back")
                self.form_score = max(50, self.form_score - 15)
                
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        self.form_score = 100
        self.check_form(landmarks)
        return self.form_score
