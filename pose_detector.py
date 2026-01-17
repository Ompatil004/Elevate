"""
Pose Detection Service for Elevate AI
This script provides pose detection functionality using MediaPipe
and streams the processed video feed.
"""
import cv2
import mediapipe as mp
from flask import Flask, render_template, Response
import argparse

app = Flask(__name__)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5
)

# Global variables
current_exercise = "bicep_curl"
reps_count = 0
stage = None  # "up" or "down" for exercises

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    import math
    # Get the landmarks
    a = [a.x, a.y]
    b = [b.x, b.y]
    c = [c.x, c.y]
    
    # Calculate the angle
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = math.degrees(radians)
    
    # Make sure the angle is positive
    if angle < 0:
        angle += 360
        
    return angle

def process_frame(frame):
    """Process a single frame for pose detection"""
    global reps_count, stage, current_exercise
    
    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the image and find poses
    results = pose.process(rgb_frame)
    
    if results.pose_landmarks:
        # Draw the pose landmarks on the image
        mp_drawing.draw_landmarks(
            frame, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
        )
        
        # Extract landmarks
        landmarks = results.pose_landmarks.landmark
        
        # Different exercises require different landmark points
        if current_exercise == "bicep_curl":
            # Get coordinates for shoulder, elbow, and wrist
            shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            
            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)
            
            # Count reps based on angle
            if angle > 160:
                stage = "down"
            if angle < 50 and stage == "down":
                stage = "up"
                reps_count += 1
                
            # Display the angle and rep count
            cv2.putText(frame, f'Angle: {int(angle)}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f'Reps: {reps_count}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        elif current_exercise == "squat":
            # Get coordinates for hip, knee, and ankle
            hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            
            # Calculate angle
            angle = calculate_angle(hip, knee, ankle)
            
            # Count reps based on angle
            if angle > 160:
                stage = "up"
            if angle < 80 and stage == "up":
                stage = "down"
                reps_count += 1
                
            # Display the angle and rep count
            cv2.putText(frame, f'Angle: {int(angle)}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f'Reps: {reps_count}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        elif current_exercise == "pushup":
            # For pushups, we'll use shoulder, elbow, and wrist
            shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            
            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)
            
            # Count reps based on angle
            if angle < 70:
                stage = "down"
            if angle > 160 and stage == "down":
                stage = "up"
                reps_count += 1
                
            # Display the angle and rep count
            cv2.putText(frame, f'Angle: {int(angle)}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f'Reps: {reps_count}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        elif current_exercise == "shoulder_press":
            # For shoulder press, we'll use hip, shoulder, and elbow
            shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            
            # Calculate angle between torso and arm
            import math
            shoulder_elbow_dist = math.sqrt((elbow.x - shoulder.x)**2 + (elbow.y - shoulder.y)**2)
            elbow_wrist_dist = math.sqrt((wrist.x - elbow.x)**2 + (wrist.y - elbow.y)**2)
            
            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)
            
            # Count reps based on angle
            if angle > 160:
                stage = "down"
            if angle < 70 and stage == "down":
                stage = "up"
                reps_count += 1
                
            # Display the angle and rep count
            cv2.putText(frame, f'Angle: {int(angle)}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f'Reps: {reps_count}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    return frame

def generate_frames():
    """Generate video frames for streaming"""
    global reps_count, stage
    
    # Open the camera
    cap = cv2.VideoCapture(0)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Process the frame
            processed_frame = process_frame(frame)
            
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            if not ret:
                continue
            
            # Convert to bytes
            frame_bytes = buffer.tobytes()
            
            # Yield the frame in the required format for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    """Set the current exercise"""
    global current_exercise, reps_count, stage
    import json
    from flask import request
    
    data = json.loads(request.data)
    current_exercise = data.get('exercise_name', 'bicep_curl')
    reps_count = 0  # Reset reps when changing exercise
    stage = None
    
    return {'status': 'success', 'current_exercise': current_exercise}

@app.route('/get_reps')
def get_reps():
    """Get the current rep count"""
    global reps_count
    return {'reps': reps_count}

@app.route('/')
def index():
    """Home page"""
    return '<h1>Pose Detection Service Running</h1><p>Access /video_feed for the camera stream</p>'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pose Detection Service')
    parser.add_argument('--port', type=int, default=8001, help='Port to run the service on')
    args = parser.parse_args()
    
    print(f"Starting Pose Detection Service on port {args.port}")
    print("Access the video feed at: http://localhost:" + str(args.port) + "/video_feed")
    
    app.run(host='0.0.0.0', port=args.port, debug=False, threaded=True)