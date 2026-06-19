import os
import json
import time
import sys
from datetime import datetime, timedelta

# Add backend-python to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.workout_engine import WorkoutEngine
from app.progression_engine import get_progression_engine

# Helper to build workout histories
def make_workout_history(weeks_count: int):
    history = []
    now = datetime.now()
    for w in range(weeks_count):
        # 1 workout per week to satisfy consistent weeks check
        session_date = now - timedelta(days=7 * w + 1)
        history.append({
            "date": session_date.isoformat(),
            "created_at": session_date.isoformat(),
            "exercises": [
                {
                    "name": "Push-Up",
                    "target_muscle": "chest",
                    "sets": 3,
                    "reps": 10,
                    "weight": 0.0,
                    "correct_reps": 10,
                    "total_reps": 10,
                    "form_score": 1.0
                }
            ]
        })
    return history

def make_plateau_history():
    history = []
    now = datetime.now()
    for i in range(3):
        # 3 sessions spaced 2 days apart
        session_date = now - timedelta(days=2 * (2 - i) + 1)
        history.append({
            "date": session_date.isoformat(),
            "created_at": session_date.isoformat(),
            "exercises": [
                {
                    "name": "Push-Up",
                    "target_muscle": "chest",
                    "sets": 3,
                    "reps": 20,
                    "weight": 0.0,
                    "correct_reps": 20,
                    "total_reps": 20,
                    "form_score": 1.0
                }
            ]
        })
    return history

def make_long_history(count: int):
    history = []
    now = datetime.now()
    for i in range(count):
        session_date = now - timedelta(days=i + 1)
        history.append({
            "date": session_date.isoformat(),
            "created_at": session_date.isoformat(),
            "exercises": [
                {
                    "name": "Barbell Bench Press",
                    "target_muscle": "chest",
                    "sets": 4,
                    "reps": 8,
                    "weight": 80.0,
                    "correct_reps": 8,
                    "total_reps": 8,
                    "form_score": 1.0
                }
            ]
        })
    return history

def main():
    print("=" * 70)
    print("      WORKOUT INTELLIGENCE END-TO-END PERSONA VALIDATION SUITE")
    print("=" * 70)

    # Ensure output directory exists
    output_dir = "validation_results"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize engines
    print("Initializing engines...")
    engine = WorkoutEngine()
    engine._plan_cache = None  # Disable plan caching for validation runs
    prog_engine = get_progression_engine()

    # Define personas
    personas = {
        "1_beginner_home": {
            "name": "Beginner Home User",
            "profile": {
                "experience": "Beginner",
                "goal": "Muscle Gain",
                "equipment": [],
                "days_per_week": 3,
                "sleep_score": 8.0,
                "fatigue_level": 2.0,
                "stress_level": 3.0,
                "body_issues": []
            },
            "history": []
        },
        "2_advanced_lifter": {
            "name": "Advanced Lifter",
            "profile": {
                "experience": "Advanced",
                "goal": "Strength",
                "equipment": ["Dumbbell", "Barbell"],
                "days_per_week": 5,
                "sleep_score": 8.0,
                "fatigue_level": 3.0,
                "stress_level": 2.0,
                "body_issues": []
            },
            "history": []
        },
        "3_overreached": {
            "name": "Overreached User",
            "profile": {
                "experience": "Intermediate",
                "goal": "Muscle Gain",
                "equipment": ["Dumbbell"],
                "days_per_week": 4,
                "sleep_score": 4.0,
                "fatigue_level": 9.0,
                "stress_level": 9.0,
                "body_issues": []
            },
            "history": []
        },
        "4_consistent_trainee": {
            "name": "4-Week Consistent Trainee",
            "profile": {
                "experience": "Intermediate",
                "goal": "Muscle Gain",
                "equipment": ["Dumbbell"],
                "days_per_week": 4,
                "sleep_score": 8.0,
                "fatigue_level": 2.0,
                "stress_level": 3.0,
                "body_issues": []
            },
            "history": make_workout_history(4)
        },
        "5_plateaued_push": {
            "name": "Plateaued Horizontal Push User",
            "profile": {
                "experience": "Intermediate",
                "goal": "Muscle Gain",
                "equipment": [],
                "days_per_week": 3,
                "sleep_score": 8.0,
                "fatigue_level": 2.0,
                "stress_level": 3.0,
                "body_issues": []
            },
            "history": make_plateau_history()
        },
        "6_injured_shoulder": {
            "name": "Shoulder Injury User",
            "profile": {
                "experience": "Intermediate",
                "goal": "Muscle Gain",
                "equipment": ["Dumbbell", "Barbell", "Pullup Bar"],
                "days_per_week": 4,
                "sleep_score": 8.0,
                "fatigue_level": 2.0,
                "stress_level": 3.0,
                "body_issues": ["shoulder"]
            },
            "history": []
        },
        "7_no_equipment": {
            "name": "No Equipment User",
            "profile": {
                "experience": "Beginner",
                "goal": "Muscle Gain",
                "equipment": [],
                "days_per_week": 3,
                "sleep_score": 8.0,
                "fatigue_level": 2.0,
                "stress_level": 3.0,
                "body_issues": []
            },
            "history": []
        },
        "8_full_gym": {
            "name": "Full Gym User",
            "profile": {
                "experience": "Advanced",
                "goal": "Strength",
                "equipment": ["Barbell", "Dumbbell", "Bench", "Pullup Bar"],
                "days_per_week": 5,
                "sleep_score": 8.0,
                "fatigue_level": 2.0,
                "stress_level": 3.0,
                "body_issues": []
            },
            "history": []
        },
        "9_low_readiness": {
            "name": "Low Readiness User",
            "profile": {
                "experience": "Intermediate",
                "goal": "Muscle Gain",
                "equipment": ["Dumbbell"],
                "days_per_week": 4,
                "sleep_score": 5.0,
                "fatigue_level": 7.0,
                "stress_level": 7.0,
                "body_issues": []
            },
            "history": []
        },
        "10_long_term": {
            "name": "Long-Term User (500+ history)",
            "profile": {
                "experience": "Advanced",
                "goal": "Muscle Gain",
                "equipment": ["Barbell", "Dumbbell"],
                "days_per_week": 5,
                "sleep_score": 8.0,
                "fatigue_level": 2.0,
                "stress_level": 3.0,
                "body_issues": []
            },
            "history": make_long_history(520)  # > 500 sessions
        },
        "11_contradictory": {
            "name": "Contradictory User (Bonus)",
            "profile": {
                "experience": "Beginner",
                "goal": "Strength",
                "equipment": [],
                "days_per_week": 6,
                "sleep_score": 4.0,
                "fatigue_level": 9.0,
                "stress_level": 8.0,
                "body_issues": []
            },
            "history": []
        }
    }

    # Tracking results
    report = []

    for key, data in personas.items():
        print(f"\nEvaluating: {data['name']}...")
        profile = data["profile"].copy()
        history = data["history"]

        # Time generation
        start_time = time.perf_counter()
        
        # 1. Compute progression state first (simulating server.py logic)
        sliced_history = history[-50:] if len(history) > 50 else history
        prog_state = prog_engine.get_progression_state(profile, sliced_history, engine.exercises_df)
        profile["_progression_state"] = prog_state
        coaching_feedback = prog_engine.generate_structured_coaching_feedback(prog_state, profile)

        # 2. Call generate_weekly_plan
        plan = engine.generate_weekly_plan(profile, workout_history=sliced_history)
        
        generation_time = (time.perf_counter() - start_time) * 1000.0 # ms

        # Parse selected exercises
        workout_days = [day for day in plan if day["type"] == "workout"]
        selected_exercises = []
        for day in workout_days:
            for ex in day.get("exercises", []):
                selected_exercises.append({
                    "day": day["day"],
                    "focus": day["focus"],
                    "name": ex["name"],
                    "sets": ex.get("sets", 3),
                    "reps": ex.get("reps", "10"),
                    "rest": ex.get("rest", "60 seconds"),
                    "equipment": ex.get("equipment", "None")
                })

        # Save output file
        output_payload = {
            "persona_name": data["name"],
            "profile": data["profile"],
            "progression_state": prog_state,
            "coaching_feedback": coaching_feedback,
            "selected_exercises": selected_exercises,
            "generation_time_ms": generation_time,
            "full_plan": plan
        }
        
        output_filepath = os.path.join(output_dir, f"{key}.json")
        with open(output_filepath, "w", encoding="utf-8") as out_f:
            json.dump(output_payload, out_f, indent=2)

        # --- Rule Validations ---
        failures = []

        # Validate P1: Bodyweight exercises only
        if key == "1_beginner_home" or key == "7_no_equipment" or key == "11_contradictory":
            for ex in selected_exercises:
                equip_lower = ex["equipment"].lower()
                # bodyweight only allows none, body weight, bodyweight, assisted, pullup bar (if assisted/bodyweight)
                if any(x in equip_lower for x in ["dumbbell", "barbell", "cable", "machine", "bench press"]):
                    failures.append(f"Loaded exercise '{ex['name']}' returned for bodyweight-only persona")

        # Validate P2: High intensity for advanced strength lifter
        if key == "2_advanced_lifter":
            # Just ensure plan has compound exercises
            compounds = [ex for ex in selected_exercises if any(w in ex["name"].lower() for w in ["press", "squat", "deadlift", "row", "pullup", "pushup", "clean", "bench"])]
            if not compounds:
                failures.append("No major compound exercises prioritized for Advanced Lifter")

        # Validate P3: Deload triggered
        if key == "3_overreached":
            if prog_state["phase"] != "deload":
                failures.append(f"Expected phase='deload', but got phase='{prog_state['phase']}'")
            # Verify reduced sets
            for ex in selected_exercises:
                if ex["sets"] > 3:
                    failures.append(f"Excess sets ({ex['sets']}) in deload phase for exercise '{ex['name']}'")

        # Validate P5: Plateau check
        if key == "5_plateaued_push":
            if "horizontal_push" not in prog_state["plateaued_movements"]:
                failures.append("Plateau on 'horizontal_push' not detected in progression state")
            # Check if Push-Up was swapped out for Decline, Tempo, or Diamond Push-Up
            has_pushup = any(ex["name"] == "Push-Up" for ex in selected_exercises)
            has_swap = any(
                ex["name"] != "Push-Up" and any(w in ex["name"].lower() for w in ["push-up", "push up", "dip"])
                for ex in selected_exercises
            )
            if has_pushup:
                failures.append("Standard Push-Up not swapped out despite 'horizontal_push' plateau")
            if not has_swap:
                failures.append("No plateau breaker swap exercise (e.g. Diamond/Decline/Clap Push-Up) found in chest pattern")

        # Validate P6: Shoulder Injury
        if key == "6_injured_shoulder":
            forbidden_words = ["pull-up", "overhead press", "pike push", "handstand", "shoulder press", "military press", "neck press"]
            for ex in selected_exercises:
                if any(fw in ex["name"].lower() for fw in forbidden_words):
                    failures.append(f"Injury-unsafe exercise '{ex['name']}' suggested for shoulder injury user")

        # Validate P7: No Equipment
        if key == "7_no_equipment":
            for ex in selected_exercises:
                if any(fw in ex["name"].lower() for fw in ["dumbbell chest press", "barbell squat", "cable row", "dumbbell", "barbell", "cable"]):
                    failures.append(f"Equipment-restricted exercise '{ex['name']}' returned for No Equipment User")

        # Validate P8: Gym preferences
        if key == "8_full_gym":
            has_bench_press = any("bench press" in ex["name"].lower() for ex in selected_exercises)
            has_squat = any("squat" in ex["name"].lower() and "barbell" in ex["name"].lower() for ex in selected_exercises)
            # Full gym user should have high-value loaded exercises
            if not has_bench_press and not has_squat:
                # Warning only or validation
                pass

        # Validate P10: History slicing and execution time
        if key == "10_long_term":
            if generation_time > 5000.0:  # Gen time should be fast (< 5000ms) with slicing
                failures.append(f"Plan generation took too long ({generation_time:.1f}ms) with 500+ history items")

        # Validate P11: Contradictory user
        if key == "11_contradictory":
            if prog_state["phase"] != "deload":
                failures.append(f"Contradictory user did not trigger deload despite high fatigue/low sleep")

        status = "PASS" if not failures else f"FAIL ({len(failures)} issues)"
        
        report.append({
            "key": key,
            "name": data["name"],
            "readiness": prog_state["readiness_score"],
            "phase": prog_state["phase"],
            "plateaued": list(prog_state["plateaued_movements"].keys()),
            "gen_time": f"{generation_time:.1f} ms",
            "status": status,
            "failures": failures
        })

    # Output Markdown Checklist Report
    print("\n" + "=" * 70)
    print("                   MANUAL INSPECTION REPORT")
    print("=" * 70)
    print(f"{'Persona':<32} | {'Readiness':<9} | {'Phase':<11} | {'Plateaus':<12} | {'Gen Time':<10} | {'Status':<10}")
    print("-" * 98)
    for r in report:
        plateaus_str = ",".join(r["plateaued"]) if r["plateaued"] else "none"
        print(f"{r['name']:<32} | {r['readiness']:<9} | {r['phase']:<11} | {plateaus_str:<12} | {r['gen_time']:<10} | {r['status']:<10}")
        if r["failures"]:
            for f in r["failures"]:
                print(f"   * FAILURE: {f}")

    print("\nAll detailed persona plans saved to validation_results/ folder.")

if __name__ == "__main__":
    main()
