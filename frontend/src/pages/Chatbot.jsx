import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ConfirmDialog from '../components/ConfirmDialog';
import { sendChatbotMessage, getProfile } from '../api';
import { logoutSafe } from '../utils/storage';
import { useTheme } from '../context/ThemeContext';

// ===== STYLES =====
const getStyles = (isDark) => ({
  page: {
    background: 'transparent',
    minHeight: '100dvh',
    color: isDark ? '#e4e4e7' : '#18181b',
    fontFamily: "'Inter', sans-serif",
    display: 'flex', flexDirection: 'column',
    overflowX: 'hidden',
    position: 'relative',
    zIndex: 1,
    paddingTop: 'clamp(64px, 9vw, 80px)'
  },
  navbar: {
    display: 'flex', alignItems: 'center',
    padding: '0 clamp(12px, 4vw, 40px)', height: 'clamp(64px, 9vw, 80px)',
    gap: 'clamp(8px, 2vw, 18px)',
    borderBottom: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.08)',
    background: isDark ? 'rgba(9, 9, 11, 0.55)' : 'rgba(240,240,248,0.82)',
    backdropFilter: 'blur(20px)',
    position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
    overflowX: 'auto'
  },
  brand: {
    flex: 1,
    fontSize: '22px', fontWeight: '900', letterSpacing: '-1px',
    background: isDark ? 'linear-gradient(to right, #fff, #a5b4fc)' : 'linear-gradient(to right, #18181b, #4f46e5)',
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
    display: 'flex', alignItems: 'center', gap: '10px'
  },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  navCenter: {
    display: 'flex', gap: 'clamp(4px, 1.5vw, 8px)', height: '100%', alignItems: 'center',
    justifyContent: 'center'
  },
  navLink: {
    display: 'flex', alignItems: 'center', padding: '8px clamp(10px, 2vw, 20px)',
    fontSize: 'clamp(11px, 1.7vw, 13px)', fontWeight: '600',
    color: isDark ? '#a1a1aa' : '#52525b',
    cursor: 'pointer', borderRadius: '20px', transition: 'all 0.2s',
    textTransform: 'uppercase', letterSpacing: '0.5px',
    border: '1px solid transparent'
  },
  navLinkActive: {
    background: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(79,70,229,0.12)',
    color: isDark ? '#fff' : '#4f46e5',
    boxShadow: isDark ? '0 0 20px rgba(255,255,255,0.05)' : '0 0 20px rgba(79,70,229,0.1)',
    border: isDark ? '1px solid rgba(255,255,255,0.05)' : '1px solid rgba(79,70,229,0.2)'
  },
  navRight: {
    flex: 1,
    display: 'flex', alignItems: 'center', gap: 'clamp(8px, 2vw, 24px)',
    justifyContent: 'flex-end'
  },
  dateDisplay: {
    fontSize: '13px', fontWeight: '600',
    color: isDark ? '#a1a1aa' : '#52525b', fontFamily: 'sans-serif',
    letterSpacing: '0.5px', marginRight: '8px'
  },
  logoutBtn: {
    display: 'flex', alignItems: 'center', gap: '8px', padding: '0 clamp(10px, 2vw, 20px)', borderRadius: '12px',
    background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)',
    color: '#ef4444', cursor: 'pointer', transition: 'all 0.2s ease', height: 'clamp(36px, 6vw, 42px)',
    fontSize: 'clamp(10px, 1.7vw, 12px)', fontWeight: '700', textTransform: 'uppercase'
  },

  // --- CHAT LAYOUT ---
  container: {
    flex: 1, maxWidth: '900px', width: '100%', margin: '0 auto',
    padding: 'clamp(10px, 3vw, 20px)', display: 'flex', flexDirection: 'column', minHeight: 0
  },
  chatWindow: {
    flex: 1,
    background: isDark ? 'rgba(24,24,27,0.72)' : 'rgba(252,252,255,0.68)',
    backdropFilter: 'blur(24px)',
    borderRadius: 'clamp(14px, 2vw, 24px)',
    border: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.08)',
    display: 'flex', flexDirection: 'column', overflow: 'hidden',
    boxShadow: isDark ? '0 20px 60px rgba(0,0,0,0.35)' : '0 8px 32px rgba(99,102,241,0.08), 0 2px 8px rgba(0,0,0,0.06)',
    position: 'relative'
  },

  // --- CHAT HEADER ---
  chatHeader: {
    padding: 'clamp(12px, 2vw, 16px) clamp(12px, 2.4vw, 24px)',
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    gap: '10px',
    borderBottom: isDark ? '1px solid rgba(255,255,255,0.06)' : '1px solid rgba(0,0,0,0.06)',
    background: isDark ? 'rgba(24,24,27,0.80)' : 'rgba(248,248,254,0.90)',
    backdropFilter: 'blur(10px)'
  },
  chatHeaderLeft: {
    display: 'flex', alignItems: 'center', gap: '12px'
  },
  chatHeaderAvatar: {
    width: '40px', height: '40px', borderRadius: '14px',
    background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '20px', boxShadow: '0 0 20px rgba(99, 102, 241, 0.3)'
  },
  chatHeaderInfo: {
    display: 'flex', flexDirection: 'column'
  },
  chatHeaderName: {
    fontSize: '15px', fontWeight: '700', color: isDark ? '#fff' : '#18181b'
  },
  chatHeaderStatus: {
    fontSize: '11px', fontWeight: '600', color: '#22c55e',
    display: 'flex', alignItems: 'center', gap: '4px'
  },
  statusDot: {
    width: '6px', height: '6px', borderRadius: '50%',
    background: '#22c55e', display: 'inline-block',
    animation: 'pulse 2s ease-in-out infinite'
  },
  clearBtn: {
    padding: '6px 14px', borderRadius: '10px',
    background: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
    border: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.08)',
    color: isDark ? '#a1a1aa' : '#52525b', fontSize: '11px', fontWeight: '700',
    cursor: 'pointer', transition: 'all 0.2s',
    textTransform: 'uppercase', letterSpacing: '0.5px'
  },

  // --- MESSAGES ---
  messagesArea: {
    flex: 1, padding: 'clamp(12px, 2.4vw, 24px)', overflowY: 'auto',
    display: 'flex', flexDirection: 'column', gap: '16px'
  },
  messageRow: { display: 'flex', width: '100%', alignItems: 'flex-end' },
  rowUser: { justifyContent: 'flex-end' },
  rowBot: { justifyContent: 'flex-start' },

  bubble: {
    maxWidth: 'min(75%, 780px)', padding: 'clamp(10px, 2vw, 14px) clamp(12px, 2.5vw, 20px)', borderRadius: '18px',
    fontSize: 'clamp(13px, 1.7vw, 14px)', lineHeight: '1.7', position: 'relative',
    wordBreak: 'break-word', whiteSpace: 'pre-wrap'
  },
  bubbleUser: {
    background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    color: '#fff', borderRadius: '18px 18px 4px 18px',
    boxShadow: '0 4px 20px rgba(99, 102, 241, 0.25)'
  },
  bubbleBot: {
    background: isDark ? 'rgba(39,39,42,0.90)' : 'rgba(242,242,252,0.96)',
    color: isDark ? '#e4e4e7' : '#18181b',
    border: isDark ? '1px solid rgba(255,255,255,0.06)' : '1px solid rgba(0,0,0,0.06)',
    borderRadius: '18px 18px 18px 4px',
    boxShadow: isDark ? '0 2px 10px rgba(0,0,0,0.15)' : '0 2px 10px rgba(0,0,0,0.06)'
  },
  botAvatarSmall: {
    width: '32px', height: '32px', borderRadius: '10px',
    background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    marginRight: '10px', fontSize: '16px', flexShrink: 0,
    boxShadow: '0 0 12px rgba(99, 102, 241, 0.3)'
  },
  messageTime: {
    fontSize: '10px', color: '#71717a', marginTop: '6px',
    paddingLeft: '4px'
  },

  // --- WELCOME SCREEN ---
  welcomeContainer: {
    flex: 1, display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    padding: 'clamp(16px, 4vw, 40px)', textAlign: 'center', gap: 'clamp(14px, 3vw, 24px)'
  },
  welcomeIcon: {
    width: '80px', height: '80px', borderRadius: '24px',
    background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '40px', boxShadow: '0 0 40px rgba(99, 102, 241, 0.3)',
    animation: 'floatBounce 3s ease-in-out infinite'
  },
  welcomeTitle: {
    fontSize: '24px', fontWeight: '800', color: isDark ? '#fff' : '#18181b',
    letterSpacing: '-0.5px'
  },
  welcomeSub: {
    fontSize: 'clamp(13px, 1.8vw, 14px)', color: isDark ? '#a1a1aa' : '#52525b', maxWidth: 'min(100%, 400px)',
    lineHeight: '1.6'
  },
  suggestionsGrid: {
    display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '10px', width: '100%', maxWidth: 'min(100%, 500px)', marginTop: '8px'
  },
  suggestionChip: {
    padding: '12px 16px', borderRadius: '14px',
    background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(99,102,241,0.06)',
    border: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(99,102,241,0.12)',
    color: isDark ? '#d4d4d8' : '#3f3f46', fontSize: '13px', fontWeight: '500',
    cursor: 'pointer', transition: 'all 0.25s ease',
    textAlign: 'left', lineHeight: '1.4',
    display: 'flex', alignItems: 'center', gap: '8px'
  },

  // --- INPUT AREA ---
  inputArea: {
    padding: 'clamp(10px, 2vw, 16px) clamp(10px, 2.4vw, 20px)',
    background: isDark ? 'rgba(24,24,27,0.80)' : 'rgba(248,248,254,0.90)',
    backdropFilter: 'blur(10px)',
    borderTop: isDark ? '1px solid rgba(255,255,255,0.06)' : '1px solid rgba(0,0,0,0.06)',
    display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap'
  },
  inputWrapper: {
    flex: 1, position: 'relative'
  },
  input: {
    width: '100%', padding: '14px 20px', borderRadius: '16px',
    background: isDark ? 'rgba(9,9,11,0.85)' : 'rgba(240,240,252,0.92)',
    border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.10)',
    color: isDark ? '#fff' : '#18181b', fontSize: '14px', fontFamily: 'inherit',
    outline: 'none', transition: 'all 0.2s', resize: 'none',
    minHeight: '48px', maxHeight: '120px', lineHeight: '1.5'
  },
  charCount: {
    position: 'absolute', right: '12px', bottom: '4px',
    fontSize: '10px', color: '#52525b', fontWeight: '600'
  },
  sendBtn: {
    width: 'clamp(42px, 7vw, 48px)', height: 'clamp(42px, 7vw, 48px)', borderRadius: '14px',
    background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    border: 'none',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    cursor: 'pointer', fontSize: '18px', color: '#fff',
    transition: 'all 0.2s',
    boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)',
    flexShrink: 0
  },
  sendBtnDisabled: {
    opacity: 0.4, cursor: 'not-allowed',
    boxShadow: 'none'
  },

  // --- ERROR BANNER ---
  errorBanner: {
    display: 'flex', alignItems: 'center', gap: '8px',
    padding: '10px 16px', margin: '0 clamp(10px, 2.4vw, 20px) 12px',
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    borderRadius: '12px', fontSize: '12px', color: '#fca5a5'
  }
});

// ===== QUICK SUGGESTION CHIPS =====
const SUGGESTIONS = [
  { icon: '💪', text: 'Suggest a workout for today' },
  { icon: '🥗', text: 'What should I eat today?' },
  { icon: '📈', text: 'How can I improve my form?' },
  { icon: '😴', text: 'Tips for better recovery' },
];

const MAX_INPUT_LENGTH = 2000;

// ===== SIMPLE MARKDOWN RENDERER =====
function renderMarkdown(text) {
  if (!text) return text;

  // Split into lines and process
  const lines = text.split('\n');
  const elements = [];
  let inList = false;
  let listItems = [];

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} style={{ margin: '8px 0', paddingLeft: '20px' }}>
          {listItems.map((item, i) => (
            <li key={i} style={{ marginBottom: '4px' }}>{processInline(item)}</li>
          ))}
        </ul>
      );
      listItems = [];
    }
    inList = false;
  };

  const processInline = (line) => {
    // Bold
    let parts = line.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, i) =>
      i % 2 === 1 ? <strong key={i}>{part}</strong> : part
    );
  };

  lines.forEach((line, i) => {
    const trimmed = line.trim();

    // Bullet list
    if (/^[-*•]\s/.test(trimmed)) {
      inList = true;
      listItems.push(trimmed.replace(/^[-*•]\s/, ''));
      return;
    }

    // Numbered list
    if (/^\d+[.)]\s/.test(trimmed)) {
      inList = true;
      listItems.push(trimmed.replace(/^\d+[.)]\s/, ''));
      return;
    }

    // End of list
    if (inList) flushList();

    // Empty line
    if (!trimmed) {
      elements.push(<br key={`br-${i}`} />);
      return;
    }

    // Heading-like (### or **)
    if (/^#{1,3}\s/.test(trimmed)) {
      elements.push(
        <div key={i} style={{ fontWeight: '700', fontSize: '15px', marginTop: '8px', marginBottom: '4px', color: 'inherit' }}>
          {processInline(trimmed.replace(/^#{1,3}\s/, ''))}
        </div>
      );
      return;
    }

    // Normal paragraph
    elements.push(
      <div key={i} style={{ marginBottom: '2px' }}>
        {processInline(trimmed)}
      </div>
    );
  });

  // Flush any remaining list
  flushList();

  return elements;
}


// ===== TYPING INDICATOR =====
function TypingIndicator({ styles }) {
  return (
    <div style={{ ...styles.messageRow, ...styles.rowBot }}>
      <div style={styles.botAvatarSmall}>🧠</div>
      <div style={{
        ...styles.bubble, ...styles.bubbleBot,
        padding: '12px 20px',
        display: 'flex', alignItems: 'center', gap: '6px'
      }}>
        <div className="typing-container">
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
        </div>
        <span style={{ fontSize: '12px', color: '#71717a', marginLeft: '8px' }}>Thinking...</span>
      </div>
    </div>
  );
}


// ===== MAIN COMPONENT =====
function Chatbot() {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const styles = getStyles(isDark);
  const [confirmDialog, setConfirmDialog] = useState({ show: false, message: '', onConfirm: null });
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [profile, setProfile] = useState({});
  const [error, setError] = useState(null);
  const [cooldown, setCooldown] = useState(false);
  
  // Bug #5 & #6 Fix: AI connection status tracking
  const [aiStatus, setAiStatus] = useState('checking'); // 'checking' → 'online' | 'offline'
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const cooldownTimerRef = useRef(null);

  const todayDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  // Load profile on mount
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await getProfile();
        setProfile(res.data || {});
      } catch {
        console.log('Could not load profile for chatbot context');
      }
    };
    loadProfile();

    // Load saved chat from sessionStorage (persists within tab)
    const savedChat = sessionStorage.getItem('elevate_chat');
    if (savedChat) {
      try {
        const parsed = JSON.parse(savedChat);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed);
        }
      } catch { /* ignore */ }
    }

    return () => {
      if (cooldownTimerRef.current) clearTimeout(cooldownTimerRef.current);
    };
  }, []);

  // Save chat to sessionStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      sessionStorage.setItem('elevate_chat', JSON.stringify(messages));
    }
  }, [messages]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Clear error after 5s
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);


  const sendMessage = useCallback(async (text) => {
    const trimmed = (text || '').trim();
    if (!trimmed || isTyping || cooldown) return;

    // Clear any previous error
    setError(null);

    // Add user message
    const userMsg = {
      role: 'user',
      text: trimmed,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput('');
    setIsTyping(true);

    // Cooldown to prevent spam
    setCooldown(true);
    cooldownTimerRef.current = setTimeout(() => setCooldown(false), 1500);

    try {
      const chatResponse = await sendChatbotMessage(trimmed, profile, updatedMessages);

      const replyText = chatResponse.data?.reply || chatResponse.data?.message || "I couldn't generate a response. Please try again.";
      
      // Bug #5 & #6 Fix: Detect if response is from AI or offline mode
      const isOffline = chatResponse.data?.offline_mode || 
                        replyText.includes('offline mode') ||
                        replyText.includes('AI service temporarily unavailable');
      
      if (isOffline) {
        setAiStatus('offline');
      } else {
        setAiStatus('online');
      }

      const botMsg = {
        role: 'bot',
        text: replyText,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error('Chat error:', err);

      let errorMsg = "I'm having trouble connecting right now. Please check that the Python backend is running.";

      if (err.response?.status === 429) {
        errorMsg = "You're sending messages too fast! Please wait a moment. 😅";
      } else if (err.code === 'ERR_NETWORK' || err.code === 'ECONNREFUSED') {
        errorMsg = "Can't reach the AI server. Make sure the Python backend (port 8000) is running.";
        setError('Connection failed — is the Python backend running on port 8000?');
      }

      setMessages(prev => [...prev, {
        role: 'bot',
        text: errorMsg,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        isError: true
      }]);
    } finally {
      setIsTyping(false);
      // Focus input after response
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [messages, profile, isTyping, cooldown]);


  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const clearChat = () => {
    setMessages([]);
    sessionStorage.removeItem('elevate_chat');
    setError(null);
  };

  const handleLogout = () => {
    setConfirmDialog({
      show: true,
      message: 'Log out?',
      onConfirm: (confirmed) => {
        if (confirmed) {
          logoutSafe();
          navigate('/');
        }
        setConfirmDialog({ show: false, message: '', onConfirm: null });
      }
    });
  };

  const showWelcome = messages.length === 0;

  return (
    <>
      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        @keyframes floatBounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

        .typing-container { display: flex; gap: 4px; align-items: center; }
        .typing-dot {
          width: 7px; height: 7px; border-radius: 50%;
          background: #6366f1; opacity: 0.4;
          animation: typingBounce 1.4s infinite both;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce {
          0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1.1); }
        }

        .chat-input:focus {
          border-color: #6366f1 !important;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        }
        .chat-input::placeholder { color: #52525b; }

        .suggestion-chip:hover {
          background: rgba(99, 102, 241, 0.1) !important;
          border-color: rgba(99, 102, 241, 0.3) !important;
          color: #c7d2fe !important;
          transform: translateY(-1px);
        }

        .clear-btn:hover {
          background: rgba(239, 68, 68, 0.1) !important;
          border-color: rgba(239, 68, 68, 0.2) !important;
          color: #ef4444 !important;
        }

        .send-active:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
        }
        .send-active:active:not(:disabled) {
          transform: translateY(0);
        }

        .nav-link-hover:hover {
          background: rgba(255,255,255,0.06) !important;
          color: #e4e4e7 !important;
        }

        /* Messages area scrollbar */
        .chat-messages::-webkit-scrollbar { width: 5px; }
        .chat-messages::-webkit-scrollbar-track { background: transparent; }
        .chat-messages::-webkit-scrollbar-thumb { background: #27272a; border-radius: 10px; }
        .chat-messages::-webkit-scrollbar-thumb:hover { background: #3f3f46; }

        /* Mobile responsive */
        @media (max-width: 640px) {
          .nav-center-hide { display: none !important; }
          .chat-container { padding: 10px !important; }
          .chat-header { padding: 12px 16px !important; }
          .messages-area { padding: 16px !important; }
          .input-area { padding: 12px !important; }
          .suggestion-grid { grid-template-columns: 1fr !important; }
          .bubble-msg { max-width: 85% !important; }
          .navbar-pad { padding: 0 16px !important; }
        }
      `}</style>

      <div style={styles.page}>
        {/* NAVBAR */}
        <nav style={styles.navbar} className="navbar-pad">
          <div style={styles.brand}><div style={styles.brandDot}></div> ELEVATE</div>
          <div style={styles.navCenter} className="nav-center-hide">
            <div style={styles.navLink} className="nav-link-hover" onClick={() => navigate('/dashboard')}>Dashboard</div>
            <div style={styles.navLink} className="nav-link-hover" onClick={() => navigate('/workout')}>Workout</div>
            <div style={styles.navLink} className="nav-link-hover" onClick={() => navigate('/nutrition')}>Nutrition</div>
            <div style={{ ...styles.navLink, ...styles.navLinkActive }}>AI Coach</div>
          </div>
          <div style={styles.navRight}>
            <div style={styles.dateDisplay}>{todayDate}</div>
            <button style={styles.logoutBtn} onClick={handleLogout}>LOGOUT</button>
          </div>
        </nav>

        {/* CHAT CONTAINER */}
        <div style={styles.container} className="chat-container">
          <div style={styles.chatWindow}>

            {/* CHAT HEADER */}
            <div style={styles.chatHeader} className="chat-header">
              <div style={styles.chatHeaderLeft}>
                <div style={styles.chatHeaderAvatar}>🧠</div>
                <div style={styles.chatHeaderInfo}>
                  <div style={styles.chatHeaderName}>Elevate AI Coach</div>
                  <div style={styles.chatHeaderStatus}>
                    {/* Bug #5 & #6 Fix: Dynamic AI status indicator */}
                    <span style={{
                      ...styles.statusDot,
                      backgroundColor: aiStatus === 'online' ? '#4ade80' : 
                                       aiStatus === 'offline' ? '#fbbf24' : '#9ca3af'
                    }}></span>
                    {aiStatus === 'online' ? 'Online • AI Powered' : 
                     aiStatus === 'offline' ? 'Offline Mode • Smart Responses' :
                     'Checking connection...'}
                  </div>
                </div>
              </div>
              {messages.length > 0 && (
                <button
                  style={styles.clearBtn}
                  className="clear-btn"
                  onClick={clearChat}
                  title="Clear conversation"
                >
                  🗑️ Clear
                </button>
              )}
            </div>

            {/* ERROR BANNER */}
            {error && (
              <div style={styles.errorBanner}>
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}

            {/* MESSAGES / WELCOME */}
            {showWelcome ? (
              <div style={styles.welcomeContainer}>
                <div style={styles.welcomeIcon}>🧠</div>
                <div style={styles.welcomeTitle}>Your AI Fitness Coach</div>
                <div style={styles.welcomeSub}>
                  Ask me about workouts, nutrition, form tips, recovery, or anything fitness-related.
                  I know your profile and goals — let's get to work!
                </div>
                <div style={styles.suggestionsGrid} className="suggestion-grid">
                  {SUGGESTIONS.map((s, i) => (
                    <button
                      key={i}
                      style={styles.suggestionChip}
                      className="suggestion-chip"
                      onClick={() => sendMessage(s.text)}
                      disabled={isTyping}
                    >
                      <span>{s.icon}</span>
                      <span>{s.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div style={styles.messagesArea} className="chat-messages messages-area">
                {messages.map((msg, i) => (
                  <div key={i}>
                    <div style={{
                      ...styles.messageRow,
                      ...(msg.role === 'user' ? styles.rowUser : styles.rowBot)
                    }}>
                      {msg.role === 'bot' && (
                        <div style={styles.botAvatarSmall}>🧠</div>
                      )}
                      <div
                        className="bubble-msg"
                        style={{
                          ...styles.bubble,
                          ...(msg.role === 'user' ? styles.bubbleUser : styles.bubbleBot),
                          ...(msg.isError ? { borderColor: 'rgba(239, 68, 68, 0.3)' } : {})
                        }}
                      >
                        {msg.role === 'bot' ? renderMarkdown(msg.text) : msg.text}
                      </div>
                    </div>
                    {msg.time && (
                      <div style={{
                        ...styles.messageTime,
                        textAlign: msg.role === 'user' ? 'right' : 'left',
                        paddingLeft: msg.role === 'bot' ? '44px' : '0'
                      }}>
                        {msg.time}
                      </div>
                    )}
                  </div>
                ))}

                {isTyping && <TypingIndicator styles={styles} />}
                <div ref={messagesEndRef} />
              </div>
            )}

            {/* INPUT AREA */}
            <form style={styles.inputArea} className="input-area" onSubmit={handleSubmit}>
              <div style={styles.inputWrapper}>
                <textarea
                  ref={inputRef}
                  className="chat-input"
                  style={styles.input}
                  placeholder="Ask about workouts, nutrition, form..."
                  value={input}
                  onChange={(e) => {
                    if (e.target.value.length <= MAX_INPUT_LENGTH) {
                      setInput(e.target.value);
                    }
                  }}
                  onKeyDown={handleKeyDown}
                  rows={1}
                  disabled={isTyping}
                />
                {input.length > 200 && (
                  <div style={{
                    ...styles.charCount,
                    color: input.length > MAX_INPUT_LENGTH - 100 ? '#ef4444' : '#52525b'
                  }}>
                    {input.length}/{MAX_INPUT_LENGTH}
                  </div>
                )}
              </div>
              <button
                type="submit"
                className="send-active"
                style={{
                  ...styles.sendBtn,
                  ...((isTyping || !input.trim() || cooldown) ? styles.sendBtnDisabled : {})
                }}
                disabled={isTyping || !input.trim() || cooldown}
              >
                ➤
              </button>
            </form>

          </div>
        </div>
      </div>

      <ConfirmDialog
        show={confirmDialog.show}
        message={confirmDialog.message}
        onConfirm={() => {
          if (confirmDialog.onConfirm) confirmDialog.onConfirm(true);
        }}
        onCancel={() => {
          if (confirmDialog.onConfirm) confirmDialog.onConfirm(false);
        }}
      />
    </>
  );
}

export default Chatbot;