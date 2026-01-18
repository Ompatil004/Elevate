import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Button, Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const styles = {
    page: { background: '#000', minHeight: '100vh', color: '#fff', overflow: 'hidden' },
    sidebar: { height: '100vh', overflowY: 'auto', borderRight: '1px solid #333' },
    main: { height: '100vh', position: 'relative', display: 'flex', flexDirection: 'column' },
    listItem: {
        padding: '15px 20px', borderBottom: '1px solid #222', 
        cursor: 'pointer', transition: '0.2s background',
        background: '#111'
    },
    activeItem: { background: '#003366', borderLeft: '5px solid #00c6ff' }
};

function Workout() {
  const [plan, setPlan] = useState([]);
  const [activeIdx, setActiveIdx] = useState(null);
  const [tracker, setTracker] = useState({ reps: 0, feedback: "Ready" });
  const [completed, setCompleted] = useState([]);
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    setPlan(JSON.parse(localStorage.getItem('workoutPlan') || "[]"));
    return () => stopCam();
  }, []);

  useEffect(() => {
    if (activeIdx === null) return;
    const interval = setInterval(async () => {
        try { const res = await axios.get(`${API_URL}/ml/workout-status`); setTracker(res.data); } catch(e){}
    }, 500);
    return () => clearInterval(interval);
  }, [activeIdx]);

  const stopCam = async () => { setActiveIdx(null); try{ await axios.post(`${API_URL}/stop_camera`); }catch(e){} };

  const startEx = async (ex, i) => {
    if(activeIdx !== null && activeIdx !== i) return; 
    setActiveIdx(i);
    let mode = "bicep_curl"; 
    if(ex.name.toLowerCase().includes("squat")) mode = "squat";
    if(ex.name.toLowerCase().includes("push")) mode = "pushup";
    await axios.post(`${API_URL}/ml/set-exercise`, {exercise_name: mode});
  };

  const finishEx = async (i) => {
    await stopCam();
    setCompleted([...completed, i]);
    alert("Set Complete!");
  };

  return (
    <div style={styles.page}>
      <Container fluid className="p-0">
        <Row className="g-0">
            <Col lg={3} style={styles.sidebar}>
                <div className="p-3 bg-dark border-bottom border-secondary d-flex justify-content-between align-items-center">
                    <h4 className="m-0 fw-bold">SESSION PLAN</h4>
                    <Button variant="outline-secondary" size="sm" onClick={() => {stopCam(); navigate('/dashboard')}}>EXIT</Button>
                </div>
                {plan.map((ex, i) => (
                    <div key={i} style={{...styles.listItem, ...(activeIdx===i ? styles.activeItem : {})}}
                         onClick={() => !completed.includes(i) && startEx(ex, i)}>
                        <div className="d-flex justify-content-between">
                            <span className="fw-bold fs-5">{ex.name}</span>
                            {completed.includes(i) && <Badge bg="success">DONE</Badge>}
                        </div>
                        <div className="text-white-50 small mt-1">{ex.sets} SETS • {ex.reps}</div>
                    </div>
                ))}
            </Col>

            <Col lg={9} style={styles.main} className="bg-black">
                {activeIdx !== null ? (
                    <>
                        <div className="position-absolute top-0 start-0 w-100 p-4 d-flex justify-content-between align-items-start" 
                             style={{background: 'linear-gradient(to bottom, rgba(0,0,0,0.9), transparent)', zIndex: 10}}>
                            <div>
                                <h1 className="display-3 fw-bold text-white">{plan[activeIdx].name}</h1>
                                <h3 className="text-info">{tracker.feedback}</h3>
                            </div>
                            <div className="text-end">
                                <h1 className="display-1 fw-bold text-info m-0" style={{lineHeight: 0.8}}>{tracker.reps}</h1>
                                <small className="text-uppercase letter-spacing-2">Reps Completed</small>
                            </div>
                        </div>

                        <img src={`${API_URL}/video_feed?t=${Date.now()}`} style={{width: '100%', height: '100%', objectFit: 'contain'}} alt="Feed"/>
                        
                        <div className="position-absolute bottom-0 w-100 p-4 d-flex justify-content-center gap-3" 
                             style={{background: 'linear-gradient(to top, rgba(0,0,0,0.9), transparent)'}}>
                            <Button variant="success" size="lg" className="px-5 py-3 fw-bold rounded-pill" onClick={() => finishEx(activeIdx)}>✅ COMPLETE SET</Button>
                            <Button variant="danger" size="lg" className="px-5 py-3 fw-bold rounded-pill" onClick={stopCam}>⏹ STOP CAMERA</Button>
                        </div>
                    </>
                ) : (
                    <div className="d-flex flex-column align-items-center justify-content-center h-100 text-secondary">
                        <div style={{fontSize: '5rem', opacity: 0.3}}>⚡</div>
                        <h2>Select an exercise from the left to begin</h2>
                    </div>
                )}
            </Col>
        </Row>
      </Container>
    </div>
  );
}
export default Workout;