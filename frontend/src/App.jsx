import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container, Row, Col, Card, Button, Form, Spinner, Alert, Badge, ButtonGroup } from 'react-bootstrap';

function App() {
  // State for Workout
  const [experience, setExperience] = useState('Beginner');
  const [workoutPlan, setWorkoutPlan] = useState(null);
  const [loadingWorkout, setLoadingWorkout] = useState(false);
  
  // State for Meal
  const [mealGoal, setMealGoal] = useState('Muscle Gain');
  const [mealPlan, setMealPlan] = useState(null);
  const [loadingMeal, setLoadingMeal] = useState(false);

  // State for Camera/Exercise Control
  const [currentExercise, setCurrentExercise] = useState('bicep_curl');
  const [cameraStatus, setCameraStatus] = useState('Ready');

  const API_URL = "http://127.0.0.1:8000";

  // --- 1. Workout Generator ---
  const getWorkout = async () => {
    setLoadingWorkout(true);
    try {
      const response = await axios.post(`${API_URL}/ml/recommend-workout`, {
        goal: "General Fitness",
        experience: experience
      });
      setWorkoutPlan(response.data.exercises);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend");
    }
    setLoadingWorkout(false);
  };

  // --- 2. Meal Planner ---
  const getMealPlan = async () => {
    setLoadingMeal(true);
    try {
      const response = await axios.post(`${API_URL}/ml/recommend-meal`, {
        goal: mealGoal,
        calorie_target: 2000
      });
      setMealPlan(response.data.recommendations);
    } catch (err) {
      console.error(err);
    }
    setLoadingMeal(false);
  };

  // --- 3. Switch Exercise Mode ---
  const setExerciseMode = async (exerciseName) => {
    setCurrentExercise(exerciseName);
    setCameraStatus('Switching...');
    try {
      await axios.post(`${API_URL}/ml/set-exercise`, {
        exercise_name: exerciseName
      });
      setCameraStatus(`Tracking: ${exerciseName.replace('_', ' ').toUpperCase()}`);
    } catch (err) {
      setCameraStatus('Error switching exercise');
    }
  };

  return (
    <div className="bg-light min-vh-100 py-5">
      <Container>
        <div className="text-center mb-5">
            <h1 className="display-4 fw-bold text-primary">Elevate <span className="text-dark">AI</span></h1>
            <p className="lead text-muted">Intelligent Fitness & Nutrition Platform</p>
        </div>

        <Row className="g-4">
          {/* --- WORKOUT GENERATOR --- */}
          <Col md={6}>
            <Card className="h-100 shadow-sm border-0 rounded-4">
              <Card.Header className="bg-primary text-white fw-bold py-3 rounded-top-4">
                 🏋️ Workout Plan
              </Card.Header>
              <Card.Body className="p-4">
                <Form.Group className="mb-3">
                    <Form.Label>Experience Level</Form.Label>
                    <Form.Select value={experience} onChange={(e) => setExperience(e.target.value)}>
                        <option value="Beginner">Beginner</option>
                        <option value="Intermediate">Intermediate</option>
                        <option value="Advanced">Advanced</option>
                    </Form.Select>
                </Form.Group>
                <Button variant="primary" className="w-100" onClick={getWorkout} disabled={loadingWorkout}>
                  {loadingWorkout ? "Generating..." : "Generate Plan"}
                </Button>

                {workoutPlan && (
                  <div className="mt-3">
                    <small className="text-muted">Today's Routine:</small>
                    <ul className="list-group list-group-flush mt-2">
                      {workoutPlan.map((ex, idx) => (
                        <li key={idx} className="list-group-item d-flex justify-content-between align-items-center">
                          {ex.name} <Badge bg="light" text="dark">{ex.bodyPart}</Badge>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>

          {/* --- MEAL PLANNER --- */}
          <Col md={6}>
            <Card className="h-100 shadow-sm border-0 rounded-4">
              <Card.Header className="bg-success text-white fw-bold py-3 rounded-top-4">
                 🥗 Nutrition Plan
              </Card.Header>
              <Card.Body className="p-4">
                <Form.Group className="mb-3">
                    <Form.Label>Goal</Form.Label>
                    <Form.Select value={mealGoal} onChange={(e) => setMealGoal(e.target.value)}>
                        <option value="Muscle Gain">Muscle Gain</option>
                        <option value="Weight Loss">Weight Loss</option>
                        <option value="Maintain">Maintain</option>
                    </Form.Select>
                </Form.Group>
                <Button variant="success" className="w-100" onClick={getMealPlan} disabled={loadingMeal}>
                  {loadingMeal ? "Analyzing..." : "Get Recommendations"}
                </Button>

                {mealPlan && (
                  <div className="mt-3">
                    <small className="text-muted">Recommended Meals:</small>
                    {mealPlan.map((meal, idx) => (
                        <div key={idx} className="d-flex justify-content-between border-bottom py-2">
                            <span>{meal.name}</span>
                            <span className="fw-bold text-success">{meal.calories} kcal</span>
                        </div>
                    ))}
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* --- LIVE TRACKER SECTION --- */}
        <Row className="mt-5">
            <Col>
                <Card className="shadow-lg border-0 bg-dark text-white rounded-4 overflow-hidden">
                    <Row className="g-0">
                        {/* Control Panel */}
                        <Col md={4} className="p-4 border-end border-secondary">
                            <h3 className="mb-4">🎥 AI Tracker</h3>
                            <p className="text-white-50 mb-4">Select an exercise to start tracking reps automatically.</p>
                            
                            <div className="d-grid gap-2">
                                <Button 
                                    variant={currentExercise === 'bicep_curl' ? "warning" : "outline-light"} 
                                    onClick={() => setExerciseMode('bicep_curl')}
                                >
                                    💪 Bicep Curls
                                </Button>
                                <Button 
                                    variant={currentExercise === 'squat' ? "warning" : "outline-light"} 
                                    onClick={() => setExerciseMode('squat')}
                                >
                                    🦵 Squats
                                </Button>
                                <Button 
                                    variant={currentExercise === 'pushup' ? "warning" : "outline-light"} 
                                    onClick={() => setExerciseMode('pushup')}
                                >
                                    🔥 Pushups
                                </Button>
                                <Button 
                                    variant={currentExercise === 'shoulder_press' ? "warning" : "outline-light"} 
                                    onClick={() => setExerciseMode('shoulder_press')}
                                >
                                    🏋️ Shoulder Press
                                </Button>
                            </div>

                            <div className="mt-4 pt-3 border-top border-secondary">
                                <small>Status:</small>
                                <div className="fw-bold text-warning">{cameraStatus}</div>
                            </div>
                        </Col>

                        {/* Video Feed */}
                        <Col md={8} className="bg-black d-flex justify-content-center align-items-center" style={{minHeight: '400px'}}>
                            <img 
                                src="http://127.0.0.1:8000/video_feed" 
                                alt="AI Feed" 
                                style={{maxWidth: '100%', maxHeight: '500px'}} 
                            />
                        </Col>
                    </Row>
                </Card>
            </Col>
        </Row>

      </Container>
    </div>
  );
}

export default App;