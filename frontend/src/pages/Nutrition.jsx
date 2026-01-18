import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, Button, Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const styles = {
    page: { background: '#0d0d0d', minHeight: '100vh', color: '#eee', padding: '20px' },
    catCard: {
        height: '300px', borderRadius: '20px', cursor: 'pointer',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        background: 'linear-gradient(135deg, #1e1e1e, #2a2a2a)',
        border: '1px solid #444', transition: '0.3s'
    },
    mealCard: { background: '#222', border: 'none', marginBottom: '20px' }
};

function Nutrition() {
  const [view, setView] = useState("categories"); 
  const [activeCat, setActiveCat] = useState("");
  const [meals, setMeals] = useState({});
  const [eatenLog, setEatenLog] = useState({});
  const navigate = useNavigate();
  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    setMeals(JSON.parse(localStorage.getItem('nutritionPlan') || "{}"));
    setEatenLog(JSON.parse(localStorage.getItem('eatenLog') || "{}"));
  }, []);

  const handleEat = (mealName) => {
    const today = new Date().toISOString().split('T')[0];
    const newLog = { ...eatenLog, [mealName]: today };
    setEatenLog(newLog);
    localStorage.setItem('eatenLog', JSON.stringify(newLog));
    
    const userId = localStorage.getItem("userId");
    axios.post(`${API_URL}/history/add`, { user_id: userId, type: "meal", name: mealName, details: "Consumed" });
  };

  const handleSwap = async (cat, idx) => {
    const current = meals[cat][idx];
    try {
        const res = await axios.post(`${API_URL}/ml/get-alternative-meal`, {
            current_meal_name: current.name, calories: current.calories
        });
        const newMeals = { ...meals };
        newMeals[cat][idx] = res.data;
        setMeals(newMeals);
        localStorage.setItem('nutritionPlan', JSON.stringify(newMeals));
        alert("Meal Swapped! 🔄");
    } catch(e) { alert("Swap failed."); }
  };

  if(view === "categories") return (
    <div style={styles.page}>
        <Container fluid>
            <div className="d-flex justify-content-between align-items-center mb-5">
                <Button variant="outline-light" onClick={() => navigate('/dashboard')}>← DASHBOARD</Button>
                <h1 className="fw-bold">NUTRITION PLAN</h1>
                <div style={{width: 100}}></div>
            </div>
            <Row className="g-4">
                {['breakfast', 'lunch', 'dinner'].map(cat => (
                    <Col md={4} key={cat}>
                        <div style={styles.catCard} onClick={() => {setActiveCat(cat); setView("list")}}
                             onMouseEnter={(e) => e.currentTarget.style.borderColor = '#00c6ff'}
                             onMouseLeave={(e) => e.currentTarget.style.borderColor = '#444'}>
                            <h2 className="text-uppercase fw-bold display-4">{cat}</h2>
                            <span className="text-muted">View Menu</span>
                        </div>
                    </Col>
                ))}
            </Row>
        </Container>
    </div>
  );

  return (
    <div style={styles.page}>
        <Container fluid>
            <div className="d-flex justify-content-between mb-4 border-bottom border-secondary pb-3">
                <Button variant="outline-light" onClick={() => setView("categories")}>← BACK TO CATEGORIES</Button>
                <h2 className="text-uppercase text-success">{activeCat} MENU</h2>
            </div>
            <Row>
                {meals[activeCat]?.map((m, i) => {
                    const isEaten = eatenLog[m.name] === new Date().toISOString().split('T')[0];
                    return (
                        <Col md={4} key={i}>
                            <Card style={styles.mealCard} className="text-white">
                                <Card.Body className="p-4">
                                    <div className="d-flex justify-content-between mb-2">
                                        <h4 className="fw-bold">{m.name}</h4>
                                        <Badge bg="warning" text="dark" className="align-self-start">{m.calories} cal</Badge>
                                    </div>
                                    <p className="text-white-50">{m.quantity}</p>
                                    
                                    <Button variant={isEaten ? "secondary" : "success"} className="w-100 mb-2 py-2 fw-bold"
                                            disabled={isEaten} onClick={() => handleEat(m.name)}>
                                        {isEaten ? "✅ EATEN TODAY" : "🍽 MARK AS EATEN"}
                                    </Button>
                                    
                                    {!isEaten && (
                                        <Button variant="outline-secondary" className="w-100" onClick={() => handleSwap(activeCat, i)}>
                                            🔄 Swap Meal
                                        </Button>
                                    )}
                                </Card.Body>
                            </Card>
                        </Col>
                    );
                })}
            </Row>
        </Container>
    </div>
  );
}
export default Nutrition;