import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="professional-footer">
      <div className="footer-content">
        <p className="footer-text">
          &copy; 2026 <span className="footer-brand">Team Elevate</span>. All rights reserved. 
          <span className="lightning-icon">⚡</span> 
          <span className="footer-subtext-inline">Built with React &amp; Vite</span>
        </p>
        <div className="footer-links">
          <Link to="/about" className="footer-link">
            About US
          </Link>
          <Link to="/terms" className="footer-link">
            Terms &amp; Policies
          </Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
