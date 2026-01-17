import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, Badge } from 'react-bootstrap';
import api from '../../utils/api';

const TrackerPage = () => {
  const [currentExercise, setCurrentExercise] = useState('bicep_curl');
  const [cameraStatus, setCameraStatus] = useState('Ready');
  const [repsCount, setRepsCount] = useState(0);
  const [exerciseHistory, setExerciseHistory] = useState([
    { id: 1, name: 'Bicep Curls', reps: 12, sets: 3, date: '2023-05-15' },
    { id: 2, name: 'Squats', reps: 15, sets: 3, date: '2023-05-14' },
    { id: 3, name: 'Pushups', reps: 10, sets: 3, date: '2023-05-13' }
  ]);

  const API_URL = "http://localhost:5000/api";

  const setExerciseMode = async (exerciseName) => {
    setCurrentExercise(exerciseName);
    setCameraStatus('Switching...');
    setRepsCount(0); // Reset reps count when switching exercises

    try {
      const response = await api.post('/ml/set-exercise', {
        exercise_name: exerciseName
      });
      setCameraStatus(`Tracking: ${exerciseName.replace('_', ' ').toUpperCase()}`);
    } catch (err) {
      console.error('Error setting exercise:', err);
      setCameraStatus('Error switching exercise');
    }
  };

  const resetTracker = () => {
    setRepsCount(0);
    setCameraStatus('Ready to track');
  };

  return (
    <Container className="py-5">
      <h1 className="mb-4">🎥 AI Exercise Tracker</h1>
      
      <Row className="mb-4">
        <Col>
          <Card className="shadow-lg border-0 bg-dark text-white rounded-4 overflow-hidden">
            <Row className="g-0">
              {/* Control Panel */}
              <Col md={4} className="p-4 border-end border-secondary">
                <h3 className="mb-4">Exercise Controls</h3>
                
                <div className="d-grid gap-2 mb-4">
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

                <div className="mt-4 p-3 bg-secondary bg-opacity-25 rounded">
                  <div className="d-flex justify-content-between mb-2">
                    <span>Current Exercise:</span>
                    <strong>{currentExercise.replace('_', ' ').toUpperCase()}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-2">
                    <span>Reps Count:</span>
                    <strong className="text-success fs-4">{repsCount}</strong>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span>Status:</span>
                    <span className={`fw-bold ${cameraStatus.includes('Error') ? 'text-danger' : 'text-warning'}`}>
                      {cameraStatus}
                    </span>
                  </div>
                </div>

                <div className="mt-3 d-grid gap-2">
                  <Button variant="success" onClick={() => setRepsCount(repsCount + 1)}>
                    +1 Rep
                  </Button>
                  <Button variant="danger" onClick={resetTracker}>
                    Reset Counter
                  </Button>
                </div>
              </Col>

              {/* Video Feed */}
              <Col md={8} className="bg-black d-flex flex-column justify-content-center align-items-center p-4" style={{ minHeight: '500px' }}>
                <div className="text-center mb-3">
                  <h4>Live Tracking Feed</h4>
                  <p className="text-white-50">Position yourself in front of the camera</p>
                </div>
                <img
                  src="http://localhost:8001/video_feed"
                  alt="AI Feed"
                  style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain' }}
                  className="border border-secondary rounded"
                />
                <div className="mt-3">
                  <Badge bg="success" className="fs-5 px-4 py-2">
                    Current Reps: {repsCount}
                  </Badge>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card className="shadow-sm border-0 rounded-4">
            <Card.Header className="bg-info text-white fw-bold py-3 rounded-top-4">
              Exercise History
            </Card.Header>
            <Card.Body>
              <div className="table-responsive">
                <Table striped bordered hover>
                  <thead>
                    <tr>
                      <th>Exercise</th>
                      <th>Reps</th>
                      <th>Sets</th>
                      <th>Date</th>
                      <th>Performance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {exerciseHistory.map(ex => (
                      <tr key={ex.id}>
                        <td>{ex.name}</td>
                        <td>{ex.reps}</td>
                        <td>{ex.sets}</td>
                        <td>{ex.date}</td>
                        <td>
                          <Badge bg={ex.reps >= 12 ? "success" : ex.reps >= 8 ? "warning" : "danger"}>
                            {ex.reps >= 12 ? "Excellent" : ex.reps >= 8 ? "Good" : "Needs Improvement"}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default TrackerPage;