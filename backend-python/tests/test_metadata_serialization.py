import unittest
from app.workout_engine import WorkoutEngine, get_workout_engine
from app.services.exercise_metadata import get_movement_pattern

class TestMetadataSerialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = get_workout_engine()

    def test_classify_exercise_mode_contains_pattern(self):
        """Test that _classify_exercise_mode includes movement_pattern and preserves legacy keys."""
        exercises_to_test = [
            ("Dumbbell Biceps Curl", "Dumbbell", "10", "curl"),
            ("Archer Push Up", "Bodyweight", "8", "horizontal_push"),
            ("Barbell Back Squat", "Barbell", "5", "squat"),
            ("Pull Up", "Bodyweight", "max", "vertical_pull"),
            ("Lateral Raise", "Dumbbell", "12", "lateral_raise"),
            ("Plank", "Bodyweight", "30-45 seconds", "plank"),
            ("Alternate Heel Touchers", "Bodyweight", "15", "crunch"),
            ("Unknown Test Exercise", "None", "10", "generic")
        ]
        
        for name, equip, reps, expected_pattern in exercises_to_test:
            with self.subTest(name=name):
                res = self.engine._classify_exercise_mode(name, equip, reps)
                
                # Check that movement_pattern is correct
                self.assertEqual(res["movement_pattern"], expected_pattern)
                
                # Check that existing keys are preserved
                self.assertIn("trackable", res)
                self.assertIn("duration_seconds", res)
                self.assertIn("is_timed", res)
                self.assertIn("needs_camera", res)
                self.assertIn("exercise_mode", res)
                
                # Check types
                self.assertIsInstance(res["trackable"], bool)
                self.assertIsInstance(res["duration_seconds"], int)
                self.assertIsInstance(res["is_timed"], bool)
                self.assertIsInstance(res["needs_camera"], bool)
                self.assertIsInstance(res["exercise_mode"], str)

    def test_warmups_contain_movement_pattern(self):
        """Test that generated warmup exercises contain movement_pattern."""
        warmups = self.engine._get_warmup_for_focus(focus="Chest")
        self.assertGreater(len(warmups), 0)
        for drill in warmups:
            self.assertIn("movement_pattern", drill)
            self.assertIsInstance(drill["movement_pattern"], str)
            self.assertEqual(drill["exercise_mode"], "warmup")
            self.assertFalse(drill["needs_camera"])

    def test_fallback_exercises_contain_movement_pattern(self):
        """Test that fallback exercises contain movement_pattern."""
        params = {"sets": 3, "reps": 10, "rest": 60}
        fallbacks = self.engine._get_fallback_exercises(params)
        self.assertGreater(len(fallbacks), 0)
        for ex in fallbacks:
            self.assertIn("movement_pattern", ex)
            self.assertIsInstance(ex["movement_pattern"], str)
            # Verify specific fallbacks from _get_fallback_exercises code
            if ex["name"] == "Push-ups":
                self.assertEqual(ex["movement_pattern"], "horizontal_push")
            elif ex["name"] == "Bodyweight Squats":
                self.assertEqual(ex["movement_pattern"], "squat")
            elif ex["name"] == "Plank":
                self.assertEqual(ex["movement_pattern"], "plank")

    def test_workout_generation_contains_movement_pattern(self):
        """Test that generated workout exercises contain movement_pattern."""
        exercises = self.engine._get_exercises_for_day(
            focus="Chest",
            goal="Muscle Gain",
            experience="Intermediate",
            equipment=["Dumbbell", "Barbell", "Bodyweight"],
            body_issues=[],
            profile={"age": 25, "streak": 0}
        )
        self.assertGreater(len(exercises), 0)
        for ex in exercises:
            self.assertIn("movement_pattern", ex)
            self.assertIsInstance(ex["movement_pattern"], str)
            self.assertNotEqual(ex["movement_pattern"], "")

if __name__ == '__main__':
    unittest.main()
