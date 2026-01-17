import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, Badge, Table, Tab, Tabs } from 'react-bootstrap';

const ProfilePage = () => {
  const [userData, setUserData] = useState({
    name: "John Doe",
    email: "john.doe@example.com",
    age: 28,
    weight: 75,
    height: 180,
    fitnessGoal: "Muscle Gain",
    experienceLevel: "Intermediate"
  });

  const [activeTab, setActiveTab] = useState('profile');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, this would send data to an API
    alert('Profile updated successfully!');
  };

  return (
    <Container className="py-5">
      <h1 className="mb-4">👤 User Profile</h1>
      
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="profile" title="Profile Info">
          <Row>
            <Col lg={8}>
              <Card className="shadow-sm border-0 rounded-4">
                <Card.Header className="bg-primary text-white fw-bold py-3 rounded-top-4">
                  Personal Information
                </Card.Header>
                <Card.Body>
                  <Form onSubmit={handleSubmit}>
                    <Row className="mb-3">
                      <Form.Group as={Col} md={6} controlId="formName">
                        <Form.Label>Name</Form.Label>
                        <Form.Control 
                          type="text" 
                          name="name" 
                          value={userData.name} 
                          onChange={handleInputChange}
                        />
                      </Form.Group>
                      
                      <Form.Group as={Col} md={6} controlId="formEmail">
                        <Form.Label>Email</Form.Label>
                        <Form.Control 
                          type="email" 
                          name="email" 
                          value={userData.email} 
                          onChange={handleInputChange}
                        />
                      </Form.Group>
                    </Row>
                    
                    <Row className="mb-3">
                      <Form.Group as={Col} md={6} controlId="formAge">
                        <Form.Label>Age</Form.Label>
                        <Form.Control 
                          type="number" 
                          name="age" 
                          value={userData.age} 
                          onChange={handleInputChange}
                        />
                      </Form.Group>
                      
                      <Form.Group as={Col} md={6} controlId="formFitnessGoal">
                        <Form.Label>Fitness Goal</Form.Label>
                        <Form.Select 
                          name="fitnessGoal" 
                          value={userData.fitnessGoal} 
                          onChange={handleInputChange}
                        >
                          <option value="Muscle Gain">Muscle Gain</option>
                          <option value="Weight Loss">Weight Loss</option>
                          <option value="Maintain">Maintain</option>
                          <option value="Endurance">Endurance</option>
                        </Form.Select>
                      </Form.Group>
                    </Row>
                    
                    <Row className="mb-3">
                      <Form.Group as={Col} md={6} controlId="formWeight">
                        <Form.Label>Weight (kg)</Form.Label>
                        <Form.Control 
                          type="number" 
                          name="weight" 
                          value={userData.weight} 
                          onChange={handleInputChange}
                        />
                      </Form.Group>
                      
                      <Form.Group as={Col} md={6} controlId="formHeight">
                        <Form.Label>Height (cm)</Form.Label>
                        <Form.Control 
                          type="number" 
                          name="height" 
                          value={userData.height} 
                          onChange={handleInputChange}
                        />
                      </Form.Group>
                    </Row>
                    
                    <Row className="mb-3">
                      <Form.Group as={Col} md={6} controlId="formExperience">
                        <Form.Label>Experience Level</Form.Label>
                        <Form.Select 
                          name="experienceLevel" 
                          value={userData.experienceLevel} 
                          onChange={handleInputChange}
                        >
                          <option value="Beginner">Beginner</option>
                          <option value="Intermediate">Intermediate</option>
                          <option value="Advanced">Advanced</option>
                        </Form.Select>
                      </Form.Group>
                    </Row>
                    
                    <Button variant="primary" type="submit">
                      Update Profile
                    </Button>
                  </Form>
                </Card.Body>
              </Card>
            </Col>
            
            <Col lg={4}>
              <Card className="shadow-sm border-0 rounded-4">
                <Card.Header className="bg-success text-white fw-bold py-3 rounded-top-4">
                  Account Summary
                </Card.Header>
                <Card.Body>
                  <div className="d-flex flex-column align-items-center mb-4">
                    <div className="rounded-circle bg-light d-flex align-items-center justify-content-center mb-3" style={{ width: '100px', height: '100px' }}>
                      <span className="display-4 text-muted">👤</span>
                    </div>
                    <h5>{userData.name}</h5>
                    <p className="text-muted">{userData.email}</p>
                  </div>
                  
                  <div className="d-grid gap-2">
                    <div className="d-flex justify-content-between">
                      <span>Workouts Completed:</span>
                      <strong>24</strong>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span>Nutrition Plans Used:</span>
                      <strong>18</strong>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span>Days Tracked:</span>
                      <strong>42</strong>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span>Current Streak:</span>
                      <strong className="text-success">7 days</strong>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
        
        <Tab eventKey="progress" title="Progress Tracking">
          <Row>
            <Col>
              <Card className="shadow-sm border-0 rounded-4">
                <Card.Header className="bg-info text-white fw-bold py-3 rounded-top-4">
                  Recent Activity
                </Card.Header>
                <Card.Body>
                  <Table striped bordered hover responsive>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Activity</th>
                        <th>Duration</th>
                        <th>Calories Burned</th>
                        <th>Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>2023-05-15</td>
                        <td>Strength Training</td>
                        <td>45 min</td>
                        <td>280 kcal</td>
                        <td>Completed all sets</td>
                      </tr>
                      <tr>
                        <td>2023-05-14</td>
                        <td>Cardio Session</td>
                        <td>30 min</td>
                        <td>220 kcal</td>
                        <td>Good pace maintained</td>
                      </tr>
                      <tr>
                        <td>2023-05-13</td>
                        <td>Yoga</td>
                        <td>60 min</td>
                        <td>180 kcal</td>
                        <td>Improved flexibility</td>
                      </tr>
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
          
          <Row className="mt-4">
            <Col md={6}>
              <Card className="shadow-sm border-0 rounded-4">
                <Card.Header className="bg-warning text-dark fw-bold py-3 rounded-top-4">
                  Weight Progress
                </Card.Header>
                <Card.Body>
                  <div className="text-center">
                    <h2>{userData.weight} kg</h2>
                    <p className="text-success">↓ 1.2 kg this month</p>
                    <div className="progress mt-3" style={{ height: '20px' }}>
                      <div 
                        className="progress-bar bg-success" 
                        role="progressbar" 
                        style={{ width: '65%' }} 
                        aria-valuenow="65" 
                        aria-valuemin="0" 
                        aria-valuemax="100"
                      >
                        Progress
                      </div>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={6}>
              <Card className="shadow-sm border-0 rounded-4">
                <Card.Header className="bg-success text-white fw-bold py-3 rounded-top-4">
                  Fitness Goals
                </Card.Header>
                <Card.Body>
                  <div className="d-flex justify-content-between mb-2">
                    <span>Muscle Gain</span>
                    <Badge bg="success">75%</Badge>
                  </div>
                  <div className="progress mb-3" style={{ height: '10px' }}>
                    <div 
                      className="progress-bar bg-success" 
                      role="progressbar" 
                      style={{ width: '75%' }} 
                      aria-valuenow="75" 
                      aria-valuemin="0" 
                      aria-valuemax="100"
                    ></div>
                  </div>
                  
                  <div className="d-flex justify-content-between mb-2">
                    <span>Strength Increase</span>
                    <Badge bg="info">60%</Badge>
                  </div>
                  <div className="progress mb-3" style={{ height: '10px' }}>
                    <div 
                      className="progress-bar bg-info" 
                      role="progressbar" 
                      style={{ width: '60%' }} 
                      aria-valuenow="60" 
                      aria-valuemin="0" 
                      aria-valuemax="100"
                    ></div>
                  </div>
                  
                  <div className="d-flex justify-content-between mb-2">
                    <span>Consistency</span>
                    <Badge bg="warning">90%</Badge>
                  </div>
                  <div className="progress" style={{ height: '10px' }}>
                    <div 
                      className="progress-bar bg-warning" 
                      role="progressbar" 
                      style={{ width: '90%' }} 
                      aria-valuenow="90" 
                      aria-valuemin="0" 
                      aria-valuemax="100"
                    ></div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
      </Tabs>
    </Container>
  );
};

export default ProfilePage;