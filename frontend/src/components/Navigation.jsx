import React, { useState } from 'react';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useNavigate } from 'react-router-dom';
import Chatbot from './Chatbot/Chatbot';

const Navigation = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const [showChatbot, setShowChatbot] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const toggleChatbot = () => {
    setShowChatbot(!showChatbot);
  };

  return (
    <>
      <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
        <Container>
          <LinkContainer to="/">
            <Navbar.Brand className="d-flex align-items-center">
              <span className="me-2">💪</span>
              Elevate AI
            </Navbar.Brand>
          </LinkContainer>

          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <LinkContainer to="/">
                <Nav.Link>Home</Nav.Link>
              </LinkContainer>
              {token && (
                <>
                  <LinkContainer to="/workouts">
                    <Nav.Link>Workouts</Nav.Link>
                  </LinkContainer>
                  <LinkContainer to="/nutrition">
                    <Nav.Link>Nutrition</Nav.Link>
                  </LinkContainer>
                  <LinkContainer to="/tracker">
                    <Nav.Link>Tracker</Nav.Link>
                  </LinkContainer>
                  <LinkContainer to="/profile">
                    <Nav.Link>Profile</Nav.Link>
                  </LinkContainer>
                </>
              )}
            </Nav>

            <Nav>
              {token && (
                <Button
                  variant="outline-info"
                  className="me-2"
                  onClick={toggleChatbot}
                >
                  💬 AI Assistant
                </Button>
              )}
              {!token ? (
                <>
                  <LinkContainer to="/login">
                    <Nav.Link>Login</Nav.Link>
                  </LinkContainer>
                  <LinkContainer to="/signup">
                    <Nav.Link>Sign Up</Nav.Link>
                  </LinkContainer>
                </>
              ) : (
                <Button variant="outline-light" onClick={handleLogout}>
                  Logout
                </Button>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Chatbot isVisible={showChatbot} onClose={toggleChatbot} />
    </>
  );
};

export default Navigation;