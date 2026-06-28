import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../components/NotificationProvider';
import { saveProfile, getProfile } from '../api';
import { updateProfileWithRegeneration, classifyError } from '../services/profileApi';
import { removeFromStorage, setToStorage, logoutSafe, StorageKeys, getTodayStr, safeJSONParse } from '../utils/storage';
import ConfirmDialog from '../components/ConfirmDialog';
import '../App.css';

// --- STYLES ---
const styles = {
  container: {
    minHeight: '100dvh',
    background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)',
    padding: 'clamp(12px, 3vw, 20px)', position: 'relative', overflowX: 'hidden', overflowY: 'auto', display: 'flex', alignItems: 'flex-start', justifyContent: 'center', fontFamily: "'Inter', sans-serif"
  },
  orbBase: { position: 'absolute', borderRadius: '50%', opacity: 0.15, filter: 'blur(80px)', animation: 'float 8s ease-in-out infinite' },
  orb1: { width: 'clamp(220px, 35vw, 400px)', height: 'clamp(220px, 35vw, 400px)', background: '#6366f1', top: '-100px', left: '-100px' },
  orb2: { width: 'clamp(200px, 30vw, 350px)', height: 'clamp(200px, 30vw, 350px)', background: '#ec4899', bottom: '-50px', right: '-50px', animation: 'float 10s ease-in-out infinite reverse' },
  
  wrapper: { maxWidth: '1100px', width: '100%', position: 'relative', zIndex: 10, marginTop: '10px', paddingBottom: '24px' },
  
  // NEW: Cancel Button Style
  cancelBtn: {
    position: 'absolute', top: '10px', right: '10px',
    background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    padding: '8px 16px', borderRadius: '12px', cursor: 'pointer',
    fontSize: '12px', fontWeight: '700', zIndex: 100,
    transition: 'all 0.2s', backdropFilter: 'blur(5px)',
    textTransform: 'uppercase', letterSpacing: '0.5px'
  },

  header: { textAlign: 'center', marginBottom: '20px', animation: 'slideDown 0.8s ease-out' },
  headerH1: { fontSize: 'clamp(28px, 5vw, 42px)', fontWeight: 900, color: '#ffffff', marginBottom: '8px', letterSpacing: '-1px', textShadow: '0 4px 10px rgba(0,0,0,0.3)' },
  headerP: { fontSize: '16px', color: '#cbd5e1', fontWeight: 400, letterSpacing: '0.3px' },
  
  form: {
    background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
    borderRadius: '24px', padding: 'clamp(14px, 3vw, 30px)',
    boxShadow: '0 25px 70px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255,255,255,0.5)',
    animation: 'slideUp 0.8s ease-out',
    position: 'relative', overflow: 'visible',
    border: '1px solid rgba(99, 102, 241, 0.1)'
  },
  
  headerRow: { display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap', marginBottom: '20px', borderBottom: '2px dashed #e2e8f0', paddingBottom: '20px' },
  avatarWrapper: { position: 'relative', width: 'clamp(84px, 18vw, 110px)', height: 'clamp(84px, 18vw, 110px)', flexShrink: 0 },
  avatarImage: { 
    width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover', 
    background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', 
    fontSize: '40px', fontWeight: '700', color: '#6366f1', 
    border: '4px solid #ffffff', cursor: 'pointer', 
    boxShadow: '0 10px 25px rgba(99, 102, 241, 0.25)' 
  },
  removeBtn: { position: 'absolute', top: 0, right: -5, background: '#ef4444', color: '#fff', width: '24px', height: '24px', borderRadius: '50%', border: '2px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', cursor: 'pointer', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' },
  uploadLabel: { fontSize: '13px', color: '#6366f1', fontWeight: '700', marginTop: '12px', textAlign: 'center', cursor: 'pointer', display: 'block', transition: 'color 0.2s' },
  nameGroup: { flex: 1, minWidth: '220px', display: 'flex', gap: '15px', flexWrap: 'wrap' },

  sectionTitle: {
    fontSize: '18px', fontWeight: 800, color: '#1e293b', marginBottom: '15px',
    display: 'flex', alignItems: 'center', gap: '10px', letterSpacing: '-0.3px'
  },
  sectionIcon: { 
    background: 'rgba(99, 102, 241, 0.1)', color: '#6366f1', 
    width: '32px', height: '32px', borderRadius: '8px', 
    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' 
  },
  
  formRow4: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '16px' },
  formRow3: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '16px' },
  
  formGroup: { display: 'flex', flexDirection: 'column', flex: 1 },
  label: { fontSize: '12px', fontWeight: 700, color: '#64748b', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' },
  
  input: {
    padding: '14px 16px', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '14px',
    fontFamily: 'inherit', transition: 'all 0.3s ease', background: '#f8fafc', color: '#334155', fontWeight: '600',
    boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.02)', width: '100%'
  },
  select: {
    padding: '14px 16px', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '14px',
    fontFamily: 'inherit', transition: 'all 0.3s ease', background: '#f8fafc',
    color: '#334155', fontWeight: '600', cursor: 'pointer', appearance: 'none', paddingRight: '32px',
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236366f1' d='M6 9L1 4h10z'/%3E%3C/svg%3E")`,
    backgroundRepeat: 'no-repeat', backgroundPosition: 'right 16px center'
  },

  multiSelectWrapper: { display: 'flex', flexDirection: 'column', position: 'relative' },
  multiSelectButton: {
    width: '100%', padding: '14px 16px', border: '1px solid #e2e8f0', borderRadius: '12px',
    background: '#f8fafc', fontSize: '14px', fontFamily: 'inherit',
    color: '#334155', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    fontWeight: '600', transition: 'all 0.3s ease',
    boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.02)'
  },
  multiSelectDropdown: {
    position: 'absolute', bottom: '115%', left: 0, right: 0,
    background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px',
    maxHeight: 'min(220px, 42dvh)', overflowY: 'auto', zIndex: 9999,
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)'
  },
  checkboxOption: { display: 'flex', alignItems: 'center', padding: '12px 16px', borderBottom: '1px solid #f1f5f9', cursor: 'pointer', transition: 'all 0.2s ease', fontSize:'13px', fontWeight:'500', color:'#475569' },
  checkboxInput: { width: '16px', height: '16px', marginRight: '12px', cursor: 'pointer', accentColor: '#6366f1' },
  selectedItems: { display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '10px' },
  selectedTag: { display: 'inline-flex', alignItems: 'center', gap: '5px', background: '#eef2ff', color: '#4f46e5', padding: '6px 12px', borderRadius: '8px', fontSize: '12px', fontWeight: '700', border:'1px solid #c7d2fe' },

  button: {
    width: '100%', padding: 'clamp(12px, 2.4vw, 16px)', marginTop: '15px',
    background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    color: 'white', border: 'none', borderRadius: '14px', fontSize: '15px', fontWeight: 700, cursor: 'pointer',
    transition: 'all 0.3s ease', boxShadow: '0 8px 25px rgba(99, 102, 241, 0.3)', letterSpacing: '0.5px'
  },
  buttonDisabled: { opacity: 0.6, cursor: 'not-allowed', filter: 'grayscale(100%)' }
};

const MultiSelect = ({ name, options, value, onChange, isOpen, onToggle, isNoneChecked }) => {
  return (
    <div style={styles.multiSelectWrapper} className="multi-select-wrapper">
      <button 
        type="button" 
        className="unified-input" 
        style={{
          ...styles.multiSelectButton,
          borderColor: isOpen ? '#6366f1' : '#e2e8f0',
          background: isOpen ? '#fff' : '#f8fafc',
          boxShadow: isOpen ? '0 0 0 4px rgba(99, 102, 241, 0.1)' : 'inset 0 1px 2px rgba(0,0,0,0.02)'
        }} 
        onClick={onToggle}
      >
        <span>{value.length > 0 ? `${value.length} selected` : 'Select...'}</span>
        <span style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s', fontSize:'10px' }}>▼</span>
      </button>
      
      {isOpen && (
        <div style={styles.multiSelectDropdown}>
          {options.map((option, index) => {
            const isChecked = value.includes(option);
            const isNoneTypeOption = option === 'None' || option === 'None (Bodyweight Only)';
            const isOptionDisabled = isNoneChecked && !isNoneTypeOption;
            return (
              <label 
                key={option} 
                style={{
                  ...styles.checkboxOption,
                  borderBottom: index === options.length -1 ? 'none' : '1px solid #f1f5f9',
                  opacity: isOptionDisabled ? 0.5 : 1, 
                  cursor: isOptionDisabled ? 'not-allowed' : 'pointer',
                  background: isChecked ? '#f8fafc' : 'transparent',
                  color: isChecked ? '#4f46e5' : '#475569',
                  fontWeight: isChecked ? '600' : '500'
                }}
                onMouseEnter={(e) => !isOptionDisabled && (e.currentTarget.style.background = '#f8fafc')}
                onMouseLeave={(e) => (e.currentTarget.style.background = isChecked ? '#f8fafc' : 'transparent')}
              >
                <input 
                  type="checkbox" 
                  style={styles.checkboxInput} 
                  checked={isChecked} 
                  disabled={isOptionDisabled} 
                  onChange={(e) => onChange(e, name)} 
                  value={option} 
                />
                {option}
              </label>
            );
          })}
        </div>
      )}
      
      {value.length > 0 && (
        <div style={styles.selectedItems}>
          {value.map(item => <div key={item} style={styles.selectedTag}>✓ {item}</div>)}
        </div>
      )}
    </div>
  );
};

function ProfileSetup({ onLogout }) {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const { showInfo, showError, showSuccess } = useNotification();

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [userAvatar, setUserAvatar] = useState(null);
  const [loading, setLoading] = useState(false);
  const [openDropdown, setOpenDropdown] = useState(null);
  const fileInputRef = useRef(null);
  const [baselineProfile, setBaselineProfile] = useState(null);
  
  // State for regeneration timing dialog
  const [regenerateDialog, setRegenerateDialog] = useState({
    show: false,
    profileUpdate: null,
    changesAffectWorkout: false,
    changesAffectMeal: false
  });

  const [formData, setFormData] = useState({
    age: '', weight: '', height: '', gender: 'Male',
    goal: 'Muscle Gain', experience: 'Beginner', dietary_preference: 'Non-Veg',
    equipment: [], allergies: [], body_issues: []
  });

  // Function to clear workout plan cache to force regeneration
  const _clearWorkoutPlanCache = () => {
    try {
      // Bug #5 Fix: Use the exact keys Workout.jsx reads to ensure invalidation works.
      removeFromStorage('workoutPlan');              // Main workout plan used by Workout.jsx
      removeFromStorage('workoutPlanTimestamp');     // Force refetch on next visit
      removeFromStorage('workoutPlanProfile');       // Profile hash for cache validation
      removeFromStorage(StorageKeys.CACHED_ENRICHED_DATA);           // Enriched exercise data
      removeFromStorage(StorageKeys.CACHED_ENRICHED_DATA_TIMESTAMP); // Enriched data timestamp
      removeFromStorage(StorageKeys.LAST_API_ENRICHMENT);            // WGER enrichment timestamp
      // Legacy keys (in case any old code wrote them)
      removeFromStorage('workout_plan_cache');
      removeFromStorage('current_workout_plan');
      removeFromStorage('weekly_workout_plan');
      console.log("✅ Workout plan cache cleared successfully");
    } catch (error) {
      console.error("❌ Error clearing workout plan cache:", error);
    }
  };

  // Function to clear meal plan cache to force regeneration
  const _clearMealPlanCache = () => {
    try {
      // Bug #5 Fix: Use the exact keys Nutrition.jsx reads to ensure cache invalidation works.
      removeFromStorage(StorageKeys.NUTRITION_CACHE);         // 'nutritionPlan' — main plan object
      removeFromStorage(StorageKeys.NUTRITION_CACHE_DATE);    // 'nutritionPlanDate' — date cache was generated
      removeFromStorage(StorageKeys.NUTRITION_CACHE_INVALID); // 'nutritionCacheInvalid' — invalidation flag
      // Volatile daily state that belongs to the old plan
      removeFromStorage('checkedFoods');
      removeFromStorage('lockedMeals');
      removeFromStorage('tickTimes');
      removeFromStorage('todayProgressStatus');
      // Legacy keys (in case any old code wrote them)
      removeFromStorage('meal_plan_cache');
      removeFromStorage('current_meal_plan');
      removeFromStorage('weekly_meal_plan');
      removeFromStorage('nutrition_cache');
      removeFromStorage('mealPlan');
      removeFromStorage('mealPlanProfile');
      console.log("✅ Meal plan cache cleared successfully");
    } catch (error) {
      console.error("❌ Error clearing meal plan cache:", error);
    }
  };

  const getMondayIndexToday = () => {
    const jsDay = new Date().getDay();
    return (jsDay + 6) % 7;
  };

  const getPlanItemIndex = (item, fallbackIdx) => {
    const idx = Number.isInteger(item?.day_of_week) ? item.day_of_week : fallbackIdx;
    return idx >= 0 && idx <= 6 ? idx : fallbackIdx;
  };

  const mergeWorkoutPlanFromToday = (currentPlan, regeneratedPlan) => {
    if (!Array.isArray(regeneratedPlan) || regeneratedPlan.length === 0) return [];

    const todayIdx = getMondayIndexToday();
    const currentByDay = new Map();
    const regeneratedByDay = new Map();

    (Array.isArray(currentPlan) ? currentPlan : []).forEach((item, i) => {
      currentByDay.set(getPlanItemIndex(item, i), item);
    });

    regeneratedPlan.forEach((item, i) => {
      regeneratedByDay.set(getPlanItemIndex(item, i), item);
    });

    const merged = [];
    for (let dayIdx = 0; dayIdx < 7; dayIdx++) {
      const existing = currentByDay.get(dayIdx);
      const regenerated = regeneratedByDay.get(dayIdx);
      const chosen = dayIdx < todayIdx ? (existing || regenerated) : (regenerated || existing);
      if (chosen) {
        merged.push({
          ...chosen,
          day_of_week: Number.isInteger(chosen.day_of_week) ? chosen.day_of_week : dayIdx,
        });
      }
    }

    return merged.length > 0 ? merged : regeneratedPlan;
  };

  useEffect(() => {
    // 1. BLOCK BACK BUTTON
    window.history.pushState(null, document.title, window.location.href);
    const handlePopState = () => {
        window.history.pushState(null, document.title, window.location.href);
        if(!isEditing) showInfo("Please complete setup or click Cancel to logout.", 3000);
    };
    window.addEventListener('popstate', handlePopState);

    // 2. LOAD EXISTING DATA
    const loadData = async () => {
        try {
            const { data } = await getProfile();
            if(data.name) {
                const parts = data.name.split(' ');
                setFirstName(parts[0]);
                if(parts.length > 1) setLastName(parts.slice(1).join(' '));
            }

            // Determine if user is editing based on existing profile data
            const hasProfileData = data && (data.age || data.weight || data.height || data.goal);
            setIsEditing(hasProfileData);
            setBaselineProfile(data || null);

            // If editing, prefill form
            if(hasProfileData) {
                setFormData({
                    age: data.age || '',
                    weight: data.weight || '',
                    height: data.height || '',
                    gender: data.gender || 'Male',
                    goal: data.goal || 'Muscle Gain',
                    experience: data.experience || 'Beginner',
                    dietary_preference: data.dietary_preference || 'Non-Veg',
                    equipment: data.equipment || [],
                    allergies: data.allergies || [],
                    body_issues: data.body_issues || []
                });
            }

            // Check if user has Google avatar
            if (data.avatar) {
                setUserAvatar(data.avatar);
                localStorage.setItem('userAvatar', data.avatar);
            }
        } catch {
            console.log("No existing profile data found.");
        }
    };
    loadData();

    // 3. LOAD AVATAR
    const storedAvatar = localStorage.getItem('userAvatar');
    if (storedAvatar) setUserAvatar(storedAvatar);

    return () => window.removeEventListener('popstate', handlePopState);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (openDropdown && !event.target.closest('.multi-select-wrapper')) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openDropdown]);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result;
        setUserAvatar(base64String);
        localStorage.setItem('userAvatar', base64String);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = (e) => {
    e.stopPropagation();
    if (window.confirm("Remove profile picture?")) {
      setUserAvatar(null);
      localStorage.removeItem('userAvatar');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleCheckbox = (e, type) => {
    const value = e.target.value; 
    const checked = e.target.checked;
    let updatedList = [...formData[type]];
    // Treat 'None (Bodyweight Only)' and 'None' as mutually-exclusive "none" options
    const isNoneValue = value === 'None' || value === 'None (Bodyweight Only)';
    const noneValues = ['None', 'None (Bodyweight Only)'];
    if (isNoneValue) {
      updatedList = checked ? [value] : updatedList.filter(item => !noneValues.includes(item));
    } else {
      // Remove any "none" selection when a real equipment item is checked
      updatedList = updatedList.filter(item => !noneValues.includes(item));
      updatedList = checked ? [...updatedList, value] : updatedList.filter(item => item !== value);
    }
    setFormData({ ...formData, [type]: updatedList });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Build profile update payload
    const profileUpdate = {
      age: parseInt(formData.age) || 25,
      weight: parseFloat(formData.weight) || 70,
      height: parseFloat(formData.height) || 170,
      gender: formData.gender || 'Male',
      goal: formData.goal || 'Muscle Gain',
      experience: formData.experience || 'Beginner',
      equipment: formData.equipment || [],
      body_issues: formData.body_issues || [],
      dietary_preference: formData.dietary_preference || 'Non-Veg',
      allergies: formData.allergies || [],
    };

    // Compare against server-loaded baseline profile, not cached local profile.
    const compareSource = baselineProfile || {};
    
    const sortedEqNew = [...(profileUpdate.equipment || [])].sort();
    const sortedEqOld = [...(compareSource.equipment || [])].sort();
    const sortedIssNew = [...(profileUpdate.body_issues || [])].sort();
    const sortedIssOld = [...(compareSource.body_issues || [])].sort();
    const sortedAllergiesNew = [...(profileUpdate.allergies || [])].sort();
    const sortedAllergiesOld = [...(compareSource.allergies || [])].sort();

    // Check what changes affect workout regeneration
    // Priority 0 Bug 4 Fix: Use delta thresholds instead of naive equality.
    // Weight changes < 10 kg don't change exercise selection — only TDEE/meal plan.
    // Age changes < 5 years don't meaningfully change volume prescription.
    const weightDelta = Math.abs(
      parseFloat(profileUpdate.weight) - parseFloat(compareSource.weight || 0)
    );
    const ageDelta = Math.abs(
      parseInt(profileUpdate.age) - parseInt(compareSource.age || 0)
    );

    const changesAffectWorkout =
      String(profileUpdate.goal) !== String(compareSource.goal) ||
      String(profileUpdate.experience) !== String(compareSource.experience) ||
      JSON.stringify(sortedEqNew) !== JSON.stringify(sortedEqOld) ||
      JSON.stringify(sortedIssNew) !== JSON.stringify(sortedIssOld) ||
      String(profileUpdate.gender) !== String(compareSource.gender) ||
      weightDelta >= 10 ||    // Only regenerate workout if weight changed by ≥10 kg
      ageDelta >= 5;          // Only regenerate workout if age changed by ≥5 years
    
    const changesAffectMeal =
      String(profileUpdate.goal) !== String(compareSource.goal) ||
      String(profileUpdate.dietary_preference) !== String(compareSource.dietary_preference) ||
      JSON.stringify(sortedAllergiesNew) !== JSON.stringify(sortedAllergiesOld) ||
      weightDelta >= 1 ||     // Meal regenerates on any weight change (TDEE-sensitive)
      String(profileUpdate.height) !== String(compareSource.height) ||
      ageDelta >= 1 ||
      String(profileUpdate.gender) !== String(compareSource.gender);

    const profileAffectsPlans = changesAffectWorkout || changesAffectMeal;

    // If changes affect plans, ask timing for existing users.
    if (isEditing && profileAffectsPlans) {
      setRegenerateDialog({
        show: true,
        profileUpdate,
        changesAffectWorkout,
        changesAffectMeal
      });
      return;
    }

    // No plan-impacting changes (e.g. name/avatar only), update directly without regeneration.
    await performProfileUpdate(profileUpdate, 'immediate', { skipPlanRegeneration: true });
  };

  /**
   * Handle regeneration timing choice
   */
  const handleRegenerateChoice = async (choice) => {
    setRegenerateDialog({ show: false, profileUpdate: null, changesAffectWorkout: false, changesAffectMeal: false });
    
    if (choice === 'cancel') {
      return;
    }
    
    await performProfileUpdate(regenerateDialog.profileUpdate, choice);
  };

  /**
   * Perform the actual profile update
   * @param {Object} profileUpdate - The profile data to update
   * @param {string} timing - 'immediate' or 'next_week'
   */
  const performProfileUpdate = async (profileUpdate, timing, options = {}) => {
    const { skipPlanRegeneration = false } = options;
    setLoading(true);

    // Priority 0 Bug 3 Fix: Clear localStorage caches BEFORE the API call.
    // Without this, Workout.jsx and Nutrition.jsx read the old 24-hr cached plan
    // even after the server has regenerated a new one.
    if (!skipPlanRegeneration) {
      _clearWorkoutPlanCache();
      _clearMealPlanCache();
    }

    try {
      console.log('📝 Performing profile update:', { profileUpdate, timing });

      // ✅ CRITICAL FIX: Save profile to Node backend (port 5000 / MongoDB) FIRST.
      // The Dashboard reads from Node via getProfile(). If we skip this step,
      // the Dashboard sees no goal/weight and instantly redirects back to /profile-setup.
      const fullName = [firstName.trim(), lastName.trim()].filter(Boolean).join(' ');
      const nodeProfilePayload = {
        ...profileUpdate,
        ...(fullName && { name: fullName }),
        ...(userAvatar !== undefined ? { avatar: userAvatar } : {}),
      };
      try {
        await saveProfile(nodeProfilePayload);
        console.log('✅ Profile saved to Node backend (MongoDB)');
      } catch (nodeErr) {
        console.error('❌ Could not save to Node backend:', nodeErr?.message || nodeErr);
        throw new Error('Unable to save profile to main database. Please ensure Node backend (port 5000) is running and try again.');
      }

      let response = {
        success: true,
        regenerated_workout: null,
        regenerated_nutrition: null,
        errors: []
      };

      if (!skipPlanRegeneration) {
        // Call the Python backend to regenerate workout/nutrition plans
        response = await updateProfileWithRegeneration(profileUpdate, {
          timeout: 15000,
          retryCount: 2,
          onRetry: (attempt) => {
            showInfo(`Retrying... Attempt ${attempt + 1}`, 2000);
          }
        });
      }

      console.log('✅ Profile update response:', response);

      if (response.success) {
        // ✅ FIX 10: Invalidate nutrition cache so Nutrition page fetches fresh plan
        console.log('🗑️ Invalidating nutrition cache and syncing regenerated workout plan...');
        setToStorage(StorageKeys.NUTRITION_CACHE_INVALID, 'true');
        removeFromStorage(StorageKeys.NUTRITION_CACHE);
        removeFromStorage(StorageKeys.NUTRITION_CACHE_DATE);
        // Also set profile update timestamp for cross-page awareness
        setToStorage(StorageKeys.PROFILE_UPDATED_AT, new Date().toISOString());

        if (response.regenerated_workout?.plan) {
          const currentWorkoutPlan = safeJSONParse('workoutPlan', []);
          const mergedWorkoutPlan = timing === 'immediate'
            ? mergeWorkoutPlanFromToday(currentWorkoutPlan, response.regenerated_workout.plan)
            : response.regenerated_workout.plan;

          localStorage.setItem('workoutPlan', JSON.stringify(mergedWorkoutPlan));
          localStorage.setItem('workoutPlanTimestamp', new Date().toISOString());
          localStorage.setItem('workoutPlanProfile', JSON.stringify({
            goal: profileUpdate.goal,
            experience: profileUpdate.experience,
            equipment: Array.isArray(profileUpdate.equipment) ? [...profileUpdate.equipment].sort() : [],
            body_issues: Array.isArray(profileUpdate.body_issues) ? [...profileUpdate.body_issues].sort() : [],
            days_per_week: profileUpdate.days_per_week || 4,
            weight: profileUpdate.weight,
            height: profileUpdate.height,
            age: profileUpdate.age,
            gender: profileUpdate.gender,
          }));
          console.log('✅ Regenerated workout plan synced (past days preserved, future days updated)');
        }

        // ✅ Persist regenerated nutrition plan with proper StorageKeys
        // Wrap raw plan in cache-compatible format that Nutrition.jsx expects
        if (response.regenerated_nutrition?.plan) {
          const rawPlan = response.regenerated_nutrition.plan;
          // ✅ FIX PA-5: profileHash MUST match the format Nutrition.jsx uses at line 185:
          //    `${profile.weight}-${profile.height}-${profile.goal}-${profile.dietary_preference || ''}-${profile.age}`
          const profileHash = `${profileUpdate.weight}-${profileUpdate.height}-${profileUpdate.goal}-${profileUpdate.dietary_preference || ''}-${profileUpdate.age}`;

          // Normalize multiple backend nutrition shapes to the frontend cache shape.
          // Supported: { days: [...] }, { meals: [...] }, { weekly_plan: { Monday: {...} } }
          let normalizedDays = [];
          if (Array.isArray(rawPlan.days) && rawPlan.days.length > 0) {
            normalizedDays = rawPlan.days;
          } else if (Array.isArray(rawPlan.meals) && rawPlan.meals.length > 0) {
            normalizedDays = rawPlan.meals;
          } else if (rawPlan.weekly_plan && typeof rawPlan.weekly_plan === 'object') {
            const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
            const baseDate = new Date();

            normalizedDays = dayNames.map((dayName, idx) => {
              const date = new Date(baseDate);
              date.setDate(baseDate.getDate() + idx);
              const dayMeals = rawPlan.weekly_plan?.[dayName] || {};

              const meals = ['breakfast', 'lunch', 'dinner', 'snack'].map((mealType) => {
                const items = Array.isArray(dayMeals?.[mealType]) ? dayMeals[mealType] : [];
                const foods = items.map((item, foodIdx) => ({
                  id: `${mealType}-${item?.name || 'food'}-${idx}-${foodIdx}`,
                  name: item?.name || 'Food Item',
                  calories: Number(item?.calories || 0),
                  protein_g: Number(item?.protein || 0),
                  carbs_g: Number(item?.carbs || 0),
                  fat_g: Number(item?.fat || 0),
                  swap_group: item?.swap_group || ''
                }));

                const totals = {
                  calories: foods.reduce((sum, f) => sum + (Number(f.calories) || 0), 0),
                  protein_g: Math.round(foods.reduce((sum, f) => sum + (Number(f.protein_g) || 0), 0) * 10) / 10,
                  carbs_g: Math.round(foods.reduce((sum, f) => sum + (Number(f.carbs_g) || 0), 0) * 10) / 10,
                  fat_g: Math.round(foods.reduce((sum, f) => sum + (Number(f.fat_g) || 0), 0) * 10) / 10,
                };

                return {
                  name: mealType.charAt(0).toUpperCase() + mealType.slice(1),
                  meal_type: mealType,
                  foods,
                  totals,
                };
              });

              const dailyTotals = {
                calories: meals.reduce((sum, meal) => sum + (Number(meal?.totals?.calories) || 0), 0),
                protein_g: Math.round(meals.reduce((sum, meal) => sum + (Number(meal?.totals?.protein_g) || 0), 0) * 10) / 10,
                carbs_g: Math.round(meals.reduce((sum, meal) => sum + (Number(meal?.totals?.carbs_g) || 0), 0) * 10) / 10,
                fat_g: Math.round(meals.reduce((sum, meal) => sum + (Number(meal?.totals?.fat_g) || 0), 0) * 10) / 10,
              };

              return {
                date: getTodayStr(date),
                day_name: dayName,
                is_today: idx === 0,
                is_future: idx > 0,
                daily_totals: dailyTotals,
                meals,
              };
            });
          }

          if (normalizedDays.length > 0) {
          const cachePayload = {
            ...rawPlan,
            days: normalizedDays,
            daily_target: rawPlan.daily_target || rawPlan.daily_targets || {},
            _profileHash: profileHash,
            _cachedAt: new Date().toISOString()
          };
          setToStorage(StorageKeys.NUTRITION_CACHE, cachePayload);
          // ✅ PA-7: Use local timezone date, same format as Dashboard/Nutrition
          const localToday = getTodayStr();
          setToStorage(StorageKeys.NUTRITION_CACHE_DATE, localToday);
          setToStorage(StorageKeys.NUTRITION_CACHE_INVALID, 'false');
          console.log('✅ Regenerated nutrition plan saved in cache-compatible format');
          }
        }

        // Update user data in localStorage
        const currentUser = safeJSONParse('user', {});
        localStorage.setItem('user', JSON.stringify({
          ...currentUser,
          ...nodeProfilePayload,
          profileComplete: true
        }));
        console.log('✅ User data updated in localStorage');

        // Show success notification
        let successMsg = 'Profile updated successfully!';
        if (timing === 'next_week') {
          successMsg += ' New plans will be applied on Monday.';
        } else if (!skipPlanRegeneration) {
          if (response.regenerated_workout) successMsg += ' Workout plan regenerated.';
          if (response.regenerated_nutrition) successMsg += ' Meal plan regenerated.';
        }
        if (response.errors && response.errors.length > 0) {
          successMsg += ' (Some regenerations will use cached plans)';
        }
        showSuccess(successMsg);

        // Redirect to dashboard after short delay
        setTimeout(() => { navigate('/dashboard'); }, 1500);
      } else {
        throw new Error(response.error || 'Failed to update profile');
      }
    } catch (err) {
      console.error('❌ Profile update error:', err);

      const errorInfo = classifyError(err);
      let userMessage = errorInfo.message;

      switch (errorInfo.type) {
        case 'connection':
        case 'network':
          userMessage = 'Cannot connect to Python backend. Please ensure it\'s running on port 8000.';
          break;
        case 'timeout':
          userMessage = 'Request timed out. The backend is taking too long. Please try again.';
          break;
        case 'authentication':
          userMessage = 'Authentication failed. Please log in again.';
          setTimeout(() => navigate('/'), 2000);
          break;
        case 'validation':
          userMessage = `Invalid data: ${errorInfo.message}`;
          break;
        case 'server':
          userMessage = `Backend error: ${errorInfo.message}. Please try again.`;
          break;
        default:
          userMessage = errorInfo.message;
      }

      showError(userMessage);
    } finally {
      setLoading(false);
    }
  };

  const isNoneEquipmentChecked = formData.equipment.includes('None (Bodyweight Only)') || formData.equipment.includes('None');
  const isNoneAllergiesChecked = formData.allergies.includes('None');
  const isNoneIssuesChecked = formData.body_issues.includes('None');

  return (
    <>
      <style>{`
        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-30px); } }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        
        .unified-input:hover, input:hover:not(:focus), select:hover:not(:focus) {
            border-color: #cbd5e1 !important;
            background: #fff !important;
            transform: translateY(-1px);
        }
        input:focus, select:focus { outline: none; border-color: #6366f1 !important; background: #fff !important; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important; transform: translateY(-2px); }
        button:hover:not(:disabled) { transform: translateY(-3px); box-shadow: 0 15px 35px rgba(99, 102, 241, 0.4); }
        button:active:not(:disabled) { transform: translateY(-1px); box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3); }
        div::-webkit-scrollbar { width: 6px; }
        div::-webkit-scrollbar-track { background: transparent; }
        div::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        
        .form-section {
            padding: 18px;
            border-radius: 20px;
            border: 1px solid transparent;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            margin-bottom: 12px;
        }
        .form-section:hover {
            background: #fff;
            box-shadow: 0 15px 40px rgba(99, 102, 241, 0.1);
            border-color: rgba(99, 102, 241, 0.3);
            transform: translateY(-2px);
        }

        @media (max-width: 480px) {
            form { padding: 16px; }
            .container { padding: 10px; }
            .wrapper { max-width: 100%; margin: 0; }
            h1 { font-size: 24px; }
            h2 { font-size: 16px; }
            .headerRow {
                flex-direction: column;
                gap: 16px;
                align-items: center;
            }
            .avatarWrapper {
                width: 80px;
                height: 80px;
            }
            .avatarImage {
                font-size: 32px;
            }
            .nameGroup {
                flex-direction: column !important;
                width: 100%;
            }
            .formGroup {
                width: 100%;
            }
            .form-row-4, .form-row-3 {
                grid-template-columns: 1fr !important;
                gap: 16px;
            }
            .sectionTitle {
                font-size: 16px;
                margin-bottom: 12px;
            }
            .label {
                font-size: 11px;
            }
            .input, .select {
                padding: 12px;
                font-size: 13px;
            }
            .multiSelectButton {
                padding: 12px;
                font-size: 13px;
            }
            .selectedTag {
                font-size: 10px;
                padding: 4px 8px;
            }
            .button {
                padding: 14px;
                font-size: 14px;
                margin-top: 10px;
            }
            .orbBase { display: none; }
        }

        @media (min-width: 481px) and (max-width: 768px) {
            form { padding: 20px; }
            h1 { font-size: 28px; }
            .nameGroup { flex-direction: column !important; }
            .form-row-4, .form-row-3 { grid-template-columns: 1fr !important; }
        }
      `}</style>

      {/* CONDITIONAL: Show Cancel button when editing, Logout when setting up */}
      {isEditing ? (
        <button onClick={() => navigate('/dashboard')} style={styles.cancelBtn}>
          CANCEL
        </button>
      ) : (
        <button onClick={() => { if(typeof onLogout === 'function') onLogout(); else { logoutSafe(); navigate('/'); } }} style={styles.cancelBtn}>
          LOGOUT
        </button>
      )}

      <div style={styles.container}>
        <div style={{ ...styles.orbBase, ...styles.orb1 }}></div>
        <div style={{ ...styles.orbBase, ...styles.orb2 }}></div>

        <div style={styles.wrapper}>
          <div style={styles.header}>
            <h1 style={styles.headerH1}>{isEditing ? "Update Profile" : "Fitness Profile"}</h1>
            <p style={styles.headerP}>{isEditing ? "Refine your plan to match your new goals" : "Tell us about yourself to generate your AI plan"}</p>
          </div>

          <form onSubmit={handleSubmit} style={styles.form}>
            
            <div style={styles.headerRow}>
              <div>
                <div style={styles.avatarWrapper}>
                  <div style={styles.avatarImage} onClick={() => fileInputRef.current.click()}>
                    {userAvatar ? <img src={userAvatar} alt="Profile" style={{width:'100%', height:'100%', borderRadius:'50%', objectFit:'cover'}} /> : (firstName ? firstName.charAt(0).toUpperCase() : 'U')}
                  </div>
                  {userAvatar && <div style={styles.removeBtn} onClick={handleRemoveImage} title="Remove Photo">✕</div>}
                </div>
                <label style={styles.uploadLabel} onClick={() => fileInputRef.current.click()}>
                  {userAvatar ? "Change Photo" : "Upload Photo"}
                </label>
                <input type="file" ref={fileInputRef} style={{display:'none'}} accept="image/*" onChange={handleImageUpload} />
              </div>

              <div style={styles.nameGroup} className="nameGroup">
                <div style={styles.formGroup}>
                    <label style={styles.label}>First Name</label>
                    <input style={styles.input} type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="John" required />
                </div>
                <div style={styles.formGroup}>
                    <label style={styles.label}>Last Name</label>
                    <input style={styles.input} type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="Doe" />
                </div>
              </div>
            </div>

            {/* 1. Basic Info */}
            <div className="form-section">
                <h3 style={styles.sectionTitle}>
                    <div style={styles.sectionIcon}>📊</div> Basic Metrics
                </h3>
                <div style={styles.formRow4} className="form-row-4">
                  <div style={styles.formGroup}><label style={styles.label}>Age</label><input style={styles.input} type="number" name="age" value={formData.age} onChange={handleChange} placeholder="Years" required /></div>
                  <div style={styles.formGroup}><label style={styles.label}>Weight (kg)</label><input style={styles.input} type="number" name="weight" value={formData.weight} onChange={handleChange} placeholder="kg" step="0.1" required /></div>
                  <div style={styles.formGroup}><label style={styles.label}>Height (cm)</label><input style={styles.input} type="number" name="height" value={formData.height} onChange={handleChange} placeholder="cm" required /></div>
                  <div style={styles.formGroup}><label style={styles.label}>Gender</label><select style={styles.select} name="gender" value={formData.gender} onChange={handleChange}><option>Male</option><option>Female</option></select></div>
                </div>
            </div>

            {/* 2. Goals */}
            <div className="form-section">
                <h3 style={styles.sectionTitle}>
                    <div style={styles.sectionIcon}>🎯</div> Goals & Lifestyle
                </h3>
                <div style={styles.formRow3} className="form-row-3">
                  <div style={styles.formGroup}><label style={styles.label}>Primary Goal</label><select style={styles.select} name="goal" value={formData.goal} onChange={handleChange}><option>Muscle Gain</option><option>Weight Loss</option><option>Maintenance</option></select></div>
                  <div style={styles.formGroup}><label style={styles.label}>Experience Level</label><select style={styles.select} name="experience" value={formData.experience} onChange={handleChange}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div>
                  <div style={styles.formGroup}><label style={styles.label}>Diet Type</label><select style={styles.select} name="dietary_preference" value={formData.dietary_preference} onChange={handleChange}><option>Non-Veg</option><option>Veg</option><option>Vegan</option></select></div>
                </div>
            </div>

            {/* 3. Customization */}
            <div className="form-section">
              <h3 style={styles.sectionTitle}>
                <div style={styles.sectionIcon}>⚕️</div> Health & Customization
              </h3>
              
              <div style={styles.formRow3} className="form-row-3">
                <div style={styles.formGroup}>
                  <label style={styles.label}>Available Equipment</label>
                  <MultiSelect 
                    name="equipment" 
                    options={[
                      // ── Essential (bodyweight baseline) ────────────────
                      'None (Bodyweight Only)',
                      'Dumbbells',
                      'Resistance Bands',
                      'Kettlebell',
                      // ── Upgrade Kit ────────────────────────────────────
                      'Weighted Vest',
                      'Medicine Ball',
                      'Stability / Yoga Ball',
                      'Pull-up Bar',
                      // ── Accessories ────────────────────────────────────
                      'Foam Roller',
                      'Ab Wheel',
                      'Jump Rope',
                      'Bosu Ball',
                      'Resistance Bands (Light)',
                    ]}
                    value={formData.equipment} 
                    onChange={handleCheckbox}
                    isOpen={openDropdown === 'equipment'}
                    onToggle={() => setOpenDropdown(openDropdown === 'equipment' ? null : 'equipment')}
                    isNoneChecked={isNoneEquipmentChecked}
                  />
                </div>

                <div style={styles.formGroup}>
                  <label style={styles.label}>Food Allergies</label>
                  <MultiSelect 
                    name="allergies" 
                    options={['None', 'Gluten', 'Lactose', 'Nuts', 'Eggs']} 
                    value={formData.allergies} 
                    onChange={handleCheckbox}
                    isOpen={openDropdown === 'allergies'}
                    onToggle={() => setOpenDropdown(openDropdown === 'allergies' ? null : 'allergies')}
                    isNoneChecked={isNoneAllergiesChecked}
                  />
                </div>

                <div style={styles.formGroup}>
                  <label style={styles.label}>Body Issues / Health</label>
                  <MultiSelect 
                    name="body_issues" 
                    options={['None', 'Diabetes', 'High BP', 'Back Pain', 'Knee Pain']} 
                    value={formData.body_issues} 
                    onChange={handleCheckbox}
                    isOpen={openDropdown === 'body_issues'}
                    onToggle={() => setOpenDropdown(openDropdown === 'body_issues' ? null : 'body_issues')}
                    isNoneChecked={isNoneIssuesChecked}
                  />
                </div>
              </div>
            </div>

            <button type="submit" style={{...styles.button, ...(loading && styles.buttonDisabled), marginTop: '15px'}} disabled={loading}>
              {loading ? "Analyzing Data..." : (isEditing ? "Save Changes" : "Generate My Plan →")}
            </button>

          </form>
        </div>
      </div>
      
      {/* Regeneration Timing Dialog */}
      {regenerateDialog.show && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}>
          <div style={{
            background: 'linear-gradient(145deg, #1e293b 0%, #0f172a 100%)',
            borderRadius: '24px',
            padding: '40px',
            maxWidth: '500px',
            width: '90%',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            boxShadow: '0 25px 80px rgba(0,0,0,0.5)'
          }}>
            <div style={{ textAlign: 'center', marginBottom: '30px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📅</div>
              <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#fff', marginBottom: '12px' }}>
                When to Apply Changes?
              </h2>
              <p style={{ fontSize: '14px', color: '#94a3b8', lineHeight: '1.6' }}>
                Your profile changes will affect your workout and meal plans.
              </p>
            </div>

            {/* What changes */}
            <div style={{
              background: 'rgba(99, 102, 241, 0.1)',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '30px'
            }}>
              <div style={{ fontSize: '12px', fontWeight: '700', color: '#6366f1', textTransform: 'uppercase', marginBottom: '12px' }}>
                Changes Detected:
              </div>
              <div style={{ fontSize: '14px', color: '#e2e8f0', lineHeight: '1.8' }}>
                {regenerateDialog.changesAffectWorkout && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span>💪</span>
                    <span>Workout plan will be updated</span>
                  </div>
                )}
                {regenerateDialog.changesAffectMeal && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span>🍽️</span>
                    <span>Meal plan will be updated</span>
                  </div>
                )}
              </div>
            </div>

            {/* Options */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
              <button
                onClick={() => handleRegenerateChoice('next_week')}
                style={{
                  padding: '16px',
                  background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '15px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)',
                  textAlign: 'left',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}
              >
                <span>📅 Apply Next Week (Recommended)</span>
                <span style={{ fontSize: '12px', fontWeight: '500', opacity: 0.8 }}>
                  Finish current week, new plans start Monday
                </span>
              </button>

              <button
                onClick={() => handleRegenerateChoice('immediate')}
                style={{
                  padding: '16px',
                  background: 'rgba(255,255,255,0.1)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '12px',
                  fontSize: '15px',
                  fontWeight: '700',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  textAlign: 'left',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}
              >
                <span>⚡ Apply Immediately</span>
                <span style={{ fontSize: '12px', fontWeight: '500', opacity: 0.8 }}>
                  Current week progress will be reset
                </span>
              </button>
            </div>

            {/* Cancel */}
            <button
              onClick={() => handleRegenerateChoice('cancel')}
              style={{
                width: '100%',
                padding: '14px',
                background: 'transparent',
                color: '#94a3b8',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default ProfileSetup;