import React, { useState, useEffect, useRef } from 'react';
import { Send, RotateCcw, Bot, User } from 'lucide-react';
import { mlAPI } from '@/services/api';
import { toast } from 'sonner';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI health assistant. How can I help you with your fitness journey today?',
      sender: 'ai',
      timestamp: new Date(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputText.trim() || loading) return;

    try {
      setLoading(true);
      setError(null);

      // Add user message to the chat
      const userMessage: Message = {
        id: Date.now().toString(),
        text: inputText,
        sender: 'user',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);
      const textToSend = inputText;
      setInputText(''); // Clear input immediately for better UX

      // Call the backend ML chat API
      const response = await mlAPI.chat({
        prompt: textToSend,
        context: 'Health and Fitness',
        response_length: 'Moderate'
      });

      // Add AI response to the chat
      const aiMessage: Message = {
        id: Date.now().toString(),
        text: response.data.response || 'I\'m not sure how to respond to that. Could you ask something related to fitness or nutrition?',
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setError(err.message || 'Error sending message');
      toast.error('Failed to send message');
      
      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now().toString(),
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: '1',
        text: 'Hello! I\'m your AI health assistant. How can I help you with your fitness journey today?',
        sender: 'ai',
        timestamp: new Date(),
      }
    ]);
    toast.info('Chat cleared');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Bot className="w-8 h-8 text-[#22C55E]" />
            <h1 className="text-2xl font-bold">AI Health Assistant</h1>
          </div>
          <button
            onClick={clearChat}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Clear Chat
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Chat Container */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden flex flex-col h-[70vh]">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] md:max-w-[70%] rounded-2xl p-4 ${
                    message.sender === 'user'
                      ? 'bg-[#22C55E] text-white rounded-br-none'
                      : 'bg-gray-100 text-gray-800 rounded-bl-none'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.sender === 'ai' && (
                      <Bot className="w-5 h-5 mt-0.5 text-[#22C55E]" />
                    )}
                    <div className="flex-1">
                      <p className="whitespace-pre-wrap">{message.text}</p>
                    </div>
                    {message.sender === 'user' && (
                      <User className="w-5 h-5 mt-0.5 text-white" />
                    )}
                  </div>
                  <div
                    className={`text-xs mt-1 ${
                      message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="max-w-[80%] md:max-w-[70%] rounded-2xl rounded-bl-none bg-gray-100 text-gray-800 p-4">
                  <div className="flex items-center gap-2">
                    <Bot className="w-5 h-5 text-[#22C55E]" />
                    <div className="flex space-x-1">
                      <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                      <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Container */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex gap-2">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about fitness, nutrition, or your workout plan..."
                className="flex-1 border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent resize-none"
                rows={1}
                disabled={loading}
              />
              <button
                onClick={handleSend}
                disabled={loading || !inputText.trim()}
                className={`flex items-center justify-center w-12 h-12 rounded-xl ${
                  loading || !inputText.trim()
                    ? 'bg-gray-300 text-gray-500'
                    : 'bg-[#22C55E] text-white hover:bg-[#16A34A]'
                } transition-colors`}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              AI assistant can provide fitness and nutrition advice. For medical concerns, please consult a professional.
            </p>
          </div>
        </div>

        {/* Tips Section */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-xl border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-2">💡 Pro Tips</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Ask about proper form for exercises</li>
              <li>• Get nutrition advice for your goals</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-2">🎯 Goal Support</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Ask for workout modifications</li>
              <li>• Get recovery recommendations</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-xl border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-2">📋 Plan Help</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Request meal plan ideas</li>
              <li>• Get exercise alternatives</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export { Chatbot };