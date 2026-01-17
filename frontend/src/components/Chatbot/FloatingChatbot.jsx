import React, { useState, useRef, useEffect } from 'react';
import { Button, Form, Card } from 'react-bootstrap';
import api from '../../utils/api';

const FloatingChatbot = ({ isVisible, onClose, onToggleVisibility }) => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your AI fitness assistant. How can I help you today?", sender: 'bot', timestamp: new Date() }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isVisible && !isMinimized) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [messages, isVisible, isMinimized]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      // Send message to backend
      const response = await api.post('/chat/message', {
        message: inputMessage
      });
      
      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        text: response.data.message,
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 2,
        text: "Sorry, I'm having trouble connecting to the AI service. Please try again later.",
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!isVisible) {
    return (
      <Button
        variant="primary"
        className="position-fixed rounded-circle d-flex align-items-center justify-content-center shadow-lg"
        style={{
          width: '60px',
          height: '60px',
          bottom: '30px',
          right: '30px',
          zIndex: '9999',
          backgroundColor: '#25D366',
          borderColor: '#25D366',
          fontSize: '24px'
        }}
        onClick={onToggleVisibility}
      >
        <span>💬</span>
      </Button>
    );
  }

  if (isMinimized) {
    return (
      <div className="position-fixed" style={{ bottom: '30px', right: '30px', zIndex: '9999' }}>
        <Button
          variant="success"
          className="rounded-pill px-3 py-2 d-flex align-items-center shadow-lg"
          style={{ backgroundColor: '#25D366', borderColor: '#25D366' }}
          onClick={() => setIsMinimized(false)}
        >
          <span className="me-2">💬</span>
          <span>AI Assistant</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="position-fixed" style={{ bottom: '30px', right: '30px', zIndex: '9999' }}>
      <Card className="shadow-lg" style={{ width: '350px', height: '500px', borderRadius: '15px', overflow: 'hidden' }}>
        <Card.Header className="d-flex justify-content-between align-items-center" style={{ backgroundColor: '#25D366', color: 'white' }}>
          <div className="d-flex align-items-center">
            <div className="rounded-circle bg-white d-flex align-items-center justify-content-center me-2" style={{ width: '30px', height: '30px' }}>
              <span className="text-success">💬</span>
            </div>
            <strong>AI Fitness Assistant</strong>
          </div>
          <div className="d-flex">
            <Button
              variant="link"
              className="text-white p-0 mx-1"
              onClick={() => setIsMinimized(true)}
              title="Minimize"
            >
              <span>_</span>
            </Button>
            <Button
              variant="link"
              className="text-white p-0 mx-1"
              onClick={onClose}
              title="Close"
            >
              <span>✕</span>
            </Button>
          </div>
        </Card.Header>
        
        <Card.Body className="d-flex flex-column p-0" style={{ height: 'calc(100% - 56px)' }}>
          <div className="flex-grow-1 overflow-auto p-3" style={{ maxHeight: '75%' }}>
            <div className="d-flex flex-column">
              {messages.map((msg) => (
                <div 
                  key={msg.id} 
                  className={`d-flex mb-3 ${msg.sender === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                >
                  <div 
                    className={`p-3 rounded-3 ${msg.sender === 'user' ? 'bg-primary text-white' : 'bg-light text-dark'}`}
                    style={{ maxWidth: '80%', borderRadius: '18px !important' }}
                  >
                    <div>{msg.text}</div>
                    <div 
                      className={`text-muted fst-italic ${msg.sender === 'user' ? 'text-white' : ''}`} 
                      style={{ fontSize: '0.7rem' }}
                    >
                      {formatTime(msg.timestamp)}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="d-flex justify-content-start mb-3">
                  <div className="p-3 rounded-3 bg-light text-dark" style={{ maxWidth: '80%', borderRadius: '18px !important' }}>
                    <div className="d-flex align-items-center">
                      <div className="spinner-border spinner-border-sm me-2" role="status">
                        <span className="visually-hidden">Loading...</span>
                      </div>
                      <span>Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div ref={messagesEndRef} />
          </div>
          
          <div className="border-top p-3">
            <Form onSubmit={handleSendMessage}>
              <div className="d-flex">
                <Form.Control
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask me about workouts, nutrition, or fitness tips..."
                  disabled={isLoading}
                  className="rounded-pill pe-4"
                  style={{ paddingLeft: '15px' }}
                />
                <Button
                  type="submit"
                  variant="success"
                  className="rounded-circle ms-2 d-flex align-items-center justify-content-center"
                  style={{ width: '40px', height: '40px', backgroundColor: '#25D366', borderColor: '#25D366' }}
                  disabled={isLoading || !inputMessage.trim()}
                >
                  <span>➤</span>
                </Button>
              </div>
            </Form>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default FloatingChatbot;