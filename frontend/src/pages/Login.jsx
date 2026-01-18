import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import "../App.css";

function Login() {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [focused, setFocused] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/auth/login",
        formData
      );

      const userId = res.data.user_id;

      localStorage.setItem("token", "dummy-token");
      localStorage.setItem("userId", userId);
      localStorage.setItem("userName", res.data.full_name);

      try {
        const profileRes = await axios.get(
          `http://127.0.0.1:8000/auth/get-profile/${userId}`
        );

        profileRes.data.is_setup
          ? navigate("/dashboard")
          : navigate("/profile-setup");
      } catch {
        navigate("/profile-setup");
      }
    } catch {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async (response) => {
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/auth/google-login",
        {
          token: response.credential,
        }
      );

      const userId = res.data.user_id;

      localStorage.setItem("token", res.data.token);
      localStorage.setItem("userId", userId);
      localStorage.setItem("userName", res.data.full_name);

      try {
        const profileRes = await axios.get(
          `http://127.0.0.1:8000/auth/get-profile/${userId}`
        );

        profileRes.data.is_setup
          ? navigate("/dashboard")
          : navigate("/profile-setup");
      } catch {
        navigate("/profile-setup");
      }
    } catch {
      setError("Google login failed. Please try again.");
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
              <button
                className="social-btn google-btn"
                type="button"
                onClick={() => {
                  window.google?.accounts?.id?.initialize({
                    client_id: "YOUR_GOOGLE_CLIENT_ID",
                    callback: handleGoogleLogin,
                  });
                  window.google?.accounts?.id?.renderButton(
                    document.querySelector(".google-btn-render")
                  );
                }}
              >
                <span>🔵</span>
                Continue with Google
              </button>
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