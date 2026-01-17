import React, { useState, useRef, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, ListGroup } from 'react-bootstrap';
import api from '../../utils/api';

const Chatbot = ({ isVisible, onClose }) => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your AI fitness assistant. How can I help you today?", sender: 'bot' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;
    
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user'
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
        id: messages.length + 2,
        text: response.data.message,
        sender: 'bot'
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: messages.length + 2,
        text: "Sorry, I'm having trouble connecting to the AI service. Please try again later.",
        sender: 'bot'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isVisible) return null;

  return (
    <Card className="position-fixed bottom-0 end-0 m-3" style={{ width: '400px', height: '500px', zIndex: 1000 }}>
      <Card.Header className="d-flex justify-content-between align-items-center bg-primary text-white">
        <span>AI Fitness Assistant</span>
        <Button variant="link" className="text-white p-0" onClick={onClose}>
          ✕
        </Button>
      </Card.Header>
      <Card.Body className="d-flex flex-column p-0" style={{ height: 'calc(100% - 40px)' }}>
        <div className="flex-grow-1 overflow-auto p-3" style={{ maxHeight: '70%' }}>
          <ListGroup variant="flush">
            {messages.map((msg) => (
              <ListGroup.Item 
                key={msg.id} 
                className={`border-0 p-2 ${msg.sender === 'user' ? 'text-end' : 'text-start'}`}
              >
                <div 
                  className={`d-inline-block p-2 rounded ${
                    msg.sender === 'user' 
                      ? 'bg-primary text-white' 
                      : 'bg-light text-dark'
                  }`}
                  style={{ maxWidth: '80%' }}
                >
                  {msg.text}
                </div>
              </ListGroup.Item>
            ))}
            {isLoading && (
              <ListGroup.Item className="border-0 p-2 text-start">
                <div className="d-inline-block p-2 rounded bg-light text-dark" style={{ maxWidth: '80%' }}>
                  Thinking...
                </div>
              </ListGroup.Item>
            )}
            <div ref={messagesEndRef} />
          </ListGroup>
        </div>
        <div className="border-top p-3">
          <Form onSubmit={handleSendMessage}>
            <div className="d-flex">
              <Form.Control
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me about workouts, nutrition, or fitness tips..."
                disabled={isLoading}
              />
              <Button 
                type="submit" 
                variant="primary" 
                className="ms-2"
                disabled={isLoading || !inputMessage.trim()}
              >
                Send
              </Button>
            </div>
          </Form>
        </div>
      </Card.Body>
    </Card>
  );
};

export default Chatbot;