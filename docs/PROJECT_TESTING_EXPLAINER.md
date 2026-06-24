# Elevate: Project Testing, Validation & Quality Assurance Guide

This document explains the complete testing strategy used in the Elevate Fitness application. It details how each layer (Frontend, Node.js Gateway, Python ML Backend) is tested, how model drift is detected, and how safety is mathematically validated.

---

## 1. High-Level Testing Strategy

Elevate is tested across three independent tiers, aligning with modern software engineering standards:

```
                  +----------------------------------------------+
                  |            ELEVATE TESTING SYSTEM            |
                  +----------------------------------------------+
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
+-------------+             +-------------+             +-------------+
|  FRONTEND   |             |   NODE JS   |             |  PYTHON ML  |
| UNIT TESTS  |             | INTEGRATION |             | VALIDATION  |
| (Vitest/JS) |             | (Jest/Super)|             |  (SciPy/KS) |
+-------------+             +-------------+             +-------------+
```

1. **Frontend Unit Testing (Vitest/Jest):** Asserts local storage states, UI confirm dialog actions, and coordinate routing flows for MediaPipe camera pages.
2. **Node.js Integration Testing (Jest/Supertest):** Asserts that auth middleware correctly reads cookies and blocks suspended users.
3. **Python AI/ML Validation Framework (SciPy/Scikit-Learn):** A custom mathematical testing harness verifying regression predictions, calculating accuracy benchmarks, and analyzing data drift.

---

## 2. Python AI/ML Validation & Testing

Your ML model validation does not just use standard software tests. It utilizes a **statistical validation framework** defined inside [evaluation_framework.py](file:///c:/Users/2004o/OneDrive/Desktop/project-deploy/backend-python/app/evaluation_framework.py).

### A. Mathematical Validation Metrics
The `ModelEvaluator` class (Lines 29–151) evaluates XGBoost predictions against ground truth validation test sets using:
* **Mean Absolute Error (MAE):** Measures average magnitude of error in target units:
  $$\text{MAE} = \frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|$$
* **Root Mean Squared Error (RMSE):** Panelizes larger prediction errors:
  $$\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}$$
* **Safety Compliance Ratio (Lines 95–113):** A custom safety check that calculates the percentage of predictions that fall within acceptable biological boundaries (e.g., ensuring a predicted daily caloric intake is within 80% to 120% of standard guidelines):
  ```python
  def _safety_compliance(self, y_true: np.ndarray, y_pred: np.ndarray, safety_bounds: Dict = None) -> float:
      # Checks if predictions are within biological boundaries
      lower_bound = y_true * safety_bounds['min']
      upper_bound = y_true * safety_bounds['max']
      within_bounds = ((y_pred >= lower_bound) & (y_pred <= upper_bound)).sum()
      return (within_bounds / len(y_pred)) * 100
  ```

### B. Statistical Data Drift Detection (KS-Test)
* **What is Data Drift?** As users interact with the app, the distribution of incoming biometrics (e.g., age, weight) might skew away from what the XGBoost model was originally trained on. This causes model accuracy to degrade.
* **Code Implementation (Lines 152–193):** The `detect_drift` method uses the **Kolmogorov-Smirnov test (KS-Test)** from `scipy.stats.ks_2samp` to compare the live user distribution against the training dataset:
  ```python
  # Perform Kolmogorov-Smirnov test for distribution similarity
  statistic, p_value = stats.ks_2samp(X_reference[col], X_current[col])
  drift_detected = p_value < 0.05  # Significant difference (drift) detected
  ```
  If the $p$-value falls below $0.05$, the system flags a **drift detected** alert, indicating the model needs to be retrained on new user logs.

### C. A/B Testing Framework
* **Code Implementation (Lines 309–386):** The `ABTestFramework` compares two models (e.g. Random Forest vs. XGBoost) by running a **paired t-test** (`stats.ttest_rel`) on their squared errors. It asserts whether model improvements are statistically significant or just random chance:
  ```python
  # Paired t-test on squared prediction errors
  t_stat, p_value = stats.ttest_rel((y_test - y_pred_control)**2, (y_test - y_pred_treatment)**2)
  is_significant = p_value < 0.05
  ```

---

## 3. Node.js Gateway Integration Testing

Located in [auth.middleware.test.js](file:///c:/Users/2004o/OneDrive/Desktop/project-deploy/backend-node/tests/auth.middleware.test.js).

* **Purpose:** Validates the core security layer.
* **What is tested:**
  1. **Token Absence Check:** Ensures requesting a protected route without a JWT cookie returns a `401 Unauthorized` status.
  2. **Invalid Token Check:** Checks that modified or expired JWT keys return `401 Token is not valid`.
  3. **Suspended Account Block:** Checks that if the database flag `isSuspended` is set to `true`, the middleware halts execution and returns a `403 Forbidden` response containing:
     ```json
     { "message": "Account is suspended. Please contact support." }
     ```

---

## 4. React Frontend Unit Testing

Located inside [frontend/src/\_\_tests\_\_/](file:///c:/Users/2004o/OneDrive/Desktop/project-deploy/frontend/src/__tests__/).

* **Purpose:** Asserts critical UI flows, utility functions, and pose tracking configurations.
* **Test Suites:**
  1. **`ConfirmDialog.test.jsx`:** Verifies that when a user triggers an action (like resetting or swapping a workout day), the dialog renders correct confirmation messages and trigger handlers.
  2. **`storage.test.js`:** Tests safe local storage getters and setters, ensuring user credentials are encrypted/decrypted correctly.
  3. **`poseRouting.test.js`:** Tests the camera routing state machine. Asserts that the app routes between the setup, live camera feed, and completed rep counting screens without crashing.

---

## 5. Mock Q&A: Answering Testing Questions in Your Viva

#### Q1: "How did you test your project?"
> **Answer:** "We tested the project at three levels. In the frontend, we used Vitest for component testing, ensuring storage utilities and pose trackers initialize reliably. In the Node.js backend, we used Jest to verify our authentication middleware, ensuring JWTs and suspended account protections function correctly. Lastly, for the Python machine learning backend, we created a custom statistical evaluation framework inside `evaluation_framework.py` that validates predictions against test splits using MAE, RMSE, and safety boundaries."

#### Q2: "How did you validate that your machine learning models are safe?"
> **Answer:** "We implemented a custom `_safety_compliance` metric inside our evaluation framework. This metric calculates the percentage of predictions that fall within biological limits—for instance, checking if predicted calorie allocations fall between 80% and 120% of standard guidelines. Additionally, the backend applies hard coded mathematical clamps that override predictions if they fall out of bounds."

#### Q3: "How do you detect when your machine learning models become outdated?"
> **Answer:** "We implemented **Data Drift Detection** using a two-sample Kolmogorov-Smirnov test (`ks_2samp`) from `scipy.stats`. By comparing the biometric features of our live user base against the original training dataset, we detect changes in input distributions. If the KS-test returns a $p$-value lower than $0.05$, the system flags a data drift warning, signaling that the models need to be retrained."

#### Q4: "Why did you use a paired t-test in your A/B testing framework?"
> **Answer:** "A paired t-test is the standard statistical test used to compare the performance of two models trained on the same data. By calculating the difference between the squared errors of our baseline model and the XGBoost model, the t-test determines whether the XGBoost model's lower error is statistically significant ($p < 0.05$) rather than just random variation."
