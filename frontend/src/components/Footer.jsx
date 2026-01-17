import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

const Footer = () => {
  return (
    <footer className="bg-dark text-light py-4 mt-5">
      <Container>
        <Row>
          <Col className="text-center">
            <p className="mb-0">&copy; {new Date().getFullYear()} Elevate AI - Intelligent Fitness & Nutrition Platform</p>
            <p className="mb-0">Empowering your fitness journey with AI technology</p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;