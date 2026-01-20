import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

// --- STYLES (Your Exact Styles Preserved) ---
const styles = {
  page: { background: '#09090b', minHeight: '100vh', color: '#e4e4e7', fontFamily: "'Inter', sans-serif", overflowX: 'hidden' },
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
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  dateDisplay: { fontSize: '13px', fontWeight: '600', color: '#a1a1aa', fontFamily: 'sans-serif', letterSpacing: '0.5px', marginRight: '8px' },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  iconButton: { width: '42px', height: '42px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', fontSize: '18px', transition: 'all 0.2s', position: 'relative' },
  notifDropdown: { position: 'absolute', top: '60px', right: '0px', width: '340px', background: '#18181b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', padding: '16px', zIndex: 2000, boxShadow: '0 20px 50px rgba(0,0,0,0.5)', animation: 'slideDown 0.2s ease-out' },
  notifItem: { padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '13px', color: '#d4d4d8' },
  logoutBtn: { display: 'flex', alignItems: 'center', gap: '8px', padding: '0 20px', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444', cursor: 'pointer', transition: 'all 0.2s ease', height: '42px' },
  logoutText: { fontSize: '12px', fontWeight: '700', letterSpacing: '0.5px', textTransform: 'uppercase' },
  container: { maxWidth: '1600px', margin: '0 auto', padding: '40px' },
  h1: { fontSize: '42px', fontWeight: '800', marginBottom: '40px', color: '#fff', letterSpacing: '-1px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' },
  card: { background: '#18181b', borderRadius: '20px', padding: '24px', border: '1px solid rgba(255,255,255,0.05)', position: 'relative', transition: 'all 0.3s ease', overflow: 'hidden', minHeight: '200px', display: 'flex', flexDirection: 'column' },
  cardDone: { opacity: 0.5, border: '1px solid #22c55e', background: 'rgba(34, 197, 94, 0.05)' },
  overlayDone: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.6)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardMissed: { opacity: 0.5, border: '1px solid #ef4444', background: 'rgba(239, 68, 68, 0.05)' },
  overlayMissed: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.6)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardLocked: { opacity: 0.6, cursor: 'not-allowed', border: '1px dashed rgba(255,255,255,0.1)' },
  overlayLocked: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.4)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardActive: { border: '2px solid #6366f1', background: 'linear-gradient(145deg, #1e1e2e 0%, #2a2a35 100%)', boxShadow: '0 0 30px rgba(99, 102, 241, 0.15)', cursor: 'pointer', transform: 'scale(1.02)' },
  dayTitle: { fontSize: '14px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px', color: '#a1a1aa' },
  focusText: { fontSize: '20px', fontWeight: '800', color: '#fff', marginBottom: '16px', lineHeight: '1.3' },
  exPreview: { fontSize: '13px', color: '#71717a', marginBottom: '4px', display: 'flex', justifyContent: 'space-between' },
  sessionContainer: { position: 'fixed', top: '80px', left: 0, width: '100%', height: 'calc(100vh - 80px)', background: '#09090b', zIndex: 500, display: 'flex', padding: '20px', gap: '20px', animation: 'fadeIn 0.3s ease-out' },
  selectionList: { flex: '0 0 350px', background: '#18181b', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', flexDirection: 'column', padding: '20px', overflowY: 'auto' },
  sidebarHeader: { fontSize: '18px', fontWeight: '800', color: '#fff', marginBottom: '20px', display:'flex', justifyContent:'space-between', alignItems:'center' },
  backBtn: { fontSize: '12px', padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff', border:'none', cursor:'pointer' },
  selectionPreview: { flex: 1, background: '#000', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: '#52525b' },
  focusContainer: { width: '100%', height: '100%', display: 'flex', gap: '20px' },
  focusLeft: { flex: '4', display: 'flex', flexDirection: 'column', background: '#18181b', borderRadius: '24px', padding: '24px', border: '1px solid rgba(255,255,255,0.05)' },
  activeExTitle: { fontSize: '28px', fontWeight: '800', color: '#fff', marginBottom: '8px', lineHeight: '1.2' },
  activeExStats: { fontSize: '16px', color: '#a5b4fc', fontWeight: '600', marginBottom: '20px', fontFamily: 'monospace' },
  gifLargeContainer: { flex: 1, background: '#09090b', borderRadius: '16px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', border: '1px solid rgba(255,255,255,0.1)', marginBottom: '20px' },
  gifLarge: { width: '100%', height: '100%', objectFit: 'contain' },
  controlsContainer: { height: '80px', display: 'flex', gap: '15px' },
  focusRight: { flex: '6', background: '#000', borderRadius: '24px', border: '2px solid #6366f1', overflow: 'hidden', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 50px rgba(99, 102, 241, 0.1)' },
  videoFeed: { width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' },
  recBadge: { position: 'absolute', top: 20, left: 20, background: 'rgba(220, 38, 38, 0.9)', padding: '6px 12px', borderRadius: '8px', color: 'white', fontWeight: '700', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px', zIndex:10 },
  exerciseItem: { padding: '18px', borderRadius: '16px', marginBottom: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer', transition: 'all 0.2s ease', position: 'relative' },
  exerciseItemActive: { background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)', borderColor: '#6366f1', boxShadow: '0 4px 20px rgba(99, 102, 241, 0.3)' },
  btnStartLarge: { padding: '15px 40px', fontSize:'16px', borderRadius: '12px', background: '#6366f1', color: 'white', border: 'none', fontWeight: '800', cursor: 'pointer', marginTop:'20px', boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)' },
  btnStop: { flex: 1, borderRadius: '16px', background: '#27272a', border: '1px solid rgba(255,255,255,0.1)', color: '#ef4444', fontWeight: '800', fontSize: '16px', cursor: 'pointer', transition:'all 0.2s' },
  btnDone: { flex: 1, borderRadius: '16px', background: '#22c55e', color: 'white', fontWeight: '800', fontSize: '16px', border:'none', cursor: 'pointer', boxShadow: '0 4px 15px rgba(34, 197, 94, 0.3)' },
  historyPanel: { position: 'fixed', top: '80px', right: '0', width: '400px', height: 'calc(100vh - 80px)', background: '#09090b', borderLeft: '1px solid rgba(255,255,255,0.1)', zIndex: 1500, padding: '24px', overflowY: 'auto', animation: 'slideInRight 0.3s ease-out', boxShadow: '-20px 0 50px rgba(0,0,0,0.5)' },
  historyItem: { background: '#18181b', borderRadius: '16px', padding: '20px', marginBottom: '16px', border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer', transition: 'all 0.2s' },
  historyDate: { fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '12px' },
  historySection: { marginBottom: '10px' },
  historyLabel: { fontSize: '11px', color: '#a5b4fc', fontWeight: '700', textTransform: 'uppercase', marginBottom: '4px' },
  historyList: { fontSize: '13px', color: '#a1a1aa', lineHeight: '1.4' }
};

const DUMMY_PLAN = [
  { day: "Monday", focus: "Chest & Triceps", exercises: [{ id: 1, name: "Barbell Bench Press", sets: 4, reps: "8-10", gif: "https://media1.tenor.com/m/Y08wX8yT5wEAAAAC/bench-press-workout.gif" }, { id: 2, name: "Incline Press", sets: 3, reps: "10-12", gif: "" }, { id: 3, name: "Cable Flys", sets: 3, reps: 15, gif: "" }] },
  { day: "Tuesday", focus: "Back & Biceps", exercises: [{ id: 4, name: "Deadlifts", sets: 3, reps: 5 }, { id: 5, name: "Lat Pulldowns", sets: 4, reps: 10 }, { id: 6, name: "Seated Row", sets: 3, reps: 12 }] },
  { day: "Wednesday", focus: "Rest & Recovery", exercises: [{ id: 7, name: "Stretching", sets: 1, reps: "20 min" }] },
  { day: "Thursday", focus: "Legs (Quads)", exercises: [{ id: 8, name: "Squats", sets: 4, reps: 8 }, { id: 9, name: "Leg Press", sets: 3, reps: 12 }] },
  { day: "Friday", focus: "Shoulders & Abs", exercises: [{ id: 10, name: "Overhead Press", sets: 4, reps: 8 }, { id: 11, name: "Lateral Raises", sets: 4, reps: 15 }] },
  { day: "Saturday", focus: "Legs (Hams)", exercises: [{ id: 12, name: "RDLs", sets: 4, reps: 10 }, { id: 13, name: "Lunges", sets: 3, reps: 12 }] },
  { day: "Sunday", focus: "Active Rest", exercises: [{ id: 14, name: "Walking", sets: 1, reps: "30 min" }] },
];

const PAST_WORKOUTS = [
    { date: "Yesterday", status: "Completed", exercises: ["Barbell Squats (4 Sets)", "Leg Press (3 Sets)", "Calf Raises (4 Sets)"] },
    { date: "Oct 24", status: "Completed", exercises: ["Bench Press (4 Sets)", "Incline Press (3 Sets)", "Tricep Dips (3 Sets)"] },
    { date: "Oct 23", status: "Missed", exercises: ["Rest Day or Skipped"] }
];

function Workout() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const notifRef = useRef(null);
  
  const [plan, setPlan] = useState([]);
  const [currentDayIndex, setCurrentDayIndex] = useState(0);
  const [activeDay, setActiveDay] = useState(null);
  const [activeExercise, setActiveExercise] = useState(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [stream, setStream] = useState(null);
  const [showNotif, setShowNotif] = useState(false);
  const [completedDays, setCompletedDays] = useState({});
  const [showHistory, setShowHistory] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState(null);
  
  const todayDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotif(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const saveLog = (name, details) => {
    const newLog = {
      name: name,
      date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      details: details,
      type: "workout"
    };
    const currentHistory = JSON.parse(localStorage.getItem('activityHistory') || "[]");
    localStorage.setItem('activityHistory', JSON.stringify([newLog, ...currentHistory]));
  };

  useEffect(() => {
    if (isCameraOn && videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [isCameraOn, stream]);

  useEffect(() => {
    const today = new Date().getDay(); 
    const adjustedToday = today === 0 ? 6 : today - 1; 
    setCurrentDayIndex(adjustedToday);

    const storedPlan = localStorage.getItem('workoutPlan');
    if (storedPlan) {
        const parsed = JSON.parse(storedPlan);
        setPlan(parsed.length > 0 ? parsed : DUMMY_PLAN);
    } else {
        setPlan(DUMMY_PLAN);
    }
    setCompletedDays({ loaded: true });
  }, []);

  const getDayStatus = (dayName) => {
    const planIndex = plan.findIndex(p => p.day === dayName);
    const isMarkedDone = localStorage.getItem(`workout_done_${dayName}`) === 'true';
    if (planIndex < currentDayIndex) return isMarkedDone ? 'completed' : 'missed';
    if (planIndex === currentDayIndex) return isMarkedDone ? 'completed' : 'active';
    return 'locked';
  };

  const handleDayClick = (dayName) => {
    const status = getDayStatus(dayName);
    if (status === 'active') {
      setActiveDay(plan.find(p => p.day === dayName));
      setActiveExercise(null);
    }
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(mediaStream);
      setIsCameraOn(true);
    } catch (err) {
      alert("Camera permission denied. Please allow camera access.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsCameraOn(false);
  };

  const handleExerciseSelect = (ex) => {
    if (isCameraOn) return; 
    setActiveExercise(ex);
  };

  const finishSession = () => {
    stopCamera();
    if(activeDay && activeExercise) {
        saveLog(activeExercise.name, `${activeExercise.sets} Sets completed`);
        localStorage.setItem(`workout_done_${activeDay.day}`, 'true');
        localStorage.setItem('todayWorkoutDone', 'true'); 
        setCompletedDays(prev => ({ ...prev, [activeDay.day]: true }));
        alert("Great job! Workout Logged.");
        setActiveDay(null); 
    }
  };

  const handleLogout = () => { localStorage.clear(); navigate('/'); };

  return (
    <div style={styles.page}>
      <style>{`
        @keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
        .icon-hover:hover { background: rgba(255,255,255,0.1) !important; }
        .logout-btn:hover { background: rgba(239, 68, 68, 0.2) !important; transform: translateY(-2px); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2); }
        .active-card-pulse { animation: pulseBorder 2s infinite; }
        @keyframes pulseBorder { 0% { border-color: #6366f1; box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); } 70% { border-color: #818cf8; box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); } 100% { border-color: #6366f1; box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); } }
        .ex-item:hover { transform: translateX(5px); background: rgba(255,255,255,0.06) !important; }
        .btn-stop:hover { background: rgba(239, 68, 68, 0.2) !important; }
        .btn-done:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(34, 197, 94, 0.5) !important; }
        .history-card:hover { border-color: #6366f1 !important; background: rgba(255,255,255,0.05) !important; }
      `}</style>

      <nav style={styles.navbar}>
        <div style={styles.brand}><div style={styles.brandDot}></div> ELEVATE</div>
        <div style={styles.navCenter}>
            <div style={styles.navLink} onClick={() => navigate('/dashboard')}>Dashboard</div>
            <div style={{...styles.navLink, ...styles.navLinkActive}}>Workout</div>
            <div style={styles.navLink} onClick={() => navigate('/nutrition')}>Nutrition</div>
            <div style={styles.navLink} onClick={() => navigate('/chatbot')}>ChatBot</div>
        </div>
        <div style={styles.navRight}>
            <div style={styles.dateDisplay}>{todayDate}</div>
            
            <button style={styles.iconButton} className="icon-hover" onClick={() => setShowHistory(!showHistory)} title="Past Workouts">🕒</button>

            {/* NOTIFICATION */}
            <div style={{position:'relative'}} ref={notifRef}>
              <button style={styles.iconButton} className="icon-hover" onClick={() => setShowNotif(!showNotif)}>🔔</button>
              {showNotif && (
                <div style={styles.notifDropdown}>
                  <div style={{fontSize:'14px', fontWeight:'700', color:'#fff', marginBottom:'12px'}}>Notifications</div>
                  <div style={styles.notifItem}>🔥 You're on a 12-day streak!</div>
                  <div style={styles.notifItem}>🏋️ Leg Day today!</div>
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
        {!activeDay && (
          <>
            <h1 style={styles.h1}>Your Weekly Plan</h1>
            <div style={styles.grid}>
              {plan.map((day, i) => {
                const status = getDayStatus(day.day);
                const isActive = status === 'active';
                let cardStyle = styles.card;
                if(status === 'completed') cardStyle = {...styles.card, ...styles.cardDone};
                if(status === 'missed') cardStyle = {...styles.card, ...styles.cardMissed};
                if(status === 'locked') cardStyle = {...styles.card, ...styles.cardLocked};
                if(status === 'active') cardStyle = {...styles.card, ...styles.cardActive};

                return (
                  <div 
                    key={i} 
                    onClick={() => handleDayClick(day.day)}
                    style={cardStyle}
                    className={isActive ? "active-card-pulse" : ""}
                  >
                    {status === 'completed' && <div style={styles.overlayDone}><div style={{fontSize:'40px'}}>✅</div><div style={{color:'#22c55e', fontWeight:'800', letterSpacing:'1px'}}>COMPLETED</div></div>}
                    {status === 'missed' && <div style={styles.overlayMissed}><div style={{fontSize:'40px'}}>❌</div><div style={{color:'#ef4444', fontWeight:'800', letterSpacing:'1px'}}>MISSED</div></div>}
                    {status === 'locked' && <div style={styles.overlayLocked}><div style={{fontSize:'30px'}}>🔒</div><div style={{color:'#a1a1aa', fontWeight:'600', fontSize:'12px'}}>WAIT FOR {day.day.toUpperCase()}</div></div>}
                    <div style={styles.dayTitle}>{day.day}</div>
                    <div style={styles.focusText}>{day.focus}</div>
                    <div style={{marginTop:'auto'}}>
                      {day.exercises.slice(0,3).map((ex, j) => (<div key={j} style={styles.exPreview}><span>{ex.name}</span><span>{ex.sets}x{ex.reps}</span></div>))}
                    </div>
                    {isActive && <div style={{marginTop:'15px', textAlign:'center', color:'#6366f1', fontWeight:'700', fontSize:'12px'}}>TAP TO START</div>}
                  </div>
                );
              })}
            </div>
          </>
        )}

        {activeDay && (
          <div style={styles.sessionContainer}>
            {!isCameraOn && (
              <>
                <div style={styles.selectionList}>
                  <div style={styles.sidebarHeader}>
                    Today's Routine
                    <button style={styles.backBtn} onClick={() => setActiveDay(null)}>Exit</button>
                  </div>
                  {activeDay.exercises.map((ex, i) => (
                    <div 
                        key={i} 
                        className="ex-item"
                        onClick={() => handleExerciseSelect(ex)}
                        style={{...styles.exerciseItem, ...(activeExercise?.id === ex.id ? styles.exerciseItemActive : {})}}
                    >
                        <div style={{color:'#fff', fontWeight:'700', fontSize:'14px'}}>{ex.name}</div>
                        <div style={{color:'#a1a1aa', fontSize:'12px'}}>{ex.sets} Sets • {ex.reps} Reps</div>
                    </div>
                  ))}
                </div>
                <div style={styles.selectionPreview}>
                    {activeExercise ? (
                        <>
                            <div style={{fontSize:'32px', fontWeight:'800', color:'#fff', marginBottom:'10px'}}>{activeExercise.name}</div>
                            <div style={{fontSize:'16px', color:'#a5b4fc', marginBottom:'30px', fontFamily:'monospace'}}>{activeExercise.sets} SETS x {activeExercise.reps} REPS</div>
                            {activeExercise.gif && <img src={activeExercise.gif} alt="Guide" style={{width:'350px', borderRadius:'16px', marginBottom:'30px', border:'1px solid rgba(255,255,255,0.1)'}} />}
                            <button style={styles.btnStartLarge} onClick={startCamera}>START AI CAMERA</button>
                        </>
                    ) : (
                        <>
                            <div style={{fontSize:'60px', marginBottom:'20px'}}>👈</div>
                            <div style={{fontSize:'18px', fontWeight:'600'}}>Select an exercise from the left to begin</div>
                        </>
                    )}
                </div>
              </>
            )}

            {isCameraOn && (
              <div style={styles.focusContainer}>
                <div style={styles.focusLeft}>
                    <div style={styles.activeExTitle}>{activeExercise.name}</div>
                    <div style={styles.activeExStats}>{activeExercise.sets} SETS • {activeExercise.reps} REPS</div>
                    <div style={styles.gifLargeContainer}>
                        <div style={{position:'absolute', top:15, left:15, background:'rgba(0,0,0,0.7)', padding:'4px 10px', borderRadius:'6px', fontSize:'12px', fontWeight:'700', color:'white', zIndex:5}}>FORM GUIDE</div>
                        {activeExercise?.gif ? <img src={activeExercise.gif} style={styles.gifLarge} alt="Guide" /> : <div style={{color:'#71717a'}}>No Visual Guide</div>}
                    </div>
                    <div style={styles.controlsContainer}>
                        <button style={styles.btnStop} onClick={stopCamera}>STOP CAMERA</button>
                        <button style={styles.btnDone} onClick={finishSession}>DONE SESSION</button>
                    </div>
                </div>
                <div style={styles.focusRight}>
                    <video ref={videoRef} autoPlay playsInline muted style={styles.videoFeed} />
                    <div style={styles.recBadge}><div style={{width:10, height:10, background:'white', borderRadius:'50%', animation:'pulseBorder 1s infinite'}}></div>REC</div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {showHistory && (
        <div style={styles.historyPanel}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'24px'}}>
                <div style={{fontSize:'20px', fontWeight:'800', color:'#fff'}}>Workout History</div>
                <button onClick={() => setShowHistory(false)} style={{background:'none', border:'none', color:'#fff', fontSize:'20px', cursor:'pointer'}}>✕</button>
            </div>
            {PAST_WORKOUTS.map((day, i) => (
                <div key={i} style={styles.historyItem} className="history-card" onClick={() => setSelectedHistory(selectedHistory === i ? null : i)}>
                    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                        <div style={styles.historyDate}>{day.date}</div>
                        <div style={{fontSize:'12px', fontWeight:'700', color: day.status === 'Completed' ? '#22c55e' : '#ef4444'}}>{day.status}</div>
                    </div>
                    {selectedHistory === i && (
                        <div style={{marginTop:'15px', paddingTop:'15px', borderTop:'1px solid rgba(255,255,255,0.1)'}}>
                            <div style={styles.historyLabel}>Exercises:</div>
                            <div style={styles.historyList}>
                                {day.exercises.map((ex, idx) => (
                                    <div key={idx} style={{marginBottom:'4px'}}>• {ex}</div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
      )}
    </div>
  );
}

export default Workout;