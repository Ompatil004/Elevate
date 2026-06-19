import pytest
from unittest.mock import MagicMock
from app.detectors import DetectorFactory
from app.pose_tracker import PoseTracker

# Create a mock landmark class for testing
class MockLandmark:
    def __init__(self, x, y, visibility=0.9):
        self.x = x
        self.y = y
        self.visibility = visibility

def make_mock_landmarks():
    # Return 33 landmarks mapping to MediaPipe points
    return [MockLandmark(0.5, 0.5) for _ in range(33)]

@pytest.fixture(autouse=True)
def reset_factory():
    """Reset DetectorFactory state before each test to avoid stale caches."""
    DetectorFactory.reset()
    yield
    DetectorFactory.reset()

# ---- DetectorFactory selection tests ----

def test_detector_factory_exact_match():
    """Verify factory returns SquatDetector for an exercise that exists in the mapping."""
    # "Barbell Full Squat" is an actual entry in exercise_mapping.json
    squat_detector = DetectorFactory.get_detector("Barbell Full Squat")
    assert squat_detector.__class__.__name__ == "SquatDetector"

def test_detector_factory_keyword_fallback():
    """Verify factory uses keyword fallback for exercises NOT in the mapping."""
    # "Barbell Squat" is not in the mapping, but keyword "squat" should match
    squat_detector = DetectorFactory.get_detector("Barbell Squat")
    assert squat_detector.__class__.__name__ == "SquatDetector"

    # "Dumbbell Bicep Curl" is not in the mapping, but keyword "curl"/"bicep" should match
    curl_detector = DetectorFactory.get_detector("Dumbbell Bicep Curl")
    assert curl_detector.__class__.__name__ == "CurlDetector"

def test_detector_factory_unknown_fallback():
    """Verify fallback to GenericDetector for completely unknown exercise."""
    unknown_detector = DetectorFactory.get_detector("Unknown Super Exercise")
    assert unknown_detector.__class__.__name__ == "GenericDetector"

def test_detector_factory_case_insensitive():
    """Verify case-insensitive lookup works for exercises in the mapping."""
    # "barbell full squat" (lowercase) should still match "Barbell Full Squat"
    detector = DetectorFactory.get_detector("barbell full squat")
    assert detector.__class__.__name__ == "SquatDetector"

# ---- Confidence tests ----

def test_confidence_filtering():
    curl_detector = DetectorFactory.get_detector("Barbell Curl")
    
    # All visible
    landmarks_good = [MockLandmark(0.5, 0.5, 0.9) for _ in range(33)]
    assert curl_detector.get_confidence(landmarks_good) > 0.8
    
    # Low visibility
    landmarks_bad = [MockLandmark(0.5, 0.5, 0.1) for _ in range(33)]
    assert curl_detector.get_confidence(landmarks_bad) < 0.2

# ---- Rep counting tests ----

def test_squat_rep_counting():
    squat_detector = DetectorFactory.get_detector("Barbell Full Squat")
    state = {"counter": 0, "stage": "up", "min_angle": 180.0}
    
    # Mock landmarks for up position (knee angle near 180)
    landmarks_up = make_mock_landmarks()
    landmarks_up[23] = MockLandmark(0.5, 0.2)  # Hip
    landmarks_up[25] = MockLandmark(0.5, 0.5)  # Knee
    landmarks_up[27] = MockLandmark(0.5, 0.8)  # Ankle
    
    counter, stage = squat_detector.count_reps(landmarks_up, state)
    assert counter == 0
    assert stage == "up"

    # Deep squat (knee angle < 90)
    landmarks_down = make_mock_landmarks()
    landmarks_down[23] = MockLandmark(0.5, 0.5)   # Hip  (same height as knee)
    landmarks_down[25] = MockLandmark(0.4, 0.5)   # Knee (shifted left)
    landmarks_down[27] = MockLandmark(0.5, 0.5)   # Ankle (same height)
    
    state["stage"] = stage
    counter, stage = squat_detector.count_reps(landmarks_down, state)
    assert stage == "down"
    
    # Rise back up
    state["stage"] = stage
    state["counter"] = counter
    counter, stage = squat_detector.count_reps(landmarks_up, state)
    assert stage == "up"
    assert counter == 1

# ---- PoseTracker integration tests ----

def test_untrackable_exercise():
    tracker = PoseTracker()
    # "Alternate Lateral Pulldown" is in the mapping with trackable: false
    tracker.set_exercise("Alternate Lateral Pulldown")
    stats = tracker.get_exercise_stats()
    assert stats["status"] == "not_trackable"
    assert "cannot be reliably tracked" in stats["message"]

def test_api_compatibility():
    tracker = PoseTracker()
    tracker.set_exercise("Barbell Full Squat")
    stats = tracker.get_exercise_stats()
    
    assert "counter" in stats
    assert "stage" in stats
    assert "exercise_completed" in stats
    assert "feedback" in stats
    assert "confidence" in stats
    assert "form_score" in stats

def test_exercise_switching():
    tracker = PoseTracker()
    tracker.set_exercise("Barbell Full Squat")
    assert tracker.current_exercise == "Barbell Full Squat"
    assert tracker.detector.__class__.__name__ == "SquatDetector"
    assert tracker.detector_state["counter"] == 0
    
    tracker.set_exercise("Dumbbell Bicep Curl")
    assert tracker.current_exercise == "Dumbbell Bicep Curl"
    assert tracker.detector.__class__.__name__ == "CurlDetector"
    assert tracker.detector_state["counter"] == 0

def test_confidence_smoothing_and_form_score(monkeypatch):
    import app.pose_tracker
    monkeypatch.setattr(app.pose_tracker, 'AI_AVAILABLE', True)
    monkeypatch.setattr(app.pose_tracker, 'mp_pose', MagicMock(), raising=False)
    monkeypatch.setattr(app.pose_tracker, '_ensure_cv2', lambda: True)
    monkeypatch.setattr(app.pose_tracker, 'cv2', MagicMock())
    
    tracker = PoseTracker()
    tracker.set_exercise("Barbell Full Squat")
    
    tracker.pose = MagicMock()
    
    class MockPoseLandmarks:
        def __init__(self, landmarks):
            self.landmark = landmarks
            
    class MockResults:
        def __init__(self, landmarks):
            if landmarks:
                self.pose_landmarks = MockPoseLandmarks(landmarks)
            else:
                self.pose_landmarks = None
                
    landmarks_good = make_mock_landmarks()
    tracker.pose.process.return_value = MockResults(landmarks_good)
    
    import numpy as np
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Frame 1
    tracker.process_frame(frame)
    assert len(tracker.confidence_history) == 1
    
    # Fast forward to trigger form score storage (every 30 frames)
    tracker.frame_count = 29
    tracker.process_frame(frame)
    assert len(tracker.confidence_history) == 2
    assert len(tracker.form_accuracy_scores) == 1

def test_form_score_storage_limit():
    tracker = PoseTracker()
    # add_form_accuracy_score limits to 20 scores
    for i in range(25):
        tracker.add_form_accuracy_score(50 + i)
        
    assert len(tracker.form_accuracy_scores) == 20
    assert tracker.form_accuracy_scores[-1] == 50 + 24
    assert tracker.form_accuracy_scores[0] == 50 + 5

def test_tracking_statistics():
    tracker = PoseTracker()
    stats = tracker.get_tracking_statistics()
    
    assert "total_exercises" in stats
    assert "trackable_exercises" in stats
    assert "non_trackable_exercises" in stats
    assert "coverage_percentage" in stats
    
    assert stats["total_exercises"] > 0
    assert stats["trackable_exercises"] <= stats["total_exercises"]
    assert stats["coverage_percentage"] >= 0.0
