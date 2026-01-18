import cv2
import numpy as np
import time
import threading
from queue import Queue

# --- Import MediaPipe safely ---
try:
    import mediapipe as mp
    from mediapipe import solutions
    mp_pose = solutions.pose
    mp_draw = solutions.drawing_utils
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class EnhancedPoseTracker:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.form_feedback = ""
        self.coaching_message = ""
        self.performance_metrics = {}
        self.current_exercise = "bicep_curl"  # Default
        self.exercise_history = []
        self.last_feedback_time = time.time()
        self.feedback_queue = Queue()
        self.safety_alerts = []
        self.difficulty_level = "moderate"  # easy, moderate, hard
        self.fatigue_detected = False
        
        if AI_AVAILABLE:
            self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        else:
            self.pose = None

    def set_exercise(self, exercise_name):
        """Switch the tracking logic based on user selection"""
        self.current_exercise = exercise_name
        self.counter = 0
        self.stage = None
        self.form_feedback = ""
        self.coaching_message = ""
        self.performance_metrics = {}
        self.fatigue_detected = False
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

    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def detect_form_errors(self, landmarks, exercise_name, calculated_angles):
        """Detect form errors based on exercise type"""
        feedback = []
        
        # Define landmark positions
        l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 
                      landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, 
                   landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, 
                   landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, 
                 landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, 
                  landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, 
                   landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, 
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, 
                 landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        
        # Spine alignment check (shoulder-hip distance)
        spine_deviation = abs(l_shoulder[1] - l_hip[1])
        
        if exercise_name == "bicep_curl":
            # Check for form errors in bicep curl
            if spine_deviation > 0.1:  # Threshold for spine deviation
                feedback.append("Keep your back straight")
            
            # Check for proper elbow position (shouldn't move too much)
            elbow_to_body_distance = self.calculate_distance(l_elbow, l_shoulder)
            if elbow_to_body_distance > 0.2:  # Threshold for elbow drift
                feedback.append("Keep your elbows close to your body")
                
        elif exercise_name == "squat":
            # Check for knee tracking over toes
            knee_angle = calculated_angles.get('knee_angle', 90)
            if knee_angle < 20:  # Knee collapsing inward
                feedback.append("Keep your knees aligned with your toes")
            
            # Check for spine alignment
            if spine_deviation > 0.15:
                feedback.append("Keep your chest up and back straight")
                
            # Check for depth (ankle-knee-hip angle)
            hip_angle = self.calculate_angle(l_shoulder, l_hip, l_knee)
            if hip_angle > 150:  # Not going deep enough
                feedback.append("Go deeper in your squat")
                
        elif exercise_name == "pushup":
            # Check for proper plank position
            if spine_deviation > 0.1:
                feedback.append("Keep your body in a straight line")
                
            # Check for full range of motion
            elbow_angle = calculated_angles.get('elbow_angle', 90)
            if elbow_angle > 150:  # Not going low enough
                feedback.append("Lower your body more")
                
        elif exercise_name == "shoulder_press":
            # Check for spine alignment
            if spine_deviation > 0.1:
                feedback.append("Keep your back straight")
                
            # Check for proper arm extension
            elbow_angle = calculated_angles.get('elbow_angle', 90)
            if elbow_angle < 160:  # Not pressing fully
                feedback.append("Fully extend your arms at the top")
                
        elif exercise_name == "lunge":
            # Check for front knee position
            knee_angle = calculated_angles.get('knee_angle', 90)
            if knee_angle < 20:  # Knee collapsing inward
                feedback.append("Keep your front knee aligned with your toe")
                
            # Check for spine alignment
            if spine_deviation > 0.1:
                feedback.append("Keep your chest up and back straight")
                
        return feedback

    def provide_coaching_cues(self, exercise_name, calculated_angles, stage, counter):
        """Provide real-time coaching cues based on exercise and performance"""
        cues = []
        
        if exercise_name == "bicep_curl":
            if stage == "up":
                cues.append("Squeeze your bicep at the top")
            elif stage == "down":
                cues.append("Control the weight on the way down")
                
        elif exercise_name == "squat":
            if stage == "down":
                cues.append("Drive through your heels to stand up")
            elif stage == "up":
                cues.append("Keep your chest up and core tight")
                
        elif exercise_name == "pushup":
            if stage == "down":
                cues.append("Push through your palms to rise up")
            elif stage == "up":
                cues.append("Engage your core and keep steady breathing")
                
        elif exercise_name == "shoulder_press":
            if stage == "up":
                cues.append("Hold for a moment at the top")
            elif stage == "down":
                cues.append("Lower with control")
                
        elif exercise_name == "lunge":
            if stage == "down":
                cues.append("Push through your front heel to return")
            elif stage == "up":
                cues.append("Keep your core engaged")
        
        # Add encouragement based on rep count
        if counter > 0 and counter % 5 == 0:
            cues.append(f"Great job! You've done {counter} reps")
        
        return cues

    def detect_safety_issues(self, landmarks, exercise_name, calculated_angles):
        """Detect potential safety issues that could lead to injury"""
        alerts = []
        
        # Define landmark positions
        l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 
                      landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, 
                   landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, 
                   landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, 
                 landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, 
                  landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, 
                   landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        
        # Check for extreme joint angles that could indicate risk
        if exercise_name in ["bicep_curl", "shoulder_press"]:
            elbow_angle = calculated_angles.get('elbow_angle', 180)
            if elbow_angle < 5:  # Elbow hyperextension risk
                alerts.append("Stop! Risk of elbow hyperextension")
        
        if exercise_name in ["squat", "lunge"]:
            knee_angle = calculated_angles.get('knee_angle', 180)
            if knee_angle < 10:  # Knee hyperextension risk
                alerts.append("Stop! Risk of knee hyperextension")
        
        # Check for spine alignment issues
        spine_deviation = abs(l_shoulder[1] - l_hip[1])
        if spine_deviation > 0.25:  # Significant spine misalignment
            alerts.append("Stop! Correct your spine alignment")
        
        return alerts

    def adjust_difficulty(self, performance_data):
        """Automatically adjust workout difficulty based on performance"""
        # Placeholder for performance-based difficulty adjustment
        # This would typically analyze rep speed, form quality, consistency, etc.
        if performance_data.get('form_accuracy', 0.8) > 0.9 and performance_data.get('consistency', 0.7) > 0.8:
            # User performing well, increase difficulty
            if self.difficulty_level == "easy":
                self.difficulty_level = "moderate"
            elif self.difficulty_level == "moderate":
                self.difficulty_level = "hard"
        elif performance_data.get('form_accuracy', 0.8) < 0.7 or performance_data.get('consistency', 0.7) < 0.6:
            # User struggling, decrease difficulty
            if self.difficulty_level == "hard":
                self.difficulty_level = "moderate"
            elif self.difficulty_level == "moderate":
                self.difficulty_level = "easy"
    
    def detect_fatigue(self, recent_performance):
        """Detect signs of fatigue based on declining performance"""
        # Placeholder for fatigue detection algorithm
        # This would analyze form degradation, slower movement, etc.
        form_degradation = recent_performance.get('form_degradation', 0)
        if form_degradation > 0.2:  # 20% decline in form quality
            self.fatigue_detected = True
            return True
        return False

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

                # Dictionary to store calculated angles for form checking
                calculated_angles = {}

                # --- EXERCISE LOGIC SWITCHER ---

                # 1. BICEP CURL (Arm Angle)
                if self.current_exercise == "bicep_curl":
                    angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                    calculated_angles['elbow_angle'] = angle
                    if angle > 160: self.stage = "down"
                    if angle < 30 and self.stage == 'down':
                        self.stage = "up"
                        self.counter += 1

                # 2. SQUAT (Knee Angle)
                elif self.current_exercise == "squat":
                    # Angle between Hip, Knee, Ankle
                    angle = self.calculate_angle(l_hip, l_knee, l_ankle)
                    calculated_angles['knee_angle'] = angle
                    # Stand: ~170-180, Squat: < 90
                    if angle > 160: self.stage = "up"
                    if angle < 90 and self.stage == 'up':
                        self.stage = "down"
                        self.counter += 1

                # 3. PUSHUP (Elbow Angle + Body Alignment)
                elif self.current_exercise == "pushup":
                    elbow_angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                    calculated_angles['elbow_angle'] = elbow_angle
                    # Up: Arms straight (> 160), Down: Arms bent (< 90)
                    if elbow_angle > 160: self.stage = "up"
                    if elbow_angle < 90 and self.stage == 'up':
                        self.stage = "down"
                        self.counter += 1

                # 4. SHOULDER PRESS (Shoulder-Elbow-Wrist, but vertical)
                elif self.current_exercise == "shoulder_press":
                    angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                    calculated_angles['elbow_angle'] = angle
                    # Down: Hands at ears (< 90), Up: Hands high (> 160)
                    if angle < 90: self.stage = "down"
                    if angle > 160 and self.stage == 'down':
                        self.stage = "up"
                        self.counter += 1

                # 5. LUNGE (Hip-Knee-Ankle like squat, but different threshold)
                elif self.current_exercise == "lunge":
                    angle = self.calculate_angle(l_hip, l_knee, l_ankle)
                    calculated_angles['knee_angle'] = angle
                    if angle > 160: self.stage = "up"
                    if angle < 100 and self.stage == 'up': # Lunges rarely go as deep as squats
                        self.stage = "down"
                        self.counter += 1

                # Form correction and safety checks
                form_errors = self.detect_form_errors(landmarks, self.current_exercise, calculated_angles)
                safety_alerts = self.detect_safety_issues(landmarks, self.current_exercise, calculated_angles)
                
                # Set form feedback
                if form_errors:
                    self.form_feedback = "; ".join(form_errors)
                else:
                    self.form_feedback = "Good form!"
                
                # Set safety alerts
                if safety_alerts:
                    self.safety_alerts = safety_alerts
                    # Draw red box for safety alerts
                    cv2.rectangle(frame, (0, 85), (frame.shape[1], 130), (0, 0, 255), -1)  # Red for danger
                    for i, alert in enumerate(safety_alerts):
                        cv2.putText(frame, f"SAFETY ALERT: {alert}", (10, 115 + i*20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
                else:
                    self.safety_alerts = []
                
                # Provide coaching cues
                coaching_cues = self.provide_coaching_cues(self.current_exercise, calculated_angles, self.stage, self.counter)
                if coaching_cues and time.time() - self.last_feedback_time > 3:  # Limit feedback frequency
                    self.coaching_message = coaching_cues[-1]  # Take the last cue
                    self.last_feedback_time = time.time()
                
                # Performance metrics for difficulty adjustment
                self.performance_metrics = {
                    'form_accuracy': 1.0 if not form_errors else max(0.5, 1.0 - len(form_errors) * 0.1),
                    'consistency': 0.8,  # Placeholder - would be calculated based on movement patterns
                    'rep_speed': 1.0  # Placeholder - would be calculated based on rep timing
                }
                
                # Adjust difficulty based on performance
                self.adjust_difficulty(self.performance_metrics)
                
                # Fatigue detection
                recent_performance = {
                    'form_degradation': 0.1 if form_errors else 0.0  # Simplified for demo
                }
                self.detect_fatigue(recent_performance)

                # --- DRAW ENHANCED UI ---
                # Draw Blue Box for main text
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

                # Form Feedback (Green for good, Yellow for warnings)
                feedback_color = (0, 255, 0) if not form_errors else (0, 255, 255)  # Green or Yellow
                cv2.putText(frame, self.form_feedback, (15, frame.shape[0] - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, feedback_color, 2, cv2.LINE_AA)

                # Coaching Message
                if self.coaching_message:
                    cv2.putText(frame, f"Coach: {self.coaching_message}", (15, frame.shape[0] - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                # Fatigue indicator
                if self.fatigue_detected:
                    cv2.putText(frame, "Fatigue Detected - Consider Rest", (frame.shape[1]//2 - 120, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

            except Exception as e:
                print(f"Error in processing frame: {e}")
                pass

        return frame, results