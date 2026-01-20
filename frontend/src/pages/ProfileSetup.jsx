import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

// --- STYLES ---
const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)',
    padding: '40px 20px', position: 'relative', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Inter', sans-serif"
  },
  orbBase: { position: 'absolute', borderRadius: '50%', opacity: 0.15, filter: 'blur(80px)', animation: 'float 8s ease-in-out infinite' },
  orb1: { width: '400px', height: '400px', background: '#6366f1', top: '-100px', left: '-100px' },
  orb2: { width: '350px', height: '350px', background: '#ec4899', bottom: '-50px', right: '-50px', animation: 'float 10s ease-in-out infinite reverse' },
  
  wrapper: { maxWidth: '1100px', width: '100%', position: 'relative', zIndex: 10 }, // Increased max-width slightly for 3 cols
  
  header: { textAlign: 'center', marginBottom: '30px', animation: 'slideDown 0.8s ease-out' },
  headerH1: { fontSize: '42px', fontWeight: 900, color: '#ffffff', marginBottom: '8px', letterSpacing: '-1px', textShadow: '0 4px 10px rgba(0,0,0,0.3)' },
  headerP: { fontSize: '16px', color: '#cbd5e1', fontWeight: 400, letterSpacing: '0.3px' },
  
  form: {
    background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)', 
    borderRadius: '24px', padding: '40px',
    boxShadow: '0 25px 70px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255,255,255,0.5)', 
    animation: 'slideUp 0.8s ease-out',
    position: 'relative', overflow: 'visible',
    border: '1px solid rgba(99, 102, 241, 0.1)'
  },
  
  headerRow: { display: 'flex', gap: '30px', alignItems: 'center', marginBottom: '30px', borderBottom: '2px dashed #e2e8f0', paddingBottom: '30px' },
  avatarWrapper: { position: 'relative', width: '110px', height: '110px', flexShrink: 0 },
  avatarImage: { 
    width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover', 
    background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', 
    fontSize: '40px', fontWeight: '700', color: '#6366f1', 
    border: '4px solid #ffffff', cursor: 'pointer', 
    boxShadow: '0 10px 25px rgba(99, 102, 241, 0.25)' 
  },
  removeBtn: { position: 'absolute', top: 0, right: -5, background: '#ef4444', color: '#fff', width: '26px', height: '26px', borderRadius: '50%', border: '2px solid #fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', cursor: 'pointer', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' },
  uploadLabel: { fontSize: '13px', color: '#6366f1', fontWeight: '700', marginTop: '12px', textAlign: 'center', cursor: 'pointer', display: 'block', transition: 'color 0.2s' },
  nameGroup: { flex: 1, display: 'flex', gap: '15px' },

  sectionTitle: { 
    fontSize: '18px', fontWeight: 800, color: '#1e293b', marginBottom: '20px', 
    display: 'flex', alignItems: 'center', gap: '10px', letterSpacing: '-0.3px'
  },
  sectionIcon: { 
    background: 'rgba(99, 102, 241, 0.1)', color: '#6366f1', 
    width: '32px', height: '32px', borderRadius: '8px', 
    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' 
  },
  
  // Grids
  formRow4: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' },
  formRow3: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' },
  
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
    maxHeight: '220px', overflowY: 'auto', zIndex: 9999,
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)'
  },
  checkboxOption: { display: 'flex', alignItems: 'center', padding: '12px 16px', borderBottom: '1px solid #f1f5f9', cursor: 'pointer', transition: 'all 0.2s ease', fontSize:'13px', fontWeight:'500', color:'#475569' },
  checkboxInput: { width: '16px', height: '16px', marginRight: '12px', cursor: 'pointer', accentColor: '#6366f1' },
  selectedItems: { display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '10px' },
  selectedTag: { display: 'inline-flex', alignItems: 'center', gap: '5px', background: '#eef2ff', color: '#4f46e5', padding: '6px 12px', borderRadius: '8px', fontSize: '12px', fontWeight: '700', border:'1px solid #c7d2fe' },

  button: {
    width: '100%', padding: '16px', marginTop: '20px', 
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
            const isOptionDisabled = isNoneChecked && option !== 'None';
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

function ProfileSetup() {
  const navigate = useNavigate();
  const location = useLocation();
  const isEditing = location.state?.isEditing || false;
  
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [userAvatar, setUserAvatar] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [openDropdown, setOpenDropdown] = useState(null);
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    age: '', weight: '', height: '', gender: 'Male', 
    goal: 'Muscle Gain', experience: 'Beginner', dietary_preference: 'Non-Veg', 
    equipment: [], allergies: [], body_issues: [] 
  });

  const logActivity = (type, actionName, details) => {
    const newLog = {
      name: actionName,
      date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      details: details,
      type: type
    };
    const currentHistory = JSON.parse(localStorage.getItem('activityHistory') || "[]");
    localStorage.setItem('activityHistory', JSON.stringify([newLog, ...currentHistory]));
  };

  useEffect(() => {
    const storedFirst = localStorage.getItem('firstName');
    const storedLast = localStorage.getItem('lastName');
    if (storedFirst) setFirstName(storedFirst);
    if (storedLast) setLastName(storedLast);
    
    if (!storedFirst && localStorage.getItem('userName')) {
        const full = localStorage.getItem('userName');
        const parts = full.split(' ');
        setFirstName(parts[0]);
        if(parts.length > 1) setLastName(parts.slice(1).join(' '));
    }

    const storedAvatar = localStorage.getItem('userAvatar');
    if (storedAvatar) setUserAvatar(storedAvatar);
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
    if (value === 'None') {
      updatedList = checked ? ['None'] : updatedList.filter(item => item !== 'None');
    } else {
      if (updatedList.includes('None')) updatedList = updatedList.filter(item => item !== 'None');
      updatedList = checked ? [...updatedList, value] : updatedList.filter(item => item !== value);
    }
    setFormData({ ...formData, [type]: updatedList });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!firstName.trim()) {
        alert("Please enter your first name!");
        setLoading(false); return;
    }
    
    localStorage.setItem('firstName', firstName.trim());
    localStorage.setItem('lastName', lastName.trim());
    localStorage.setItem('userName', `${firstName.trim()} ${lastName.trim()}`);

    const userId = localStorage.getItem('userId');
    if (!userId) {
        setError("User ID missing. Please login again.");
        setLoading(false); return;
    }

    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      logActivity('profile', isEditing ? 'Profile Updated' : 'Setup Complete', 'Updated user stats');
      alert(isEditing ? "Profile Updated!" : "Setup Complete!");
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      setError("Failed to save profile. Is backend running?");
    } finally {
      setLoading(false);
    }
  };

  const isNoneEquipmentChecked = formData.equipment.includes('None');
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
            padding: 25px;
            border-radius: 20px;
            border: 1px solid transparent; 
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            margin-bottom: 15px;
        }
        .form-section:hover {
            background: #fff;
            box-shadow: 0 15px 40px rgba(99, 102, 241, 0.1);
            border-color: rgba(99, 102, 241, 0.3);
            transform: translateY(-3px);
        }

        @media (max-width: 768px) { 
            form { padding: 25px; } 
            h1 { font-size: 28px; } 
            .nameGroup { flex-direction: column !important; }
            .form-row-4, .form-row-3 { grid-template-columns: 1fr !important; } 
        }
      `}</style>

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
                <div style={styles.formRow4}>
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
                <div style={styles.formRow3}>
                  <div style={styles.formGroup}><label style={styles.label}>Primary Goal</label><select style={styles.select} name="goal" value={formData.goal} onChange={handleChange}><option>Muscle Gain</option><option>Weight Loss</option><option>Maintenance</option></select></div>
                  <div style={styles.formGroup}><label style={styles.label}>Experience Level</label><select style={styles.select} name="experience" value={formData.experience} onChange={handleChange}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div>
                  <div style={styles.formGroup}><label style={styles.label}>Diet Type</label><select style={styles.select} name="dietary_preference" value={formData.dietary_preference} onChange={handleChange}><option>Non-Veg</option><option>Veg</option><option>Vegan</option></select></div>
                </div>
            </div>

            {/* 3. Customization (UPDATED TO 3 COLUMNS) */}
            <div className="form-section">
              <h3 style={styles.sectionTitle}>
                <div style={styles.sectionIcon}>⚕️</div> Health & Customization
              </h3>
              
              {/* NOW A SINGLE ROW WITH 3 COLUMNS */}
              <div style={styles.formRow3}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Available Equipment</label>
                  <MultiSelect 
                    name="equipment" 
                    options={['None', 'Dumbbells', 'Yoga Mat', 'Resistance Bands', 'Pull-up Bar']} 
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

            <button type="submit" style={{...styles.button, ...(loading && styles.buttonDisabled)}} disabled={loading}>
              {loading ? "Analyzing Data..." : (isEditing ? "Save Changes" : "Generate My Plan →")}
            </button>

          </form>
        </div>
      </div>
    </>
  );
}

export default ProfileSetup;