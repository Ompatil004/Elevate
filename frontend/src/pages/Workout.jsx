import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../components/NotificationProvider';
import { getProfile } from '../api';
import ConfirmDialog from '../components/ConfirmDialog';
import axios from 'axios';

// Define full weekday names array
const weekdayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

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
    flex: 1,
    fontSize: '22px', fontWeight: '900', letterSpacing: '-1px',
    background: 'linear-gradient(to right, #fff, #a5b4fc)',
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
    display: 'flex', alignItems: 'center', gap: '10px'
  },
  navCenter: {
    display: 'flex', gap: '8px', height: '100%', alignItems: 'center',
    justifyContent: 'center'
  },
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
  navRight: {
    flex: 1,
    display: 'flex', alignItems: 'center', gap: '24px',
    justifyContent: 'flex-end'
  },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  dateDisplay: { fontSize: '13px', fontWeight: '600', color: '#a1a1aa', fontFamily: 'sans-serif', letterSpacing: '0.5px', marginRight: '8px' },
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
  historyList: { fontSize: '13px', color: '#a1a1aa', lineHeight: '1.4' },
  restDay: { padding: '20px', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '12px', color: '#f59e0b', fontSize: '14px', textAlign: 'center', fontWeight: '500' }
};

const PAST_WORKOUTS = [];

const getTodayIdx = () => {
  const jsDay = new Date().getDay();
  return (jsDay + 6) % 7;
};

const isRestDay = (day) => {
  if (day?.is_placeholder) return false;
  const label = `${day.day || day.focus || ''}`.toLowerCase();
  const note = `${day.note || ''}`.toLowerCase();
  return label.includes('rest') || note.includes('rest');
};

const getDayStatus = (day, todayIdx, completedIds = new Set()) => {
  if (day?.is_placeholder) return 'NO PLAN';
  if (isRestDay(day)) return 'REST';
  const dow = day.day_of_week ?? 0;
  if (completedIds.has(dow)) return 'COMPLETED';
  if (dow === todayIdx) return 'TODAY';
  if (dow < todayIdx) return 'PAST'; // changed from MISSED
  return 'UPCOMING';
};

function Workout() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const notifRef = useRef(null);
  const { showError, showSuccess, showInfo } = useNotification();
  const [confirmDialog, setConfirmDialog] = useState({ show: false, message: '', onConfirm: null });

  const [userProfile, setUserProfile] = useState(null);
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
  const [poseTrackingAvailable, setPoseTrackingAvailable] = useState(true);
  const [poseTrackingError, setPoseTrackingError] = useState(null);

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
    const fetchWorkoutPlan = async () => {
      try {
        console.log('🔍 Step 1: Fetching user profile...');
        const profileRes = await getProfile();
        const profile = profileRes.data;
        console.log('✅ Full profile:', profile);
        setUserProfile(profile);

        const apiBase = import.meta.env.VITE_PY_BACKEND || 'http://localhost:8000';
        console.log('🔍 Step 2: Calling backend at:', apiBase);

        const response = await axios.post(`${apiBase}/workout`, {
          age: profile.age || 25,
          weight: profile.weight || 70,
          height: profile.height || 175,
          gender: profile.gender || 'Male',
          goal: profile.goal || 'Muscle Gain',
          experience: profile.experience || 'Beginner',
          days_per_week: profile.days_per_week || 7, // FIX: default to full week
          streak: profile.streak || 0,
          equipment: Array.isArray(profile.equipment) ? profile.equipment : (profile.equipment ? [profile.equipment] : []),
          body_issues: Array.isArray(profile.body_issues) ? profile.body_issues : (profile.body_issues ? [profile.body_issues] : []),
          dietary_preference: profile.dietary_preference || 'Non-Veg'
        });

        console.log('✅ Backend response:', response.data);

        if (!response.data?.success) {
          throw new Error(response.data?.error || 'Failed to generate plan');
        }

        const weeklyPlan = response.data.workout || [];
        const normalized = normalizeWeeklyPlan(weeklyPlan); // FIX: ensure 7 days
        setPlan(normalized);
        localStorage.setItem('workoutPlan', JSON.stringify(normalized));
        showSuccess(`✅ Workout plan ready! (${response.data.exercises_count} exercises)`, 3000);
      } catch (error) {
        console.error('❌ Workout error:', error);
        console.error('❌ Response:', error.response?.data);
        showError('Failed to generate workout. Check backend.', 4000);
      }
    };

    const storedProfile = JSON.parse(localStorage.getItem('workoutPlanProfile') || '{}');
    const currentProfile = userProfile ? {
      goal: userProfile.goal,
      experience: userProfile.experience,
      equipment: userProfile.equipment,
      body_issues: userProfile.body_issues
    } : null;

    const profileChanged = currentProfile &&
      JSON.stringify(storedProfile) !== JSON.stringify(currentProfile);

    if (!localStorage.getItem('workoutPlan') || profileChanged) {
      fetchWorkoutPlan();
    } else {
      const cached = localStorage.getItem('workoutPlan');
      if (cached) setPlan(normalizeWeeklyPlan(JSON.parse(cached))); // FIX: normalize cached
    }
  }, [userProfile]);

  useEffect(() => {
    const checkPoseTracking = async () => {
      try {
        const response = await fetch('http://localhost:5001/health', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
          throw new Error('Pose tracking service unavailable');
        }

        setPoseTrackingAvailable(true);
        setPoseTrackingError(null);
      } catch (error) {
        console.warn('Pose tracking service not available:', error.message);
        setPoseTrackingAvailable(false);
        setPoseTrackingError('Pose tracking unavailable. You can still track workouts manually.');
        showInfo('Pose tracking is currently unavailable. Manual tracking mode enabled.', 5000);
      }
    };

    checkPoseTracking();
  }, [showInfo]);

  const normalizeWeeklyPlan = (rawPlan = []) => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    // Create a map from the backend response
    const indexed = new Map(
      (Array.isArray(rawPlan) ? rawPlan : []).map((d) => {
        const idx = d.day_of_week ?? 0;
        return [idx, { 
          ...d, 
          day_of_week: idx, 
          day: d.day || days[idx],
          is_placeholder: false // Mark as real data
        }];
      })
    );

    // Map all 7 days, filling missing ones with placeholders
    return days.map((label, idx) =>
      indexed.get(idx) || {
        day_of_week: idx,
        day: label,
        focus: 'No Plan',
        note: 'Not scheduled',
        exercises: [],
        is_placeholder: true,
        type: 'unplanned'
      }
    );
  };

  const safePlan = Array.isArray(plan) ? plan : [];
  const todayIdx = getTodayIdx();

  const completedIds = new Set(
    safePlan
      .map((d, idx) => {
        const key = `workout_done_${d.day || `Day ${idx + 1}`}`;
        return localStorage.getItem(key) === 'true' ? (d.day_of_week ?? idx) : null;
      })
      .filter((v) => v !== null)
  );

  const handleDayClick = (dayIdx) => {
    const day = safePlan[dayIdx];
    if (day && !isRestDay(day)) {
      setActiveDay(day);
      setActiveExercise(null);
    }
  };

  const startCamera = async () => {
    if (!poseTrackingAvailable) {
      showInfo('Camera-based pose tracking is currently unavailable. Please use manual tracking.', 3000);
      return;
    }
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(mediaStream);
      setIsCameraOn(true);
    } catch (err) {
      showError("Camera permission denied. Please allow camera access.", 5000);
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
      showSuccess("Great job! Workout Logged.", 3000);
      setActiveDay(null);
    }
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

        {poseTrackingError && (
          <div style={{
            padding: '12px',
            background: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '8px',
            margin: '20px 40px',
            color: '#f59e0b',
            fontSize: '13px'
          }}>
            ⚠️ {poseTrackingError}
          </div>
        )}

        <div style={styles.container}>
          {!activeDay && (
            <>
              <h1 style={styles.h1}>Your Weekly Plan</h1>
              <div style={styles.grid}>
                {safePlan.length > 0 ? (
                  safePlan
                    .sort((a, b) => (a.day_of_week ?? 0) - (b.day_of_week ?? 0))
                    .map((day, idx) => {
                      const isRest = isRestDay(day);
                      const isPlaceholder = !!day.is_placeholder;
                      const status = getDayStatus(day, todayIdx, completedIds);
                      const isToday = status === 'TODAY';
                      const dayExercises = day.exercises || []; // FIXED: Define here

                      let cardStyle = {...styles.card};
                      if (status === 'TODAY') {
                        cardStyle = {...cardStyle, ...styles.cardActive};
                      } else if (status === 'COMPLETED') {
                        cardStyle = {...cardStyle, ...styles.cardDone};
                      } else if (status === 'PAST') {
                        cardStyle = {...cardStyle, ...styles.cardMissed};
                      } else if (isRest || isPlaceholder) {
                        cardStyle = {...cardStyle, border: '1px dashed rgba(255,255,255,0.2)', opacity: 0.7};
                      }

                      return (
                        <div 
                          key={idx} 
                          style={cardStyle}
                          onClick={() => !isRest && !isPlaceholder && isToday && handleDayClick(idx)}
                        >
                          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px'}}>
                            <div>
                              <div style={styles.dayTitle}>
                                {weekdayNames[day.day_of_week ?? idx] || `Day ${idx + 1}`}
                              </div>
                              <div style={styles.focusText}>
                                {day.focus || day.day || 'Workout'}
                              </div>
                            </div>
                            <div style={{
                              padding: '4px 10px',
                              borderRadius: '20px',
                              fontSize: '11px',
                              fontWeight: '700',
                              textTransform: 'uppercase',
                              background: status === 'TODAY' ? 'rgba(99, 102, 241, 0.2)' :
                                         status === 'COMPLETED' ? 'rgba(34, 197, 94, 0.2)' :
                                         status === 'PAST' ? 'rgba(239, 68, 68, 0.2)' :
                                         status === 'REST' ? 'rgba(245, 158, 11, 0.2)' :
                                         status === 'NO PLAN' ? 'rgba(113, 113, 122, 0.2)' :
                                         'rgba(161, 161, 170, 0.2)',
                              color: status === 'TODAY' ? '#a5b4fc' :
                                    status === 'COMPLETED' ? '#22c55e' :
                                    status === 'PAST' ? '#ef4444' :
                                    status === 'REST' ? '#f59e0b' :
                                    status === 'NO PLAN' ? '#a1a1aa' :
                                    '#a1a1aa',
                              border: `1px solid ${status === 'TODAY' ? 'rgba(99, 102, 241, 0.3)' :
                                       status === 'COMPLETED' ? 'rgba(34, 197, 94, 0.3)' :
                                       status === 'PAST' ? 'rgba(239, 68, 68, 0.3)' :
                                       status === 'REST' ? 'rgba(245, 158, 11, 0.3)' :
                                       status === 'NO PLAN' ? 'rgba(113, 113, 122, 0.3)' :
                                       'rgba(161, 161, 170, 0.3)'}`
                            }}>
                              {status}
                            </div>
                          </div>

                          {isRest ? (
                            <div style={styles.restDay}>
                              😴 Rest Day - Recovery & Preparation
                              <div style={{ marginTop: '12px', fontSize: '11px', opacity: 0.9 }}>
                                No workout today. Focus on recovery, stretching, or light walking.
                              </div>
                            </div>
                          ) : isPlaceholder ? (
                            <div style={styles.restDay}>
                              📅 No plan for this day
                              <div style={{ marginTop: '12px', fontSize: '11px', opacity: 0.9 }}>
                                Generate a new plan to fill this day.
                              </div>
                            </div>
                          ) : (
                            <>
                              {dayExercises.length > 0 && (
                                <div style={{flex:1, marginBottom:'12px'}}>
                                  {dayExercises.slice(0, 3).map((ex, i) => (
                                    <div key={i} style={styles.exPreview}>
                                      <span>• {ex.name}</span>
                                      <span>{ex.sets}x{ex.reps}</span>
                                    </div>
                                  ))}
                                  {dayExercises.length > 3 && (
                                    <div style={{...styles.exPreview, color:'#a1a1aa', fontSize:'11px'}}>
                                      +{dayExercises.length - 3} more exercises
                                    </div>
                                  )}
                                </div>
                              )}
                              {isToday && (
                                <button
                                  onClick={() => handleDayClick(idx)}
                                  style={{
                                    width: '100%',
                                    padding: '12px',
                                    borderRadius: '12px',
                                    border: 'none',
                                    background: '#6366f1',
                                    color: 'white',
                                    fontWeight: '700',
                                    fontSize: '14px',
                                    cursor: 'pointer',
                                    marginTop: 'auto'
                                  }}
                                >
                                  START WORKOUT
                                </button>
                              )}
                            </>
                          )}
                        </div>
                      );
                    })
                ) : (
                  <div style={{gridColumn: '1 / -1', textAlign: 'center', padding: '40px', color: '#a1a1aa', fontSize: '16px'}}>
                    No plan yet. Generate to see your week.
                  </div>
                )}
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
                    {activeDay.exercises && activeDay.exercises.map((ex, i) => (
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
                      <button style={styles.btnStop} className="btn-stop" onClick={stopCamera}>STOP CAMERA</button>
                      <button style={styles.btnDone} className="btn-done" onClick={finishSession}>DONE SESSION</button>
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
            {PAST_WORKOUTS.length > 0 ? (
              PAST_WORKOUTS.map((day, i) => (
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
              ))
            ) : (
              <div style={{textAlign:'center', padding:'40px', color:'#52525b'}}>No workout history yet</div>
            )}
          </div>
        )}
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

export default Workout;