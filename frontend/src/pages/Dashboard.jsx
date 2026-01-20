import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { QUOTES } from '../data/quotes';

// --- FULL PREMIUM STYLES ---
const styles = {
  page: {
    background: '#09090b',
    minHeight: '100vh',
    color: '#e4e4e7',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    backgroundImage: `
      radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%), 
      radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.08), transparent 25%)
    `,
    paddingBottom: '40px'
  },
  dateDisplay: { 
    fontSize: '13px', fontWeight: '600', 
    color: '#a1a1aa', fontFamily: 'sans-serif', 
    letterSpacing: '0.5px', marginRight: '8px' 
  },
  navbar: {
    display: 'flex', alignItems: 'center', 
    padding: '0 40px', height: '80px',
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    background: 'rgba(9, 9, 11, 0.6)', backdropFilter: 'blur(16px)',
    position: 'sticky', top: 0, zIndex: 1000
  },
  brand: { 
    flex: 1, // <--- FORCE EQUAL WIDTH
    fontSize: '22px', fontWeight: '900', letterSpacing: '-1px', 
    background: 'linear-gradient(to right, #fff, #a5b4fc)', 
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', 
    display: 'flex', alignItems: 'center', gap: '10px' 
  },
  navCenter: { 
    display: 'flex', gap: '8px', height: '100%', alignItems: 'center',
    justifyContent: 'center' // <--- CENTER CONTENT
  },
  navLink: {
    display: 'flex', alignItems: 'center', padding: '8px 20px',
    fontSize: '13px', fontWeight: '600', color: '#a1a1aa',
    cursor: 'pointer', borderRadius: '20px', transition: 'all 0.2s',
    textTransform: 'uppercase', letterSpacing: '0.5px',
    border: '1px solid transparent' // <--- PREVENTS JUMPING
  },
  navLinkActive: { 
    background: 'rgba(255,255,255,0.1)', color: '#fff', 
    boxShadow: '0 0 20px rgba(255,255,255,0.05)', 
    border: '1px solid rgba(255,255,255,0.05)' 
  },
  navRight: { 
    flex: 1, // <--- FORCE EQUAL WIDTH
    display: 'flex', alignItems: 'center', gap: '24px', 
    justifyContent: 'flex-end' // <--- PUSH CONTENT TO RIGHT
  },
  iconButton: {
    width: '42px', height: '42px', borderRadius: '12px',
    background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', 
    color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', 
    cursor: 'pointer', fontSize: '18px', transition: 'all 0.2s', position: 'relative'
  },
  notifDropdown: {
    position: 'absolute', top: '60px', right: '0px',
    width: '340px', background: '#18181b', border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '16px', padding: '16px', zIndex: 2000,
    boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
    animation: 'slideDown 0.2s ease-out'
  },
  notifItem: { 
    padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)', 
    fontSize: '13px', color: '#d4d4d8', display: 'flex', gap: '10px', alignItems: 'center' 
  },
  logoutBtn: {
    display: 'flex', alignItems: 'center', gap: '8px',
    padding: '0 20px', borderRadius: '12px',
    background: 'rgba(239, 68, 68, 0.1)', 
    border: '1px solid rgba(239, 68, 68, 0.2)',
    color: '#ef4444', cursor: 'pointer', transition: 'all 0.2s ease',
    height: '42px'
  },
  logoutText: { fontSize: '12px', fontWeight: '700', letterSpacing: '0.5px', textTransform: 'uppercase' },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  container: { 
    maxWidth: '1600px', margin: '0 auto', padding: '40px', 
    display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' 
  },
  bentoBox: {
    background: '#18181b', border: '1px solid rgba(255,255,255,0.05)',
    borderRadius: '24px', padding: '32px',
    display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden',
    transition: 'transform 0.2s ease, border-color 0.2s ease',
  },
  heroSection: { 
    gridColumn: 'span 12', 
    background: 'linear-gradient(120deg, #18181b 0%, #0f0f11 100%)',
    display: 'flex', flexDirection: 'row', alignItems: 'center',
    justifyContent: 'space-between', gap: '40px', minHeight: '360px',
    padding: '48px',
    boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
  },
  heroLeft: { display: 'flex', alignItems: 'flex-start', gap: '32px', flex: 1.2, minWidth: '400px' },
  avatarWrapper: { position: 'relative', width: '160px', height: '160px', flexShrink: 0, cursor: 'pointer' },
  avatarContainer: {
    width: '100%', height: '100%', 
    borderRadius: '50%',
    background: 'conic-gradient(from 0deg, #6366f1, #ec4899, #6366f1)',
    padding: '4px', boxShadow: '0 10px 50px rgba(99, 102, 241, 0.3)',
    transition: 'transform 0.2s'
  },
  avatarImage: {
    width: '100%', height: '100%', borderRadius: '50%',
    background: '#18181b', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '64px', fontWeight: '700', color: '#fff', objectFit: 'cover'
  },
  editIconBadge: {
    position: 'absolute', bottom: '5px', right: '5px',
    width: '40px', height: '40px', borderRadius: '50%',
    background: '#4f46e5', border: '4px solid #18181b',
    color: '#fff', fontSize: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: '0 4px 20px rgba(0,0,0,0.6)', zIndex: 10,
    transition: 'all 0.2s ease'
  },
  heroTextContent: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '12px', paddingTop: '15px' },
  h1: { 
    fontSize: '52px', fontWeight: '800', 
    background: 'linear-gradient(to right, #ffffff 0%, #a5b4fc 100%)', 
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
    margin: 0, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '10px',
    filter: 'drop-shadow(0 4px 20px rgba(99, 102, 241, 0.3))',
    lineHeight: '1.1'
  },
  quoteCard: {
    background: 'rgba(255,255,255,0.03)', borderLeft: '4px solid #6366f1',
    padding: '16px 24px', borderRadius: '0 12px 12px 0',
    fontStyle: 'italic', color: '#a1a1aa', fontSize: '15px', lineHeight: '1.6',
    marginTop: '8px', maxWidth: '450px' 
  },
  heroCenter: { flex: 0.8, display: 'flex', justifyContent: 'center', alignItems: 'center' },
  circleBtn: {
    width: '200px', height: '200px', borderRadius: '50%',
    border: 'none', cursor: 'pointer',
    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
    gap: '8px', color: '#fff',
    transition: 'all 0.3s ease',
    textShadow: '0 2px 10px rgba(0,0,0,0.3)',
    position: 'relative',
    zIndex: 10
  },
  btnBlue: { background: 'linear-gradient(135deg, #4f46e5 0%, #312e81 100%)' },
  btnPink: { background: 'linear-gradient(135deg, #ec4899 0%, #be185d 100%)' },
  btnGreen: { background: 'linear-gradient(135deg, #22c55e 0%, #14532d 100%)' },
  heroRight: { display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center', gap: '20px', flex: 1 },
  streakLabel: { fontSize: '13px', fontWeight: '700', color: '#a1a1aa', letterSpacing: '3px', textTransform: 'uppercase' },
  streakNumber: {
    fontSize: '90px', fontWeight: '900', lineHeight: 0.8,
    background: 'linear-gradient(to bottom, #fff 30%, #6366f1 100%)',
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
    filter: 'drop-shadow(0 0 30px rgba(99,102,241,0.3))'
  },
  weekGrid: { display: 'flex', gap: '10px' },
  dayCircle: {
    width: '46px', height: '46px', borderRadius: '14px',
    background: '#27272a', display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '16px', border: '1px solid rgba(255,255,255,0.05)', 
    transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)', cursor: 'default',
    fontWeight: '700', color: '#71717a'
  },
  dayActive: { background: 'rgba(99, 102, 241, 0.1)', borderColor: '#6366f1', boxShadow: '0 0 15px rgba(99, 102, 241, 0.2)', color: '#fff' },
  dayDone: { background: 'rgba(34, 197, 94, 0.1)', borderColor: '#22c55e', color: '#fff', boxShadow: '0 0 15px rgba(34, 197, 94, 0.2)' },
  
  statsRow: { gridColumn: 'span 12', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' },
  
  // --- MACRO BAR STYLES ---
  macroBarBG: { width: '100%', height: '8px', background: '#27272a', borderRadius: '10px', marginTop: '8px', overflow: 'hidden' },
  macroBarFill: { height: '100%', borderRadius: '10px', transition: 'width 0.5s ease' },

  // --- GLASS CONTROL ---
  glassPill: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    background: 'rgba(255,255,255,0.03)', borderRadius: '50px',
    padding: '4px', marginTop: '20px',
    border: '1px solid rgba(255,255,255,0.08)',
    boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.3)', width: '100%', maxWidth: '280px'
  },
  glassBtn: {
    width: '40px', height: '40px', borderRadius: '50%',
    background: 'transparent', border: 'none', 
    color: '#fff', fontSize: '20px', cursor: 'pointer',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    transition: 'all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1)',
  },
  glassText: { fontSize: '12px', fontWeight: '700', color: '#a1a1aa', letterSpacing: '1px', textTransform: 'uppercase' },

  chartSection: { gridColumn: 'span 8', height: '550px' },
  activitySection: { gridColumn: 'span 4', height: '550px', display: 'flex', flexDirection: 'column' },
  sectionHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }, 
  sectionTitle: { fontSize: '22px', fontWeight: '800', color: '#fff', display: 'flex', alignItems: 'center', gap: '12px', letterSpacing: '-0.5px' },
  sectionAccent: { width: '4px', height: '24px', background: '#6366f1', borderRadius: '4px' }, 
  chartControls: { display: 'flex', gap: '16px' },
  chartTabs: { display: 'flex', gap: '4px', background: 'rgba(255,255,255,0.05)', padding: '4px', borderRadius: '10px' },
  chartTab: { padding: '6px 14px', borderRadius: '8px', fontSize: '11px', fontWeight: '700', cursor: 'pointer', transition: 'all 0.2s', border: 'none', color: '#71717a', background: 'transparent' },
  chartTabActive: { background: '#27272a', color: '#fff', boxShadow: '0 2px 10px rgba(0,0,0,0.2)' },
  listRow: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)', borderRadius: '16px', marginBottom: '8px', cursor: 'pointer', background: 'transparent' },
  modalOverlay: { position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0, 0, 0, 0.85)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10000, animation: 'fadeIn 0.3s ease' },
  modalContent: { position: 'relative', maxWidth: '500px', width: '90%', background: '#18181b', borderRadius: '24px', padding: '10px', boxShadow: '0 25px 50px rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.1)' },
  modalImage: { width: '100%', borderRadius: '16px', display: 'block' },
  closeModalBtn: { position: 'absolute', top: '-15px', right: '-15px', width: '32px', height: '32px', borderRadius: '50%', background: '#fff', color: '#000', border: 'none', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 10px rgba(0,0,0,0.3)' }
};

// --- CHART ---
const ActivityChart = ({ data, mode, period }) => {
    const [hoveredPoint, setHoveredPoint] = useState(null);
    if (!data || data.length === 0) return null;
    const width = 1000; const height = 300; const padding = { top: 10, right: 30, bottom: 40, left: 60 };
    const chartWidth = width - padding.left - padding.right; const chartHeight = height - padding.top - padding.bottom;
    let yMax = Math.max(...data) * 1.2; let yMin = 0; let unit = ''; let steps = 4;
    if (mode === 'water') { unit = ' L'; yMax = 4; } if (mode === 'sleep') { unit = ' h'; yMax = 12; } if (mode === 'meal') { unit = ''; yMax = 3000; } if (mode === 'workout') { unit = ' min'; yMax = 120; }
    const yRange = yMax - yMin; const stepX = chartWidth / (data.length - 1);
    const getPoint = (i) => { const x = padding.left + (i * stepX); const y = padding.top + chartHeight - ((data[i] - yMin) / yRange) * chartHeight; return [x, y]; };
    const [startX, startY] = getPoint(0); let d = `M ${startX} ${startY}`;
    for (let i = 0; i < data.length - 1; i++) { const [x0, y0] = getPoint(Math.max(i - 1, 0)); const [x1, y1] = getPoint(i); const [x2, y2] = getPoint(i + 1); const [x3, y3] = getPoint(Math.min(i + 2, data.length - 1)); const cp1x = x1 + (x2 - x0) / 6; const cp1y = y1 + (y2 - y0) / 6; const cp2x = x2 - (x3 - x1) / 6; const cp2y = y2 - (y3 - y1) / 6; d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${x2} ${y2}`; }
    const areaPath = `${d} L ${padding.left + chartWidth} ${padding.top + chartHeight} L ${padding.left} ${padding.top + chartHeight} Z`;
    const yLabels = []; for (let i = 0; i <= steps; i++) { const val = yMin + (yRange / steps) * i; const labelVal = mode === 'water' || mode === 'sleep' ? val.toFixed(1) : Math.round(val); yLabels.push({ y: padding.top + chartHeight - (i * (chartHeight / steps)), val: labelVal }); }
    const xLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const todayDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    return (
        <div style={{flex: 1, position: 'relative', width: '100%', cursor: 'crosshair', overflow: 'hidden'}}>
            <svg key={mode} viewBox={`0 0 ${width} ${height}`} style={{width: '100%', height: '100%', overflow: 'visible', animation: 'fadeIn 0.6s ease'}}>
                <defs><linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#818cf8" stopOpacity="0.5" /><stop offset="100%" stopColor="#818cf8" stopOpacity="0" /></linearGradient></defs>
                {yLabels.map((label, i) => (<g key={i}><line x1={padding.left} y1={label.y} x2={width - padding.right} y2={label.y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" /><text x={padding.left - 15} y={label.y + 4} textAnchor="end" fill="#a1a1aa" fontSize="12" fontFamily="'Inter', sans-serif" fontWeight="500">{label.val}{unit}</text></g>))}
                {period === 'week' && xLabels.map((day, i) => { const xPos = padding.left + (i * stepX); return <text key={i} x={xPos} y={height - 10} textAnchor="middle" fill="#a1a1aa" fontSize="12" fontFamily="'Inter', sans-serif" fontWeight="500">{day}</text>; })}
                <path d={areaPath} fill="url(#chartGradient)" /> <path d={d} fill="none" stroke="#818cf8" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                {data.map((val, i) => { const [cx, cy] = getPoint(i); return (<g key={i} onMouseEnter={() => setHoveredPoint(i)} onMouseLeave={() => setHoveredPoint(null)}><rect x={cx - stepX/2} y={padding.top} width={stepX} height={chartHeight} fill="transparent" /><circle cx={cx} cy={cy} r={hoveredPoint === i ? "6" : "0"} fill="#09090b" stroke="#fff" strokeWidth="2" style={{transition: 'all 0.15s ease-out', filter: 'drop-shadow(0 0 6px rgba(255,255,255,0.8))'}} /></g>); })}
            </svg>
            <div style={{position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', pointerEvents: 'none', opacity: hoveredPoint !== null ? 1 : 0, transition: 'opacity 0.2s ease'}}>
                {hoveredPoint !== null && (() => { const [cx, cy] = getPoint(hoveredPoint); const val = mode === 'water' || mode === 'sleep' ? data[hoveredPoint].toFixed(1) : Math.round(data[hoveredPoint]); return (<div style={{position: 'absolute', left: `${(cx / width) * 100}%`, top: `${(cy / height) * 100}%`, transform: 'translate(-50%, -130%)', transition: 'left 0.1s linear, top 0.1s linear', background: 'rgba(24, 24, 27, 0.95)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px', padding: '8px 16px', boxShadow: '0 4px 20px rgba(0,0,0,0.5)', textAlign: 'center', minWidth: '70px', backdropFilter: 'blur(8px)'}}><div style={{fontSize:'10px', color:'#a1a1aa', textTransform:'uppercase', letterSpacing:'1px', marginBottom:'2px'}}>{mode}</div><div style={{fontSize:'16px', fontWeight:'700', color:'#fff', fontFamily:'sans-serif'}}>{val}<span style={{fontSize:'12px', color:'#818cf8', marginLeft:'2px'}}>{unit}</span></div><div style={{position:'absolute', bottom:'-5px', left:'50%', transform:'translateX(-50%) rotate(45deg)', width:'10px', height:'10px', background:'rgba(24,24,27,0.95)', borderRight:'1px solid rgba(255,255,255,0.15)', borderBottom:'1px solid rgba(255,255,255,0.15)'}}></div></div>); })()}
            </div>
        </div>
    );
};

const DEFAULT_HISTORY = [
    { name: "Welcome to Elevate", date: "Just now", details: "Start tracking!", type: "workout" }
];

function Dashboard() {
  const [displayName, setDisplayName] = useState('Titan');
  const [userAvatar, setUserAvatar] = useState(null);
  const [showImageModal, setShowImageModal] = useState(false);
  const [showNotif, setShowNotif] = useState(false);
  const notifRef = useRef(null);

  const [stats, setStats] = useState({ workoutCount: 0, mealCount: 0, streak: 12, focusScore: 60 });
  
  // --- ADDED DUMMY DATA FOR MACROS ---
  const [macros, setMacros] = useState({ p: 120, c: 180, f: 55, pMax: 180, cMax: 250, fMax: 70, calories: 1850, calMax: 2500, fiber: 25 });
  
  const [water, setWater] = useState(1.2);
  const [sleep, setSleep] = useState(7.0);
  const [status, setStatus] = useState("workout");
  const [chartMode, setChartMode] = useState('workout'); 
  const [chartPeriod, setChartPeriod] = useState('week'); 
  const [chartData, setChartData] = useState([30, 45, 25, 60, 40, 75, 50]); 
  
  const [recentHistory, setRecentHistory] = useState(() => {
    const saved = localStorage.getItem('activityHistory');
    if (saved && saved !== '[]') {
        try { return JSON.parse(saved); } catch(e) { return DEFAULT_HISTORY; }
    }
    localStorage.setItem('activityHistory', JSON.stringify(DEFAULT_HISTORY));
    return DEFAULT_HISTORY;
  });

  const [weeklyProgress, setWeeklyProgress] = useState([]);
  const navigate = useNavigate();
  const todayDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  const currentQuote = useMemo(() => { if (!QUOTES || QUOTES.length === 0) return "Stay hard."; const now = new Date(); const start = new Date(now.getFullYear(), 0, 0); const dayOfYear = Math.floor((now - start) / (1000 * 60 * 60 * 24)); const year = now.getFullYear(); const infiniteIndex = dayOfYear + (year * 365); return QUOTES[infiniteIndex % QUOTES.length]; }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotif(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const storedHistory = localStorage.getItem('activityHistory');
    let parsedHistory = [];
    if (storedHistory) { try { parsedHistory = JSON.parse(storedHistory); } catch (e) { parsedHistory = []; } }
    if (!parsedHistory || parsedHistory.length === 0) {
        const seed = [{ name: "Welcome to Elevate", date: "Just now", details: "Start tracking!", type: "workout" }];
        localStorage.setItem('activityHistory', JSON.stringify(seed));
        setRecentHistory(seed);
    } else {
        setRecentHistory(parsedHistory);
    }
    const fName = localStorage.getItem('firstName');
    if (fName && fName !== 'null') { setDisplayName(fName); } 
    else { const uName = localStorage.getItem('userName'); if (uName && uName !== 'null') { setDisplayName(uName.split(' ')[0]); } }
    const storedAvatar = localStorage.getItem('userAvatar'); if(storedAvatar) setUserAvatar(storedAvatar);
    checkDayReset();
    generateWeeklyData();
    updateChart(chartMode, chartPeriod);
  }, []); 

  const logActivity = (type, name, details) => {
    const newLog = { name: name, date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), details: details, type: type };
    setRecentHistory(prev => { const updated = [newLog, ...prev]; localStorage.setItem('activityHistory', JSON.stringify(updated)); return updated; });
  };

  const removeLastLog = (type) => {
    setRecentHistory(prev => {
        const index = prev.findIndex(item => item.type === type);
        if (index !== -1) {
            const newHistory = [...prev];
            newHistory.splice(index, 1); 
            localStorage.setItem('activityHistory', JSON.stringify(newHistory));
            return newHistory;
        }
        return prev;
    });
  };

  useEffect(() => {
    let score = 50 + Math.min(sleep * 4, 32) + Math.min(water * 6, 18);
    if(score > 100) score = 100;
    setStats(prev => ({ ...prev, focusScore: Math.floor(score) }));
  }, [water, sleep]);

  useEffect(() => { updateChart(chartMode, chartPeriod); }, [chartMode, chartPeriod]);

  const handleWaterAdd = () => { setWater(water + 0.2); logActivity('water', 'Hydration', '+200ml Water'); };
  const handleWaterRemove = () => { if (water > 0) { setWater(Math.max(0, water - 0.2)); removeLastLog('water'); } };
  const handleSleepAdd = () => { setSleep(sleep + 0.5); logActivity('sleep', 'Sleep Update', 'Added 30 mins'); };
  const handleSleepRemove = () => { if (sleep > 0) { setSleep(Math.max(0, sleep - 0.5)); removeLastLog('sleep'); } };

  const handleLogout = () => { localStorage.clear(); navigate('/'); };
  const updateChart = (mode, period) => { setChartData([40, 50, 60, 40, 70, 80, 50]); };
  
  const checkDayReset = () => {
    const wDone = localStorage.getItem('todayWorkoutDone') === 'true';
    const mDone = localStorage.getItem('todayMealsDone') === 'true';
    if (!wDone) { setStatus('workout'); } 
    else if (wDone && !mDone) { setStatus('meal'); } 
    else { setStatus('done'); }
  };
  
  const handleAction = () => { if (status === 'workout') { navigate('/workout'); } else if (status === 'meal') { navigate('/nutrition'); } };
  const generateWeeklyData = () => { setWeeklyProgress(['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, index) => ({ day, status: index < 3 ? "done" : "pending" }))); };

  return (
    <div style={styles.page}>
      <style>{`
        * { box-sizing: border-box; }
        body { margin: 0; }
        .hover-card:hover { transform: translateY(-6px); border-color: rgba(255,255,255,0.15) !important; cursor: pointer; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .hover-scale:hover { transform: scale(1.05); }
        .nav-item:hover { color: #fff !important; }
        
        /* MACRO HOVER EFFECTS */
        .macro-item { transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1), filter 0.2s; }
        .macro-item:hover { transform: scale(1.05); filter: brightness(1.2); }
        
        @keyframes ring { 0% { transform: rotate(0); } 10% { transform: rotate(15deg); } 20% { transform: rotate(-15deg); } 30% { transform: rotate(10deg); } 40% { transform: rotate(-10deg); } 100% { transform: rotate(0); } }
        .icon-hover:hover { background: rgba(255,255,255,0.1) !important; animation: ring 1s ease; }
        @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }
        @keyframes pulse-blue-intense { 0% { box-shadow: 0 0 10px 0 rgba(79, 70, 229, 0.8); transform: scale(1.05); } 50% { box-shadow: 0 0 50px 15px rgba(79, 70, 229, 0.6); transform: scale(1.1); } 100% { box-shadow: 0 0 10px 0 rgba(79, 70, 229, 0.8); transform: scale(1.05); } }
        .btn-blue-pulse { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.7); animation: pulse-blue-intense 2s infinite; }
        .btn-blue-pulse:hover { animation-duration: 0.8s; }
        .btn-pink-pulse { box-shadow: 0 0 0 0 rgba(236, 72, 153, 0.7); animation: pulse-blue-intense 2s infinite; }
        .btn-pink-pulse:hover { animation-duration: 0.8s; box-shadow: 0 0 50px 15px rgba(236, 72, 153, 0.6); }
        .btn-green-pulse { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); animation: pulse-blue-intense 2s infinite; }
        .btn-green-pulse:hover { animation-duration: 0.8s; box-shadow: 0 0 50px 15px rgba(34, 197, 94, 0.6); }
        .day-item:hover { transform: scale(1.15); border-color: #6366f1 !important; box-shadow: 0 0 20px rgba(99, 102, 241, 0.4) !important; color: #fff; }
        .activity-list::-webkit-scrollbar { width: 6px; }
        .activity-list::-webkit-scrollbar-track { background: transparent; }
        .activity-list::-webkit-scrollbar-thumb { background: #27272a; border-radius: 4px; }
        .activity-row { border-left: 3px solid transparent; transition: all 0.2s ease; }
        .activity-row:hover { background: rgba(255, 255, 255, 0.08) !important; transform: translateX(10px); border-left: 3px solid #6366f1; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .edit-icon-hover:hover { transform: scale(1.15); background: #4338ca !important; box-shadow: 0 0 25px rgba(79, 70, 229, 0.8) !important; }
        .logout-btn:hover { background: rgba(239, 68, 68, 0.2) !important; transform: translateY(-2px); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2); }
        .control-btn-hover:hover { background: rgba(255,255,255,0.15) !important; transform: scale(1.1); }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>

      {showImageModal && userAvatar && (
        <div style={styles.modalOverlay} onClick={() => setShowImageModal(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeModalBtn} onClick={() => setShowImageModal(false)}>✕</button>
            <img src={userAvatar} alt="Full Profile" style={styles.modalImage} />
          </div>
        </div>
      )}

      <nav style={styles.navbar}>
        <div style={styles.brand}><div style={styles.brandDot}></div> ELEVATE</div>
        <div style={styles.navCenter}>
            <div style={{...styles.navLink, ...styles.navLinkActive}}>Dashboard</div>
            <div style={styles.navLink} onClick={() => navigate('/workout')}>Workout</div>
            <div style={styles.navLink} onClick={() => navigate('/nutrition')}>Nutrition</div>
            <div style={styles.navLink} onClick={() => navigate('/chatbot')}>ChatBot</div>
        </div>
        <div style={styles.navRight}>
            <div style={styles.dateDisplay}>{todayDate}</div>
            <div style={{position:'relative'}} ref={notifRef}>
              <button style={styles.iconButton} className="icon-hover" onClick={() => setShowNotif(!showNotif)}>🔔</button>
              {showNotif && (
                <div style={styles.notifDropdown}>
                  <div style={{fontSize:'14px', fontWeight:'700', color:'#fff', marginBottom:'12px'}}>Notifications</div>
                  <div style={styles.notifItem}>🔥 You're on a 12-day streak!</div>
                  <div style={styles.notifItem}>🥗 Don't forget to log lunch.</div>
                  <div style={{...styles.notifItem, borderBottom:'none', color:'#a1a1aa', fontSize:'12px', justifyContent:'center', marginTop:'8px'}}>No new alerts</div>
                </div>
              )}
            </div>
            <button style={styles.logoutBtn} className="logout-btn" onClick={handleLogout}>
                <span style={styles.logoutText}>LOGOUT</span>
            </button>
        </div>
      </nav>

      <div style={styles.container}>
        <div style={{...styles.bentoBox, ...styles.heroSection}}>
            <div style={styles.heroLeft}>
                <div style={styles.avatarWrapper} onClick={() => navigate('/profile-setup', { state: { isEditing: true } })}>
                    <div style={styles.avatarContainer}>
                        {userAvatar ? <img src={userAvatar} alt="Profile" style={styles.avatarImage} /> : <div style={styles.avatarImage}>{displayName ? displayName.charAt(0).toUpperCase() : 'T'}</div>}
                    </div>
                    <div style={styles.editIconBadge} className="edit-icon-hover">✎</div>
                </div>
                <div style={styles.heroTextContent}>
                    <h1 style={styles.h1}>Hello, {displayName}</h1>
                    <div style={styles.quoteCard}>"{currentQuote}"</div>
                </div>
            </div>
            
            <div style={styles.heroCenter}>
                {status === 'workout' && <button style={{...styles.circleBtn, ...styles.btnBlue}} className="btn-blue-pulse" onClick={handleAction}><span style={{fontSize:'32px'}}>🏋️</span><span style={{fontSize:'16px', fontWeight:'800'}}>START</span></button>}
                {status === 'meal' && <button style={{...styles.circleBtn, ...styles.btnPink}} className="btn-pink-pulse" onClick={handleAction}><span style={{fontSize:'32px'}}>🍽</span><span style={{fontSize:'16px', fontWeight:'800'}}>LOG MEAL</span></button>}
                {status === 'done' && <button style={{...styles.circleBtn, ...styles.btnGreen}} className="btn-green-pulse" disabled><span style={{fontSize:'32px'}}>✅</span><span style={{fontSize:'16px', fontWeight:'800'}}>ALL SET</span></button>}
            </div>

            <div style={styles.heroRight}>
                <div style={{textAlign: 'right'}}>
                    <div style={styles.streakLabel}>CURRENT STREAK</div>
                    <div style={{display:'flex', gap:15}}><div style={styles.streakNumber}>{stats.streak}</div><div style={{fontSize:'80px', animation:'float 3s infinite'}}>🔥</div></div>
                </div>
                <div style={styles.weekGrid}>
                    {weeklyProgress.map((item, i) => (
                        <div key={i} className="day-item" style={{...styles.dayCircle, ...(item.status === 'done' ? styles.dayDone : styles.dayActive)}}>{item.status === 'done' ? '🔥' : item.day}</div>
                    ))}
                </div>
            </div>
        </div>
        
        {/* STATS ROW */}
        <div style={styles.statsRow}>
            {/* MACRO BOX WITH HOVER EFFECTS */}
            <div style={{...styles.bentoBox}} className="hover-card">
                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px'}}>
                    <div style={{fontSize: '14px', fontWeight: '700', color: '#fff'}}>MACROS TODAY</div>
                    <div style={{fontSize: '12px', color: '#a1a1aa'}}>{macros.calories} / {macros.calMax} cal</div>
                </div>
                <div className="macro-item" style={{marginBottom: '12px', cursor: 'pointer'}} title={`Total: ${macros.calories} cal`}>
                    <div style={{display:'flex', justifyContent:'space-between', fontSize:'11px', color:'#fff', marginBottom:'4px'}}><span>Total Calories</span></div>
                    <div style={{...styles.macroBarBG, overflow: 'hidden'}}><div style={{...styles.macroBarFill, width: `${Math.min(100, (macros.calories/macros.calMax)*100)}%`, background: '#fff'}}></div></div>
                </div>
                <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'12px'}}>
                    <div className="macro-item" style={{cursor: 'pointer'}} title={`${macros.p}g Protein`}>
                        <div style={{fontSize:'10px', color:'#a1a1aa', marginBottom:'4px'}}>Prot ({macros.p}g)</div>
                        <div style={{...styles.macroBarBG, height:'4px', overflow: 'hidden'}}><div style={{...styles.macroBarFill, width: `${Math.min(100, (macros.p/macros.pMax)*100)}%`, background: '#6366f1'}}></div></div>
                    </div>
                    <div className="macro-item" style={{cursor: 'pointer'}} title={`${macros.c}g Carbs`}>
                        <div style={{fontSize:'10px', color:'#a1a1aa', marginBottom:'4px'}}>Carb ({macros.c}g)</div>
                        <div style={{...styles.macroBarBG, height:'4px', overflow: 'hidden'}}><div style={{...styles.macroBarFill, width: `${Math.min(100, (macros.c/macros.cMax)*100)}%`, background: '#22c55e'}}></div></div>
                    </div>
                    <div className="macro-item" style={{cursor: 'pointer'}} title={`${macros.f}g Fats`}>
                        <div style={{fontSize:'10px', color:'#a1a1aa', marginBottom:'4px'}}>Fat ({macros.f}g)</div>
                        <div style={{...styles.macroBarBG, height:'4px', overflow: 'hidden'}}><div style={{...styles.macroBarFill, width: `${Math.min(100, (macros.f/macros.fMax)*100)}%`, background: '#eab308'}}></div></div>
                    </div>
                </div>
                <div className="macro-item" style={{marginTop: '12px', cursor: 'pointer'}} title={`${macros.fiber}g Fiber`}>
                    <div style={{display:'flex', justifyContent:'space-between', fontSize:'11px', color:'#a1a1aa', marginBottom:'4px'}}><span>Fiber Estimate</span><span>{macros.fiber}g / 35g</span></div>
                    <div style={{...styles.macroBarBG, overflow: 'hidden'}}><div style={{...styles.macroBarFill, width: `${Math.min(100, (macros.fiber/35)*100)}%`, background: '#a855f7'}}></div></div>
                </div>
            </div>
            
            {/* HYDRATION */}
            <div style={{...styles.bentoBox, background: 'linear-gradient(135deg, #1e3a8a 0%, #172554 100%)', border: '1px solid rgba(96, 165, 250, 0.2)'}} className="hover-card">
                <div style={{fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '10px'}}>HYDRATION</div>
                <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center'}}>
                    <div style={{fontSize: '48px', fontWeight: '800', color: '#fff'}}>{water.toFixed(1)} <span style={{fontSize:'16px', fontWeight:'500', color:'#93c5fd'}}>L</span></div>
                    <div style={{fontSize: '12px', color: '#bfdbfe'}}>Goal: 3.0 L</div>
                </div>
                <div style={{display: 'flex', justifyContent: 'center'}}>
                    <div style={styles.glassPill}>
                        <button style={styles.glassBtn} className="control-btn-hover" onClick={handleWaterRemove}>-</button>
                        <span style={styles.glassText}>ADJUST</span>
                        <button style={styles.glassBtn} className="control-btn-hover" onClick={handleWaterAdd}>+</button>
                    </div>
                </div>
            </div>
            
            {/* READINESS */}
            <div style={{...styles.bentoBox}} className="hover-card">
                <div style={{display:'flex', justifyContent:'space-between'}}>
                    <div style={{fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '10px'}}>READINESS</div>
                    <div style={{fontSize: '14px', fontWeight: '800', color: stats.focusScore > 80 ? '#22c55e' : '#f59e0b'}}>{stats.focusScore}%</div>
                </div>
                <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center'}}>
                    <div style={{fontSize: '48px', fontWeight: '800', color: '#fff', fontFamily: 'monospace'}}>{Math.floor(sleep)}<span style={{color:'#6366f1'}}>:</span>{((sleep % 1) * 60).toString().padStart(2, '0')}</div>
                    <div style={{fontSize: '12px', color: '#a1a1aa'}}>Hours Slept</div>
                </div>
                <div style={{display: 'flex', justifyContent: 'center'}}>
                    <div style={styles.glassPill}>
                        <button style={styles.glassBtn} className="control-btn-hover" onClick={handleSleepRemove}>-</button>
                        <span style={styles.glassText}>SET TIME</span>
                        <button style={styles.glassBtn} className="control-btn-hover" onClick={handleSleepAdd}>+</button>
                    </div>
                </div>
            </div>
        </div>

        {/* TRENDS */}
        <div style={{...styles.bentoBox, ...styles.chartSection}}>
            <div style={styles.sectionHeader}>
                <div style={styles.sectionTitle}><div style={styles.sectionAccent}></div> TRENDS</div>
                <div style={styles.chartControls}>
                    <div style={styles.chartTabs}>
                        {['workout', 'meal', 'sleep', 'water'].map(m => (
                            <button key={m} style={{...styles.chartTab, ...(chartMode === m ? styles.chartTabActive : {})}} onClick={() => setChartMode(m)}>{m.toUpperCase()}</button>
                        ))}
                    </div>
                    <div style={styles.chartTabs}>
                        {['week', 'month'].map(p => (
                            <button key={p} style={{...styles.chartTab, ...(chartPeriod === p ? styles.chartTabActive : {})}} onClick={() => setChartPeriod(p)}>{p.toUpperCase()}</button>
                        ))}
                    </div>
                </div>
            </div>
            <ActivityChart data={chartData} mode={chartMode} period={chartPeriod} />
        </div>

        {/* RECENT ACTIVITY */}
        <div style={{...styles.bentoBox, ...styles.activitySection}}>
            <div style={styles.sectionHeader}>
                <div style={styles.sectionTitle}><div style={styles.sectionAccent}></div> ACTIVITY</div>
            </div>
            <div className="activity-list" style={{flex: 1, overflowY: 'auto', paddingRight: '4px'}}>
                {recentHistory.map((h, i) => (
                    <div key={i} style={styles.listRow} className="activity-row">
                        <div style={{display: 'flex', gap: '12px', alignItems: 'center'}}>
                            <div style={{
                                width: '36px', height: '36px', borderRadius: '10px', 
                                background: h.type === 'workout' ? 'rgba(34, 197, 94, 0.1)' 
                                          : h.type === 'meal' ? 'rgba(236, 72, 153, 0.1)' 
                                          : h.type === 'sleep' ? 'rgba(99, 102, 241, 0.1)' 
                                          : h.type === 'water' ? 'rgba(56, 189, 248, 0.1)'
                                          : 'rgba(245, 158, 11, 0.1)', 
                                display:'flex', alignItems:'center', justifyContent:'center', fontSize:'16px'
                            }}>
                                {h.type === 'workout' ? '🏋️' 
                                : h.type === 'meal' ? '🍎' 
                                : h.type === 'sleep' ? '😴' 
                                : h.type === 'water' ? '💧'
                                : '👤'} 
                            </div>
                            <div>
                                <div style={{color: '#fff', fontSize: '14px', fontWeight: '600'}}>{h.name}</div>
                                <div style={{color: '#71717a', fontSize: '13px', fontFamily: 'sans-serif'
                                }}>{h.date}</div>
                            </div>
                        </div>
                        <div style={{fontSize: '12px', color: '#a1a1aa', fontWeight: '500'}}>{h.details}</div>
                    </div>
                ))}
            </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;