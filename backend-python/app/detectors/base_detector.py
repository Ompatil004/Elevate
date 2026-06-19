import numpy as np
from typing import List, Dict, Any, Tuple

class BaseDetector:
    """
    Abstract base class for all movement pattern detectors.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feedback = []
        self.confidence = 1.0
        self.form_score = 100
        
    def calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        """Calculate angle between three points (a, b, c) at joint b."""
        a_arr = np.array(a)
        b_arr = np.array(b)
        c_arr = np.array(c)
        
        radians = np.arctan2(c_arr[1] - b_arr[1], c_arr[0] - b_arr[0]) - np.arctan2(a_arr[1] - b_arr[1], a_arr[0] - b_arr[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360.0 - angle
        return angle

    def get_keypoints(self, landmarks) -> Dict[str, List[float]]:
        """Extract main joint keypoints from landmarks."""
        # MediaPipe Pose landmark indices:
        # L_Shoulder=11, R_Shoulder=12, L_Elbow=13, R_Elbow=14, L_Wrist=15, R_Wrist=16
        # L_Hip=23, R_Hip=24, L_Knee=25, R_Knee=26, L_Ankle=27, R_Ankle=28
        points = {}
        try:
            points['l_shoulder'] = [landmarks[11].x, landmarks[11].y, landmarks[11].visibility]
            points['r_shoulder'] = [landmarks[12].x, landmarks[12].y, landmarks[12].visibility]
            points['l_elbow'] = [landmarks[13].x, landmarks[13].y, landmarks[13].visibility]
            points['r_elbow'] = [landmarks[14].x, landmarks[14].y, landmarks[14].visibility]
            points['l_wrist'] = [landmarks[15].x, landmarks[15].y, landmarks[15].visibility]
            points['r_wrist'] = [landmarks[16].x, landmarks[16].y, landmarks[16].visibility]
            points['l_hip'] = [landmarks[23].x, landmarks[23].y, landmarks[23].visibility]
            points['r_hip'] = [landmarks[24].x, landmarks[24].y, landmarks[24].visibility]
            points['l_knee'] = [landmarks[25].x, landmarks[25].y, landmarks[25].visibility]
            points['r_knee'] = [landmarks[26].x, landmarks[26].y, landmarks[26].visibility]
            points['l_ankle'] = [landmarks[27].x, landmarks[27].y, landmarks[27].visibility]
            points['r_ankle'] = [landmarks[28].x, landmarks[28].y, landmarks[28].visibility]
        except Exception:
            pass
        return points

    def get_confidence(self, landmarks) -> float:
        """Calculate mean confidence (visibility) of active tracking landmarks."""
        kps = self.get_keypoints(landmarks)
        if not kps:
            return 0.0
        
        # Determine relevant joints based on configured tracking joint
        joint_type = self.config.get('joint', 'avg')
        relevant_joints = []
        if joint_type == 'knee':
            relevant_joints = ['l_hip', 'r_hip', 'l_knee', 'r_knee', 'l_ankle', 'r_ankle']
        elif joint_type == 'elbow':
            relevant_joints = ['l_shoulder', 'r_shoulder', 'l_elbow', 'r_elbow', 'l_wrist', 'r_wrist']
        elif joint_type == 'hip':
            relevant_joints = ['l_shoulder', 'r_shoulder', 'l_hip', 'r_hip', 'l_knee', 'r_knee']
        elif joint_type == 'shoulder':
            relevant_joints = ['l_hip', 'r_hip', 'l_shoulder', 'r_shoulder', 'l_elbow', 'r_elbow']
        else:
            relevant_joints = list(kps.keys())
            
        visibilities = [kps[j][2] for j in relevant_joints if j in kps]
        if not visibilities:
            return 0.0
        return float(np.mean(visibilities))

    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
        """Perform state-machine based rep counting with hysteresis and ROM check."""
        raise NotImplementedError

    def check_form(self, landmarks) -> List[str]:
        """Perform form validation and update self.feedback."""
        raise NotImplementedError

    def get_feedback(self) -> List[str]:
        """Get the latest structured feedback messages."""
        return self.feedback

    def calculate_form_score(self, landmarks) -> int:
        """Calculate a dynamic form score from 0 to 100."""
        raise NotImplementedError
