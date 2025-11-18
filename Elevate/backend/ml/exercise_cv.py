"""
Computer Vision Module for Exercise Rep Counting
Integrates with the exercise planner to count reps for recommended exercises
"""

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Optional
import time
import os


class ExerciseRepCounter:
    """
    A computer vision class to count reps for various exercises using MediaPipe pose estimation.
    """

    def __init__(self, data_dir: str = "ml/data"):
        # Initialize MediaPipe components
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Exercise tracking variables
        self.counter = 0
        self.stage = None  # Movement phase (up/down, down/up, etc.)
        self.current_exercise = None
        self.exercise_config = {}
        
        # Load exercise database to map exercises to tracking methods
        self.exercise_database = self.load_exercise_database(data_dir)
        
        # General landmark mappings by body part and movement pattern
        self.exercise_patterns = {
            'upper_arm': {  # For bicep curls, tricep extensions, etc.
                'keypoints': ['LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST'],
                'angle_calculation': self.calculate_elbow_angle,
                'movement_direction': 'vertical',
                'rep_threshold': (160, 30),  # Typical for curls
                'exercise_keywords': ['curl', 'bicep', 'tricep', 'extension', 'hammer']
            },
            'shoulder': {  # For shoulder presses, lateral raises, etc.
                'keypoints': ['LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST'],
                'angle_calculation': self.calculate_elbow_angle,
                'movement_direction': 'vertical',
                'rep_threshold': (90, 170),  # For pressing movements
                'exercise_keywords': ['press', 'raise', 'shoulder', 'lateral', 'front', 'overhead']
            },
            'chest': {  # For chest presses, push-ups
                'keypoints': ['LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST'],
                'angle_calculation': self.calculate_elbow_angle,
                'movement_direction': 'vertical',
                'rep_threshold': (160, 90),  # For pressing movements
                'exercise_keywords': ['push', 'press', 'chest', 'fly', 'dip']
            },
            'back': {  # For rowing movements
                'keypoints': ['LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST'],
                'angle_calculation': self.calculate_elbow_angle,
                'movement_direction': 'vertical',
                'rep_threshold': (30, 160),  # Reverse for pulling movements
                'exercise_keywords': ['row', 'pull', 'lat', 'pulldown', 'pullup', 'chinup']
            },
            'upper_legs': {  # For squats, lunges, leg press
                'keypoints': ['LEFT_HIP', 'LEFT_KNEE', 'LEFT_ANKLE'],
                'angle_calculation': self.calculate_knee_angle,
                'movement_direction': 'vertical',
                'rep_threshold': (170, 80),  # For leg movements
                'exercise_keywords': ['squat', 'lunge', 'press', 'leg', 'thigh', 'quadriceps']
            },
            'lower_legs': {  # For calf raises, etc.
                'keypoints': ['LEFT_KNEE', 'LEFT_ANKLE', 'LEFT_HEEL'],
                'angle_calculation': self.calculate_ankle_angle,
                'movement_direction': 'vertical',
                'rep_threshold': (170, 80),
                'exercise_keywords': ['calf', 'raise', 'heel']
            },
            'waist': {  # For core exercises like situps, crunches
                'keypoints': ['LEFT_SHOULDER', 'LEFT_HIP', 'LEFT_KNEE'],
                'angle_calculation': self.calculate_hip_angle,
                'movement_direction': 'vertical',
                'rep_threshold': (170, 90),
                'exercise_keywords': ['sit', 'crunch', 'abdominal', 'ab', 'plank', 'curl', 'raise']
            }
        }
    
    def load_exercise_database(self, data_dir: str) -> pd.DataFrame:
        """Load the exercise database from CSV."""
        try:
            csv_path = os.path.join(data_dir, "fitness_exercises_processed.csv")
            if os.path.exists(csv_path):
                return pd.read_csv(csv_path)
            else:
                # Load original CSV if processed doesn't exist
                csv_path = os.path.join(data_dir, "fitness_exercises.csv")
                if os.path.exists(csv_path):
                    return pd.read_csv(csv_path)
                else:
                    print("Exercise database not found, using default configuration.")
                    return pd.DataFrame()
        except Exception as e:
            print(f"Error loading exercise database: {e}")
            return pd.DataFrame()
    
    def calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
        """
        Calculate the angle between three points.
        
        Args:
            a: First point [x, y]
            b: Mid point (vertex) [x, y] 
            c: End point [x, y]
        
        Returns:
            Angle in degrees
        """
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def calculate_elbow_angle(self, landmarks, side='LEFT') -> float:
        """Calculate elbow angle for exercises like bicep curls and push-ups."""
        if side == 'LEFT':
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        else:
            shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        
        return self.calculate_angle(shoulder, elbow, wrist)
    
    def calculate_knee_angle(self, landmarks, side='LEFT') -> float:
        """Calculate knee angle for exercises like squats."""
        if side == 'LEFT':
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        else:
            hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                   landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        
        return self.calculate_angle(hip, knee, ankle)
    
    def calculate_ankle_angle(self, landmarks, side='LEFT') -> float:
        """Calculate ankle angle for exercises like calf raises."""
        if side == 'LEFT':
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            heel = [landmarks[self.mp_pose.PoseLandmark.LEFT_HEEL.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HEEL.value].y]
        else:
            knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            heel = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HEEL.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HEEL.value].y]
        
        return self.calculate_angle(knee, ankle, heel)
    
    def calculate_hip_angle(self, landmarks, side='LEFT') -> float:
        """Calculate hip angle for exercises like situps."""
        if side == 'LEFT':
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        else:
            shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                   landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        
        return self.calculate_angle(shoulder, hip, knee)
    
    def determine_exercise_pattern(self, exercise_name: str) -> str:
        """
        Determine the appropriate exercise pattern based on exercise name.
        
        Args:
            exercise_name: Name of the exercise
        
        Returns:
            Pattern name (e.g., 'upper_arm', 'upper_legs', etc.)
        """
        normalized_name = exercise_name.lower()
        
        # Check against each pattern's keywords
        for pattern_name, pattern_config in self.exercise_patterns.items():
            for keyword in pattern_config['exercise_keywords']:
                if keyword in normalized_name:
                    return pattern_name
        
        # If no keyword match is found, try matching by body part if available in database
        if not self.exercise_database.empty:
            # Find the exercise in the database based on name
            for idx, row in self.exercise_database.iterrows():
                if normalized_name in row['name'].lower() or row['name'].lower() in normalized_name:
                    body_part = str(row['bodyPart']).lower()
                    
                    # Map body parts to patterns
                    body_part_to_pattern = {
                        'upper arms': 'upper_arm',
                        'lower arms': 'upper_arm',  # For triceps exercises
                        'chest': 'chest',
                        'shoulders': 'shoulder',
                        'back': 'back',
                        'upper legs': 'upper_legs',
                        'lower legs': 'lower_legs',
                        'waist': 'waist'
                    }
                    
                    for bp, pattern in body_part_to_pattern.items():
                        if bp in body_part:
                            return pattern
                    # If no specific pattern found, return 'upper_arm' as default
                    return 'upper_arm'
        
        # Default to upper_arm for most arm exercises
        return 'upper_arm'
    
    def set_exercise(self, exercise_name: str) -> bool:
        """
        Configure the counter for a specific exercise based on the exercise database.
        
        Args:
            exercise_name: Name of the exercise (e.g., "Bench Press", "Squat", etc.)
        
        Returns:
            True if exercise is supported, False otherwise
        """
        # Determine the appropriate exercise pattern
        pattern_name = self.determine_exercise_pattern(exercise_name)
        
        if pattern_name in self.exercise_patterns:
            self.current_exercise = exercise_name
            self.exercise_config = self.exercise_patterns[pattern_name]
            self.counter = 0
            self.stage = None
            return True
        
        # If no pattern could be determined, return False
        return False
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Process a single video frame to detect pose and count reps.
        
        Args:
            frame: Input video frame
            
        Returns:
            Tuple of (processed frame, rep data dictionary)
        """
        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)
        
        # Recolor image to RGB for MediaPipe processing
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Make detection
        results = self.pose.process(image)
        
        # Recolor back to BGR for rendering
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        rep_data = {
            'counter': self.counter,
            'stage': self.stage,
            'current_exercise': self.current_exercise,
            'angle': None
        }
        
        # Extract landmarks if pose is detected
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Get the appropriate angle calculation based on exercise
            if self.current_exercise and self.exercise_config:
                angle = self.exercise_config['angle_calculation'](landmarks)
                rep_data['angle'] = int(angle)
                
                # Visualize angle on screen
                self.visualize_angle(image, landmarks, angle)
                
                # Rep counting logic based on exercise type
                self.count_reps(angle, rep_data)
                
        except Exception as e:
            # This block will be executed if no landmarks are detected
            pass
        
        # Render landmarks on image
        self.mp_drawing.draw_landmarks(
            image, 
            results.pose_landmarks, 
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
            self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
        )
        
        # Draw rep counter display
        self.draw_counter_display(image)
        
        return image, rep_data
    
    def visualize_angle(self, image: np.ndarray, landmarks, angle: float):
        """Visualize the calculated angle on the image."""
        # Determine which landmarks to use based on the exercise pattern
        if 'knee' in str(self.exercise_config.get('keypoints', [])):
            # Use knee landmarks for leg exercises
            landmark_point = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        else:
            # Use elbow landmarks for most other exercises
            landmark_point = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        
        # Convert normalized coordinates to pixel coordinates
        image_height, image_width, _ = image.shape
        display_point = tuple(np.multiply(landmark_point, [image_width, image_height]).astype(int))
        
        # Draw angle text
        cv2.putText(image, str(int(angle)), 
                   display_point, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    
    def count_reps(self, angle: float, rep_data: Dict):
        """Count reps based on the exercise configuration."""
        if not self.exercise_config:
            return
        
        max_angle, min_angle = self.exercise_config['rep_threshold']
        
        # Determine movement direction and phase based on the exercise type
        if 'upper_arm' in str(self.exercise_config) or 'bicep' in self.current_exercise.lower():
            # For arm exercises like curls: up when angle < min_angle, rep when goes from down (angle > max_angle) to up
            if angle > max_angle:
                self.stage = "down"
            if angle < min_angle and self.stage == "down":
                self.stage = "up"
                self.counter += 1
                print(f"{self.current_exercise} Rep Count: {self.counter}")
        
        elif 'shoulder' in str(self.exercise_config) or 'press' in self.current_exercise.lower():
            # For shoulder presses: down when angle < min_angle, up when angle > max_angle
            if angle < min_angle:
                self.stage = "down"
            if angle > max_angle and self.stage == "down":
                self.stage = "up"
                self.counter += 1
                print(f"{self.current_exercise} Rep Count: {self.counter}")
        
        elif 'upper_legs' in str(self.exercise_config) or 'squat' in self.current_exercise.lower():
            # For leg exercises like squats: down when angle < min_angle, rep when goes from down to up
            if angle < min_angle:
                self.stage = "down"
            if angle > max_angle and self.stage == "down":
                self.stage = "up"
                self.counter += 1
                print(f"{self.current_exercise} Rep Count: {self.counter}")
        
        elif 'back' in str(self.exercise_config) or 'row' in self.current_exercise.lower():
            # For pulling movements: down when angle > max_angle, up when angle < min_angle
            if angle > max_angle:
                self.stage = "down"
            if angle < min_angle and self.stage == "down":
                self.stage = "up"
                self.counter += 1
                print(f"{self.current_exercise} Rep Count: {self.counter}")
    
    def draw_counter_display(self, image: np.ndarray):
        """Draw the rep counter display on the image."""
        # Setup status box
        cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)
        
        # Rep data
        cv2.putText(image, 'REPS', (15, 12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(self.counter), 
                    (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Stage data
        cv2.putText(image, 'STAGE', (85, 12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(self.stage), 
                    (80, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Exercise name
        if self.current_exercise:
            cv2.putText(image, f'EX: {self.current_exercise.upper()}', (10, image.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    
    def reset_counter(self):
        """Reset the rep counter."""
        self.counter = 0
        self.stage = None
    
    def start_exercise_tracking(self, exercise_name: str, camera_index: int = 0):
        """
        Start tracking a specific exercise using the webcam.
        
        Args:
            exercise_name: Name of the exercise to track
            camera_index: Index of the camera to use (default 0)
        """
        if not self.set_exercise(exercise_name):
            print(f"Exercise '{exercise_name}' pattern could not be determined. Using default configuration.")
            # Set to a general upper arm exercise as default
            self.current_exercise = exercise_name
            self.exercise_config = self.exercise_patterns['upper_arm']
            self.counter = 0
            self.stage = None
        
        # Open video capture
        cap = cv2.VideoCapture(camera_index)
        
        print(f"Starting exercise tracking for: {exercise_name}")
        print("Press 'q' to quit")
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                print("Failed to grab frame")
                break
            
            # Process the frame
            processed_frame, rep_data = self.process_frame(frame)
            
            # Display the resulting frame
            cv2.imshow('Exercise Tracker', processed_frame)
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"Exercise session completed. Total reps: {self.counter}")


def track_exercise_from_planner(exercise_name: str):
    """
    Function to track an exercise recommended by the exercise planner.
    
    Args:
        exercise_name: Name of the exercise as returned by the exercise planner
    """
    counter = ExerciseRepCounter()
    counter.start_exercise_tracking(exercise_name)


if __name__ == "__main__":
    # Example usage
    print("Elevate Exercise Rep Counter")
    counter = ExerciseRepCounter()
    
    # Test with different exercises
    test_exercises = [
        "Bench Press",
        "Squat",
        "Bicep Curl",
        "Pull-up",
        "Shoulder Press"
    ]
    
    print("Testing exercise pattern detection:")
    for ex in test_exercises:
        pattern = counter.determine_exercise_pattern(ex)
        print(f"  {ex} -> {pattern}")
    
    # For testing purposes, start with a specific exercise
    # counter.start_exercise_tracking("Bicep Curl")


    