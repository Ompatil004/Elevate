import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Button, ProgressBar } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const styles = {
  page: {
    background: 'radial-gradient(circle at center, #1a2a6c, #b21f1f, #fdbb2d)',
    minHeight: '100vh',
    color: 'white',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column'
  },
  glassCard: {
    background: 'rgba(0, 0, 0, 0.6)',
    backdropFilter: 'blur(15px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '20px',
    padding: '40px',
    height: '100%',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
  },
  statNumber: { fontSize: '5rem', fontWeight: 'bold', lineHeight: 1, marginBottom: '10px' }
};

function Dashboard() {
  const [stats, setStats] = useState({ workoutCount: 0, mealCount: 0 });
  const navigate = useNavigate();

  useEffect(() => {
    const w = JSON.parse(localStorage.getItem('workoutPlan') || "[]");
    const n = JSON.parse(localStorage.getItem('nutritionPlan') || "{}");
    let m = (n.breakfast?.length||0) + (n.lunch?.length||0) + (n.dinner?.length||0);
    setStats({ workoutCount: w.length, mealCount: m });
  }, []);

  return (
    <div style={styles.page}>
      <Container fluid className="d-flex flex-column flex-grow-1">
        <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h1 className="display-4 fw-bold">DASHBOARD</h1>
                <p className="lead text-white-50">Welcome back, Titan.</p>
            </div>
            <Button variant="outline-light" size="lg" onClick={() => navigate('/login')}>LOGOUT</Button>
        </div>

        <Row className="flex-grow-1 g-4">
            <Col md={4}>
                <div style={styles.glassCard} onClick={() => navigate('/workout')}
                     onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-10px)'}
                     onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
                    <div className="text-info mb-2" style={{fontSize: '3rem'}}>🏋️</div>
                    <h2 className="text-uppercase fw-bold text-info">Workout</h2>
                    <div style={styles.statNumber}>{stats.workoutCount}</div>
                    <p className="fs-5 opacity-75">Exercises ready</p>
                    <ProgressBar now={0} variant="info" style={{height: '8px'}} className="mb-4 bg-secondary"/>
                    <Button variant="info" size="lg" className="w-100 fw-bold rounded-pill">START SESSION</Button>
                </div>
            </Col>

            <Col md={4}>
                <div style={{...styles.glassCard, cursor: 'default', background: 'rgba(255,255,255,0.05)'}}>
                    <h3 className="text-white-50 mb-5">WEEKLY GOALS</h3>
                    <div className="d-flex justify-content-between align-items-end mb-4 border-bottom border-secondary pb-3">
                        <span className="h1 mb-0">🔥 0</span>
                        <small className="text-uppercase">Streak</small>
                    </div>
                    <div className="d-flex justify-content-between align-items-end mb-4 border-bottom border-secondary pb-3">
                        <span className="h1 mb-0">⚖️ --</span>
                        <small className="text-uppercase">Weight</small>
                    </div>
                    <div className="mt-auto p-3 bg-dark rounded border border-warning">
                        <span className="text-warning">⚡ "Consistency is the only magic pill."</span>
                    </div>
                </div>
            </Col>

            <Col md={4}>
                <div style={styles.glassCard} onClick={() => navigate('/nutrition')}
                     onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-10px)'}
                     onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
                    <div className="text-success mb-2" style={{fontSize: '3rem'}}>🥗</div>
                    <h2 className="text-uppercase fw-bold text-success">Nutrition</h2>
                    <div style={styles.statNumber}>{stats.mealCount}</div>
                    <p className="fs-5 opacity-75">Meals prepared</p>
                    <ProgressBar now={0} variant="success" style={{height: '8px'}} className="mb-4 bg-secondary"/>
                    <Button variant="success" size="lg" className="w-100 fw-bold rounded-pill">VIEW MEALS</Button>
                </div>
            </Col>
        </Row>
      </Container>
    </div>
  );
}
export default Dashboard;