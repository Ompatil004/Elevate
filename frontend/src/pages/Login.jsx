import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useNotification } from "../components/NotificationProvider";
import { loginUser, getProfile, loginWithGoogle } from "../api";
import { loadGoogleSDK } from "../utils/googleAuth";
import "../App.css";

function Login({ setIsAuthenticated }) {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [focused, setFocused] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { showError, showInfo } = useNotification();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
        navigate("/dashboard", { replace: true });
    }
    loadGoogleSDK('google-signin-button', handleGoogleResponse, (errorMessage) => showError(errorMessage, 5000));
  }, [navigate]);

  const handleGoogleResponse = async (response) => {
    try {
      setLoading(true);
      setError("");

      const { data } = await loginWithGoogle(response.credential);

      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      if (setIsAuthenticated) setIsAuthenticated(true);  

      try {
        const profileRes = await getProfile();
        const userProfile = profileRes.data;

        if (userProfile.goal && userProfile.age) {
          navigate("/dashboard", { replace: true });
        } else {
          navigate("/profile-setup", { replace: true });
        }
      } catch (err) {
        navigate("/profile-setup", { replace: true });
      }
    } catch (err) {
      console.error("Google Sign-In Error:", err);
      setError(err.response?.data?.error || "Google authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
        console.log('🔵 Attempting login...');
        const { data } = await loginUser({
            email: formData.email,
            password: formData.password
        });

        console.log('✅ Login response:', data);
        console.log('🔑 Token:', data.token);
        
        localStorage.setItem("token", data.token);
        localStorage.setItem("user", JSON.stringify(data.user));
        
        console.log('💾 Token saved to localStorage');
        
        if (setIsAuthenticated) {
            setIsAuthenticated(true);
        }

        try {
            const profileRes = await getProfile();
            const userProfile = profileRes.data;

            if (userProfile.goal && userProfile.age) {
                navigate("/dashboard", { replace: true });
            } else {
                navigate("/profile-setup", { replace: true });
            }
        } catch (err) {
            navigate("/profile-setup", { replace: true });
        }

    } catch (err) {
        console.error('❌ Login error:', err);
        setError(err.response?.data?.msg || "Invalid email or password");
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="login-container dark-theme">
      <div className="fitness-bg-element">💪</div>
      <div className="fitness-bg-element">🏃</div>
      <div className="fitness-bg-element">🥗</div>
      <div className="fitness-bg-element">📊</div>

      <div className="animated-orb orb-1"></div>
      <div className="animated-orb orb-2"></div>
      <div className="animated-orb orb-3"></div>

      <div className="login-card dark-card">
        <div className="login-left">
          <div className="left-content">
            <h1>Elevate</h1>
            <p className="subtitle">Your Personal Fitness Revolution</p>

            <div className="login-left-feature">
              <div className="feature-item">
                <span className="feature-icon">🏋️</span>
                <span className="feature-text">Workout Plans</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📈</span>
                <span className="feature-text">Progress Tracking</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🍎</span>
                <span className="feature-text">Nutrition Guide</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">💪</span>
                <span className="feature-text">Strength Goals</span>
              </div>
            </div>

            <div className="stats-showcase">
              <div className="stat-box">Smart recommendations based on your body data</div>
              <div className="stat-box">Progress analytics with visual insights</div>
              <div className="stat-box">Designed for consistency, not shortcuts</div>
            </div>
          </div>
        </div>

        <div className="login-right">
          <div className="right-content">
            <div className="welcome-header">
              <h3>Welcome Back</h3>
              <p className="login-subtitle">Sign in to your account to continue</p>
            </div>

            {error && <div className="alert-custom error-shake">{error}</div>}

            <form onSubmit={handleSubmit}>
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
                    placeholder="Enter your password"
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

              <div className="remember-forgot">
                <label className="remember-me">
                  <input type="checkbox" />
                  <span>Remember me</span>
                </label>
                <Link to="#" className="forgot-password">Forgot password?</Link>
              </div>

              <button
                type="submit"
                className="btn-login"
                disabled={loading}
              >
                <span className="btn-text">
                  {loading ? "Signing in..." : "Sign In"}
                </span>
                <span className="btn-icon">→</span>
              </button>
            </form>

            <div className="divider">
              <span>OR</span>
            </div>

            <div className="social-login-google">
              <div id="google-signin-button"></div>
            </div>

            <div className="login-footer">
              <small>
                Don't have an account? <Link to="/register" className="signup-link">Create one</Link>
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;