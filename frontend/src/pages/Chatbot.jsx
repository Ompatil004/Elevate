import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../components/NotificationProvider';
import ConfirmDialog from '../components/ConfirmDialog';

const styles = { 
  page: {
    background: '#09090b',
    minHeight: '100vh',
    color: '#e4e4e7',
    fontFamily: "'Inter', sans-serif",
    display: 'flex', flexDirection: 'column',
    backgroundImage: `
      radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.15), transparent 35%),
      radial-gradient(circle at 100% 100%, rgba(236, 72, 153, 0.1), transparent 35%)
    `
  },
  // --- FIXED NAVBAR (Matches Dashboard Perfectly) ---
  navbar: {
    display: 'flex', alignItems: 'center',
    padding: '0 40px', height: '80px',
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    background: 'rgba(9, 9, 11, 0.6)', backdropFilter: 'blur(16px)',
    position: 'sticky', top: 0, zIndex: 1000
  },
  // LEFT SIDE (Flex 1 forces equal width)
  brand: { 
    flex: 1, 
    fontSize: '22px', fontWeight: '900', letterSpacing: '-1px', 
    background: 'linear-gradient(to right, #fff, #a5b4fc)', 
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', 
    display: 'flex', alignItems: 'center', gap: '10px' 
  },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },

  // CENTER (Centered by flex logic)
  navCenter: { 
    display: 'flex', gap: '8px', height: '100%', alignItems: 'center',
    justifyContent: 'center' 
  },
  
  // BUTTONS (Transparent border prevents jump)
  navLink: {
    display: 'flex', alignItems: 'center', padding: '8px 20px',
    fontSize: '13px', fontWeight: '600', color: '#a1a1aa',
    cursor: 'pointer', borderRadius: '20px', transition: 'all 0.2s',
    textTransform: 'uppercase', letterSpacing: '0.5px',
    border: '1px solid transparent'
  },
  navLinkActive: { 
    background: 'rgba(255,255,255,0.1)', color: '#fff', 
    boxShadow: '0 0 20px rgba(255,255,255,0.05)', 
    border: '1px solid rgba(255,255,255,0.05)'
  },

  // RIGHT SIDE (Flex 1 forces equal width + Right align)
  navRight: { 
    flex: 1, 
    display: 'flex', alignItems: 'center', gap: '24px', 
    justifyContent: 'flex-end' 
  },

  dateDisplay: { 
    fontSize: '13px', fontWeight: '600', 
    color: '#a1a1aa', fontFamily: 'sans-serif', 
    letterSpacing: '0.5px', marginRight: '8px'
  },
  logoutBtn: {
    display: 'flex', alignItems: 'center', gap: '8px', padding: '0 20px', borderRadius: '12px',
    background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)',
    color: '#ef4444', cursor: 'pointer', transition: 'all 0.2s ease', height: '42px',
    fontSize: '12px', fontWeight: '700', textTransform: 'uppercase'
  },

  // --- CHAT CONTAINER ---
  container: {
    flex: 1, maxWidth: '1000px', width: '100%', margin: '0 auto',
    padding: '20px', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 80px)'
  },
  chatWindow: {
    flex: 1, background: '#18181b', borderRadius: '24px',
    border: '1px solid rgba(255,255,255,0.05)',
    display: 'flex', flexDirection: 'column', overflow: 'hidden',
    boxShadow: '0 20px 50px rgba(0,0,0,0.3)',
    position: 'relative'
  },
  messagesArea: {
    flex: 1, padding: '30px', overflowY: 'auto',
    display: 'flex', flexDirection: 'column', gap: '20px'
  },
  
  // --- MESSAGE BUBBLES ---
  messageRow: { display: 'flex', width: '100%' },
  rowUser: { justifyContent: 'flex-end' },
  rowBot: { justifyContent: 'flex-start' },
  
  bubble: {
    maxWidth: '70%', padding: '16px 24px', borderRadius: '20px',
    fontSize: '15px', lineHeight: '1.6', position: 'relative',
    boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
  },
  bubbleUser: {
    background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    color: '#fff', borderRadius: '20px 20px 0 20px'
  },
  bubbleBot: {
    background: '#27272a', color: '#e4e4e7',
    border: '1px solid rgba(255,255,255,0.05)',
    borderRadius: '20px 20px 20px 0'
  },
  avatarBot: {
    width: '36px', height: '36px', borderRadius: '50%',
    background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    marginRight: '12px', fontSize: '18px', boxShadow: '0 0 15px rgba(168, 85, 247, 0.4)'
  },

  // --- INPUT AREA ---
  inputArea: {
    padding: '20px', background: 'rgba(24, 24, 27, 0.8)',
    backdropFilter: 'blur(10px)', borderTop: '1px solid rgba(255,255,255,0.05)',
    display: 'flex', gap: '15px', alignItems: 'center'
  },
  input: {
    flex: 1, padding: '16px 24px', borderRadius: '16px',
    background: '#09090b', border: '1px solid rgba(255,255,255,0.1)',
    color: '#fff', fontSize: '15px', fontFamily: 'inherit',
    outline: 'none', transition: 'border-color 0.2s'
  },
  sendBtn: {
    width: '54px', height: '54px', borderRadius: '16px',
    background: '#fff', border: 'none',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    cursor: 'pointer', fontSize: '20px', color: '#09090b',
    transition: 'transform 0.2s', boxShadow: '0 0 20px rgba(255,255,255,0.2)'
  }
};

const INITIAL_MESSAGES = [
  { role: 'bot', text: "Hi! I'm your AI Coach. How can I help you reach your goals today?" }
];

function Chatbot() {
  const navigate = useNavigate();
  const { showError, showSuccess } = useNotification();
  const [confirmDialog, setConfirmDialog] = useState({ show: false, message: '', onConfirm: null });

  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const showConfirmDialog = (message, onConfirm) => {
    setConfirmDialog({ show: true, message, onConfirm });
  };

  const handleConfirm = () => {
    if (confirmDialog.onConfirm) {
      confirmDialog.onConfirm(true);
    }
    setConfirmDialog({ show: false, message: '', onConfirm: null });
  };

  const handleCancelConfirm = () => {
    if (confirmDialog.onConfirm) {
      confirmDialog.onConfirm(false);
    }
    setConfirmDialog({ show: false, message: '', onConfirm: null });
  };

  // Today's Date Logic
  const todayDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // 1. Add User Message
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    // 2. Simulate AI Delay
    setTimeout(() => {
        const botMsg = { 
            role: 'bot', 
            text: "That's a great question! Based on your profile, I'd recommend focusing on progressive overload. Would you like me to adjust your plan?" 
        };
        setMessages(prev => [...prev, botMsg]);
        setIsTyping(false);
    }, 1500);
  };

  const handleLogout = () => {
    showConfirmDialog("Log out?", (confirmed) => {
      if (confirmed) {
        localStorage.clear();
        navigate('/');
      }
    });
  };

  return (
    <>
      <div style={styles.page}>
      <nav style={styles.navbar}>
        <div style={styles.brand}><div style={styles.brandDot}></div> ELEVATE</div>
        <div style={styles.navCenter}>
            <div style={styles.navLink} onClick={() => navigate('/dashboard')}>Dashboard</div>
            <div style={styles.navLink} onClick={() => navigate('/workout')}>Workout</div>
            <div style={styles.navLink} onClick={() => navigate('/nutrition')}>Nutrition</div>
            <div style={{...styles.navLink, ...styles.navLinkActive}}>AI Coach</div>
        </div>
        <div style={styles.navRight}>
            <div style={styles.dateDisplay}>{todayDate}</div>
            <button style={styles.logoutBtn} onClick={handleLogout}>LOGOUT</button>
        </div>
      </nav>

      <div style={styles.container}>
        <div style={styles.chatWindow}>
            <div style={styles.messagesArea}>
                {messages.map((msg, i) => (
                    <div key={i} style={{...styles.messageRow, ...(msg.role === 'user' ? styles.rowUser : styles.rowBot)}}>
                        {msg.role === 'bot' && <div style={styles.avatarBot}>🤖</div>}
                        <div style={{...styles.bubble, ...(msg.role === 'user' ? styles.bubbleUser : styles.bubbleBot)}}>
                            {msg.text}
                        </div>
                    </div>
                ))}
                
                {isTyping && (
                    <div style={{...styles.messageRow, ...styles.rowBot}}>
                        <div style={styles.avatarBot}>🤖</div>
                        <div style={{...styles.bubble, ...styles.bubbleBot, padding:'12px 20px'}}>
                            <span className="typing-dot">.</span><span className="typing-dot">.</span><span className="typing-dot">.</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form style={styles.inputArea} onSubmit={handleSend}>
                <input 
                    style={styles.input} 
                    placeholder="Ask about your workout, diet, or form..." 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                />
                <button type="submit" style={styles.sendBtn}>➤</button>
            </form>
        </div>
      </div>

      <style>{`
        .typing-dot { animation: blink 1.4s infinite both; margin: 0 1px; font-size: 20px; }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink { 0% { opacity: 0.2; } 20% { opacity: 1; } 100% { opacity: 0.2; } }
        
        input:focus { border-color: #6366f1 !important; box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2); }
        button:hover { transform: scale(1.05); }
        button:active { transform: scale(0.95); }
        
        /* Scrollbar */
        div::-webkit-scrollbar { width: 6px; }
        div::-webkit-scrollbar-track { background: transparent; }
        div::-webkit-scrollbar-thumb { background: #27272a; border-radius: 10px; }
      `}</style>
    </div>
    <ConfirmDialog
      show={confirmDialog.show}
      message={confirmDialog.message}
      onConfirm={handleConfirm}
      onCancel={handleCancelConfirm}
    />
    </>
  );
}

export default Chatbot;