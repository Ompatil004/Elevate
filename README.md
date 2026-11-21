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
│   │   ├── api/                  # Domain-sliced modular API clients
│   │   │   ├── apiClient.js      # Axios instance, CSRF, and interceptors
│   │   │   ├── authApi.js        # Authentication endpoints
│   │   │   ├── profileApi.js     # User profile and metrics
│   │   │   ├── workoutApi.js     # Workout generation and variations
│   │   │   ├── nutritionApi.js   # Meal plans and food database
│   │   │   ├── adminApi.js       # Admin portal and telemetry
│   │   │   └── chatbotApi.js     # AI coach assistant endpoints
│   │   ├── features/             # Feature-sliced modular business logic & UI
│   │   │   ├── dashboard/        # ActivityChart & hero radial calculations
│   │   │   ├── nutrition/        # MacroStat, MealCard, MealSwapModal, HistoryPanel
│   │   │   ├── pose-detection/   # Biomechanical angle math, safety checks, rep FSM
│   │   │   └── workout/          # DaySelector, swap modals, variations, animations
│   │   ├── components/           # Reusable UI components (Navbar, AuroraBackground, etc.)
│   │   ├── pages/                # Core route views (Dashboard, Workout, Nutrition, Chatbot)
│   │   ├── pages/admin/          # Full Admin Panel pages
│   │   └── App.jsx               # Router & Auth State
│   └── package.json
│
├── backend-node/                 # Express API Gateway & Auth Service
│   ├── server.js                 # Server entry point
│   ├── middleware/               # Authoritative Auth, Admin Auth, CSRF, Rate Limiting
│   ├── models/                   # Mongoose Schemas (User, Exercise, SystemConfig, AuditLog)
│   ├── routes/                   # Auth, Profile, Admin, and Python Reverse Proxy
│   ├── tests/                    # Jest automated integration & unit tests
│   └── package.json
│
├── backend-python/               # FastAPI AI & Machine Learning Service
│   ├── server.py                 # FastAPI application with modern Lifespan lifecycle
│   ├── app/
│   │   ├── feature_pipeline.py   # Machine learning feature extraction with canonical encoders
│   │   ├── workout_engine.py     # 7-Day ML Workout Generator (XGBoost)
│   │   ├── workout_rules.py      # Exercise safety, frequency gating, and split rules
│   │   ├── nutrition_engine/     # Combinatorial meal generator (0% fallback rate)
│   │   ├── pose_tracker.py       # Biomechanical joint analysis
│   │   └── gemini_service.py     # Gemini AI Chatbot with offline circuit breaker
│   ├── tests/                    # Pytest automated test suite (93 tests)
│   ├── requirements.txt
│   └── Dockerfile
│
├── AUTONOMOUS_REFACTORING_PROGRESS.md # Progress tracking ledger
├── FINAL_IMPLEMENTATION_REPORT.md     # Detailed transformation implementation report
├── FINAL_TEST_REPORT.md               # 156 automated tests verification report
├── FINAL_PROJECT_ARCHITECTURE.md      # Architecture diagrams & microservice flow
├── FINAL_PROJECT_STRUCTURE.md         # Directory structure & module guide
├── REMAINING_ISSUES.md                # Edge cases & future roadmap
└── CHANGELOG.md                       # Comprehensive version changelog
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

Elevate maintains a zero-tolerance regression standard with **156 automated test cases** passing with 100% success rate across all layers:

```bash
# 1. Frontend Unit & Integration Tests (37 Vitest tests)
cd frontend
npm run test:unit

# 2. Frontend ESLint Static Analysis (0 errors, 0 warnings)
cd frontend
npm run lint

# 3. Frontend Production Build Check
cd frontend
npm run build

# 4. Node.js Backend Tests (26 Jest tests covering auth, DB suspension checks, proxying)
cd backend-node
npm test

# 5. Python Machine Learning & API Tests (93 Pytest tests + 19 subtests)
cd backend-python
pytest tests/
```

---

## 🚀 Deployment & Health Checks

The project is pre-configured with Infrastructure as Code via `render.yaml` for zero-configuration cloud deployment on **Render**, **Railway**, or **AWS**:

1. **Frontend**: Deployed as a Static Site (`frontend/dist`) or containerized with `frontend/Dockerfile`.
2. **Node.js API Gateway**: Deployed as a Node Web Service (`backend-node`) with lightweight health checks.
3. **Python ML Backend**: Deployed as a Python Web Service (`backend-python`) or containerized with `backend-python/Dockerfile`.

### Health & Readiness Architecture

Both backend services expose dedicated, standards-compliant probes:

| Endpoint | Probe Type | Behavior | Target Response |
| :--- | :--- | :--- | :--- |
| `GET /health` | **Liveness** | Ultra-lightweight check returning 200 without DB/ML queries. Safe for Render health checks and container orchestrators. | `{"status":"ok","service":"...","timestamp":"..."}` |
| `GET /ready` | **Readiness** | Validates live MongoDB connectivity and ML engine readiness. Returns 200 when ready, 503 when dependencies fail. | `{"status":"ready","checks":{...}}` |

### Render Free Tier & Uptime Clarification

- **Free Tier Inactivity:** Render Free tier web services spin down after 15 minutes of inactivity. Health endpoints allow orchestrators to know when a container is healthy, but do not independently prevent free instances from sleeping.
- **No Internal Self-Pinging:** Internal infinite self-ping loops are intentionally avoided to prevent container resource contention and artificial wakeups.
- **Always-On Production:** For 100% uptime with zero cold starts, upgrade web services to a paid Render instance (Starter or Standard tier), or configure a legitimate external uptime monitor (e.g. UptimeRobot, Better Uptime) with a standard 10–15 minute check interval.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by **[Om Patil](https://github.com/Ompatil004)**

*(If you found this project helpful, don't forget to give it a ⭐️!)*

</div>