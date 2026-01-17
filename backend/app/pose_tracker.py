import cv2
import numpy as np

# --- Import MediaPipe safely ---
try:
    import mediapipe as mp
    from mediapipe import solutions
    mp_pose = solutions.pose
    mp_draw = solutions.drawing_utils
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class PoseTracker:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.current_exercise = "bicep_curl"  # Default
        
        if AI_AVAILABLE:
            self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        else:
            self.pose = None

    def set_exercise(self, exercise_name):
        """Switch the tracking logic based on user selection"""
        self.current_exercise = exercise_name
        self.counter = 0
        self.stage = None
        print(f"Switched to: {self.current_exercise}")

    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0: angle = 360-angle
        return angle

    def process_frame(self, frame):
        if not AI_AVAILABLE or self.pose is None:
            return frame, None

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if results.pose_landmarks:
            # Draw Skeleton
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            try:
                landmarks = results.pose_landmarks.landmark
                
                # --- GET KEY BODY POINTS ---
                # Left Side
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                l_elbow    = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                l_wrist    = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,    landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                l_hip      = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,      landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                l_knee     = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                l_ankle    = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,    landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                # --- EXERCISE LOGIC SWITCHER ---
                
                # 1. BICEP CURL (Arm Angle)
                if self.current_exercise == "bicep_curl":
                    angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                    if angle > 160: self.stage = "down"
                    if angle < 30 and self.stage == 'down':
                        self.stage = "up"
                        self.counter += 1

                # 2. SQUAT (Knee Angle)
                elif self.current_exercise == "squat":
                    # Angle between Hip, Knee, Ankle
                    angle = self.calculate_angle(l_hip, l_knee, l_ankle)
                    # Stand: ~170-180, Squat: < 90
                    if angle > 160: self.stage = "up"
                    if angle < 90 and self.stage == 'up':
                        self.stage = "down"
                        self.counter += 1

                # 3. PUSHUP (Elbow Angle + Body Alignment)
                elif self.current_exercise == "pushup":
                    elbow_angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                    # Up: Arms straight (> 160), Down: Arms bent (< 90)
                    if elbow_angle > 160: self.stage = "up"
                    if elbow_angle < 90 and self.stage == 'up':
                        self.stage = "down"
                        self.counter += 1

                # 4. SHOULDER PRESS (Shoulder-Elbow-Wrist, but vertical)
                elif self.current_exercise == "shoulder_press":
                    angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                    # Down: Hands at ears (< 90), Up: Hands high (> 160)
                    if angle < 90: self.stage = "down"
                    if angle > 160 and self.stage == 'down':
                        self.stage = "up"
                        self.counter += 1
                
                # 5. LUNGE (Hip-Knee-Ankle like squat, but different threshold)
                elif self.current_exercise == "lunge":
                    angle = self.calculate_angle(l_hip, l_knee, l_ankle)
                    if angle > 160: self.stage = "up"
                    if angle < 100 and self.stage == 'up': # Lunges rarely go as deep as squats
                        self.stage = "down"
                        self.counter += 1

                # --- DRAW UI ---
                # Draw Blue Box for text
                cv2.rectangle(frame, (0,0), (300, 85), (245,117,16), -1)
                
                # Exercise Name
                cv2.putText(frame, self.current_exercise.upper(), (15,25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                
                # Counter
                cv2.putText(frame, str(self.counter), (10,75), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                
                # Stage
                if self.stage:
                    cv2.putText(frame, self.stage, (100,75), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 2, cv2.LINE_AA)
                           
            except Exception as e:
                pass
            
        return frame, results