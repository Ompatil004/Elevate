import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Badge, Table } from 'react-bootstrap';
import api from '../../utils/api';

const NutritionPage = () => {
  const [mealGoal, setMealGoal] = useState('Muscle Gain');
  const [calorieTarget, setCalorieTarget] = useState(2000);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [savedMeals, setSavedMeals] = useState([]);

  const API_URL = "http://localhost:5000/api";

  const getMealPlan = async () => {
    setLoading(true);
    try {
      const response = await api.post('/ml/predict_meal', {
        goal: mealGoal,
        calorie_target: calorieTarget
      });
      setMealPlan(response.data.recommendations);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend");
    }
    setLoading(false);
  };

  // Load saved meals on component mount
  useEffect(() => {
    // In a real app, this would fetch from an API
    const mockSavedMeals = [
      {
        id: 1,
        name: "Muscle Gain Plan",
        meals: [
          { name: "Breakfast: Oatmeal with protein", calories: 450 },
          { name: "Lunch: Grilled chicken with rice", calories: 650 },
          { name: "Dinner: Salmon with vegetables", calories: 550 }
        ],
        date: "2023-05-15"
      },
      {
        id: 2,
        name: "Weight Loss Plan",
        meals: [
          { name: "Breakfast: Greek yogurt", calories: 200 },
          { name: "Lunch: Salad with lean protein", calories: 350 },
          { name: "Dinner: Grilled fish with vegetables", calories: 400 }
        ],
        date: "2023-05-14"
      }
    ];
    setSavedMeals(mockSavedMeals);
  }, []);

  return (
    <Container className="py-5">
      <h1 className="mb-4">🥗 Nutrition Plans</h1>
      
      <Row className="mb-4">
        <Col md={6}>
          <Card className="shadow-sm border-0 rounded-4">
            <Card.Header className="bg-success text-white fw-bold py-3 rounded-top-4">
              Generate Meal Plan
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Goal</Form.Label>
                <Form.Select value={mealGoal} onChange={(e) => setMealGoal(e.target.value)}>
                  <option value="Muscle Gain">Muscle Gain</option>
                  <option value="Weight Loss">Weight Loss</option>
                  <option value="Maintain">Maintain</option>
                </Form.Select>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Calorie Target</Form.Label>
                <Form.Control 
                  type="number" 
                  value={calorieTarget} 
                  onChange={(e) => setCalorieTarget(Number(e.target.value))}
                  min="1200"
                  max="5000"
                />
              </Form.Group>
              
              <Button 
                variant="success" 
                className="w-100" 
                onClick={getMealPlan} 
                disabled={loading}
              >
                {loading ? "Analyzing..." : "Generate Meal Plan"}
              </Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card className="shadow-sm border-0 rounded-4">
            <Card.Header className="bg-info text-white fw-bold py-3 rounded-top-4">
              Today's Meal Plan
            </Card.Header>
            <Card.Body>
              {mealPlan ? (
                <div>
                  <Table striped bordered hover responsive>
                    <thead>
                      <tr>
                        <th>Meal</th>
                        <th>Calories</th>
                        <th>Protein (g)</th>
                        <th>Carbs (g)</th>
                        <th>Fat (g)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mealPlan.map((meal, idx) => (
                        <tr key={idx}>
                          <td>{meal.name}</td>
                          <td>{meal.calories} kcal</td>
                          <td>{meal.protein || Math.floor(meal.calories * 0.25 / 4)}g</td>
                          <td>{meal.carbs || Math.floor(meal.calories * 0.5 / 4)}g</td>
                          <td>{meal.fat || Math.floor(meal.calories * 0.25 / 9)}g</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                  <div className="d-flex justify-content-between align-items-center mt-3">
                    <div>
                      <strong>Total: </strong>
                      {mealPlan.reduce((sum, meal) => sum + meal.calories, 0)} kcal
                    </div>
                    <Button variant="success">
                      Save Plan
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-muted">Generate a meal plan to see it here</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card className="shadow-sm border-0 rounded-4">
            <Card.Header className="bg-dark text-white fw-bold py-3 rounded-top-4">
              Saved Meal Plans
            </Card.Header>
            <Card.Body>
              {savedMeals.length > 0 ? (
                <div className="table-responsive">
                  <Table striped bordered hover>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Date</th>
                        <th>Meals</th>
                        <th>Calories</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {savedMeals.map(meal => (
                        <tr key={meal.id}>
                          <td>{meal.name}</td>
                          <td>{meal.date}</td>
                          <td>{meal.meals.length} meals</td>
                          <td>{meal.meals.reduce((sum, m) => sum + m.calories, 0)} kcal</td>
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
                <p className="text-muted">No saved meal plans yet</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default NutritionPage;