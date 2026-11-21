# REMAINING ISSUES & FUTURE ENHANCEMENT ROADMAP
## Elevate Fitness & Nutrition Intelligence Platform

> **Date:** November 20, 2026  
> **Status:** All Blocking, Critical, High, and Medium Issues Resolved  
> **Repository:** `Elevate-fitness`  

---

## 1. Resolved Issues Summary

All verified bugs and architectural flaws identified in the Technical Audit and Improvement Roadmap have been resolved:
- **P0-01 (JWT Expiration & Cookie MaxAge Mismatch):** Fixed (7d user, 2h admin, cookies match).
- **P0-02 (Account Suspension Bypass):** Fixed (authoritative DB query on every request).
- **P0-03 (Frontend ESLint Errors):** Fixed (0 errors across 162 modules).
- **P0-04 (Nutrition Candidate Fallback Regression):** Fixed (fallback rate dropped to 0.00%).
- **P1-02 (Unbounded MongoDB Activity Arrays):** Fixed (capped with `$slice: -100`).
- **P1-03 (Timezone Hardcoding):** Fixed (standard IANA timezone resolution).
- **P2-F1 to P2-F5 (Monolith Decompositions):** Completed (`api.js`, `PoseDetector.jsx`, `Nutrition.jsx`, `Workout.jsx`, `Dashboard.jsx`).
- **P2-ML2 (LabelEncoder Vocabulary Drift):** Fixed (pre-fitted canonical equipment/injury vocabulary, 0 warnings).
- **P2-L1 (FastAPI on_event Deprecation):** Fixed (migrated to `@asynccontextmanager` `lifespan(app: FastAPI)`).

---

## 2. Low-Priority Non-Blocking Considerations & Third-Party Library Notes

The items below are non-blocking considerations, external deprecation advisories from third-party SDK maintainers, and architectural suggestions for future scaling:

### 2.1 Google Generative AI Python SDK Modernization
- **Notice:** Google has announced that support for the legacy `google-generativeai` package will end in favor of the new unified `google.genai` SDK.
- **Current Mitigation:** The existing implementation in `backend-python/app/gemini_service.py` is fully functional, passes all unit tests, and is wrapped in an offline circuit breaker that provides structured rule-based responses if the API is unreachable.
- **Future Recommendation:** Migrate from `import google.generativeai as genai` to `from google import genai` when upgrading Python dependencies to version 3.12+.

### 2.2 Python Runtime Version Alignment
- **Notice:** Google Cloud Core libraries issue an informational notice that Python 3.11 reaches end-of-life support in October 2027.
- **Current Mitigation:** The virtual environment runs Python 3.11.8 cleanly with 100% test pass rate across all 93 tests.
- **Future Recommendation:** In late 2026 or early 2027, update the Python runtime base Docker image to Python 3.12 LTS.

### 2.3 Distributed Multi-Instance Rate Limiting
- **Notice:** Node.js Express rate limiting currently uses memory-based sliding window tracking (`express-rate-limit`).
- **Current Behavior:** Flawless for single-instance or vertically scaled deployments.
- **Future Recommendation:** If horizontally scaling the Node.js backend across a Kubernetes cluster or multiple container replicas behind a round-robin load balancer, configure `rate-limit-redis` to share rate-limiting counters across all instances.

### 2.4 Browser-Side WebAssembly Model Caching
- **Notice:** The MediaPipe Pose Landmarker `.task` file is fetched at runtime by the browser and cached in the browser's HTTP cache.
- **Current Mitigation:** `poseModelPreload.js` warms up the model asset in the background upon navigation to workout routes.
- **Future Recommendation:** Implement an explicit IndexedDB or Service Worker cache for the 15MB MediaPipe task bundle to enable full offline execution in Progressive Web App (PWA) mode.
