import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser, loginWithGoogle } from '../api'; // Import API bridge
import { loadGoogleSDK } from "../utils/googleAuth";
import '../App.css';

import { syncUserSession, persistSessionUser } from '../utils/sessionUtils';

const SUBMIT_COOLDOWN_MS = 1200;

const getRegisterErrorMessage = (err) => {
    const validationErrors = err?.response?.data?.errors;
    if (Array.isArray(validationErrors) && validationErrors.length > 0) {
        return validationErrors
            .map((item) => item?.message || item?.msg || 'Invalid input')
            .filter(Boolean)
            .join(' ');
    }

    return err?.response?.data?.message || 'Registration failed';
};


const Register = () => {
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        password: ''
    });

    const [error, setError] = useState('');
    const [success, setSuccess] = useState(''); // New state for success message
    const [notification, setNotification] = useState({ show: false, message: '', type: '' }); // State for notification messages
    const [loading, setLoading] = useState(false);
    const [, setFocused] = useState(null);
    const [showPassword, setShowPassword] = useState(false);
    const lastSubmitAtRef = useRef(0);
    const navigate = useNavigate();
    const googleAuthEnabled = String(import.meta.env.VITE_ENABLE_GOOGLE_AUTH || 'true').toLowerCase() === 'true';

    // Initialize Google SDK after component mounts
    useEffect(() => {
        if (googleAuthEnabled) {
            loadGoogleSDK('google-signup-button', handleGoogleResponse, (errorMessage) => {
                setNotification({
                    show: true,
                    message: errorMessage,
                    type: 'error'
                });
                // Hide notification after 5 seconds
                setTimeout(() => {
                    setNotification({ show: false, message: '', type: '' });
                }, 5000);
            });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [googleAuthEnabled]);


    const handleGoogleResponse = async (response) => {
        try {
            setLoading(true);
            setError("");

            // Send the Google token to our backend
            const { data } = await loginWithGoogle(response.credential);

            // Save token and user info
            syncUserSession(data.user);
            persistSessionUser(data.user);

            // Since Google users are already registered, redirect to profile setup or dashboard
            navigate("/profile-setup", { replace: true });
        } catch (err) {
            console.error("Google Sign-Up Error:", err);
            setError(err.response?.data?.error || "Google authentication failed");
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        const now = Date.now();
        if (now - lastSubmitAtRef.current < SUBMIT_COOLDOWN_MS) {
            setError('Please wait a moment before trying again.');
            return;
        }
        lastSubmitAtRef.current = now;

        const name = formData.full_name.trim();
        const email = formData.email.trim();
        const password = formData.password;

        if (name.length < 2 || name.length > 80) {
            setError('Full name must be between 2 and 80 characters.');
            return;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            setError('Please enter a valid email address.');
            return;
        }

        if (
            password.length < 8
            || !/[a-z]/.test(password)
            || !/[A-Z]/.test(password)
            || !/[0-9]/.test(password)
            || !/[^A-Za-z0-9]/.test(password)
        ) {
            setError('Password must be 8+ chars with upper, lower, number, and symbol.');
            return;
        }

        setLoading(true);

        try {
            // 1. Call Node.js Backend
            await registerUser({
                name,
                email,
                password
            });

            // 2. SUCCESS: Show stylish message instead of alert
            setSuccess('Account created successfully! Redirecting to login...');

            // 3. Wait 2 seconds, then go to Login
            setTimeout(() => {
                navigate('/login', { replace: true });
            }, 2000);

        } catch (err) {
            console.error(err);
            setError(getRegisterErrorMessage(err));
            setLoading(false); // Only stop loading on error (keep loading spinner on success)
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

                        {/* --- ERROR MESSAGE --- */}
                        {error && (
                            <div className="alert-custom error-shake">
                                {error}
                            </div>
                        )}

                        {/* --- SUCCESS MESSAGE (Stylish Green Box) --- */}
                        {success && (
                            <div className="alert-custom" style={{
                                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                                color: '#4ade80',
                                border: '1px solid rgba(34, 197, 94, 0.2)',
                                textAlign: 'center',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '8px'
                            }}>
                                <span>✅</span> {success}
                            </div>
                        )}

                        {/* --- NOTIFICATION MESSAGE --- */}
                        {notification.show && (
                            <div className={`alert-custom ${notification.type}-notification`} style={{
                                backgroundColor: notification.type === 'error'
                                    ? 'rgba(239, 68, 68, 0.1)'
                                    : notification.type === 'warning'
                                        ? 'rgba(245, 158, 11, 0.1)'
                                        : 'rgba(34, 197, 94, 0.1)',
                                color: notification.type === 'error'
                                    ? '#fecaca'
                                    : notification.type === 'warning'
                                        ? '#fde68a'
                                        : '#a7f3d0',
                                border: notification.type === 'error'
                                    ? '1px solid rgba(239, 68, 68, 0.3)'
                                    : notification.type === 'warning'
                                        ? '1px solid rgba(245, 158, 11, 0.3)'
                                        : '1px solid rgba(34, 197, 94, 0.3)',
                                textAlign: 'center',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '8px'
                            }}>
                                <span>{notification.type === 'error' ? '❌' : notification.type === 'warning' ? '⚠️' : 'ℹ️'}</span> {notification.message}
                            </div>
                        )}

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
                                        maxLength={80}
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
                                        maxLength={120}
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
                                        maxLength={128}
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
                                disabled={loading || success} // Disable button if loading or success (prevents double submit)
                                style={success ? { opacity: 0.7, cursor: 'default' } : {}}
                            >
                                <span className="btn-text">
                                    {success ? "Redirecting..." : (loading ? "Creating Account..." : "Sign Up")}
                                </span>
                                {!success && <span className="btn-icon">→</span>}
                            </button>
                        </form>

                        <div className="divider">
                            <span>OR</span>
                        </div>

                        <div className="social-login-google">
                            {googleAuthEnabled ? <div id="google-signup-button"></div> : null}
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