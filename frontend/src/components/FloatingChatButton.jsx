import React from 'react';
import { Button } from 'react-bootstrap';

const FloatingChatButton = ({ onClick }) => {
  return (
    <Button
      onClick={onClick}
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        width: '60px',
        height: '60px',
        borderRadius: '50%',
        backgroundColor: '#007bff',
        border: 'none',
        boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
        zIndex: 1050,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '24px',
        color: 'white',
      }}
      className="floating-chat-button"
    >
      💬
    </Button>
  );
};

export default FloatingChatButton;
