import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import '../App.css';

const Register = () => {
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [focused, setFocused] = useState(null);
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await axios.post('http://127.0.0.1:8000/auth/register', formData);
            alert("Registration Successful! Please Login.");
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.detail || "Registration failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container dark-theme">
            {/* Animated Background Elements */}
            <div className="fitness-bg-element">💪</div>
            <div className="fitness-bg-element">🏃</div>
            <div className="fitness-bg-element">🥗</div>
            <div className="fitness-bg-element">📊</div>

            {/* Animated gradient orbs */}
            <div className="animated-orb orb-1"></div>
            <div className="animated-orb orb-2"></div>
            <div className="animated-orb orb-3"></div>

            <div className="login-card dark-card">
                <div className="login-left">
                    <div className="left-content">
                        <h1>Elevate</h1>
                        <p className="subtitle">Start Your Fitness Journey Today</p>

                        <div className="login-left-feature">
                            <div className="feature-item">
                                <span className="feature-icon">🎯</span>
                                <span className="feature-text">Set Custom Goals</span>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">🔥</span>
                                <span className="feature-text">Track Workouts</span>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">📱</span>
                                <span className="feature-text">Mobile Friendly</span>
                            </div>
                            <div className="feature-item">
                                <span className="feature-icon">🏆</span>
                                <span className="feature-text">Achieve Success</span>
                            </div>
                        </div>

                        <div className="stats-showcase">
                            <div className="stat-box">Join thousands building their best selves</div>
                            <div className="stat-box">Personalized workout & nutrition plans</div>
                            <div className="stat-box">Community support & expert guidance</div>
                        </div>
                    </div>
                </div>

                <div className="login-right">
                    <div className="right-content">
                        <div className="welcome-header">
                            <h3>Create Account</h3>
                            <p className="login-subtitle">Join our fitness community today</p>
                        </div>

                        {error && <div className="alert-custom">{error}</div>}

                        <form onSubmit={handleRegister}>
                            <div className="form-group-custom">
                                <label htmlFor="fullname">
                                    <span className="label-icon">👤</span>
                                    Full Name
                                </label>
                                <div className="input-wrapper">
                                    <input
                                        id="fullname"
                                        type="text"
                                        name="full_name"
                                        placeholder="Enter your full name"
                                        onChange={handleChange}
                                        onFocus={() => setFocused('fullname')}
                                        onBlur={() => setFocused(null)}
                                        value={formData.full_name}
                                        required
                                    />
                                    <div className="input-underline"></div>
                                </div>
                            </div>

                            <div className="form-group-custom">
                                <label htmlFor="email">
                                    <span className="label-icon">📧</span>
                                    Email Address
                                </label>
                                <div className="input-wrapper">
                                    <input
                                        id="email"
                                        type="email"
                                        name="email"
                                        placeholder="Enter your email"
                                        onChange={handleChange}
                                        onFocus={() => setFocused('email')}
                                        onBlur={() => setFocused(null)}
                                        value={formData.email}
                                        required
                                    />
                                    <div className="input-underline"></div>
                                </div>
                            </div>

                            <div className="form-group-custom">
                                <label htmlFor="password">
                                    <span className="label-icon">🔑</span>
                                    Password
                                </label>
                                <div className="input-wrapper">
                                    <input
                                        id="password"
                                        type={showPassword ? "text" : "password"}
                                        name="password"
                                        placeholder="Create a strong password"
                                        onChange={handleChange}
                                        onFocus={() => setFocused('password')}
                                        onBlur={() => setFocused(null)}
                                        value={formData.password}
                                        required
                                    />
                                    <button 
                                        type="button" 
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="password-toggle"
                                    >
                                        {showPassword ? "👁️" : "👁️‍🗨️"}
                                    </button>
                                    <div className="input-underline"></div>
                                </div>
                            </div>

                            <button
                                type="submit"
                                className="btn-login"
                                disabled={loading}
                            >
                                <span className="btn-text">
                                    {loading ? "Creating Account..." : "Sign Up"}
                                </span>
                                <span className="btn-icon">→</span>
                            </button>
                        </form>

                        <div className="divider">
                            <span>OR</span>
                        </div>

                        <div className="social-login-google">
                            <button className="social-btn google-btn" type="button">
                                <span>🔵</span>
                                Sign up with Google
                            </button>
                        </div>

                        <div className="login-footer">
                            <small>
                                Already have an account? <Link to="/login" className="signup-link">Sign In</Link>
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;