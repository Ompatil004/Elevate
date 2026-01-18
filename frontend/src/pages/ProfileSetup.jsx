import React, { useState } from 'react';
import axios from 'axios';
import { Container, Form, Button, Card, Row, Col, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

function ProfileSetup() {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    age: '',
    weight: '',
    height: '',
    gender: 'Male',
    goal: 'Muscle Gain',
    experience: 'Beginner',
    dietary_preference: 'Non-Veg',
    // Checkboxes will be handled separately
    equipment: [],
    allergies: []
  });

  // Handle Text/Select Inputs
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle Multi-Select Checkboxes (Equipment & Allergies)
  const handleCheckbox = (e, type) => {
    const { value, checked } = e.target;
    let updatedList = [...formData[type]];
    
    if (checked) {
      updatedList.push(value);
    } else {
      updatedList = updatedList.filter((item) => item !== value);
    }
    
    setFormData({ ...formData, [type]: updatedList });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const userId = localStorage.getItem('userId');
    if (!userId) {
        setError("User ID missing. Please login again.");
        return;
    }

    try {
      // 1. FORMAT DATA CORRECTLY (Strings -> Numbers)
      const payload = {
        user_id: userId, // CRITICAL: Send the ID
        age: parseInt(formData.age),
        weight: parseFloat(formData.weight),
        height: parseFloat(formData.height),
        gender: formData.gender,
        goal: formData.goal,
        experience: formData.experience,
        dietary_preference: formData.dietary_preference,
        equipment: formData.equipment,
        allergies: formData.allergies.length > 0 ? formData.allergies : ["None"]
      };

      console.log("Sending Payload:", payload); // Debugging

      // 2. SEND TO BACKEND
      await axios.post('http://127.0.0.1:8000/auth/update-profile', payload);
      
      alert("Profile Setup Complete! Building your plan...");
      navigate('/dashboard');

    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
          // Show exact error from backend (e.g., "Field required")
          setError(`Error: ${JSON.stringify(err.response.data.detail)}`);
      } else {
          setError("Failed to save profile. Is backend running?");
      }
    }
  };

  return (
    <Container className="py-5 d-flex justify-content-center">
      <Card className="shadow-lg p-4" style={{ maxWidth: '600px', width: '100%' }}>
        <h2 className="text-center text-primary mb-4">Tell Us About You</h2>
        
        {error && <Alert variant="danger">{error}</Alert>}

        <Form onSubmit={handleSubmit}>
          <Row>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Age</Form.Label>
                <Form.Control type="number" name="age" value={formData.age} onChange={handleChange} required />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Weight (kg)</Form.Label>
                <Form.Control type="number" name="weight" value={formData.weight} onChange={handleChange} required />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Height (cm)</Form.Label>
                <Form.Control type="number" name="height" value={formData.height} onChange={handleChange} required />
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label>Gender</Form.Label>
            <Form.Select name="gender" value={formData.gender} onChange={handleChange}>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Goal</Form.Label>
            <Form.Select name="goal" value={formData.goal} onChange={handleChange}>
              <option value="Muscle Gain">Muscle Gain (Build Mass)</option>
              <option value="Weight Loss">Weight Loss (Burn Fat)</option>
              <option value="Maintenance">Maintenance (Stay Fit)</option>
            </Form.Select>
          </Form.Group>

        <Form.Group className="mb-3">
            <Form.Label>Dietary Preference</Form.Label>
            <Form.Select name="dietary_preference" value={formData.dietary_preference} onChange={handleChange}>
              <option value="Non-Veg">Non-Veg Only</option>
              <option value="Veg">Vegetarian Only</option>
              <option value="Both">Both (Veg & Non-Veg)</option> {/* NEW OPTION */}
              <option value="Vegan">Vegan</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Available Equipment (Check all that apply)</Form.Label>
            <div className="d-flex flex-wrap gap-3">
              {['Dumbbells', 'Yoga Mat', 'Resistance Bands', 'Pull-up Bar', 'None (Bodyweight)'].map((item) => (
                <Form.Check 
                    key={item}
                    type="checkbox" 
                    label={item} 
                    value={item} 
                    onChange={(e) => handleCheckbox(e, 'equipment')}
                />
              ))}
            </div>
          </Form.Group>

          <Form.Group className="mb-4">
             <Form.Label>Allergies</Form.Label>
             <div className="d-flex flex-wrap gap-3">
               {['Gluten', 'Lactose Intolerant', 'Nuts', 'Diabetes', 'None'].map((item) => (
                 <Form.Check 
                     key={item}
                     type="checkbox" 
                     label={item} 
                     value={item} 
                     onChange={(e) => handleCheckbox(e, 'allergies')}
                 />
               ))}
             </div>
          </Form.Group>

          <Button variant="primary" type="submit" size="lg" className="w-100">
            Generate My AI Plan 🚀
          </Button>
        </Form>
      </Card>
    </Container>
  );
}

export default ProfileSetup;