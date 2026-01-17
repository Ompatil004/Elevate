import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Badge, Table } from 'react-bootstrap';
import api from '../../utils/api';

const WorkoutsPage = () => {
  const [experience, setExperience] = useState('Beginner');
  const [workoutPlan, setWorkoutPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [savedWorkouts, setSavedWorkouts] = useState([]);

  const API_URL = "http://localhost:5000/api";

  const getWorkout = async () => {
    setLoading(true);
    try {
      const response = await api.post('/ml/suggest_workout', {
        goal: "General Fitness",
        experience: experience
      });
      setWorkoutPlan(response.data.exercises);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend");
    }
    setLoading(false);
  };

  // Load saved workouts on component mount
  useEffect(() => {
    // In a real app, this would fetch from an API
    const mockSavedWorkouts = [
      {
        id: 1,
        name: "Upper Body Strength",
        exercises: [
          { name: "Push-ups", sets: 3, reps: 12 },
          { name: "Bicep Curls", sets: 3, reps: 10 },
          { name: "Shoulder Press", sets: 3, reps: 8 }
        ],
        date: "2023-05-15"
      },
      {
        id: 2,
        name: "Lower Body Power",
        exercises: [
          { name: "Squats", sets: 4, reps: 10 },
          { name: "Lunges", sets: 3, reps: 12 },
          { name: "Calf Raises", sets: 3, reps: 15 }
        ],
        date: "2023-05-14"
      }
    ];
    setSavedWorkouts(mockSavedWorkouts);
  }, []);

  return (
    <Container className="py-5">
      <h1 className="mb-4">🏋️ Workout Plans</h1>
      
      <Row className="mb-4">
        <Col md={6}>
          <Card className="shadow-sm border-0 rounded-4">
            <Card.Header className="bg-primary text-white fw-bold py-3 rounded-top-4">
              Generate New Workout
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Experience Level</Form.Label>
                <Form.Select value={experience} onChange={(e) => setExperience(e.target.value)}>
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </Form.Select>
              </Form.Group>
              
              <Button 
                variant="primary" 
                className="w-100" 
                onClick={getWorkout} 
                disabled={loading}
              >
                {loading ? "Generating..." : "Generate Workout Plan"}
              </Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card className="shadow-sm border-0 rounded-4">
            <Card.Header className="bg-info text-white fw-bold py-3 rounded-top-4">
              Today's Workout
            </Card.Header>
            <Card.Body>
              {workoutPlan ? (
                <div>
                  <Table striped bordered hover responsive>
                    <thead>
                      <tr>
                        <th>Exercise</th>
                        <th>Body Part</th>
                        <th>Sets</th>
                        <th>Reps</th>
                      </tr>
                    </thead>
                    <tbody>
                      {workoutPlan.map((ex, idx) => (
                        <tr key={idx}>
                          <td>{ex.name}</td>
                          <td><Badge bg="secondary">{ex.bodyPart}</Badge></td>
                          <td>{ex.sets || 3}</td>
                          <td>{ex.reps || 10}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                  <Button variant="success" className="w-100">
                    Save Workout
                  </Button>
                </div>
              ) : (
                <p className="text-muted">Generate a workout plan to see it here</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card className="shadow-sm border-0 rounded-4">
            <Card.Header className="bg-dark text-white fw-bold py-3 rounded-top-4">
              Saved Workouts
            </Card.Header>
            <Card.Body>
              {savedWorkouts.length > 0 ? (
                <div className="table-responsive">
                  <Table striped bordered hover>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Date</th>
                        <th>Exercises</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {savedWorkouts.map(workout => (
                        <tr key={workout.id}>
                          <td>{workout.name}</td>
                          <td>{workout.date}</td>
                          <td>{workout.exercises.length} exercises</td>
                          <td>
                            <Button variant="outline-primary" size="sm" className="me-2">
                              View
                            </Button>
                            <Button variant="outline-success" size="sm">
                              Load
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              ) : (
                <p className="text-muted">No saved workouts yet</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default WorkoutsPage;