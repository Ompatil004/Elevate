import React, { useState } from 'react';
import axios from 'axios';
import { Container, Form, Button, Card, Alert } from 'react-bootstrap';
import { useNavigate, Link } from 'react-router-dom';

function Login() {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      // 1. Send Login Request
      const res = await axios.post("http://127.0.0.1:8000/auth/login", formData);
      const userId = res.data.user_id;

      // 2. Save Basic Credentials
      localStorage.setItem("token", "dummy-token");
      localStorage.setItem("userId", userId);
      localStorage.setItem("userName", res.data.full_name);

      // 3. CHECK PROFILE STATUS (The Fix)
      // We ask the backend if this user is "setup" yet
      try {
        const profileRes = await axios.get(`http://127.0.0.1:8000/auth/get-profile/${userId}`);
        
        if (profileRes.data.is_setup) {
             console.log("✅ Profile exists. Going to Dashboard.");
             alert("Welcome back!");
             navigate("/dashboard");
        } else {
             console.log("⚠️ New User. Going to Setup.");
             alert("Login Successful! Please complete your profile.");
             navigate("/profile-setup");
        }
      } catch (profileErr) {
        // If getting profile fails (e.g., 404), assume they are new
        console.warn("Profile check failed, sending to setup:", profileErr);
        navigate("/profile-setup");
      }

    } catch (err) {
      console.error(err);
      setError("Invalid email or password");
    }
  };

  return (
    <Container className="d-flex justify-content-center align-items-center min-vh-100 bg-light">
      <Card className="p-4 shadow-lg" style={{ maxWidth: '400px', width: '100%' }}>
        <h2 className="text-center mb-4">Login</h2>
        {error && <Alert variant="danger">{error}</Alert>}
        
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Email address</Form.Label>
            <Form.Control type="email" name="email" onChange={handleChange} required />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Password</Form.Label>
            <Form.Control type="password" name="password" onChange={handleChange} required />
          </Form.Group>

          <Button variant="primary" type="submit" className="w-100">
            Login
          </Button>
        </Form>
        <div className="mt-3 text-center">
            <small>Don't have an account? <Link to="/register">Register</Link></small>
        </div>
      </Card>
    </Container>
  );
}

export default Login;