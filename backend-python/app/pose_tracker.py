import cv2
import numpy as np
import pandas as pd
from datetime import datetime

# --- Import MediaPipe safely ---
try:
    import mediapipe as mp
    from mediapipe import solutions
    mp_pose = solutions.pose
    mp_draw = solutions.drawing_utils
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


def _ensure_cv2() -> bool:
    return hasattr(cv2, "cvtColor") and hasattr(cv2, "putText")

class PoseTracker:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.current_exercise = "bicep_curl"  # Default
        self.target_reps = 10  # Default target repetitions
        self.exercise_completed = False   # renamed (was is_exercise_completed)
        self.exercise_skipped = False     # renamed (was is_exercise_skipped)
        self.completed_exercises = []  # Track completed exercises
        self.skipped_exercises = []  # Track skipped exercises
        self.total_exercises_in_workout = 0  # Total exercises in the current workout
        self.workout_plan = []  # Store the current workout plan
        self.workout_session_active = False  # Track if a workout session is active
        self.streak_days = 0  # Track consecutive workout days
        self.last_workout_date = None  # Track the last workout date
        self.base_intensity = 1.0  # Base intensity multiplier
        self.intensity_multiplier = 1.0  # Current intensity multiplier based on streak
        self.adjusted_reps = 10  # Adjusted reps based on intensity
        self.adjusted_sets = 3  # Adjusted sets based on intensity
        self.total_workouts_completed = 0  # Track total workouts completed
        self.total_workouts_skipped = 0  # Track total workouts skipped
        self.form_accuracy_scores = []  # Track form accuracy scores
        self.confidence_history = []  # Track recent frame confidence values
        self.frame_count = 0  # Track how many frames have been processed
        self.current_experience_level = "Beginner"  # Track current experience level
        self.upgrade_suggested = False  # Track if upgrade has been suggested
        self.upgrade_readiness_score = 0  # Track readiness score for upgrade
        self.detector = None
        self.detector_config = {}
        self.detector_state = {"counter": 0, "stage": None, "min_angle": 180.0}

        self._configure_detector(self.current_exercise)

        if AI_AVAILABLE:
            self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        else:
            self.pose = None

    def _configure_detector(self, exercise_name):
        try:
            from app.detectors import DetectorFactory

            self.detector = DetectorFactory.get_detector(exercise_name)
            self.detector_config = DetectorFactory.get_exercise_config(exercise_name)
        except Exception:
            self.detector = None
            self.detector_config = {}
        self.detector_state = {"counter": 0, "stage": None, "min_angle": 180.0}

    def process_frame(self, frame):
        # Handle case where AI is not available
        if not AI_AVAILABLE or self.pose is None:
            # Return original frame with error message if AI is not available
            cv2.putText(frame, 'AI Not Available', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame, None

        try:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = self.pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error processing frame: {e}")
            # Return original frame with error indication
            cv2.putText(frame, 'Pose Detection Error', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame, None

        try:
            landmarks = results.pose_landmarks.landmark

            # --- 1. BICEP CURL (Arms) ---
            if self.current_exercise == "bicep_curl":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = self.calculate_angle(shoulder, elbow, wrist)

                if angle > 160:
                    self.stage = "down"
                    self.feedback = "Up!"
                if angle < 30 and self.stage == 'down':
                    self.stage = "up"
                    self.counter += 1
                    self.feedback = "Good!"

            # --- 2. SQUAT (Legs) ---
            elif self.current_exercise == "squat":
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                angle = self.calculate_angle(hip, knee, ankle)

                if angle > 170:
                    self.stage = "up"
                    self.feedback = "Sit Back!"
                if angle < 90 and self.stage == 'up':
                    self.stage = "down"
                    self.counter += 1
                    self.feedback = "Rise!"

            # --- 3. PUSH-UP (Chest) ---
            elif self.current_exercise == "pushup":
                # Calculate Elbow Angle
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = self.calculate_angle(shoulder, elbow, wrist)

                # Push-up Logic (Check if body is horizontal roughly)
                if angle > 160:
                    self.stage = "up"
                    self.feedback = "Go Down!"
                if angle < 90 and self.stage == 'up':
                    self.stage = "down"
                    self.counter += 1
                    self.feedback = "Push Up!"

            # --- CHECK COMPLETION ---
            if self.counter >= self.target_reps:
                self.exercise_completed = True
                self.feedback = " SET COMPLETE!"

        except Exception as e:
            pass

        # ... (Drawing code remains the same)
        mp_drawing = mp.solutions.drawing_utils # type: ignore

        # Draw Scoreboard
        cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
        cv2.putText(image, 'REPS', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, str(self.counter), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(image, self.stage if self.stage else "-", (60,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)

        return image, self.counter

    def set_exercise(self, exercise_name):
        """Switch the tracking logic based on user selection"""
        # Reset the exercise state before setting a new exercise
        self.reset_exercise_state()

        self.current_exercise = exercise_name
        self._configure_detector(exercise_name)
        # Set target reps based on exercise type (could be customized per exercise)
        self.target_reps = 10  # Default to 10 reps
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

    def get_confidence(self, landmarks):
        """Return an average visibility score for the current landmarks."""
        if not landmarks:
            return 0.0

        visibilities = []
        for landmark in landmarks:
            visibility = getattr(landmark, "visibility", None)
            if visibility is not None:
                visibilities.append(float(visibility))

        if not visibilities:
            return 0.0
        return float(sum(visibilities) / len(visibilities))

    def check_form_correctness(self, pose_landmarks):
        """Check if the current pose matches the expected form for the exercise"""
        if not pose_landmarks or not AI_AVAILABLE:
            return False

        try:
            landmarks = pose_landmarks.landmark

            # Define exercise-specific form checks
            if self.current_exercise == "bicep_curl":
                # For bicep curl, check if shoulders are stable and not swinging
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                r_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

                # Check if shoulders are relatively stable (not moving excessively)
                shoulder_distance = abs(l_shoulder[1] - r_shoulder[1])  # Vertical distance
                if shoulder_distance > 0.1:  # If shoulders are moving too much
                    return False

                # Check if the elbow is moving in the correct plane
                l_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                l_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                # Check if the movement is primarily in the sagittal plane (front-back)
                # For bicep curls, the wrist should stay relatively in line with the shoulder
                horizontal_deviation = abs(l_wrist[0] - l_shoulder[0])
                if horizontal_deviation > 0.2:  # If wrist moves too far horizontally
                    return False

                return True  # Form looks correct for bicep curl

            elif self.current_exercise == "squat":
                # For squat, check if knees track over toes and back stays straight
                l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                # Check if knee tracks over ankle (not collapsing inward)
                knee_ankle_alignment = abs(l_knee[0] - l_ankle[0])
                if knee_ankle_alignment > 0.1:  # If knee collapses inward too much
                    return False

                # Check if hips and shoulders stay aligned
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                hip_shoulder_alignment = abs(l_hip[1] - l_shoulder[1])
                if hip_shoulder_alignment > 0.15:  # If torso leans too far forward/back
                    return False

                return True  # Form looks correct for squat

            elif self.current_exercise == "pushup":
                # For pushup, check if body stays in straight line
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                # Check if body is in straight line (shoulder-hip-ankle alignment)
                body_alignment = abs((l_shoulder[1] - l_hip[1]) - (l_hip[1] - l_ankle[1]))
                if body_alignment > 0.15:  # If body sags or arches too much
                    return False

                return True  # Form looks correct for pushup

            elif self.current_exercise == "shoulder_press":
                # For shoulder press, check if core stays engaged and movement is vertical
                l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                l_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

                # Check if torso remains relatively vertical (not leaning back excessively)
                torso_angle = abs(l_hip[1] - l_shoulder[1])
                if torso_angle > 0.15:  # If torso leans back too much
                    return False

                return True  # Form looks correct for shoulder press

            elif self.current_exercise == "lunge":
                # For lunge, check if front knee tracks over toe and back leg is stable
                l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                # Check if knee tracks over ankle (not collapsing inward)
                knee_ankle_alignment = abs(l_knee[0] - l_ankle[0])
                if knee_ankle_alignment > 0.1:  # If knee collapses inward too much
                    return False

                return True  # Form looks correct for lunge

            # Default to True if exercise not recognized
            return True

        except Exception as e:
            print(f"Error checking form correctness: {e}")
            return False

    def process_frame(self, frame):
        if not AI_AVAILABLE or self.pose is None:
            return frame, None

        self.frame_count += 1

        # Create space for exercise GIF on the left side of the frame
        # Assuming the original frame dimensions
        height, width = frame.shape[:2]

        # Create a new frame with extra space on the left for the GIF
        gif_width = width // 3  # Reserve 1/3 of the width for the GIF
        new_width = width + gif_width
        combined_frame = np.zeros((height, new_width, 3), dtype=np.uint8)

        # Place the original camera frame on the right side
        combined_frame[:, gif_width:new_width] = frame

        # Draw a border to separate the GIF area from the camera feed
        cv2.rectangle(combined_frame, (gif_width, 0), (gif_width, height), (200, 200, 200), 2)

        # Add exercise name in the GIF area
        exercise_text = f"Current Exercise: {self.current_exercise.replace('_', ' ').title()}"
        cv2.putText(combined_frame, exercise_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Add instruction text in the GIF area
        instruction_text = "Perform the exercise"
        cv2.putText(combined_frame, instruction_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        try:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Use original frame for pose detection
            results = self.pose.process(image_rgb)

            # Check if pose detection was successful
            if not results.pose_landmarks:
                # Handle case where no pose landmarks were detected
                self.handle_no_pose_landmarks(combined_frame, gif_width)
                # Return early since there are no landmarks to process
                return combined_frame, results
        except Exception as e:
            print(f"Error processing frame: {e}")
            # Show error message on the frame
            cv2.putText(combined_frame, 'Camera Error - Check Permissions', (gif_width + 50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return combined_frame, None

        current_confidence = 0.0

        if results.pose_landmarks:
            current_confidence = float(self.get_confidence(results.pose_landmarks.landmark))

            # Determine if the form is correct based on the exercise and current stage
            form_correct = self.check_form_correctness(results.pose_landmarks)

            # Define colors based on form correctness
            if form_correct:
                # Green for correct form
                landmark_color = (0, 255, 0)  # BGR: Green
                connection_color = (0, 255, 0)  # BGR: Green
            else:
                # Red for incorrect form
                landmark_color = (0, 0, 255)  # BGR: Red
                connection_color = (0, 0, 255)  # BGR: Red

            # Draw Skeleton with color based on form correctness
            # We need to draw each connection individually to control colors
            self.draw_styled_landmarks(combined_frame[:, gif_width:new_width], results.pose_landmarks, landmark_color, connection_color)

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

                # Define exercise-specific thresholds
                exercise_thresholds = {
                    "bicep_curl": {
                        "down_threshold": 160,
                        "up_threshold": 45,
                        "rep_trigger": lambda angle, stage: angle < 45 and stage == 'down'
                    },
                    "squat": {
                        "up_threshold": 160,
                        "down_threshold": 90,
                        "rep_trigger": lambda angle, stage: angle < 90 and stage == 'up'
                    },
                    "pushup": {
                        "up_threshold": 160,
                        "down_threshold": 90,
                        "rep_trigger": lambda angle, stage: angle < 90 and stage == 'up'
                    },
                    "shoulder_press": {
                        "down_threshold": 110,
                        "up_threshold": 160,
                        "rep_trigger": lambda angle, stage: angle > 160 and stage == 'down'
                    },
                    "lunge": {
                        "up_threshold": 160,
                        "down_threshold": 100,
                        "rep_trigger": lambda angle, stage: angle < 100 and stage == 'up'
                    }
                }

                # Only update rep counting if exercise is not completed
                if not self.exercise_completed:
                    # 1. BICEP CURL (Arm Angle)
                    if self.current_exercise == "bicep_curl":
                        angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                        thresholds = exercise_thresholds["bicep_curl"]

                        if angle > thresholds["down_threshold"]:
                            self.stage = "down"
                        if thresholds["rep_trigger"](angle, self.stage):
                            self.stage = "up"
                            self.counter += 1

                    # 2. SQUAT (Knee Angle)
                    elif self.current_exercise == "squat":
                        # Angle between Hip, Knee, Ankle
                        angle = self.calculate_angle(l_hip, l_knee, l_ankle)
                        thresholds = exercise_thresholds["squat"]

                        if angle > thresholds["up_threshold"]:
                            self.stage = "up"
                        if thresholds["rep_trigger"](angle, self.stage):
                            self.stage = "down"
                            self.counter += 1

                    # 3. PUSHUP (Elbow Angle + Body Alignment)
                    elif self.current_exercise == "pushup":
                        elbow_angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                        thresholds = exercise_thresholds["pushup"]

                        if elbow_angle > thresholds["up_threshold"]:
                            self.stage = "up"
                        if thresholds["rep_trigger"](elbow_angle, self.stage):
                            self.stage = "down"
                            self.counter += 1

                    # 4. SHOULDER PRESS (Shoulder-Elbow-Wrist, but vertical)
                    elif self.current_exercise == "shoulder_press":
                        angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
                        thresholds = exercise_thresholds["shoulder_press"]

                        if angle < thresholds["down_threshold"]:
                            self.stage = "down"
                        if thresholds["rep_trigger"](angle, self.stage):
                            self.stage = "up"
                            self.counter += 1

                    # 5. LUNGE (Hip-Knee-Ankle like squat, but different threshold)
                    elif self.current_exercise == "lunge":
                        angle = self.calculate_angle(l_hip, l_knee, l_ankle)
                        thresholds = exercise_thresholds["lunge"]

                        if angle > thresholds["up_threshold"]:
                            self.stage = "up"
                        if thresholds["rep_trigger"](angle, self.stage):
                            self.stage = "down"
                            self.counter += 1

                # Check if exercise is completed (after all sets)
                # Assuming target reps are set elsewhere - default to 10 for demo purposes
                target_reps = getattr(self, 'target_reps', 10)

                if self.counter >= target_reps:
                    # Exercise completed - show green tick and disable interaction
                    # Keep the skeleton visible but prevent rep counting

                    # Draw a semi-transparent overlay to indicate completion
                    overlay = combined_frame[gif_width:new_width].copy()
                    cv2.rectangle(overlay, (0, 0), (combined_frame.shape[1] - gif_width, combined_frame.shape[0]), (0, 100, 0), -1)
                    cv2.addWeighted(overlay, 0.4, combined_frame[gif_width:new_width], 0.6, 0, combined_frame[gif_width:new_width])

                    # Draw green tick symbol
                    center_x = (combined_frame.shape[1] - gif_width) // 2
                    center_y = combined_frame.shape[0] // 2

                    # Draw a large green tick mark
                    tick_points = np.array([
                        [center_x - 50, center_y],
                        [center_x - 20, center_y + 30],
                        [center_x + 30, center_y - 30]
                    ], np.int32)

                    cv2.polylines(combined_frame, [tick_points], False, (0, 255, 0), 8)

                    # Add completion text
                    cv2.putText(combined_frame, "EXERCISE COMPLETED!", (center_x - 150, center_y - 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

                    # Add rep count
                    cv2.putText(combined_frame, f"{self.counter}/{target_reps} Reps", (center_x - 80, center_y + 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

                    # Mark as completed to prevent further interaction
                    self.exercise_completed = True

                    # Still draw the skeleton but don't update rep count
                    # We'll draw the skeleton with a neutral color since the exercise is done
                    self.draw_styled_landmarks(combined_frame[:, gif_width:new_width], results.pose_landmarks, (200, 200, 200), (200, 200, 200))
                else:
                    # Regular UI when exercise is ongoing
                    # Draw Blue Box for text on the camera feed side
                    cv2.rectangle(combined_frame[:, gif_width:new_width], (0,0), (300, 85), (245,117,16), -1)

                    # Exercise Name
                    cv2.putText(combined_frame[:, gif_width:new_width], self.current_exercise.upper(), (15,25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)

                    # Counter
                    cv2.putText(combined_frame[:, gif_width:new_width], str(self.counter), (10,75),
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

                    # Stage
                    if self.stage:
                        cv2.putText(combined_frame[:, gif_width:new_width], self.stage, (100,75),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 2, cv2.LINE_AA)

            except Exception as e:
                pass

        self.confidence_history.append(current_confidence)
        if len(self.confidence_history) > 120:
            self.confidence_history = self.confidence_history[-120:]
        if self.frame_count % 30 == 0:
            self.add_form_accuracy_score(round(current_confidence * 100, 2))

        return combined_frame, results

    def handle_camera_error(self, frame, error_message):
        """Handle camera-related errors gracefully"""
        if frame is not None:
            # Show error message on the frame
            cv2.putText(frame, error_message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, 'Please check camera permissions', (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
        return frame

    def handle_pose_detection_failure(self, frame):
        """Handle pose detection failures gracefully"""
        if frame is not None:
            # Show message indicating pose detection is not working
            cv2.putText(frame, 'Pose Detection Unavailable', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            cv2.putText(frame, 'Ensure good lighting and clear view', (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 1)
        return frame

    def handle_no_pose_landmarks(self, combined_frame, gif_width):
        """Handle case where no pose landmarks are detected"""
        # Show message in the camera area that pose is not detected
        cv2.putText(combined_frame, 'No Pose Detected', (gif_width + 50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
        cv2.putText(combined_frame, 'Ensure full body is visible in camera', (gif_width + 50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 1)
        return combined_frame

    def is_exercise_finished(self):
        """Check if the exercise is completed"""
        return self.exercise_completed

    def skip_current_exercise(self):
        """Mark the current exercise as skipped"""
        self.skipped_exercise = {
            "exercise_name": self.current_exercise,
            "skipped_at": datetime.now(),
            "reps_completed": self.counter,
            "status": "skipped"
        }
        self.exercise_skipped = True
        return self.skipped_exercise

    def is_exercise_skipped_flag(self):
        """Check if the current exercise was skipped"""
        return self.exercise_skipped

    def reset_exercise_state(self):
        """Reset the exercise state to allow a new exercise"""
        self.counter = 0
        self.stage = None
        self.exercise_completed = False
        self.exercise_skipped = False
        self.detector_state = {"counter": 0, "stage": None, "min_angle": 180.0}
        if hasattr(self, 'skipped_exercise'):
            delattr(self, 'skipped_exercise')

    def start_workout_session(self, workout_plan):
        """Initialize a new workout session with the given plan"""
        self.workout_plan = workout_plan
        self.total_exercises_in_workout = len(workout_plan)
        self.completed_exercises = []
        self.skipped_exercises = []
        self.workout_session_active = True
        # Set the first exercise
        if workout_plan:
            first_exercise = workout_plan[0]
            self.set_exercise(first_exercise.get('name', 'bicep_curl') if isinstance(first_exercise, dict) else str(first_exercise))
        return True

    def mark_exercise_completed(self):
        """Mark the current exercise as completed and add to completed list"""
        if self.workout_session_active:
            completed_exercise = {
                "exercise_name": self.current_exercise,
                "completed_at": datetime.now(),
                "reps_completed": self.counter,
                "status": "completed"
            }
            self.completed_exercises.append(completed_exercise)
            self.exercise_completed = True
            # Update streak when exercise is completed
            self.update_streak(workout_completed_today=True)
            # Log the activity for analytics
            self.update_activity_log("exercise_completed", completed_exercise)
            return completed_exercise
        return None

    def mark_exercise_skipped(self):
        """Mark the current exercise as skipped and add to skipped list"""
        if self.workout_session_active:
            skipped_exercise = {
                "exercise_name": self.current_exercise,
                "skipped_at": datetime.now(),
                "reps_completed": self.counter,
                "status": "skipped"
            }
            self.skipped_exercises.append(skipped_exercise)
            self.exercise_skipped = True
            # Update streak when exercise is skipped
            self.update_streak(workout_completed_today=False)
            # Log the activity for analytics
            self.update_activity_log("exercise_skipped", skipped_exercise)
            return skipped_exercise
        return None

    def is_workout_completed(self):
        """Check if all exercises in the workout have been completed or skipped"""
        if not self.workout_session_active:
            return False
        total_tracked = len(self.completed_exercises) + len(self.skipped_exercises)
        return total_tracked >= self.total_exercises_in_workout

    def get_current_exercise_index(self):
        """Get the index of the current exercise in the workout plan"""
        if not self.workout_plan:
            return -1

        # Find the current exercise in the plan
        for i, exercise in enumerate(self.workout_plan):
            exercise_name = exercise.get('name', str(exercise)) if isinstance(exercise, dict) else str(exercise)
            if exercise_name == self.current_exercise:
                return i
        return -1

    def get_next_exercise(self):
        """Get the next exercise in the workout plan"""
        current_index = self.get_current_exercise_index()
        if current_index != -1 and current_index + 1 < len(self.workout_plan):
            next_exercise = self.workout_plan[current_index + 1]
            return next_exercise.get('name', str(next_exercise)) if isinstance(next_exercise, dict) else str(next_exercise)
        return None

    def move_to_next_exercise(self):
        """Move to the next exercise in the workout plan"""
        next_exercise_name = self.get_next_exercise()
        if next_exercise_name:
            self.set_exercise(next_exercise_name)
            self.exercise_completed = False
            self.exercise_skipped = False
            return True
        return False

    def update_streak(self, workout_completed_today=True):
        """Update the workout streak based on consecutive days"""
        from datetime import date

        today = date.today()

        if workout_completed_today:
            # Increment completed workouts count
            self.total_workouts_completed += 1
        else:
            # Increment skipped workouts count
            self.total_workouts_skipped += 1

        if self.last_workout_date is None:
            # First workout
            self.last_workout_date = today
            self.streak_days = 1
        else:
            # Calculate days since last workout
            days_since_last = (today - self.last_workout_date).days

            if days_since_last == 1:
                # Consecutive day - increment streak
                self.streak_days += 1
            elif days_since_last == 0:
                # Same day - no change to streak
                pass
            else:
                # Break in streak - reset to 1
                self.streak_days = 1

            self.last_workout_date = today

        # Update intensity based on streak
        self.update_intensity_based_on_streak()

        return self.streak_days

    def update_intensity_based_on_streak(self):
        """Gradually increase intensity based on streak"""
        # Store previous values to determine if there was a change
        prev_intensity = getattr(self, 'intensity_multiplier', 1.0)

        # Increase intensity gradually based on streak
        # Every 3 days of streak, slightly increase intensity
        base_multiplier = 1.0
        additional_multiplier = min(self.streak_days // 3 * 0.1, 0.5)  # Cap at 50% increase

        self.intensity_multiplier = base_multiplier + additional_multiplier

        # Adjust reps and sets based on intensity
        self.adjusted_reps = max(8, int(10 * self.intensity_multiplier))  # Base 10 reps
        self.adjusted_sets = max(2, min(5, 3 + (self.streak_days // 5)))  # Increase sets gradually

        # Cap the increases to ensure safety
        self.adjusted_reps = min(self.adjusted_reps, 20)  # Max 20 reps
        self.adjusted_sets = min(self.adjusted_sets, 5)  # Max 5 sets

        # Generate explanation for intensity change
        if self.intensity_multiplier > prev_intensity:
            self.intensity_explanation = f"Intensity increased due to {self.streak_days}-day workout streak. Consistency pays off!"
        elif self.intensity_multiplier == prev_intensity and self.streak_days > 0:
            self.intensity_explanation = f"Maintaining current intensity. Keep up the {self.streak_days}-day streak!"
        else:
            self.intensity_explanation = f"Intensity adjusted based on your {self.streak_days}-day streak."

    def get_intensity_explanation(self):
        """Get explanation for current intensity level"""
        return getattr(self, 'intensity_explanation', f"Intensity set based on your {self.streak_days}-day streak.")

    def get_adjusted_workout_params(self):
        """Get the adjusted workout parameters based on streak"""
        return {
            "streak_days": self.streak_days,
            "intensity_multiplier": round(self.intensity_multiplier, 2),
            "adjusted_reps": self.adjusted_reps,
            "adjusted_sets": self.adjusted_sets,
            "last_workout_date": self.last_workout_date.isoformat() if self.last_workout_date else None,
            "intensity_explanation": self.get_intensity_explanation()
        }

    def adjust_meal_macros_for_intensity(self, base_macros):
        """Adjust meal plan macros based on workout intensity"""
        # Increase calories and protein based on intensity
        adjusted_macros = base_macros.copy()

        # Increase calories proportionally to intensity
        adjusted_macros['calories'] = int(base_macros['calories'] * self.intensity_multiplier)

        # Increase protein for muscle recovery based on intensity
        adjusted_macros['protein'] = int(base_macros['protein'] * self.intensity_multiplier)

        # Slightly adjust carbs and fats based on workout intensity
        adjusted_macros['carbs'] = int(base_macros['carbs'] * self.intensity_multiplier)
        adjusted_macros['fats'] = int(base_macros['fats'] * self.intensity_multiplier)

        return adjusted_macros

    def adjust_meal_plan_by_experience_level(self, base_macros):
        """Adjust meal plan based on experience level"""
        adjusted_macros = base_macros.copy()

        if self.current_experience_level == "Beginner":
            # Beginner: Recovery focused - moderate calories, balanced nutrients
            adjusted_macros['calories'] = int(base_macros['calories'] * 1.0)  # Base calories
            adjusted_macros['protein'] = int(base_macros['protein'] * 1.0)   # Moderate protein
            adjusted_macros['carbs'] = int(base_macros['carbs'] * 1.0)       # Balanced carbs for energy
            adjusted_macros['fats'] = int(base_macros['fats'] * 1.0)         # Healthy fats for recovery

            # Add more recovery-focused nutrients
            adjusted_macros['anti_inflammatory'] = True  # Emphasize anti-inflammatory foods
            adjusted_macros['hydration_focus'] = True    # Emphasize hydration

        elif self.current_experience_level == "Intermediate":
            # Intermediate: Higher protein for muscle building and repair
            adjusted_macros['calories'] = int(base_macros['calories'] * 1.15)  # 15% increase
            adjusted_macros['protein'] = int(base_macros['protein'] * 1.25)   # 25% increase for muscle building
            adjusted_macros['carbs'] = int(base_macros['carbs'] * 1.1)        # Slightly higher for energy
            adjusted_macros['fats'] = int(base_macros['fats'] * 1.05)         # Moderate increase

            # Add more protein-focused nutrients
            adjusted_macros['post_workout_protein'] = True  # Emphasize post-workout protein
            adjusted_macros['energy_balance'] = True        # Focus on energy balance

        elif self.current_experience_level == "Advanced":
            # Advanced: Performance focused - higher calories, optimized macros
            adjusted_macros['calories'] = int(base_macros['calories'] * 1.3)   # 30% increase for high intensity
            adjusted_macros['protein'] = int(base_macros['protein'] * 1.4)     # 40% increase for performance
            adjusted_macros['carbs'] = int(base_macros['carbs'] * 1.25)        # Higher carbs for energy
            adjusted_macros['fats'] = int(base_macros['fats'] * 1.15)          # Higher healthy fats for endurance

            # Add performance-focused nutrients
            adjusted_macros['performance_nutrients'] = True  # Emphasize performance nutrients
            adjusted_macros['timing_optimized'] = True       # Focus on nutrient timing
            adjusted_macros['micronutrient_dense'] = True    # Emphasize micronutrient density
        else:
            # Default to base macros if level is unknown
            adjusted_macros = base_macros.copy()

        return adjusted_macros

    def get_meal_plan_recommendations(self):
        """Get specific meal plan recommendations based on experience level"""
        if self.current_experience_level == "Beginner":
            return {
                "focus": "Recovery and Foundation",
                "protein_sources": ["Lean chicken", "Fish", "Greek yogurt", "Eggs"],
                "carb_sources": ["Oats", "Sweet potatoes", "Fruits", "Brown rice"],
                "fat_sources": ["Avocado", "Nuts", "Olive oil", "Fatty fish"],
                "meal_timing": "Regular meals every 3-4 hours",
                "hydration": "2-3 liters of water daily, plus post-workout",
                "supplements": ["Multivitamin", "Omega-3"]
            }
        elif self.current_experience_level == "Intermediate":
            return {
                "focus": "Muscle Building and Performance",
                "protein_sources": ["Lean meats", "Protein powder", "Cottage cheese", "Legumes"],
                "carb_sources": ["Quinoa", "Bananas", "Whole grains", "Starchy vegetables"],
                "fat_sources": ["Nuts", "Seeds", "Fatty fish", "Nut butters"],
                "meal_timing": "Pre/post-workout nutrition emphasized",
                "hydration": "3-4 liters of water daily, electrolyte balance",
                "supplements": ["Protein powder", "Creatine", "BCAAs"]
            }
        elif self.current_experience_level == "Advanced":
            return {
                "focus": "Performance Optimization",
                "protein_sources": ["High-quality proteins", "Fast-absorbing proteins", "Plant-based options"],
                "carb_sources": ["Complex carbs", "Simple carbs around workouts", "Performance grains"],
                "fat_sources": ["Performance fats", "MCT oils", "Essential fatty acids"],
                "meal_timing": "Strategic nutrient timing, carb periodization",
                "hydration": "Advanced hydration strategies, intra-workout drinks",
                "supplements": ["Performance supplements", "Adaptogens", "Electrolytes"]
            }
        else:
            return {
                "focus": "General Nutrition",
                "protein_sources": ["Any quality proteins"],
                "carb_sources": ["Any quality carbs"],
                "fat_sources": ["Any healthy fats"],
                "meal_timing": "Regular nutrition schedule",
                "hydration": "Standard hydration",
                "supplements": ["Basic supplements"]
            }

    def load_exercise_dataset(self):
        """Load the exercise dataset from the data files"""
        import os
        import pandas as pd

        # fixed path: backend-python/data (not app/data)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ex_processed = os.path.join(base_dir, 'data', 'exercises_processed.csv')
        ex_raw = os.path.join(base_dir, 'data', 'exercises.csv')

        # Load exercise data
        if os.path.exists(ex_processed):
            df_ex = pd.read_csv(ex_processed)
            df_ex.rename(columns={'equipment': 'Equipment', 'name': 'Name'}, inplace=True)
        elif os.path.exists(ex_raw):
            df_ex = pd.read_csv(ex_raw)
        else:
            print(" Exercise data files not found")
            return pd.DataFrame()

        return df_ex

    def validate_exercise_dataset(self):
        """Validate the exercise dataset against current workout execution logic"""
        df_ex = self.load_exercise_dataset()

        if df_ex.empty:
            return {
                "validation_passed": False,
                "message": "No exercise data found to validate",
                "valid_exercises": [],
                "invalid_exercises": [],
                "summary": {"total_exercises": 0, "valid": 0, "invalid": 0}
            }

        # Required columns for workout execution logic
        required_columns = [
            'Name',           # Exercise name
            'Equipment',      # Equipment needed
            'Target_Muscle',  # Muscle group targeted
            'Avoid_If',       # Injuries to avoid with
            'Check_Type',     # Type of check for form
            'Alternative_Swap'  # Alternative exercise option
        ]

        # Additional columns for sets, reps, and difficulty
        additional_columns = [
            'Sets',           # Number of sets
            'Reps',           # Number of reps
            'Difficulty',     # Exercise difficulty level
            'Video_URL',      # Video demonstration
            'Progression_Next' # Next progression exercise
        ]

        valid_exercises = []
        invalid_exercises = []

        for idx, exercise in df_ex.iterrows():
            exercise_name = exercise.get('Name', f'Exercise_{idx}')
            validation_issues = []

            # Check required columns exist
            for col in required_columns:
                if col not in df_ex.columns:
                    validation_issues.append(f"Missing required column: {col}")
                    continue

                if pd.isna(exercise.get(col)) or exercise.get(col) == '':
                    validation_issues.append(f"Missing value in required column: {col}")

            # Check if exercise has the required body keypoints for posture detection
            # This is implicit in MediaPipe - we assume all exercises can use the standard landmarks
            # but we should check if Target_Muscle is properly defined
            target_muscle = exercise.get('Target_Muscle', '')
            if pd.isna(target_muscle) or target_muscle == '' or target_muscle.lower() == 'nan':
                validation_issues.append("Missing or invalid Target_Muscle")

            # Check if equipment is properly defined
            equipment = exercise.get('Equipment', '')
            if pd.isna(equipment) or equipment == '' or equipment.lower() == 'nan':
                validation_issues.append("Missing or invalid Equipment")

            # Check if difficulty is properly defined
            difficulty = exercise.get('Difficulty', '')
            if pd.isna(difficulty) or difficulty == '' or difficulty.lower() == 'nan':
                validation_issues.append("Missing or invalid Difficulty")

            # Check if exercise has metadata for sets and reps
            has_sets_reps = False
            if 'Sets' in df_ex.columns and 'Reps' in df_ex.columns:
                sets = exercise.get('Sets')
                reps = exercise.get('Reps')
                if not pd.isna(sets) and sets != '' and sets != 'nan' and not pd.isna(reps) and reps != '' and reps != 'nan':
                    has_sets_reps = True

            if not has_sets_reps:
                validation_issues.append("Missing sets or reps metadata")

            # Determine if exercise is valid
            if len(validation_issues) == 0:
                valid_exercises.append({
                    "name": exercise_name,
                    "equipment": exercise.get('Equipment', 'Unknown'),
                    "target_muscle": exercise.get('Target_Muscle', 'Unknown'),
                    "difficulty": exercise.get('Difficulty', 'Unknown')
                })
            else:
                invalid_exercises.append({
                    "name": exercise_name,
                    "issues": validation_issues,
                    "equipment": exercise.get('Equipment', 'Unknown'),
                    "target_muscle": exercise.get('Target_Muscle', 'Unknown'),
                    "difficulty": exercise.get('Difficulty', 'Unknown')
                })

        # Prepare validation report
        total_exercises = len(df_ex)
        valid_count = len(valid_exercises)
        invalid_count = len(invalid_exercises)

        validation_report = {
            "validation_passed": invalid_count == 0,
            "message": f"Dataset validation completed: {valid_count} valid, {invalid_count} invalid out of {total_exercises} exercises",
            "valid_exercises": valid_exercises,
            "invalid_exercises": invalid_exercises,
            "summary": {
                "total_exercises": total_exercises,
                "valid": valid_count,
                "invalid": invalid_count,
                "valid_percentage": round((valid_count / total_exercises) * 100, 2) if total_exercises > 0 else 0
            }
        }

        return validation_report

    def evaluate_dataset_sufficiency(self):
        """Evaluate whether the current dataset is sufficient for all supported goals, levels, and exercises"""
        import os
        import pandas as pd

        # Load exercise data
        df_ex = self.load_exercise_dataset()

        # Load nutrition data
        nut_processed = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'nutrition_production_final_v4.csv')

        if os.path.exists(nut_processed):
            df_nut = pd.read_csv(nut_processed)
            df_nut.rename(columns={'carbohydrates_g': 'Carbs', 'fat_g': 'Fats', 'food_name': 'Name', 'diet_type': 'Tags', 'meal_type': 'Type', 'allergens': 'Allergens', 'calories_kcal': 'calories'}, inplace=True)
        else:
            print(" Nutrition data files not found")
            df_nut = pd.DataFrame()

        # Define supported goals
        supported_goals = ["Muscle Gain", "Weight Loss", "Maintain", "Endurance", "Strength"]

        # Define experience levels
        experience_levels = ["Beginner", "Intermediate", "Advanced"]

        # Define equipment categories
        equipment_categories = ["Body Weight", "Dumbbells", "Yoga Mat", "Resistance Bands", "Pull-up Bar", "None"]

        # Define target muscle groups
        target_muscles = [
            "Chest", "Back", "Legs", "Shoulders", "Arms", "Biceps", "Triceps",
            "Abs", "Waist", "Glutes", "Calves", "Cardio", "Full Body"
        ]

        # Define difficulty levels
        difficulty_levels = ["Beginner", "Intermediate", "Advanced"]

        # Evaluate exercise dataset sufficiency
        exercise_evaluation = {
            "goals_coverage": {},
            "levels_coverage": {},
            "equipment_coverage": {},
            "muscle_groups_coverage": {},
            "difficulty_coverage": {},
            "total_exercises": len(df_ex),
            "unique_equipment": [],
            "unique_muscles": [],
            "unique_difficulties": []
        }

        if not df_ex.empty:
            # Count exercises by goal (based on equipment and muscle groups)
            for goal in supported_goals:
                # For now, we'll count exercises that could support each goal
                # This is a simplified approach - in reality, you'd need more complex logic
                exercise_evaluation["goals_coverage"][goal] = len(df_ex)  # Placeholder

            # Count exercises by experience level
            if 'Difficulty' in df_ex.columns:
                for level in experience_levels:
                    level_exercises = df_ex[df_ex['Difficulty'].str.contains(level, case=False, na=False)]
                    exercise_evaluation["levels_coverage"][level] = len(level_exercises)

                # Get unique difficulties
                exercise_evaluation["unique_difficulties"] = df_ex['Difficulty'].dropna().unique().tolist()

            # Count exercises by equipment
            if 'Equipment' in df_ex.columns:
                for equipment in equipment_categories:
                    equipment_exercises = df_ex[df_ex['Equipment'].str.contains(equipment, case=False, na=False)]
                    exercise_evaluation["equipment_coverage"][equipment] = len(equipment_exercises)

                # Get unique equipment
                exercise_evaluation["unique_equipment"] = df_ex['Equipment'].dropna().unique().tolist()

            # Count exercises by target muscle
            if 'Target_Muscle' in df_ex.columns:
                for muscle in target_muscles:
                    muscle_exercises = df_ex[df_ex['Target_Muscle'].str.contains(muscle, case=False, na=False)]
                    exercise_evaluation["muscle_groups_coverage"][muscle] = len(muscle_exercises)

                # Get unique muscles
                exercise_evaluation["unique_muscles"] = df_ex['Target_Muscle'].dropna().unique().tolist()

            # Count exercises by difficulty
            if 'Difficulty' in df_ex.columns:
                for difficulty in difficulty_levels:
                    difficulty_exercises = df_ex[df_ex['Difficulty'].str.contains(difficulty, case=False, na=False)]
                    exercise_evaluation["difficulty_coverage"][difficulty] = len(difficulty_exercises)

        # Evaluate nutrition dataset sufficiency
        nutrition_evaluation = {
            "dietary_preferences": {},
            "meal_types": {},
            "total_meals": len(df_nut),
            "allergen_coverage": [],
            "calorie_ranges": {}
        }

        if not df_nut.empty:
            # Count meals by dietary preference
            if 'Tags' in df_nut.columns:
                veg_meals = len(df_nut[df_nut['Tags'].isin(['Veg', 'Vegan'])])
                vegan_meals = len(df_nut[df_nut['Tags'] == 'Vegan'])
                non_veg_meals = len(df_nut[~df_nut['Tags'].isin(['Veg', 'Vegan'])])

                nutrition_evaluation["dietary_preferences"] = {
                    "Vegetarian": veg_meals,
                    "Vegan": vegan_meals,
                    "Non-Vegetarian": non_veg_meals
                }

            # Count meals by type
            if 'Type' in df_nut.columns:
                meal_types = df_nut['Type'].value_counts().to_dict()
                nutrition_evaluation["meal_types"] = meal_types

            # Get allergen coverage
            if 'Allergens' in df_nut.columns:
                allergens = df_nut['Allergens'].dropna().unique().tolist()
                nutrition_evaluation["allergen_coverage"] = allergens

            # Get calorie ranges
            if 'calories' in df_nut.columns:
                nutrition_evaluation["calorie_ranges"] = {
                    "min": df_nut['calories'].min() if not df_nut.empty else 0,
                    "max": df_nut['calories'].max() if not df_nut.empty else 0,
                    "avg": df_nut['calories'].mean() if not df_nut.empty else 0
                }

        # Identify gaps in exercise variety
        exercise_gaps = []

        if not df_ex.empty:
            # Check if all muscle groups are covered
            for muscle in target_muscles:
                if muscle not in exercise_evaluation["muscle_groups_coverage"] or exercise_evaluation["muscle_groups_coverage"][muscle] == 0:
                    exercise_gaps.append(f"Missing exercises for {muscle} muscle group")

            # Check if all equipment categories are covered
            for equipment in equipment_categories:
                if equipment not in exercise_evaluation["equipment_coverage"] or exercise_evaluation["equipment_coverage"][equipment] == 0:
                    exercise_gaps.append(f"Missing exercises for {equipment} equipment")

            # Check if all difficulty levels are covered
            for difficulty in difficulty_levels:
                if difficulty not in exercise_evaluation["difficulty_coverage"] or exercise_evaluation["difficulty_coverage"][difficulty] == 0:
                    exercise_gaps.append(f"Missing exercises for {difficulty} difficulty level")
        else:
            exercise_gaps.append("No exercise data found")

        # Identify gaps in meal data
        meal_gaps = []

        if not df_nut.empty:
            # Check if all dietary preferences are covered
            if 'Tags' not in df_nut.columns or len(df_nut) == 0:
                meal_gaps.append("Missing dietary preference data")
            else:
                if nutrition_evaluation["dietary_preferences"]["Vegetarian"] == 0:
                    meal_gaps.append("Insufficient vegetarian meal options")
                if nutrition_evaluation["dietary_preferences"]["Vegan"] == 0:
                    meal_gaps.append("Insufficient vegan meal options")

            # Check if all meal types are covered
            if 'Type' not in df_nut.columns or len(nutrition_evaluation["meal_types"]) == 0:
                meal_gaps.append("Missing meal type classifications")
            else:
                required_meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
                for meal_type in required_meal_types:
                    if meal_type not in nutrition_evaluation["meal_types"]:
                        meal_gaps.append(f"Missing {meal_type} meal options")
        else:
            meal_gaps.append("No nutrition data found")

        # Overall sufficiency assessment
        overall_assessment = {
            "exercise_data_sufficient": len(exercise_gaps) == 0 and len(df_ex) > 0,
            "nutrition_data_sufficient": len(meal_gaps) == 0 and len(df_nut) > 0,
            "exercise_gaps": exercise_gaps,
            "meal_gaps": meal_gaps,
            "recommendations": []
        }

        # Generate recommendations based on gaps
        if len(exercise_gaps) > 0:
            overall_assessment["recommendations"].append("Add exercises to cover missing muscle groups, equipment types, and difficulty levels")

        if len(meal_gaps) > 0:
            overall_assessment["recommendations"].append("Expand nutrition dataset with more diverse meal options covering all dietary preferences and meal types")

        if len(df_ex) < 50:  # Arbitrary threshold - could be adjusted
            overall_assessment["recommendations"].append("Consider expanding exercise dataset for better variety")

        if len(df_nut) < 30:  # Arbitrary threshold - could be adjusted
            overall_assessment["recommendations"].append("Consider expanding nutrition dataset for better meal variety")

        # Combine all evaluations
        sufficiency_report = {
            "exercise_evaluation": exercise_evaluation,
            "nutrition_evaluation": nutrition_evaluation,
            "overall_assessment": overall_assessment,
            "dataset_health": {
                "exercise_count": len(df_ex),
                "nutrition_count": len(df_nut),
                "exercise_gaps_count": len(exercise_gaps),
                "meal_gaps_count": len(meal_gaps)
            }
        }

        return sufficiency_report

    def get_analytics_data(self):
        """Get analytics data for charts based on user activity"""
        import datetime

        # Calculate various metrics for analytics
        total_workouts = self.total_workouts_completed + self.total_workouts_skipped
        skip_rate = self.calculate_skip_rate()
        avg_accuracy = self.calculate_average_form_accuracy()

        # Count meal logs from activity log
        meal_logs_count = 0
        if hasattr(self, 'activity_log'):
            meal_logs_count = len([entry for entry in self.activity_log if entry.get('type') == 'meal_logged'])

        # Prepare analytics data
        analytics_data = {
            "workout_metrics": {
                "total_workouts": total_workouts,
                "completed_workouts": self.total_workouts_completed,
                "skipped_workouts": self.total_workouts_skipped,
                "skip_rate": round(skip_rate, 2),
                "current_streak": self.streak_days,
                "intensity_multiplier": round(self.intensity_multiplier, 2)
            },
            "form_metrics": {
                "average_accuracy": round(avg_accuracy, 2),
                "accuracy_samples": len(self.form_accuracy_scores),
                "latest_accuracy": self.form_accuracy_scores[-1] if self.form_accuracy_scores else 0
            },
            "nutrition_metrics": {
                "meal_logs_count": meal_logs_count,
                "last_meal_log": self.get_last_meal_log()
            },
            "progress_metrics": {
                "experience_level": self.current_experience_level,
                "upgrade_readiness": self.upgrade_readiness_score,
                "upgrade_suggested": self.upgrade_suggested
            },
            "activity_log_summary": {
                "total_activities": len(getattr(self, 'activity_log', [])),
                "recent_activities": getattr(self, 'activity_log', [])[-5:]  # Last 5 activities
            },
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        return analytics_data

    def get_last_meal_log(self):
        """Get the most recent meal log from activity log"""
        if hasattr(self, 'activity_log'):
            meal_logs = [entry for entry in self.activity_log if entry.get('type') == 'meal_logged']
            if meal_logs:
                return meal_logs[-1]  # Return the most recent meal log
        return None

    def calculate_trends(self):
        """Calculate daily, weekly, and overall trends from activity data"""
        import datetime
        from datetime import timedelta

        # Initialize trend data
        trend_data = {
            "daily_trends": {},
            "weekly_trends": {},
            "overall_trends": {},
            "trend_analysis": {}
        }

        # Get activity log
        activity_log = getattr(self, 'activity_log', [])
        if not activity_log:
            return trend_data

        # Convert timestamps to datetime objects
        for entry in activity_log:
            if isinstance(entry.get('timestamp'), str):
                try:
                    entry['timestamp'] = datetime.datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    # If parsing fails, skip this entry
                    continue

        # Sort by timestamp
        activity_log = sorted([entry for entry in activity_log if isinstance(entry.get('timestamp'), datetime.datetime)],
                              key=lambda x: x['timestamp'])

        if not activity_log:
            return trend_data

        # Calculate daily trends (last 7 days)
        today = datetime.datetime.now().date()
        seven_days_ago = today - timedelta(days=7)

        daily_workouts = {}
        daily_meals = {}

        for entry in activity_log:
            entry_date = entry['timestamp'].date()

            # Only consider last 7 days for daily trends
            if entry_date >= seven_days_ago:
                date_str = entry_date.isoformat()

                # Count workouts
                if entry['type'] in ['exercise_completed', 'workout_completed']:
                    daily_workouts[date_str] = daily_workouts.get(date_str, 0) + 1

                # Count meals
                if entry['type'] == 'meal_logged':
                    daily_meals[date_str] = daily_meals.get(date_str, 0) + 1

        # Fill in missing days with 0
        for i in range(7):
            date = (seven_days_ago + timedelta(days=i)).isoformat()
            if date not in daily_workouts:
                daily_workouts[date] = 0
            if date not in daily_meals:
                daily_meals[date] = 0

        trend_data["daily_trends"] = {
            "workouts": daily_workouts,
            "meals": daily_meals
        }

        # Calculate weekly trends (last 4 weeks)
        current_week = today.isocalendar()[:2]  # (year, week_number)

        weekly_data = {}
        for i in range(4):
            # Calculate week number for i weeks ago
            past_date = today - timedelta(weeks=i)
            week_key = f"{past_date.year}-W{past_date.isocalendar()[1]}"

            # Count activities for this week
            week_start = past_date - timedelta(days=past_date.weekday())  # Monday
            week_end = week_start + timedelta(days=6)  # Sunday

            week_workouts = 0
            week_meals = 0

            for entry in activity_log:
                entry_date = entry['timestamp'].date()
                if week_start <= entry_date <= week_end:
                    if entry['type'] in ['exercise_completed', 'workout_completed']:
                        week_workouts += 1
                    elif entry['type'] == 'meal_logged':
                        week_meals += 1

            weekly_data[week_key] = {
                "workouts": week_workouts,
                "meals": week_meals
            }

        trend_data["weekly_trends"] = weekly_data

        # Calculate overall trends
        total_workouts = 0
        total_meals = 0
        first_activity_date = None
        last_activity_date = None

        for entry in activity_log:
            if first_activity_date is None or entry['timestamp'].date() < first_activity_date:
                first_activity_date = entry['timestamp'].date()
            if last_activity_date is None or entry['timestamp'].date() > last_activity_date:
                last_activity_date = entry['timestamp'].date()

            if entry['type'] in ['exercise_completed', 'workout_completed']:
                total_workouts += 1
            elif entry['type'] == 'meal_logged':
                total_meals += 1

        # Calculate consistency metrics
        if first_activity_date and last_activity_date:
            total_days = (last_activity_date - first_activity_date).days + 1
            active_days = len(set(entry['timestamp'].date() for entry in activity_log
                                if entry['type'] in ['exercise_completed', 'workout_completed', 'meal_logged']))

            workout_consistency = (total_workouts / active_days) if active_days > 0 else 0
            meal_consistency = (total_meals / active_days) if active_days > 0 else 0
        else:
            total_days = 0
            active_days = 0
            workout_consistency = 0
            meal_consistency = 0

        trend_data["overall_trends"] = {
            "total_workouts": total_workouts,
            "total_meals": total_meals,
            "total_days": total_days,
            "active_days": active_days,
            "workout_consistency": round(workout_consistency, 2),
            "meal_consistency": round(meal_consistency, 2),
            "first_activity": first_activity_date.isoformat() if first_activity_date else None,
            "last_activity": last_activity_date.isoformat() if last_activity_date else None
        }

        # Calculate trend analysis
        trend_analysis = {}

        # Analyze daily workout trend
        daily_dates = sorted(daily_workouts.keys())
        if len(daily_dates) >= 2:
            recent_workouts = [daily_workouts[date] for date in daily_dates[-3:]]  # Last 3 days
            previous_workouts = [daily_workouts[date] for date in daily_dates[-6:-3]]  # Previous 3 days

            if len(previous_workouts) > 0:
                recent_avg = sum(recent_workouts) / len(recent_workouts)
                previous_avg = sum(previous_workouts) / len(previous_workouts) if previous_workouts else 0

                if previous_avg > 0:
                    workout_change = ((recent_avg - previous_avg) / previous_avg) * 100
                else:
                    workout_change = float('inf') if recent_avg > 0 else 0

                trend_analysis["workout_trend_direction"] = "increasing" if workout_change > 0 else "decreasing" if workout_change < 0 else "stable"
                trend_analysis["workout_trend_change_percent"] = round(workout_change, 2)
            else:
                trend_analysis["workout_trend_direction"] = "insufficient_data"
                trend_analysis["workout_trend_change_percent"] = 0

        # Analyze weekly workout trend
        weekly_keys = sorted(weekly_data.keys())
        if len(weekly_keys) >= 2:
            recent_week = weekly_data[weekly_keys[-1]]["workouts"]
            previous_week = weekly_data[weekly_keys[-2]]["workouts"]

            if previous_week > 0:
                weekly_change = ((recent_week - previous_week) / previous_week) * 100
            else:
                weekly_change = float('inf') if recent_week > 0 else 0

            trend_analysis["weekly_workout_trend_direction"] = "increasing" if weekly_change > 0 else "decreasing" if weekly_change < 0 else "stable"
            trend_analysis["weekly_workout_trend_change_percent"] = round(weekly_change, 2)
        else:
            trend_analysis["weekly_workout_trend_direction"] = "insufficient_data"
            trend_analysis["weekly_workout_trend_change_percent"] = 0

        trend_data["trend_analysis"] = trend_analysis

        return trend_data

    def update_activity_log(self, activity_type, details=None):
        """Log user activity for analytics tracking"""
        import datetime

        activity_entry = {
            "type": activity_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "details": details or {},
            "streak_days": self.streak_days,
            "current_level": self.current_experience_level
        }

        # Store in a temporary log (in a real app, this would go to a database)
        if not hasattr(self, 'activity_log'):
            self.activity_log = []

        self.activity_log.append(activity_entry)

        # Keep only recent activities (last 30 entries)
        if len(self.activity_log) > 30:
            self.activity_log = self.activity_log[-30:]

        return activity_entry

    def log_meal_completion(self, meal_info, calories_consumed=None):
        """Log meal completion for analytics tracking"""
        import datetime

        meal_entry = {
            "type": "meal_logged",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "meal_info": meal_info,
            "calories_consumed": calories_consumed,
            "current_level": self.current_experience_level
        }

        # Store in activity log
        if not hasattr(self, 'activity_log'):
            self.activity_log = []

        self.activity_log.append(meal_entry)

        # Keep only recent activities (last 30 entries)
        if len(self.activity_log) > 30:
            self.activity_log = self.activity_log[-30:]

        return meal_entry

    def calculate_skip_rate(self):
        """Calculate the skip rate for the user"""
        total_workouts = self.total_workouts_completed + self.total_workouts_skipped
        if total_workouts == 0:
            return 0.0
        return (self.total_workouts_skipped / total_workouts) * 100

    def calculate_average_form_accuracy(self):
        """Calculate the average form accuracy based on stored scores"""
        if not self.form_accuracy_scores:
            return 0.0
        return sum(self.form_accuracy_scores) / len(self.form_accuracy_scores)

    def add_form_accuracy_score(self, score):
        """Add a form accuracy score to the tracking list"""
        # Limit to last 20 scores to keep it recent
        if len(self.form_accuracy_scores) >= 20:
            self.form_accuracy_scores.pop(0)
        self.form_accuracy_scores.append(score)

    def get_exercise_stats(self):
        """Return a compatibility summary used by the refactored tests/UI."""
        from app.detectors import DetectorFactory
        try:
            from app.progression_engine import build_form_feedback as _bff
        except ImportError:
            _bff = None

        config = self.detector_config or DetectorFactory.get_exercise_config(self.current_exercise)
        raw_form_score = self.calculate_average_form_accuracy()
        # Detectors return 0–100; normalise to 0.0–1.0 for build_form_feedback
        form_score_normalised = raw_form_score / 100.0 if raw_form_score > 1.0 else raw_form_score
        form_feedback = (
            _bff(form_score_normalised, self.current_exercise) if _bff else {}
        )

        if config.get("trackable") is False:
            return {
                "status": "not_trackable",
                "message": f"{self.current_exercise} cannot be reliably tracked with pose landmarks.",
                "counter": self.counter,
                "stage": self.stage,
                "exercise_completed": self.exercise_completed,
                "feedback": getattr(self, "feedback", ""),
                "confidence": self.confidence_history[-1] if self.confidence_history else 0.0,
                "form_score": raw_form_score,
                "form_feedback": form_feedback,
            }

        return {
            "status": "trackable",
            "counter": self.counter,
            "stage": self.stage,
            "exercise_completed": self.exercise_completed,
            "feedback": getattr(self, "feedback", ""),
            "confidence": self.confidence_history[-1] if self.confidence_history else 0.0,
            "form_score": raw_form_score,
            "form_feedback": form_feedback,
        }

    def get_tracking_statistics(self):
        """Return the tracking coverage summary expected by the regression tests."""
        from app.detectors import DetectorFactory

        mapping = DetectorFactory.get_mapping()
        total_exercises = len(mapping)
        trackable_exercises = sum(1 for cfg in mapping.values() if cfg.get("trackable", True) is not False)
        non_trackable_exercises = max(total_exercises - trackable_exercises, 0)
        coverage_percentage = round((trackable_exercises / total_exercises) * 100, 2) if total_exercises else 0.0

        return {
            "total_exercises": total_exercises,
            "trackable_exercises": trackable_exercises,
            "non_trackable_exercises": non_trackable_exercises,
            "coverage_percentage": coverage_percentage,
        }

    def evaluate_upgrade_readiness(self):
        """Evaluate if user is ready to upgrade from Beginner to Intermediate or Intermediate to Advanced"""
        # Calculate various metrics
        skip_rate = self.calculate_skip_rate()
        avg_accuracy = self.calculate_average_form_accuracy()

        # Define thresholds based on current level
        if self.current_experience_level == "Beginner":
            # Beginner to Intermediate thresholds
            min_streak_days = 14  # At least 2 weeks of consistent workouts
            max_skip_rate = 20.0  # Less than 20% skip rate
            min_accuracy = 75.0   # At least 75% average form accuracy
            max_level = "Intermediate"
        elif self.current_experience_level == "Intermediate":
            # Intermediate to Advanced thresholds (stricter requirements)
            min_streak_days = 30  # At least 1 month of consistent workouts
            max_skip_rate = 10.0  # Less than 10% skip rate (more consistent)
            min_accuracy = 85.0   # At least 85% average form accuracy (higher precision)
            max_level = "Advanced"
        else:
            # Already at highest level or unknown level
            return {
                "ready_for_upgrade": False,
                "readiness_score": 0,
                "current_streak": self.streak_days,
                "skip_rate": round(skip_rate, 2),
                "average_accuracy": round(avg_accuracy, 2),
                "total_workouts_completed": self.total_workouts_completed,
                "total_workouts_skipped": self.total_workouts_skipped,
                "thresholds": {
                    "min_streak_days": 0,
                    "max_skip_rate": 0,
                    "min_accuracy": 0
                },
                "current_level": self.current_experience_level,
                "next_level": None
            }

        # Calculate readiness score (0-100)
        readiness_score = 0

        # Streak contribution (0-40 points)
        if self.streak_days >= min_streak_days:
            streak_contribution = 40
        else:
            streak_contribution = min(40, (self.streak_days / min_streak_days) * 40)

        # Skip rate contribution (0-30 points)
        if skip_rate <= max_skip_rate:
            skip_contribution = 30
        else:
            skip_contribution = max(0, 30 - ((skip_rate - max_skip_rate) * 3))  # Stricter penalty for higher levels

        # Form accuracy contribution (0-30 points)
        if avg_accuracy >= min_accuracy:
            accuracy_contribution = 30
        else:
            accuracy_contribution = min(30, (avg_accuracy / min_accuracy) * 30)

        readiness_score = streak_contribution + skip_contribution + accuracy_contribution

        # Store the score and check if upgrade is suggested
        self.upgrade_readiness_score = readiness_score

        # Check if user meets all criteria for upgrade suggestion
        is_ready = (
            self.streak_days >= min_streak_days and
            skip_rate <= max_skip_rate and
            avg_accuracy >= min_accuracy
        )

        self.upgrade_suggested = is_ready and self.current_experience_level in ["Beginner", "Intermediate"]

        # Generate explanation for upgrade readiness
        if self.upgrade_suggested:
            if self.current_experience_level == "Beginner":
                explanation = f"Congratulations! Your {self.streak_days}-day streak, {round(avg_accuracy, 1)}% form accuracy, and {round(skip_rate, 1)}% skip rate show you're ready for intermediate challenges."
            elif self.current_experience_level == "Intermediate":
                explanation = f"Excellent! Your {self.streak_days}-day streak, {round(avg_accuracy, 1)}% accuracy, and consistent routine show you're ready for advanced workouts."
            else:
                explanation = f"You've met the requirements for advancement with your {self.streak_days}-day streak and {round(avg_accuracy, 1)}% accuracy."
        else:
            # Explain what's needed to reach the next level
            streak_needed = max(0, min_streak_days - self.streak_days)
            accuracy_needed = max(0, min_accuracy - avg_accuracy)
            skip_rate_improvement = max(0, skip_rate - max_skip_rate)

            explanation_parts = []
            if streak_needed > 0:
                explanation_parts.append(f"{streak_needed} more consecutive workout days")
            if accuracy_needed > 0:
                explanation_parts.append(f"{round(accuracy_needed, 1)}% better form accuracy")
            if skip_rate_improvement > 0:
                explanation_parts.append(f"{round(skip_rate_improvement, 1)}% lower skip rate")

            if explanation_parts:
                explanation = f"To reach the next level, work on: {', '.join(explanation_parts)}."
            else:
                explanation = f"Keep up the great work! You're making good progress toward the next level."

        return {
            "ready_for_upgrade": self.upgrade_suggested,
            "readiness_score": round(readiness_score, 2),
            "current_streak": self.streak_days,
            "skip_rate": round(skip_rate, 2),
            "average_accuracy": round(avg_accuracy, 2),
            "total_workouts_completed": self.total_workouts_completed,
            "total_workouts_skipped": self.total_workouts_skipped,
            "current_level": self.current_experience_level,
            "next_level": max_level,
            "thresholds": {
                "min_streak_days": min_streak_days,
                "max_skip_rate": max_skip_rate,
                "min_accuracy": min_accuracy
            },
            "explanation": explanation
        }

    def suggest_upgrade(self):
        """Return upgrade suggestion if user is ready"""
        readiness = self.evaluate_upgrade_readiness()

        if readiness["ready_for_upgrade"]:
            # Customize message based on current level
            if self.current_experience_level == "Beginner":
                message = "Congratulations! You're ready to advance from Beginner to Intermediate level."
                next_steps = [
                    "Increased workout complexity",
                    "More challenging exercises",
                    "Higher intensity routines"
                ]
            elif self.current_experience_level == "Intermediate":
                message = "Excellent! You're ready to advance from Intermediate to Advanced level."
                next_steps = [
                    "Maximum workout intensity",
                    "Expert-level exercises",
                    "Elite training routines"
                ]
            else:
                message = "You're ready to advance to the next level!"
                next_steps = ["Continue your excellent progress!"]

            return {
                "upgrade_suggested": True,
                "message": message,
                "reasons": [
                    f"Consistent workout streak of {self.streak_days} days",
                    f"Low skip rate of {readiness['skip_rate']}%",
                    f"Good form accuracy of {readiness['average_accuracy']}%"
                ],
                "next_steps": next_steps,
                "readiness_score": readiness["readiness_score"],
                "current_level": readiness["current_level"],
                "next_level": readiness["next_level"],
                "explanation": readiness["explanation"]
            }
        else:
            return {
                "upgrade_suggested": False,
                "message": "Keep working on your consistency and form to unlock the next level!",
                "current_status": readiness,
                "explanation": readiness["explanation"]
            }

    def draw_styled_landmarks(self, image, pose_landmarks, landmark_color, connection_color):
        """Draw landmarks and connections with custom colors based on form correctness"""
        # Draw connections
        for connection in mp_pose.POSE_CONNECTIONS:
            start_idx = connection[0]
            end_idx = connection[1]

            # Get coordinates
            start_landmark = pose_landmarks.landmark[start_idx]
            end_landmark = pose_landmarks.landmark[end_idx]

            # Convert to pixel coordinates
            start_point = (int(start_landmark.x * image.shape[1]), int(start_landmark.y * image.shape[0]))
            end_point = (int(end_landmark.x * image.shape[1]), int(end_landmark.y * image.shape[0]))

            # Draw line with specified connection color
            cv2.line(image, start_point, end_point, connection_color, 2)

        # Draw landmarks
        for landmark in pose_landmarks.landmark:
            # Convert to pixel coordinates
            point = (int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0]))
            # Draw landmark point with specified landmark color
            cv2.circle(image, point, 4, landmark_color, -1)
