import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

// --- STYLES (Your Exact Styles Preserved) ---
const styles = {
  page: { background: '#09090b', minHeight: '100vh', color: '#e4e4e7', fontFamily: "'Inter', sans-serif", position: 'relative' },
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
  dateDisplay: { fontSize: '13px', fontWeight: '600', color: '#a1a1aa', fontFamily: 'sans-serif', letterSpacing: '0.5px', marginRight: '8px' },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  iconButton: { width: '42px', height: '42px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', fontSize: '18px', transition: 'all 0.2s', position: 'relative' },
  notifDropdown: { position: 'absolute', top: '60px', right: '0px', width: '340px', background: '#18181b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', padding: '16px', zIndex: 2000, boxShadow: '0 20px 50px rgba(0,0,0,0.5)', animation: 'slideDown 0.2s ease-out' },
  notifItem: { padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '13px', color: '#d4d4d8' },
  logoutBtn: { display: 'flex', alignItems: 'center', gap: '8px', padding: '0 20px', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444', cursor: 'pointer', transition: 'all 0.2s ease', height: '42px' },
  logoutText: { fontSize: '12px', fontWeight: '700', letterSpacing: '0.5px', textTransform: 'uppercase' },
  container: { maxWidth: '1200px', margin: '0 auto', padding: '40px' },
  h1: { fontSize: '36px', fontWeight: '800', marginBottom: '40px', color: '#fff', letterSpacing: '-1px' },
  card: { background: '#18181b', borderRadius: '24px', padding: '32px', border: '1px solid rgba(255,255,255,0.05)', height:'100%', boxShadow: '0 20px 40px rgba(0,0,0,0.2)', transition: 'all 0.3s ease', position:'relative', overflow:'hidden' },
  cardCompleted: { border: '1px solid #22c55e', background: 'linear-gradient(145deg, #18181b 0%, rgba(34, 197, 94, 0.05) 100%)', pointerEvents: 'none', opacity: 0.8 },
  completedBadge: { position:'absolute', top:15, right:15, background:'rgba(34, 197, 94, 0.1)', color:'#22c55e', padding:'4px 10px', borderRadius:'20px', fontSize:'11px', fontWeight:'800', border:'1px solid #22c55e' },
  title: { fontSize: '20px', fontWeight: '800', marginBottom: '20px', textTransform:'uppercase', letterSpacing:'1px', display:'flex', alignItems:'center', gap:'10px' },
  itemRow: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 12px', borderBottom: '1px solid rgba(255,255,255,0.05)', transition: 'background 0.2s ease', borderRadius: '8px' },
  itemLeft: { display: 'flex', alignItems: 'center', gap: '12px', flex:1 },
  checkbox: { width: '20px', height: '20px', borderRadius: '6px', border: '2px solid #52525b', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s' },
  checkboxChecked: { background: '#22c55e', borderColor: '#22c55e' },
  itemText: { fontSize: '14px', fontWeight: '500', color: '#e4e4e7', transition: 'all 0.2s' },
  itemTextDone: { color: '#52525b', textDecoration: 'line-through' },
  swapBtn: { background: 'transparent', border: 'none', color: '#6366f1', cursor: 'pointer', fontSize: '16px', opacity: 0.5, transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '6px', pointerEvents:'auto' },
  modalBackdrop: { position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)', zIndex: 2000, display: 'flex', alignItems: 'center', justifyContent: 'center', animation: 'fadeIn 0.2s ease' },
  modalCard: { background: '#18181b', padding: '32px', borderRadius: '24px', width: '400px', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 25px 50px rgba(0,0,0,0.5)', textAlign: 'center', animation: 'scaleUp 0.2s ease' },
  modalTitle: { fontSize: '20px', fontWeight: '800', color: '#fff', marginBottom: '10px' },
  modalText: { fontSize: '14px', color: '#a1a1aa', marginBottom: '24px', lineHeight: '1.5' },
  modalBtnRow: { display: 'flex', gap: '12px' },
  modalBtnCancel: { flex: 1, padding: '12px', borderRadius: '12px', background: '#27272a', color: '#fff', border: 'none', fontWeight: '700', cursor: 'pointer' },
  modalBtnConfirm: { flex: 1, padding: '12px', borderRadius: '12px', background: '#6366f1', color: '#fff', border: 'none', fontWeight: '700', cursor: 'pointer' },
  historyPanel: { position: 'fixed', top: '80px', right: '0', width: '400px', height: 'calc(100vh - 80px)', background: '#09090b', borderLeft: '1px solid rgba(255,255,255,0.1)', zIndex: 1500, padding: '24px', overflowY: 'auto', animation: 'slideInRight 0.3s ease-out', boxShadow: '-20px 0 50px rgba(0,0,0,0.5)' },
  historyItem: { background: '#18181b', borderRadius: '16px', padding: '20px', marginBottom: '16px', border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer', transition: 'all 0.2s' },
  historyDate: { fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '12px' },
  historySection: { marginBottom: '10px' },
  historyLabel: { fontSize: '11px', color: '#a5b4fc', fontWeight: '700', textTransform: 'uppercase', marginBottom: '4px' },
  historyFoodList: { fontSize: '13px', color: '#a1a1aa', lineHeight: '1.4' }
};

const DUMMY_PLAN = {
  breakfast: [ { id: 'b1', item: "Oatmeal with Berries", swapped: false }, { id: 'b2', item: "3 Boiled Eggs", swapped: false }, { id: 'b3', item: "Green Tea", swapped: false } ],
  lunch: [ { id: 'l1', item: "Grilled Chicken Breast", swapped: false }, { id: 'l2', item: "Brown Rice (1 cup)", swapped: false }, { id: 'l3', item: "Steamed Broccoli", swapped: false } ],
  dinner: [ { id: 'd1', item: "Salmon Fillet", swapped: false }, { id: 'd2', item: "Quinoa Salad", swapped: false } ],
  snack: [ { id: 's1', item: "Greek Yogurt", swapped: false }, { id: 's2', item: "Almonds (10 pcs)", swapped: false } ]
};

const PAST_HISTORY = [
    { date: "Yesterday", status: "80% Complete", menu: { breakfast: ["Oatmeal", "Eggs"], lunch: ["Chicken", "Rice"], dinner: ["(Missed)"], snack: ["Apple"] } },
    { date: "Oct 24", status: "100% Complete", menu: { breakfast: ["Pancakes"], lunch: ["Sandwich"], dinner: ["Steak"], snack: ["Protein Bar"] } }
];

const ALTERNATIVES = [ "Protein Smoothie", "Tofu Scramble", "Turkey Sandwich", "Lentil Soup", "Cottage Cheese Bowl" ];

function Nutrition() {
  const navigate = useNavigate();
  const notifRef = useRef(null);
  
  const [plan, setPlan] = useState({});
  const [completedItems, setCompletedItems] = useState({}); 
  const [showNotif, setShowNotif] = useState(false);
  const [swapTarget, setSwapTarget] = useState(null);
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
      type: "meal"
    };
    const currentHistory = JSON.parse(localStorage.getItem('activityHistory') || "[]");
    localStorage.setItem('activityHistory', JSON.stringify([newLog, ...currentHistory]));
  };

  useEffect(() => {
    const lastDate = localStorage.getItem('lastMealDate');
    const today = new Date().toDateString();

    if (lastDate !== today) {
        setCompletedItems({});
        localStorage.setItem('lastMealDate', today);
        localStorage.removeItem('todayMealsDone'); 
    }

    const storedPlan = localStorage.getItem('nutritionPlan');
    if (storedPlan) {
        try {
            const parsed = JSON.parse(storedPlan);
            const normalized = {};
            Object.keys(parsed).forEach((cat) => {
                normalized[cat] = parsed[cat].map((food, i) => ({
                    ...food,
                    id: food.id || `${cat}-${i}`,
                    swapped: food.swapped || false
                }));
            });
            setPlan(Object.keys(normalized).length ? normalized : DUMMY_PLAN);
        } catch(e) { setPlan(DUMMY_PLAN); }
    } else {
        setPlan(DUMMY_PLAN);
    }
  }, []);

  useEffect(() => {
    if (Object.keys(plan).length === 0) return;
    const mainMeals = ['breakfast', 'lunch', 'dinner'];
    const allMainMealsDone = mainMeals.every(category => {
        if (!plan[category]) return true; 
        return plan[category].every(item => completedItems[item.id]);
    });

    if (allMainMealsDone) {
        localStorage.setItem('todayMealsDone', 'true');
    } else {
        localStorage.setItem('todayMealsDone', 'false');
    }
  }, [completedItems, plan]);

  const handleLogout = () => { localStorage.clear(); navigate('/'); };

  const toggleItem = (itemId, itemName) => {
    const newState = !completedItems[itemId];
    setCompletedItems(prev => ({ ...prev, [itemId]: newState }));
    if (newState) saveLog('Meal Logged', `Ate ${itemName}`);
  };

  const isCategoryComplete = (categoryKey) => {
    if (!plan[categoryKey]) return false;
    return plan[categoryKey].every(item => completedItems[item.id]);
  };

  const initiateSwap = (category, index, item) => {
    if (completedItems[item.id]) return; 
    setSwapTarget({ category, index, item });
  };

  const confirmSwap = () => {
    if (!swapTarget) return;
    const { category, index } = swapTarget;
    const randomNew = ALTERNATIVES[Math.floor(Math.random() * ALTERNATIVES.length)];
    setPlan(prevPlan => {
      const newCategoryList = [...prevPlan[category]];
      newCategoryList[index] = { ...newCategoryList[index], item: randomNew, swapped: true };
      return { ...prevPlan, [category]: newCategoryList };
    });
    setSwapTarget(null);
  };

  return (
    <div style={styles.page}>
      <style>{`
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scaleUp { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
        @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
        .icon-hover:hover { background: rgba(255,255,255,0.1) !important; }
        .logout-btn:hover { background: rgba(239, 68, 68, 0.2) !important; transform: translateY(-2px); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2); }
        .swap-btn:hover { opacity: 1 !important; transform: rotate(180deg); }
        .item-row:hover { background: rgba(255,255,255,0.02); }
        .history-card:hover { border-color: #6366f1 !important; background: rgba(255,255,255,0.05) !important; }
      `}</style>

      <nav style={styles.navbar}>
        <div style={styles.brand}><div style={styles.brandDot}></div> ELEVATE</div>
        <div style={styles.navCenter}>
            <div style={styles.navLink} onClick={() => navigate('/dashboard')}>Dashboard</div>
            <div style={styles.navLink} onClick={() => navigate('/workout')}>Workout</div>
            <div style={{...styles.navLink, ...styles.navLinkActive}}>Nutrition</div>
            <div style={styles.navLink} onClick={() => navigate('/chatbot')}>ChatBot</div>
        </div>
        <div style={styles.navRight}>
            <div style={styles.dateDisplay}>{todayDate}</div>
            <button style={styles.iconButton} className="icon-hover" onClick={() => setShowHistory(!showHistory)} title="Past Meals">🕒</button>
            
            {/* NOTIFICATION */}
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
        <h1 style={styles.h1}>Your Daily Nutrition</h1>
        
        <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(350px, 1fr))', gap:'24px'}}>
            {Object.keys(plan).map((category) => {
              const isComplete = isCategoryComplete(category);
              let accentColor = '#a1a1aa';
              if(category.includes('breakfast')) accentColor = '#fcd34d'; 
              if(category.includes('lunch')) accentColor = '#34d399'; 
              if(category.includes('dinner')) accentColor = '#f472b6'; 
              if(category.includes('snack')) accentColor = '#60a5fa'; 

              return (
                <div key={category} style={{...styles.card, ...(isComplete ? styles.cardCompleted : {})}}>
                    {isComplete && <div style={styles.completedBadge}>✓ COMPLETED</div>}
                    <h2 style={{...styles.title, color: accentColor}}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                    </h2>
                    {plan[category].map((food, idx) => {
                        const isChecked = !!completedItems[food.id];
                        return (
                            <div key={food.id} style={styles.itemRow} className="item-row">
                                <div style={styles.itemLeft} onClick={() => toggleItem(food.id, food.item)}>
                                    <div style={{...styles.checkbox, ...(isChecked ? styles.checkboxChecked : {})}}>
                                        {isChecked && <span style={{color:'#fff', fontSize:'12px', fontWeight:'bold'}}>✓</span>}
                                    </div>
                                    <div style={{...styles.itemText, ...(isChecked ? styles.itemTextDone : {})}}>
                                        {food.item}
                                        {food.swapped && <span style={{fontSize:'10px', color: accentColor, marginLeft:'8px', border:`1px solid ${accentColor}`, padding:'2px 4px', borderRadius:'4px'}}>AI SWAP</span>}
                                    </div>
                                </div>
                                {!isChecked && (
                                    <button style={styles.swapBtn} className="swap-btn" title="Swap this meal" onClick={() => initiateSwap(category, idx, food)}>🔄</button>
                                )}
                            </div>
                        );
                    })}
                </div>
              );
            })}
        </div>
      </div>

      {showHistory && (
        <div style={styles.historyPanel}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'24px'}}>
                <div style={{fontSize:'20px', fontWeight:'800', color:'#fff'}}>Meal History</div>
                <button onClick={() => setShowHistory(false)} style={{background:'none', border:'none', color:'#fff', fontSize:'20px', cursor:'pointer'}}>✕</button>
            </div>
            {PAST_HISTORY.map((day, i) => (
                <div key={i} style={styles.historyItem} className="history-card" onClick={() => setSelectedHistory(selectedHistory === i ? null : i)}>
                    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                        <div style={styles.historyDate}>{day.date}</div>
                        <div style={{fontSize:'12px', fontWeight:'700', color: day.status.includes('100') ? '#22c55e' : '#f59e0b'}}>{day.status}</div>
                    </div>
                    {selectedHistory === i && (
                        <div style={{marginTop:'15px', paddingTop:'15px', borderTop:'1px solid rgba(255,255,255,0.1)'}}>
                            {Object.entries(day.menu).map(([meal, items]) => (
                                <div key={meal} style={styles.historySection}>
                                    <div style={styles.historyLabel}>{meal}</div>
                                    <div style={styles.historyFoodList}>
                                        {items.join(', ')}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ))}
        </div>
      )}

      {swapTarget && (
        <div style={styles.modalBackdrop}>
            <div style={styles.modalCard}>
                <div style={{fontSize:'40px', marginBottom:'15px'}}>🍲</div>
                <div style={styles.modalTitle}>Swap Meal Item?</div>
                <div style={styles.modalText}>
                    Do you want to swap <strong>"{swapTarget.item.item}"</strong>?<br/>
                    Our AI will find a nutritionally equivalent alternative.
                </div>
                <div style={styles.modalBtnRow}>
                    <button style={styles.modalBtnCancel} onClick={() => setSwapTarget(null)}>No, Keep it</button>
                    <button style={styles.modalBtnConfirm} onClick={confirmSwap}>Yes, Swap it</button>
                </div>
            </div>
        </div>
      )}
    </div>
  );
}

export default Nutrition;