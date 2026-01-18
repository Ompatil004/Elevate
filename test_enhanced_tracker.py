"""
Test script for Enhanced Pose Tracker
This script demonstrates the Virtual Trainer Improvements
"""
import cv2
import sys
import os

# Add the backend directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.enhanced_pose_tracker import EnhancedPoseTracker

def main():
    print("Starting Enhanced Pose Tracker Demo...")
    print("Press 'q' to quit, 'e' to cycle through exercises")
    
    # Initialize the enhanced pose tracker
    tracker = EnhancedPoseTracker()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    # Exercise list to cycle through
    exercises = ["bicep_curl", "squat", "pushup", "shoulder_press", "lunge"]
    current_exercise_idx = 0
    
    print(f"Current exercise: {exercises[current_exercise_idx]}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process the frame with enhanced pose tracking
        processed_frame, results = tracker.process_frame(frame)
        
        # Display current exercise
        cv2.putText(processed_frame, f"Exercise: {exercises[current_exercise_idx]}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display instructions
        cv2.putText(processed_frame, "Press 'q' to quit, 'e' to change exercise", 
                   (10, processed_frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show the frame
        cv2.imshow('Enhanced Pose Tracker - Virtual Trainer', processed_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            current_exercise_idx = (current_exercise_idx + 1) % len(exercises)
            tracker.set_exercise(exercises[current_exercise_idx])
            print(f"Switched to: {exercises[current_exercise_idx]}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Demo ended.")

if __name__ == "__main__":
    main()