import React, { useState } from 'react';

const UserProfile = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        age: '',
        gender: '',
        weight: '',
        height: '',
        goal: '',
        experience: '',
        equipment: [],
        body_issues: [],
        dietary_preference: '',
        allergies: []
    });

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        try {
            const response = await fetch('http://localhost:8000/api/users/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                setMessage('✅ Profile saved successfully!');
            } else {
                setMessage('❌ Failed to save profile');
            }
        } catch (error) {
            setMessage('❌ Error: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const styles = {
        container: {
            maxWidth: '600px',
            margin: '50px auto',
            padding: '30px',
            background: 'white',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        },
        heading: {
            textAlign: 'center',
            marginBottom: '30px',
            color: '#333'
        },
        form: {
            display: 'flex',
            flexDirection: 'column',
            gap: '15px'
        },
        input: {
            padding: '12px',
            border: '1px solid #ddd',
            borderRadius: '5px',
            fontSize: '16px'
        },
        button: {
            padding: '12px',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
        },
        buttonDisabled: {
            padding: '12px',
            background: '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'not-allowed',
            fontSize: '16px',
            fontWeight: 'bold'
        },
        message: {
            textAlign: 'center',
            marginTop: '10px',
            fontWeight: 'bold'
        }
    };

    return (
        <div style={styles.container}>
            <h2 style={styles.heading}>Create Your Profile</h2>
            <form onSubmit={handleSubmit} style={styles.form}>
                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    value={formData.username}
                    onChange={handleChange}
                    style={styles.input}
                    required
                />
                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={handleChange}
                    style={styles.input}
                    required
                />
                <input
                    type="number"
                    name="age"
                    placeholder="Age"
                    value={formData.age}
                    onChange={handleChange}
                    style={styles.input}
                    required
                />
                <select 
                    name="gender" 
                    value={formData.gender} 
                    onChange={handleChange} 
                    style={styles.input}
                    required
                >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                </select>
                <input
                    type="number"
                    name="weight"
                    placeholder="Weight (kg)"
                    value={formData.weight}
                    onChange={handleChange}
                    style={styles.input}
                    required
                />
                <input
                    type="number"
                    name="height"
                    placeholder="Height (cm)"
                    value={formData.height}
                    onChange={handleChange}
                    style={styles.input}
                    required
                />
                <select 
                    name="goal" 
                    value={formData.goal} 
                    onChange={handleChange} 
                    style={styles.input}
                    required
                >
                    <option value="">Select Goal</option>
                    <option value="Weight Loss">Weight Loss</option>
                    <option value="Muscle Gain">Muscle Gain</option>
                    <option value="Maintenance">Maintenance</option>
                </select>
                <select 
                    name="experience" 
                    value={formData.experience} 
                    onChange={handleChange} 
                    style={styles.input}
                    required
                >
                    <option value="">Select Experience</option>
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                </select>
                <select 
                    name="dietary_preference" 
                    value={formData.dietary_preference} 
                    onChange={handleChange} 
                    style={styles.input}
                    required
                >
                    <option value="">Select Dietary Preference</option>
                    <option value="Veg">Vegetarian</option>
                    <option value="Non-Veg">Non-Vegetarian</option>
                </select>
                
                <button 
                    type="submit" 
                    disabled={loading}
                    style={loading ? styles.buttonDisabled : styles.button}
                >
                    {loading ? 'Saving...' : 'Save Profile'}
                </button>

                {message && <p style={styles.message}>{message}</p>}
            </form>
        </div>
    );
};

export default UserProfile;