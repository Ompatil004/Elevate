<div align="center">

# 🏋️‍♂️ Elevate Fitness Platform

### *Next-Gen AI-Powered Fitness & Nutrition Platform with Real-Time Pose Tracking*

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Elevate%20App-6C63FF?style=for-the-badge&logo=render&logoColor=white)](https://elevate-frontend-wglm.onrender.com)
[![React](https://img.shields.io/badge/React-19.2-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Node.js](https://img.shields.io/badge/Node.js-Express_5.2-339933?style=flat-square&logo=nodedotjs&logoColor=white)](https://nodejs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-9.1.5-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://www.mongodb.com)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-FF6F00?style=flat-square&logo=google&logoColor=white)](https://mediapipe.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.2.0-111111?style=flat-square)](https://xgboost.ai)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

---

</div>

Elevate is an intelligent, full-stack fitness and nutrition platform engineered to deliver **hyper-personalized workout routines**, **custom nutrition plans**, **real-time AI computer vision rep counting**, and an **interactive Gemini AI Coach**. Designed to eliminate cookie-cutter workout plans, Elevate uses machine learning (XGBoost) and biometrics to continuously adapt to your fitness level, equipment availability, schedule, and recovery data.

🌐 **Live Website**: [https://elevate-frontend-wglm.onrender.com](https://elevate-frontend-wglm.onrender.com)

---

## 🌟 Key Features

### 1. 🤖 AI-Powered Workout Engine
- **ML Prescriptions**: Utilizes XGBoost models to predict optimal sets, rep ranges, rest durations, and movement intensities based on user profiles.
- **Biometric Adaptation & Safety Layer**: Automatically adjusts volume and intensity for seniors, beginners, or users with prior joint injuries or health conditions.
- **1,300+ Exercise Library**: Intelligent mapping matching equipment (dumbbells, bodyweight, barbells, cables) and experience levels.
- **Dynamic Rest/Workout Swapping**: Convert rest days into workout days on the fly with automatic schedule re-balancing.

### 2. 🥗 Personalised AI Nutrition Engine
- **Macro & Caloric Precision**: Calculates BMR and TDEE adjusted for specific goals (Fat Loss, Muscle Gain, Maintenance, Recomp).
- **Dietary Preference Filtering**: Native support for Vegan, Vegetarian, Keto, High-Protein, and Allergen filtering.
- **Interactive Meal Swapping**: Swap out unappealing meals while maintaining precise daily macro targets.

### 3. 📹 Real-Time In-Browser Pose Detection & Rep Counter
- **MediaPipe Vision (WASM)**: High-precision 3D body landmark extraction running completely client-side.
- **3-Phase Finite State Machine**: Accurately counts reps (`rest → contracting → extended → rest`) with noise-gated hysteresis and range-of-motion validation.
- **Real-Time Form Correction**: Detects biomechanical mistakes (e.g., knee caving, flare elbows) and gives instant voice/visual feedback.

### 4. 💬 Google Gemini AI Fitness Coach
- **Context-Aware Recommendations**: Answers queries with full knowledge of your recent workouts, daily sleep, hydration, and goal trajectories.
- **Graceful Fallback**: Built-in offline fallback engine and circuit breakers ensure responsive coaching even during API outages.

### 5. 📊 Comprehensive Dashboard & Trend Tracking
- **Daily Check-Ins**: Track water intake, sleep hours, fatigue, and daily workout completions.
- **Streak & Consistency Metrics**: Gamified streak system with progressive overload recommendations.

### 6. 🛡️ Enterprise-Grade Admin Portal
- Complete management panel (`/admin/*`) for user suspension, content CRUD (exercises, rules), system maintenance toggle, and immutable audit logging.

---

## 🏗️ System Architecture

Elevate follows a dual-backend microservices architecture connected to a single MongoDB database, with Node.js operating as an API Gateway for security and auth delegation.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           BROWSER (React SPA)                           │
│  • Modern Dark UI (Vite + React 19)                                    │
│  • MediaPipe PoseLandmarker (In-Browser WASM Pose Detection)            │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────┐
│     Node.js / Express API Gateway     │ │  Python / FastAPI AI Engine   │
│              (Port 5000)              │ │          (Port 8000)          │
│ • Authentication & JWT Cookie Auth   │ │ • XGBoost ML Predictions      │
│ • User Profile & Activity Tracking    │ │ • Workout & Nutrition Engines │
│ • Admin Management & Audit Logging    │ │ • Google Gemini AI Integration│
│ • CSRF Protection & Rate Limiting     │ │ • Render Keep-Alive Service   │
└───────────────────┬───────────────────┘ └───────────────┬───────────────┘
                    │                                     │
                    └───────────────────┬─────────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────┐
                        │        MongoDB Atlas          │
                        │  (Database: elevate_fitness)  │
                        └───────────────────────────────┘
```

---

## 🛠️ Tech Stack

### **Frontend**
- **Framework**: React 19 (Vite 7)
- **Computer Vision**: `@mediapipe/tasks-vision` (Client-side WASM pose landmark detection)
- **HTTP & Routing**: Axios, React Router DOM v7
- **Styling**: Vanilla CSS3 (Custom Design System, Glassmorphism, CSS Variables, Dark Mode)
- **Testing**: Vitest, React Testing Library

### **Backend (Node.js API Gateway)**
- **Runtime**: Node.js v18+ / Express 5
- **Authentication**: JWT (HttpOnly Cookies), Google OAuth 2.0 (`google-auth-library`), bcryptjs
- **Security**: Double-Submit CSRF (`csrf-csrf`), Rate-Limiting (`express-rate-limit`), Security Alerts (Nodemailer)
- **Database ODM**: Mongoose 9

### **Backend (Python AI / ML Microservice)**
- **Framework**: FastAPI 0.135 (Uvicorn 0.42)
- **Machine Learning**: XGBoost 3.2, Scikit-Learn 1.8, Pandas, NumPy
- **Computer Vision**: MediaPipe Python, OpenCV
- **AI Integration**: Google Generative AI (`google-generativeai` Gemini 1.5/2.5)
- **Async Database**: Motor 3.7 (MongoDB Async), PyJWT, Tenacity (Circuit Breaker)

---

## 📁 Repository Structure

```
Elevate-fitness/
├── frontend/                     # React 19 SPA (Vite)
│   ├── src/
│   │   ├── components/           # PoseDetector, Navbar, AuroraBackground, etc.
│   │   ├── pages/                # Dashboard, Workout, Nutrition, Chatbot, ProfileSetup
│   │   ├── pages/admin/          # Full Admin Panel pages
│   │   ├── api.js                # Centralized API service layer
│   │   └── App.jsx               # Router & Auth State
│   └── package.json
│
├── backend-node/                 # Express API Gateway & Auth Service
│   ├── server.js                 # Server entry point
│   ├── middleware/               # Auth, Admin Auth, CSRF, Rate Limiting
│   ├── models/                   # Mongoose Schemas (User, Exercise, SystemConfig, AuditLog)
│   ├── routes/                   # Auth, Profile, Admin, and Python Reverse Proxy
│   └── package.json
│
├── backend-python/               # FastAPI AI & Machine Learning Service
│   ├── server.py                 # FastAPI application & Keep-Alive task
│   ├── app/
│   │   ├── workout_engine.py     # 7-Day ML Workout Generator
│   │   ├── meal_engine.py        # 7-Day Nutrition Generator
│   │   ├── pose_tracker.py       # Server-side Pose & Form Tracking
│   │   ├── gemini_service.py     # Gemini AI Chatbot Integration
│   │   ├── multi_output_xgboost_model.py # ML Workout Parameter Models
│   │   ├── multitarget_nutrition_model.py# ML Nutrition Parameter Models
│   │   ├── safety_layer.py       # Health & Safety Guardrails
│   │   └── detectors/            # Exercise-specific Pose Detectors
│   ├── requirements.txt
│   └── Dockerfile
│
└── PROJECT_ELEVATE_OVERVIEW.md   # Deep Technical Overview Document
```

---

## ⚡ Quick Start & Local Setup

### Prerequisites
- **Node.js**: `v18.x` or higher
- **Python**: `v3.11.x` recommended
- **MongoDB**: Local MongoDB instance or MongoDB Atlas URI

---

### 1. Clone the Repository
```bash
git clone https://github.com/Ompatil004/Elevate.git
cd Elevate-fitness
```

---

### 2. Configure Environment Variables

#### **Frontend (`frontend/.env`)**
```env
VITE_API_URL=http://localhost:5000/api
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id
VITE_API_NINJAS_KEY=your_api_ninjas_key
VITE_USDA_API_KEY=your_usda_api_key
```

#### **Node Backend (`backend-node/.env`)**
```env
PORT=5000
NODE_ENV=development
MONGO_URI=mongodb://localhost:27017/elevate_fitness
JWT_SECRET=your_super_secret_jwt_key
ADMIN_JWT_SECRET=your_admin_jwt_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
CORS_ORIGINS=http://localhost:5173
```

#### **Python Backend (`backend-python/.env`)**
```env
PORT=8000
MONGO_URI=mongodb://localhost:27017/elevate_fitness
JWT_SECRET=your_super_secret_jwt_key
GEMINI_API_KEY=your_google_gemini_api_key
CORS_ORIGINS=http://localhost:5173,http://localhost:5000
```

---

### 3. Install Dependencies & Run

#### **Option A: Running Services Manually**

**1. Python AI Backend (Port 8000):**
```bash
cd backend-python
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn server:app --reload --port 8000
```

**2. Node.js API Gateway (Port 5000):**
```bash
cd backend-node
npm install
npm start
```

**3. Frontend (Port 5173):**
```bash
cd frontend
npm install
npm run dev
```

#### **Option B: Windows One-Click Script**
Double-click `start_all.bat` at the repository root to launch all three servers simultaneously in separate terminals.

---

## 🧪 Testing & Quality Assurance

```bash
# Run Frontend Tests (Vitest)
cd frontend
npm run test:unit

# Run Node.js Backend Tests (Jest)
cd backend-node
npm run test:unit

# Run Python Backend Tests (Pytest)
cd backend-python
pytest tests/ -v
```

---

## 🚀 Deployment

The project is pre-configured for simple cloud deployment on platforms like **Render**, **Railway**, or **AWS**:

1. **Frontend**: Deployed as a Web Service / Static Site using Vite build output or Docker (`frontend/Dockerfile`).
2. **Node Backend**: Deployed as a Node Web Service (`npm start`).
3. **Python Backend**: Deployed as a Dockerized Web Service (`backend-python/Dockerfile`).
   - Includes automatic self-ping keep-alive service (`RENDER_EXTERNAL_URL`) to eliminate 15-minute free tier cold starts!

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by **[Om Patil](https://github.com/Ompatil004)**

*(If you found this project helpful, don't forget to give it a ⭐️!)*

</div>