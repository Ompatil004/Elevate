# Codebase Structural Map

## backend-node/models/User.js
```javascript
    // Bug #6c: Added 'Maintenance' (full word) + 'Maintain' (short form used in meal engine).
    // Both spellings are used across frontend and backend; allow either.
    // Provide explicit support for flattened macros from the React saveTrends
```

## backend-node/routes/auth.js
```javascript
// Initialize Google OAuth client
// Helper function to generate JWT
const generateToken = (userId) => {
  // [Logic Hidden]
// ==========================================
// REGISTER
// ==========================================
router.post('/register', async (req, res) => {
  // [Logic Hidden]
    // Check if user exists
    // Hash password
    // Create user
    // Generate token
// ==========================================
// LOGIN
// ==========================================
router.post('/login', async (req, res) => {
  // [Logic Hidden]
    // Check password
    // Generate token
// ==========================================
// GOOGLE LOGIN
// ==========================================
router.post('/google', async (req, res) => {
  // [Logic Hidden]
    // Verify Google token
    // Find or create user
      // Update avatar if user exists but doesn't have one
    // Generate JWT
// ==========================================
// LOGOUT
// ==========================================
router.post('/logout', (req, res) => {
  // [Logic Hidden]
```

## backend-node/routes/profile.js
```javascript
const toDateKey = (raw) => {
  // [Logic Hidden]
const inferMealType = (entry) => {
  // [Logic Hidden]
const buildMealData = (entry, fallbackType) => ({
  // [Logic Hidden]
const computeDayTotals = (dayEntry) => {
  // [Logic Hidden]
const normalizeMealHistory = (rawMeals = []) => {
  // [Logic Hidden]
    const upsertMeal = (dateKey, mealType, mealData) => {
      // [Logic Hidden]
// GET /api/profile
router.get('/', auth, async (req, res) => {
  // [Logic Hidden]
// POST /api/profile/update
router.post('/update', auth, async (req, res) => {
  // [Logic Hidden]
        // Get the current user profile to compare with new data
        // Fields that should trigger workout plan regeneration
        // Check if any of these fields have changed
        // SAFE: Build update object with whitelisted fields only
                // Ensure array fields stay arrays
        // If profile changes require workout regeneration, clear the old plan from frontend cache
            // In a real implementation, we might want to trigger a background job to regenerate the plan
            // For now, we'll just notify the frontend that it needs to regenerate the plan
// ==========================================
// HISTORY ENDPOINTS
// ==========================================
// GET /api/profile/workout-history
router.get('/workout-history', auth, async (req, res) => {
  // [Logic Hidden]
// POST /api/profile/workout-history
router.post('/workout-history', auth, async (req, res) => {
  // [Logic Hidden]
        // Add new workout log to the front
        // Keep only last 50 workouts for performance
// GET /api/profile/meal-history
router.get('/meal-history', auth, async (req, res) => {
  // [Logic Hidden]
        // Persist normalized format so future reads/writes are consistent.
// POST /api/profile/meal-history
router.post('/meal-history', auth, async (req, res) => {
  // [Logic Hidden]
        // Keep only last 100 entries
// GET /api/profile/trends
router.get('/trends', auth, async (req, res) => {
  // [Logic Hidden]
        // Keep response backwards-compatible while supporting optional period filtering.
        const filtered = trends.filter((entry) => {
          // [Logic Hidden]
// POST /api/profile/trends
router.post('/trends', auth, async (req, res) => {
  // [Logic Hidden]
        const existingIndex = user.trends.findIndex((entry) => entry.date === trendData.date);
        if (existingIndex >= 0) {
          // [Logic Hidden]
```

## backend-node/routes/users.js
```javascript
const toDateKey = (raw) => {
  // [Logic Hidden]
const inferMealType = (entry) => {
  // [Logic Hidden]
const buildMealData = (entry, mealType) => ({
  // [Logic Hidden]
const computeTotals = (dayEntry) => {
  // [Logic Hidden]
const normalizeGroupedMeals = (rawMeals = []) => {
  // [Logic Hidden]
  const upsert = (dateKey, mealType, data) => {
    // [Logic Hidden]
// Test route to verify the file is loaded
router.get('/test', (req, res) => {
  // [Logic Hidden]
// POST /api/users/save - Save user profile data
router.post('/save', auth, async (req, res) => {
  // [Logic Hidden]
    // Find the user by ID from the token
    // SAFE: Only update whitelisted profile fields to prevent schema corruption
    // Update the updatedAt field
    // Save the updated user
// POST /api/users/workout/save - Save workout data
router.post('/workout/save', auth, async (req, res) => {
  // [Logic Hidden]
    // Find the user by ID from the token
    // Add workout data to user (you can customize this based on your needs)
    // Add timestamp to the workout data
    // Limit the number of stored workouts to prevent the document from growing too large
    // Save the updated user
// POST /api/users/meals/save - Save meal data & return today's totals
router.post('/meals/save', auth, async (req, res) => {
  // [Logic Hidden]
    // Find the user by ID from the token
    // ✅ Use grouped daily meal history format for consistency with /profile/meal-history.
    // Legacy mixed formats are normalized before upsert.
    // Use dayName from frontend (local date: YYYY-MM-DD) as canonical date
    // Fallback uses server local date to stay consistent
    let dayEntry = normalized.find((d) => d.date === dateKey);
    if (!dayEntry) {
      // [Logic Hidden]
    // Save the updated user
    // Compute today's aggregate macros from grouped meals.
    const todayEntry = user.meals.find((d) => d.date === dateKey) || { total_calories: 0, total_protein: 0, total_carbs: 0, total_fat: 0 };
      // [Logic Hidden]
```

## backend-node/server.js
```javascript
const missingEnv = requiredEnv.filter((k) => !process.env[k]);
if (missingEnv.length > 0) {
  // [Logic Hidden]
// MongoDB Connection
// Middleware
// Routes
// Health check
app.get('/health', (req, res) => {
  // [Logic Hidden]
// Test database connection
app.get('/test-db', async (req, res) => {
  // [Logic Hidden]
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  // [Logic Hidden]
```

## backend-python/app/data_health_analysis.py
```python
def analyze_exercises_data(file_path):
    # [Logic Hidden]
    """
    Analyze exercises data for quality issues and insights
    """
        # 1. Missing Values Analysis
        # 2. Duplicate Analysis
        # 3. Data Types and Consistency
        # 4. Categorical Variable Analysis
            # Check for inconsistent entries (potential typos)
        # 5. Numerical Variables Summary
        # 6. Equipment Analysis
        # 7. Target Muscle Analysis
        # 8. Difficulty Level Analysis
        # 9. Potential Issues Summary
def analyze_nutrition_data(file_path):
    # [Logic Hidden]
    """
    Analyze nutrition data for quality issues and insights
    """
        # 1. Missing Values Analysis
        # 2. Duplicate Analysis
        # 3. Data Types and Consistency
        # 4. Categorical Variable Analysis
        # 5. Nutritional Values Analysis
                # Check for negative values (invalid)
                # Check for extremely high values (potential outliers)
                    Q3 = nutri_df[col].quantile(0.75)
                    Q1 = nutri_df[col].quantile(0.25)
                    IQR = Q3 - Q1
        # 6. Meal Type Analysis
        # 7. Dietary Tags Analysis
        # 8. Potential Issues Summary
def analyze_class_imbalance(df, column_name):
    # [Logic Hidden]
    """
    Analyze class imbalance for a categorical column
    """
        # Flag highly imbalanced classes (less than 5% or more than 70%)
def analyze_feature_gaps(user_profile_example=None):
    # [Logic Hidden]
    """
    Analyze potential gaps in feature representation
    """
    # Define expected user profile features
    # Potential gaps in current datasets
    # Recommend new columns to add
def generate_comprehensive_report(exercises_df, nutrition_df):
    # [Logic Hidden]
    """
    Generate a comprehensive health report
    """
def generate_data_cleaning_strategy(exercises_df, nutrition_df):
    # [Logic Hidden]
    """
    Generate a data cleaning strategy based on identified issues
    """
def main():
    # [Logic Hidden]
    """
    Main function to run the complete analysis
    """
    # Analyze exercises data
    # Analyze nutrition data
    # Perform class imbalance analysis if dataframes exist
        # Common categorical columns in exercises data
        # Common categorical columns in nutrition data
    # Analyze feature gaps
    # Generate data cleaning strategy
    # Generate comprehensive report
```

## backend-python/app/db.py
```python
# Load environment variables
# MongoDB connection settings
MONGODB_URL = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/elevate_fitness")
# Global client variable
async def connect_to_mongo():
    # [Logic Hidden]
    """Connect to MongoDB"""
        # Test the connection
async def close_mongo_connection():
    # [Logic Hidden]
    """Close MongoDB connection"""
def get_database():
    # [Logic Hidden]
    """Get the database instance"""
    # Extract database name from the connection string
    # Handle different MongoDB URI formats
        # Format: mongodb://host:port/database_name
        # or mongodb://username:password@host:port/database_name
            # Remove query parameters if present
        # Format: mongodb+srv://host/database_name
            # Remove query parameters if present
        # Fallback: extract from custom format
            # Remove query parameters if present
    # Ensure the database name is valid (doesn't contain dots)
        # If database name contains dots, use the default
def get_user_collection():
    # [Logic Hidden]
    """Get the user collection instance"""
def get_workout_history_collection():
    # [Logic Hidden]
    """Get the workout history collection instance"""
def get_meal_history_collection():
    # [Logic Hidden]
    """Get the meal history collection instance"""
def get_workout_completion_collection():
    # [Logic Hidden]
    """Get the workout completion collection instance"""
def get_meal_completion_collection():
    # [Logic Hidden]
    """Get the meal completion collection instance"""
```

## backend-python/app/deterministic_meal_engine.py
```python
"""
Deterministic 7-Day Meal Engine — Dataset-Driven
Loads ALL meals directly from data/nutrition_processed.csv.
Selects meals using Mifflin-St Jeor TDEE, macro ratios, dietary
preference filtering, allergen exclusion, and Swap_Group matching.
Every calorie/macro value displayed is the EXACT value from the
dataset — no random multipliers, no dummy data.
"""
class MealEngine:
    # [Logic Hidden]
    """
    Dataset-driven meal engine with exact macro accountability.
    """
    def __init__(self, nutrition_data_path: str = None):
        # [Logic Hidden]
        # Standardise column names once
        # Fill NaNs
        # Normalise meal_type to lowercase (Breakfast → breakfast)
        # Macro ratios by goal
        # Activity multipliers (Mifflin-St Jeor)
        # Meal calorie distribution
    # ─────────────────────────────────────────────
    #  CORE:  calorie / macro target calculations
    # ─────────────────────────────────────────────
    def calculate_daily_targets(self, profile: Dict) -> Dict:
        # [Logic Hidden]
        """Mifflin-St Jeor BMR → TDEE → goal adjustment → macros"""
    # ─────────────────────────────────────────────
    #  FILTERING: dietary pref, allergens, goal
    # ─────────────────────────────────────────────
    def _filter_foods(self, profile: Dict) -> pd.DataFrame:
        # [Logic Hidden]
        # Dietary preference
            # Further exclude non-veg swap groups
        # Allergens
        # Goal-match preference: prefer goal-matching foods, but fall back to all
        # Bug #3a Fix: Filter out raw ingredient-only entries (spices, condiments, etc.)
        # These are not suitable as standalone meal options in the swap UI.
        RAW_INGREDIENT_PATTERNS = [
            # Also filter entries with extremely low calories (< 20 kcal) as they're likely
            # condiment/spice amounts, not meals.
    # ─────────────────────────────────────────────
    #  MEAL SELECTION  — greedy calorie-fit picker
    # ─────────────────────────────────────────────
    def _pick_meals_for_slot(self, pool: pd.DataFrame, target_cal: float,
                              target_macros: Dict, used_names: set,
                              seed: int = 0, meal_type: str = 'lunch') -> List[Dict]:
        # [Logic Hidden]
        """
        Pick food items from `pool` whose summed calories are
        within ±15 % of `target_cal`.  Deterministic per seed.
        """
        # Exclude already-used names (cross-meal dedup for the day)
        # Dynamic dish count by slot and calorie target.
        # This avoids rigid fixed counts across users and days.
            # Snack is optional when the target allocation is very small.
        # First pass: greedily pick items that fit
        # Make sure we got at least 1
    # ─────────────────────────────────────────────
    #  PUBLIC:  generate a 7-day weekly plan
    # ─────────────────────────────────────────────
    def generate_weekly_plan(self, profile: Dict) -> Dict:
        # [Logic Hidden]
        # Split pool by meal type
                # Mix the seed with day_idx+mt for deterministic variety
        # ─── Summary ───
    # ─────────────────────────────────────────────
    #  SWAP: Mathematical Macro Similarity Engine
    # ─────────────────────────────────────────────
    def get_swap_options(self, food_name: str, meal_type: str,
                         profile: Dict, limit: int = 5) -> List[Dict]:
        # [Logic Hidden]
        """
        Industry-level recommendation engine:
        Finds alternatives by calculating Euclidean distance across scaled macro vectors
        [calories, protein, carbs, fat], heavily penalizing items that disrupt the user's
        daily calorie or protein targets.
        """
        # 1. Locate the original food item
            # Fallback: Just return random items of the same meal_type
            # 2. Candidate Pool: Same meal_type OR same Swap_Group, excluding the original
            # 3. Vectorized Distance Calculation (Macro Similarity)
            # Weights: Calories (2.0x), Protein (1.5x), Carbs (1.0x), Fat (1.0x)
            # We normalize the diff by the original value (or 1 to avoid div-by-zero)
            # Total Euclid-like penalty score
            # 4. Sort by best mathematical match
        # 5. Format results
    # ─────────────────────────────────────────────
    #  Internal helpers
    # ─────────────────────────────────────────────
    def _build_weekly_summary(self, weekly_plan: Dict, targets: Dict) -> Dict:
        # [Logic Hidden]
        # Shopping list
# ─── Module-level convenience functions kept for backward compat ───
def algorithm_logic():
    # [Logic Hidden]
def pseudocode():
    # [Logic Hidden]
def optimization_strategy():
    # [Logic Hidden]
def example_weekly_json():
    # [Logic Hidden]
def shopping_list_generator_logic():
    # [Logic Hidden]
```

## backend-python/app/evaluation_framework.py
```python
"""
Reusable Evaluation Framework for Workout and Nutrition Models
This module provides a comprehensive evaluation framework for ML models
with metrics, safety checks, drift detection, and A/B testing capabilities.
"""
class ModelEvaluator:
    # [Logic Hidden]
    """
    Reusable evaluation framework for ML models
    """
    def __init__(self, model_name: str, model_type: str = "regression"):
        # [Logic Hidden]
        # Setup logging
        # Initialize metrics
    def _setup_logging(self) -> logging.Logger:
        # [Logic Hidden]
        """
        Setup logging for the evaluator
        """
        # Create formatter
        # Console handler
        # File handler
    def _rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        # [Logic Hidden]
        """Root Mean Square Error"""
    def _mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        # [Logic Hidden]
        """Mean Absolute Error"""
    def _precision(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        # [Logic Hidden]
        """Precision score"""
    def _recall(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        # [Logic Hidden]
        """Recall score"""
    def _safety_compliance(self, y_true: np.ndarray, y_pred: np.ndarray, safety_bounds: Dict = None) -> float:
        # [Logic Hidden]
        """
        Calculate safety compliance percentage
        """
            # Default safety bounds for nutrition/workout models
        # Calculate how many predictions are within bounds
    def evaluate_model(self, 
                     model, 
                     X_test: pd.DataFrame, 
                     y_test: np.ndarray, 
                     safety_bounds: Dict = None,
                     feature_names: List[str] = None) -> Dict:
        # [Logic Hidden]
        """
        Comprehensive model evaluation
        """
        # Make predictions
        # Calculate metrics
        # Feature importance (if available)
        # Store results
    def detect_drift(self, X_current: pd.DataFrame, X_reference: pd.DataFrame, threshold: float = None) -> Dict:
        # [Logic Hidden]
        """
        Detect data drift between current and reference datasets
        """
        # Compare statistical properties of features
                # Perform Kolmogorov-Smirnov test for distribution similarity
        # Overall drift assessment
    def compare_models(self, 
                      X_train: pd.DataFrame, 
                      y_train: np.ndarray, 
                      X_test: pd.DataFrame, 
                      y_test: np.ndarray,
                      feature_names: List[str] = None) -> Dict:
        # [Logic Hidden]
        """
        Compare XGBoost vs Random Forest models
        """
        # Initialize models
        # Train models
        # Evaluate models
        # Cross-validation comparison
    def plot_feature_importance(self, feature_importance: Dict, top_n: int = 10) -> plt.Figure:
        # [Logic Hidden]
        """
        Plot feature importance
        """
        # Sort features by importance
    def plot_predictions_vs_actual(self, y_true: np.ndarray, y_pred: np.ndarray) -> plt.Figure:
        # [Logic Hidden]
        """
        Plot predictions vs actual values
        """
    def generate_report(self, results: Dict, model_comparison: Dict = None) -> str:
        # [Logic Hidden]
        """
        Generate evaluation report
        """
        """
        if model_comparison:
            winner = model_comparison['winner']
            xgb_rmse = model_comparison['xgboost']['evaluation']['rmse']
            rf_rmse = model_comparison['random_forest']['evaluation']['rmse']
            report += f"""
        Model Comparison:
        -----------------
        XGBoost RMSE: {xgb_rmse:.4f}
        Random Forest RMSE: {rf_rmse:.4f}
        Winner: {winner}
        """
class ABTestFramework:
    # [Logic Hidden]
    """
    A/B Testing framework for model comparison
    """
    def __init__(self, control_model, treatment_model, test_name: str = "A/B Test"):
        # [Logic Hidden]
        # Setup logging
    def _setup_logging(self) -> logging.Logger:
        # [Logic Hidden]
        """
        Setup logging for A/B testing
        """
    def run_ab_test(self, 
                   X_test: pd.DataFrame, 
                   y_test: np.ndarray,
                   metric_func: Callable = mean_squared_error,
                   significance_level: float = 0.05) -> Dict:
        # [Logic Hidden]
        """
        Run A/B test between control and treatment models
        """
        # Get predictions from both models
        # Calculate metrics for both models
        # Perform statistical test (paired t-test)
        # Determine significance
def create_evaluation_folder_structure():
    # [Logic Hidden]
    """
    Create the recommended folder structure for the evaluation framework
    """
def example_execution_flow():
    # [Logic Hidden]
    """
    Example execution flow demonstrating the evaluation framework
    """
    # Create sample data
    # Simulated workout data
    # Simulated targets (sets, reps, rest_time, intensity)
    # Split data
    # Initialize evaluator
    # Train a sample model
    # Evaluate the model
    # Compare models
    # Detect drift
    # Create slightly different reference data
    # A/B Testing example
    # Generate report
    # Save results
    # Create folder structure
    # Run example execution
```

## backend-python/app/feature_pipeline.py
```python
"""
Complete ML Feature Pipeline for Elevate Fitness Workout Recommendation Engine
This module defines the full feature pipeline from raw user inputs to model-ready features,
with deterministic processing, safety overrides, and progressive overload capabilities.
"""
class FeaturePipeline:
    # [Logic Hidden]
    """
    Complete feature pipeline for workout recommendation engine
    """
    def __init__(self):
        # [Logic Hidden]
        # Initialize encoders
        # Fit encoders with default values
        # Scaler for numerical features
        # Feature names for reference
        # Define target mappings
    def _fit_encoders(self):
        # [Logic Hidden]
        """Fit encoders with default values"""
        # Experience levels
        # Fitness goals
        # Gender
        # Equipment (will be fitted when first data comes in)
        # Injury flags (will be fitted when first data comes in)
    def validate_input(self, user_profile: Dict) -> Dict:
        # [Logic Hidden]
        """
        Validate and sanitize raw user input
        """
        # Required fields with defaults
        # Validate ranges
    def calculate_derived_features(self, user_profile: Dict) -> Dict:
        # [Logic Hidden]
        """
        Calculate derived features from raw input
        """
        # BMI calculation
        # Experience score (numerical representation)
        # Recovery score — 4-factor model (sleep, hydration, stress, fatigue)
        # Consistency score (already normalized)
        # Equipment richness score (normalized count of equipment)
        # Intensity capacity score (combines experience and recovery)
        # ── Progressive overload delta (redesigned multi-factor formula) ──
        #
        # progression_delta = base_rate × adherence × recovery × experience_mod
        #
        # base_rate:       3-7 % depending on experience
        # adherence:       0.6 × completion + 0.4 × streak_factor
        # recovery:        4-factor recovery score (computed above)
        # experience_mod:  Beginner 0.70 | Intermediate 1.00 | Advanced 1.15
        #
        # Adherence score: blend completion proxy (consistency) with streak
        # Age-adjusted capacity (older users may need adjusted intensity)
    def encode_features(self, user_profile: Dict) -> np.ndarray:
        # [Logic Hidden]
        """
        Encode categorical and multi-categorical features
        """
        # Encode categorical features
        # Experience encoding
            # If new value, use the most common (Beginner = 0)
        # Goal encoding
            # If new value, use the most common (Muscle Gain = 0)
        # Gender encoding
            # If new value, default to Male = 0
        # Equipment multi-hot encoding
            # If new equipment list, fit and transform
        # Injury multi-hot encoding
            # If new injury list, fit and transform
        # Create feature vector
        # Concatenate with encoded equipment and injury vectors
    def scale_features(self, feature_vector: np.ndarray) -> np.ndarray:
        # [Logic Hidden]
        """
        Scale numerical features while preserving categorical encodings
        """
        # Reshape if needed
        # Fit scaler if not already fitted
        # Transform features
    def process_user_profile(self, user_profile: Dict) -> np.ndarray:
        # [Logic Hidden]
        """
        Complete feature pipeline: Raw Input  Processed Features
        """
        # Step 1: Validate input
        # Step 2: Calculate derived features
        # Step 3: Encode features
        # Step 4: Scale features
    def get_feature_importance_template(self) -> Dict:
        # [Logic Hidden]
        """
        Return template for feature importance explanation
        """
    def cold_start_strategy(self, user_profile: Dict) -> Dict:
        # [Logic Hidden]
        """
        Handle cold start scenario with similarity-based matching
        """
        # For new users with limited history, use demographic and goal-based templates
        # Base template on experience and goal
        # Adjust for goal
def explain_pipeline_design():
    # [Logic Hidden]
    """
    Detailed explanation of the feature pipeline design
    """
    """)
    print("\n" + "=" * 40)
    print("SECTION 2  DERIVED FEATURES")
    print("=" * 40)
    print("""
Formulas and Importance:
1. BMI = weight / (height/100)^2
   - Importance: Health screening and load adjustment
2. Experience Score = mapping[experience] (1-3)
   - Importance: Determines baseline intensity and complexity
3. Recovery Score = avg(sleep/10, hydration/10, (10-stress)/10)
   - Importance: Adjusts intensity based on readiness to train
4. Consistency Score = user_provided_value
   - Importance: Influences progression rate and motivation strategies
5. Equipment Richness = min(1.0, len(equipment)/10)
   - Importance: Measures resource availability for exercise variety
6. Intensity Capacity = (experience_score * 0.6) + (recovery_score * 0.4)
   - Importance: Combined measure of ability to handle intense training
7. Progressive Overload Delta = base * adherence * recovery * experience_mod
   - Importance: Controls rate of progression to prevent plateaus
8. Age-Adjusted Capacity = intensity_capacity * age_factor
   - Importance: Accounts for age-related changes in recovery and capacity
    """)
    print("\n" + "=" * 40)
    print("SECTION 3  TARGET VARIABLES")
    print("=" * 40)
    print("""
ML Targets Defined:
- Exercise Category: Chest, Back, Legs, Shoulders, Arms, Core
  - Model: Multi-class classification
  - Purpose: Muscle group targeting based on goals and equipment
- Sets: 1-6 (integer regression/classification)
  - Model: Regression or ordinal classification
  - Purpose: Volume prescription based on experience and recovery
- Rep Range (low, high): 1-25 (pair of integers)
  - Model: Paired regression
  - Purpose: Intensity prescription based on goals (hypertrophy, strength, endurance)
- Rest Time: 30-240 seconds (integer regression)
  - Model: Regression
  - Purpose: Recovery optimization based on intensity and goals
- Intensity Level: Low, Moderate, High, Very High (classification)
  - Model: Multi-class classification
  - Purpose: Overall workout intensity based on capacity and goals
- Workout Split: Full Body, Upper/Lower, Push/Pull/Legs, etc. (classification)
  - Model: Multi-class classification
  - Purpose: Weekly structure based on days available and experience
Separate models needed because:
1. Different target types (classification vs regression)
2. Different feature importance for each target
3. Safety considerations vary by target
4. Different progression patterns for each aspect
    """)
    print("\n" + "=" * 40)
    print("SECTION 4  ENCODING STRATEGY")
    print("=" * 40)
    print("""
Encoding Approaches:
1. Label Encoding: 
   - Applied to: experience, goal, gender
   - Tradeoff: Preserves ordinal relationships but assumes equal distances between categories
2. One-Hot Encoding:
   - Applied to: exercise categories, workout splits
   - Tradeoff: Creates sparse matrices but treats categories equally
3. Multi-Hot Encoding (MultiLabelBinarizer):
   - Applied to: equipment, injuries
   - Tradeoff: Handles multiple simultaneous values but increases dimensionality
4. Binary Encoding:
   - Applied to: injury flags
   - Tradeoff: Efficient for yes/no features
    """)
    print("\n" + "=" * 40)
    print("SECTION 5  SCALING STRATEGY")
    print("=" * 40)
    print("""
Scaling Decisions:
1. Scaled: age, weight, height, bmi, days_per_week, session_time, 
          workout_history_count, streak_count, consistency_score, 
          recovery_score, equipment_richness, intensity_capacity, 
          progressive_overload_delta, age_adjusted_capacity
   - Reason: Ensures equal contribution to distance calculations and gradient descent
2. Left Raw: encoded categorical features (already normalized 0-1)
   - Reason: Already in appropriate range for ML models
3. Special Handling: equipment and injury vectors (binary, 0-1 range)
   - Reason: Natural binary representation
    """)
    print("\n" + "=" * 40)
    print("SECTION 6  COLD START STRATEGY")
    print("=" * 40)
    print("""
Cold Start Approach:
1. Similarity-Based Matching:
   - Compare new user demographics (age, gender, experience) to existing user clusters
   - Use k-nearest neighbors on demographic features
   - Apply successful patterns from similar users
2. Baseline Template Plans:
   - Beginner: Conservative intensity (50%), slow progression (3% weekly)
   - Intermediate: Moderate intensity (70%), moderate progression (5% weekly)
   - Advanced: Higher intensity (80%), faster progression (7% weekly)
3. Goal-Specific Adjustments:
   - Weight Loss: Higher volume, shorter rest, cardio emphasis
   - Muscle Gain: Moderate-heavy loads, 6-12 rep range, adequate rest
   - Strength: Heavy loads, 1-5 rep range, longer rest periods
   - Endurance: Lighter loads, higher reps, shorter rest periods
    """)
    print("\n" + "=" * 40)
    print("SECTION 7  PIPELINE FLOW")
    print("=" * 40)
    print("""
Step-by-Step Data Flow:
1. Raw Input  Validation
   - Sanitize and normalize input values
   - Apply default values for missing fields
   - Range-check all numerical inputs
2. Validation  Feature Engineering
   - Calculate derived features (BMI, scores, deltas)
   - Apply domain knowledge transformations
   - Create composite indicators
3. Feature Engineering  Encoding
   - Convert categorical to numerical representations
   - Apply multi-hot encoding for multi-value fields
   - Preserve interpretability where possible
4. Encoding  Scaling
   - Apply standardization to numerical features
   - Maintain binary nature of encoded features
   - Prepare for ML algorithm requirements
5. Scaling  Model
   - Feed to trained ML models for predictions
   - Generate multiple target predictions
   - Apply ensemble methods if available
6. Model  Safety Override
   - Check for injury contraindications
   - Verify intensity is appropriate for experience
   - Apply safety caps and limits
7. Safety Override  Final Output
   - Format recommendations for frontend
   - Include confidence scores
   - Provide safety warnings if needed
    """)
if __name__ == "__main__":
    # Example usage
    pipeline = FeaturePipeline()
    # Example user profile
    user_profile = {
        'age': 28,
        'weight': 75.0,
        'height': 180.0,
        'gender': 'Male',
        'experience': 'Intermediate',
        'goal': 'Muscle Gain',
        'equipment': ['Dumbbell', 'Barbell', 'Bench'],
        'injuries': ['Knee'],
        'days_per_week': 4,
        'session_time': 60,
        'workout_history_count': 25,
        'streak_count': 3,
        'consistency': 0.8,
        'sleep_score': 8.0,
        'hydration_score': 7.5,
        'stress_level': 4.0
    }
    # Process the profile
    features = pipeline.process_user_profile(user_profile)
    print(f"Generated feature vector shape: {features.shape}")
    print(f"Sample of features: {features[:10]}...")  # First 10 features
    # Show cold start strategy
    cold_start = pipeline.cold_start_strategy(user_profile)
    print(f"Cold start template: {cold_start}")
    # Explain the design
    explain_pipeline_design()
```

## backend-python/app/gemini_service.py
```python
# Ensure .env is loaded before reading key
# ===== LAZY INITIALIZATION WITH MODEL FALLBACK =====
# Models to try in order (first working one wins)
MODEL_CANDIDATES = [
def _get_model() -> Optional[genai.GenerativeModel]:
    # [Logic Hidden]
    """Lazily initialize the Gemini model on first use with automatic fallback."""
        # Bug #4: Show a helpful, actionable message when the key is missing.
    # Try each model candidate until one works
            # Quick validation call
def generate_workout_config(profile: Dict[str, Any], intensity: float) -> Tuple[int, str, int, list]:
    # [Logic Hidden]
    """
    Given a user profile and an intensity goal, use Gemini to intelligently
    determine the perfect: (sets, reps_range, rest_time_sec, rest_days_list)
    """
    """
    try:
        response = model.generate_content(prompt)
        text_resp = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_resp)
        return int(data.get('sets', 3)), str(data.get('reps', '10-12')), int(data.get('rest', 60)), list(data.get('rest_days', [2, 6]))
    except Exception as e:
        print(f"Failed to generate AI request: {e}")
        return 3, "10-12", 60, [2, 6]
# ===== CHATBOT =====
# Maximum conversation history to send to Gemini (prevents token overflow)
MAX_HISTORY_MESSAGES = 20
# Maximum characters per user message
MAX_MESSAGE_LENGTH = 2000
# ===== OFFLINE FALLBACK RESPONSES =====
FALLBACK_RESPONSES = {
    'greeting': "Hey there! 👋 I'm your Elevate AI Coach. While my AI brain is currently recharging (API quota reached), I can still share some tips!\n\n💡 **Quick Tip:** Focus on compound exercises like squats, deadlifts, and bench press — they give you the most bang for your buck!\n\nI'll be fully back online when the API quota resets. Try again later!",
    'workout': "Great that you're thinking about workouts! 💪\n\nHere are some general tips based on fitness best practices:\n\n• **Beginners:** 3-4 days/week, full body splits\n• **Intermediate:** 4-5 days/week, upper/lower or push/pull/legs\n• **Advanced:** 5-6 days/week, specific muscle group splits\n\n**Note:** My AI brain is recharging (API quota reached). For personalized AI recommendations, please try again later!",
    'nutrition': "Nutrition is key! 🥗\n\nHere are some fundamentals:\n\n• **Muscle Gain:** Eat in a caloric surplus (~300-500 cal above maintenance)\n• **Weight Loss:** Eat in a moderate deficit (~300-500 cal below maintenance)\n• **Protein:** Aim for 1.6-2.2g per kg of bodyweight daily\n• **Water:** At least 2-3 liters per day\n\n**Note:** My AI engine is recharging. Try again later for personalized meal advice!",
    'recovery': "Recovery is just as important as training! 😴\n\n• **Sleep:** 7-9 hours per night\n• **Rest days:** At least 1-2 per week\n• **Stretching:** 10-15 mins post-workout\n• **Hydration:** Stay consistent throughout the day\n\n**Note:** My AI brain is currently recharging. Full personalized coaching will resume soon!",
    'default': "Thanks for your question! 🤔\n\nI'm experiencing a temporary AI service interruption (API quota reached), so I can't give you a fully personalized answer right now.\n\n**In the meantime:**\n• Check out the Workout page for your exercise plan\n• Visit the Nutrition page for meal recommendations\n• I'll be fully operational after the API quota resets\n\nPlease try again in a few hours! 💪"
}
def _get_fallback_response(message: str) -> str:
    """Return a helpful offline response when the AI is unavailable."""
def _build_system_prompt(profile: Dict[str, Any]) -> str:
    # [Logic Hidden]
    """Build the system prompt with user profile context."""
def _trim_history(history: list) -> list:
    # [Logic Hidden]
    """Trim conversation history to prevent token overflow."""
def get_chatbot_response(user_message: str, profile: Dict[str, Any], chat_history: list = None) -> str:
    # [Logic Hidden]
    """
    Generate an AI response to a user's fitness question.
    Falls back to smart offline responses when AI is unavailable.
    """
    # Sanitize input
    # If model is unavailable, use smart offline fallback
    # Build conversation context from history
        # If quota exhausted, use fallback
```

## backend-python/app/hybrid_volume_optimizer.py
```python
"""
Hybrid Volume Optimizer for Sets/Reps
======================================
Combines rule-based logic with user-specific adaptation.
ML models can be plugged in when available.
Author: Elevate Team
"""
# -*- coding: utf-8 -*-
class HybridVolumeOptimizer:
    # [Logic Hidden]
    """
    Smart hybrid system for calculating optimal sets/reps.
    Phases:
    1. Rule-based starting point (safe, proven defaults)
    2. User-specific adaptation (learns from THEIR workouts)
    3. ML enhancement (when models available)
    """
    def __init__(self):
        # [Logic Hidden]
        # ML models (optional - will use rules if not available)
        # Try to load ML models
        # Progression engine for multi-factor overload
        # Rule-based configuration
    def _try_load_ml_models(self):
        # [Logic Hidden]
        """Try to load ML models, gracefully degrade if not available"""
            # Silently fail - will use rules
    def calculate_optimal_sets(
        self,
        user_profile: Dict,
        workout_history: List[Dict] = None,
        exercise_type: str = 'compound'
    ) -> int:
        # [Logic Hidden]
        """
        Calculate optimal sets using hybrid approach.
        Args:
            user_profile: User's current profile
            workout_history: List of completed workouts (for adaptation)
            exercise_type: 'compound' or 'isolation'
        Returns:
            Optimal number of sets
        """
        # Phase 1: Rule-based starting point
        # Phase 2: User-specific adaptation (if history available)
        # Phase 3: ML adjustment (if model available)
            # Blend ML prediction with rule-based (weight depends on data confidence)
        # Apply safety caps
    def calculate_optimal_reps(
        self,
        user_profile: Dict,
        workout_history: List[Dict] = None,
        intensity: float = 0.75
    ) -> str:
        # [Logic Hidden]
        """
        Calculate optimal rep range using hybrid approach.
        Args:
            user_profile: User's current profile
            workout_history: List of completed workouts
            intensity: Target intensity (0.0-1.0)
        Returns:
            Rep range string (e.g., "8-12")
        """
        # Phase 1: Rule-based starting point
        # Phase 2: User-specific adaptation
        # Phase 3: ML adjustment
            # Blend rep ranges
        # Apply age-based safety adjustments
    def _get_rule_based_sets(self, user_profile: Dict, exercise_type: str) -> int:
        # [Logic Hidden]
        """Phase 1: Get rule-based starting sets"""
        # Base sets from experience
        # Adjust for goal
        # Adjust for exercise type
        # Age adjustment (safety)
    def _get_rule_based_reps(self, user_profile: Dict, intensity: float) -> str:
        # [Logic Hidden]
        """Phase 1: Get rule-based starting reps"""
        # Base reps from goal
        # Adjust for experience
            # Beginners benefit from higher reps (practice, lighter weight)
            # Advanced can handle lower reps with heavier weight
        # Adjust for intensity
    def _adapt_based_on_history(
        self,
        base_sets: int,
        workout_history: List[Dict],
        user_profile: Dict
    ) -> int:
        # [Logic Hidden]
        """Phase 2: Adapt sets based on user's workout history — uses ProgressionEngine when available"""
        # ── Use ProgressionEngine if available ──
                # Build current params from base
                # Estimate completion from recent history
        # ── Fallback: original heuristic ──
    def _adapt_reps_based_on_history(
        self,
        base_reps: str,
        workout_history: List[Dict],
        user_profile: Dict
    ) -> str:
        # [Logic Hidden]
        """Phase 2: Adapt rep range based on user's history"""
        # Analyze recent performance
        # Check if user consistently hits top of rep range
        # Adjust rep range based on performance
            # User consistently hits top  increase difficulty
            # User struggling  decrease difficulty
    def _predict_with_ml_model(self, user_profile: Dict, target: str) -> float:
        # [Logic Hidden]
        """Phase 3: Predict using ML model if available"""
        # This would use the loaded ML models
        # For now, return rule-based fallback
    def _apply_safety_caps(self, sets: int, user_profile: Dict) -> int:
        # [Logic Hidden]
        """Apply safety caps based on user characteristics"""
        # Age caps
        # Experience caps
        # Injury considerations
        # Absolute bounds
    def _apply_age_based_rep_adjustments(self, rep_range: str, user_profile: Dict) -> str:
        # [Logic Hidden]
        """Apply age-based safety adjustments to rep range"""
            # Older adults: higher reps, lighter weight
            # Ensure minimum rep of 8 for safety
            # Younger users: moderate reps, focus on form
    def _shift_rep_range(self, rep_range: str, shift: int) -> str:
        # [Logic Hidden]
        """Shift rep range up or down"""
    def _blend_rep_ranges(self, range1: str, range2: str, weight: float) -> str:
        # [Logic Hidden]
        """Blend two rep ranges based on confidence weight"""
    def get_volume_recommendation(
        self,
        user_profile: Dict,
        workout_history: List[Dict] = None,
        exercise_name: str = '',
        exercise_type: str = 'compound'
    ) -> Dict:
        # [Logic Hidden]
        """
        Get complete volume recommendation (sets, reps, rest) for an exercise.
        Returns:
            Dict with sets, reps, rest_time, and reasoning
        """
        # Calculate intensity based on goal
        # Calculate optimal sets and reps
        # Calculate rest time
        # Build reasoning
    def _calculate_rest_time(self, intensity: float, user_profile: Dict) -> int:
        # [Logic Hidden]
        """Calculate rest time based on intensity and goal"""
        # Base rest from intensity
        # Age adjustment
        # Goal adjustment
    def _build_reasoning(
        self,
        sets: int,
        reps: str,
        user_profile: Dict,
        workout_history: List[Dict] = None
    ) -> str:
        # [Logic Hidden]
        """Build human-readable reasoning for recommendations"""
        # Experience reason
        # Goal reason
        # Age reason
        # History-based reason
# Singleton pattern
def get_hybrid_optimizer():
    # [Logic Hidden]
    """Get or create hybrid optimizer instance"""
```

## backend-python/app/main.py
```python
# ===== LOGGING CONFIGURATION =====
@app.on_event("startup")
async def startup_event():
    # [Logic Hidden]
@app.on_event("shutdown")
async def shutdown_event():
    # [Logic Hidden]
# ===== CORS CONFIGURATION (FIXED) =====
# CRITICAL: Cannot use "*" with allow_credentials=True
# Must specify exact origins
# ===== MODELS =====
class UserProfile(BaseModel):
    # [Logic Hidden]
class ProfileUpdateRequest(BaseModel):
    # [Logic Hidden]
    """Pydantic model for profile update with validation"""
class WorkoutPlanRequest(BaseModel):
    # [Logic Hidden]
class MealPlanRequest(BaseModel):
    # [Logic Hidden]
class NutritionRequest(BaseModel):
    # [Logic Hidden]
class NutritionSwapRequest(BaseModel):
    # [Logic Hidden]
# ===== MISSING ENDPOINTS (ADD THESE) =====
@app.post("/api/users/save")
async def save_user_profile(profile: UserProfile):
    # [Logic Hidden]
    """Save user profile"""
@app.post("/api/workout/save")
async def save_workout_plan(data: dict):
    # [Logic Hidden]
    """Save workout plan"""
@app.post("/api/meals/save")
async def save_meal_plan(data: dict):
    # [Logic Hidden]
    """Save meal plan"""
@app.post("/api/progress/save")
async def save_progress(data: dict):
    # [Logic Hidden]
    """Save user progress"""
# Add these endpoints BEFORE the bottom of the file
@app.post("/generate-plan")
async def generate_plan(profile: dict):
    # [Logic Hidden]
    """Generate AI workout and meal plan"""
@app.post("/nutrition")
async def generate_nutrition(request: NutritionRequest):
    # [Logic Hidden]
@app.post("/nutrition/swap")
async def swap_food(request: NutritionSwapRequest):
    # [Logic Hidden]
@app.put("/profile/update")
async def update_profile_endpoint(profile: UserProfile):
    # [Logic Hidden]
    """
    Update user profile - Basic endpoint without regeneration
    Production-grade with:
    - Pydantic validation
    - Structured error handling
    - Detailed logging
    """
        # Validate required fields
        # Simulate database update (replace with actual DB logic)
@app.put("/profile/update-with-regeneration")
async def update_profile_and_regenerate(profile: UserProfile):
    # [Logic Hidden]
    """Update user profile and regenerate workout/meal plans if needed"""
        # Debug: Print the received profile to see what's being received
        # Determine if changes require plan regeneration
        # Regenerate workout plan if needed
        # Regenerate meal plan if needed
@app.put("/profile/update-safe")
async def update_profile_safe(profile_data: ProfileUpdateRequest):
    # [Logic Hidden]
    """
    SAFE PROFILE UPDATE ENDPOINT - Production Ready
    Features:
    - Graceful degradation (profile updates even if regeneration fails)
    - Comprehensive error handling
    - Transaction-like safety
    - Detailed logging with request IDs
    - Proper HTTP status codes
    Request Body:
    - All fields optional (partial updates supported)
    - Validated with Pydantic constraints
    """
    # Initialize response structure
        # ===== STEP 1: LOG INCOMING REQUEST =====
        # ===== STEP 2: VALIDATE INPUT =====
        # ===== STEP 3: SIMULATE JWT DECODE (Add real JWT logic here) =====
        # In production, decode JWT from x-auth-token header
        # Example: token = request.headers.get("x-auth-token")
        #          user = decode_jwt(token)
        # ===== STEP 4: LOAD EXISTING PROFILE (Simulated DB read) =====
            # Replace with actual DB query
            # existing_profile = await db.profiles.find_one({"user_id": user_id})
        # ===== STEP 5: MERGE AND UPDATE PROFILE =====
        # ===== STEP 6: SAVE TO DATABASE (Simulated) =====
            # Replace with actual DB update
            # await db.profiles.update_one({"user_id": user_id}, {"$set": updated_profile})
        # ===== STEP 7: DETECT CHANGES FOR REGENERATION =====
        def check_workout_changes(old: dict, new: dict) -> bool:
            # [Logic Hidden]
            """Check if changes affect workout plans"""
        def check_meal_changes(old: dict, new: dict) -> bool:
            # [Logic Hidden]
            """Check if changes affect meal plans"""
        # ===== STEP 8: REGENERATE WORKOUT (ISOLATED - FAILURE WON'T BLOCK PROFILE UPDATE) =====
                # Replace with actual regeneration logic
                # workout_result = await regenerate_workout(user_id, updated_profile)
        # ===== STEP 9: REGENERATE MEAL (ISOLATED - FAILURE WON'T BLOCK PROFILE UPDATE) =====
                # Replace with actual regeneration logic
                # meal_result = await regenerate_meal(user_id, updated_profile)
        # ===== STEP 10: BUILD SUCCESS RESPONSE =====
        # Set appropriate status based on errors
# ===== EXISTING ENDPOINTS =====
@app.get("/health")
async def health_check():
    # [Logic Hidden]
@app.post("/ml/get-weekly-plan")
async def get_weekly_plan(request: WorkoutPlanRequest):
    # [Logic Hidden]
    """Generate weekly workout plan"""
@app.post("/ml/get-daily-meals")
async def get_daily_meals(request: MealPlanRequest):
    # [Logic Hidden]
    """Generate daily meal plan"""
# ===== STARTUP =====
@app.on_event("startup")
async def startup_event():
    # [Logic Hidden]
@app.on_event("shutdown")
async def shutdown_event():
    # [Logic Hidden]
```

## backend-python/app/meal_engine.py
```python
"""
MealEngine — Wrapper that delegates to the dataset-driven
DeterministicMealEngine for all meal plan generation and swapping.
"""
class MealEngine:
    # [Logic Hidden]
    """
    Thin wrapper kept for backward-compatibility with the rest of the codebase.
    All heavy lifting is done by DatasetMealEngine (deterministic_meal_engine.py).
    """
    def __init__(self):
        # [Logic Hidden]
    # ─────────────────────────────────────────────
    #  suggest_daily_meals — called by /nutrition
    # ─────────────────────────────────────────────
    def suggest_daily_meals(self, user_profile: Dict,
                            workout_intensity: str = "moderate") -> Dict:
        # [Logic Hidden]
        """
        Generate daily meal recommendations from the dataset.
        Returns exactly the format the frontend expects.
        """
        # Generate the full weekly plan from real dataset
        # Pick today's day
        # Flatten into a single list of meals for the frontend
    # ─────────────────────────────────────────────
    #  generate_meal_plan — weekly with workout integration
    # ─────────────────────────────────────────────
    def generate_meal_plan(self, profile: Dict,
                           weekly_workout_plan: List[Dict] = None) -> Dict:
        # [Logic Hidden]
        """
        Generate weekly meal plan, adjusting activity level based on actual workout plan.
        """
        # BUG FIX: Derive activity level from workout plan if available
            # Map exercise volume to activity level for TDEE calculation
    # ─────────────────────────────────────────────
    #  get_swap_options — used by /nutrition/swap
    # ─────────────────────────────────────────────
    def get_swap_options(self, food_name: str, meal_type: str,
                          profile: Dict, limit: int = 5) -> List[Dict]:
        # [Logic Hidden]
# ─── Singleton accessor ───
def get_meal_engine():
    # [Logic Hidden]
```

## backend-python/app/ml_utils.py
```python
# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
class MLService:
    # [Logic Hidden]
    def __init__(self):
        # [Logic Hidden]
        # 1. Define Paths (Priority: Processed > Raw)
    def load_data(self):
        # [Logic Hidden]
        # --- LOAD EXERCISES ---
        # --- LOAD NUTRITION ---
        # Safety Fills to prevent crashes
    def calculate_macros(self, user):
        # [Logic Hidden]
        """ Calculates BMR & Macros based on Goal """
    def recommend_workout(self, user_profile, equipment_list):
        # [Logic Hidden]
        """ Generates the Fixed Plan (Objective #1) """
        # 1. Equipment Filter
        # 2. Injury Filter (Objective #1 - Safety)
        # 3. Split Logic
            # Muscle Mapping
                    # --- OBJECTIVE #17: PROGRESSIVE OVERLOAD ---
    def recommend_meals(self, goal, preference, allergies, target_calories):
        # [Logic Hidden]
        """ Generates Meal Plan (Objective #2) """
    def recommend_weekly_meals(self, goal, preference, allergies, weekly_workout_plan):
        # [Logic Hidden]
        """ Generates a fixed weekly meal plan aligned with the workout structure """
        # Generate a meal plan for each day of the week
            # Calculate daily calories based on workout intensity
            # For now, use a consistent daily calorie target
            # Define meal targets for each day
                    # Default meal if none found
    def recommend_weekly_workout(self, user_profile, equipment_list):
        # [Logic Hidden]
        """ Generates a 7-day weekly workout plan that repeats by default """
        # 1. Equipment Filter
        # 2. Injury Filter (Safety)
        # 3. Weekly Split based on experience and days per week
        # Define weekly schedule based on experience and days
                # Add light stretching or recovery activities
                # Add cardio exercises
                    # Default cardio if none found
                # Add light movement and stretching
                # Muscle Mapping for workout days
                        # Determine sets/reps based on experience
    # --- NEW: SWAP FUNCTION (Restored for your Button) ---
    def get_alternative_meal(self, swap_group, exclude_name):
        # [Logic Hidden]
        """ Finds a different meal in the same group """
# Create Singleton
```

## backend-python/app/multitarget_nutrition_model.py
```python
"""
Multi-Target XGBoost Regression System for Nutrition Prediction
This module implements a multi-target regression model to predict:
- breakfast_calories
- lunch_calories
- dinner_calories
- snack_calories
- protein_total
- carbs_total
- fats_total
With post-processing constraints and production considerations.
"""
class MultiTargetNutritionModel:
    # [Logic Hidden]
    """
    Production-ready multi-target XGBoost model for nutrition parameter prediction
    """
    def __init__(self, random_state: int = 42):
        # [Logic Hidden]
        # Initialize the base model
        # Wrap with MultiOutputRegressor
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        # [Logic Hidden]
        """
        Prepare features from the dataframe
        """
        # Define feature columns (these should match your user profile features)
        # Select features
        X = df[feature_columns].copy()
        # Ensure all values are numeric
        X = X.fillna(0)
        X = X.astype(float)
        # Store feature names
        # Define target columns
    def _create_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        # [Logic Hidden]
        """
        Create synthetic training data for demonstration
        In production, this would be replaced with real user nutrition history
        """
        # Generate synthetic user profiles
        # Calculate BMR using Mifflin-St Jeor equation
        # Calculate TDEE based on activity level
        # Adjust TDEE based on goal
        # Generate realistic target values based on features
        # Calorie distribution by meal
        # Calculate total calories
        # Calculate macros based on goal and dietary preferences
        # Protein requirements (g per kg body weight)
        # Carbs and fats based on goal
        # Apply macros based on goal
        # Ensure protein is calculated properly
        # Recalculate carbs to account for protein and fat
        # Ensure all targets are within reasonable bounds
    def train(self, 
              X_train: pd.DataFrame, 
              y_train: np.ndarray, 
              X_val: pd.DataFrame = None, 
              y_val: np.ndarray = None,
              hyperparameter_tuning: bool = True,
              cv_folds: int = 3) -> Dict:
        # [Logic Hidden]
        """
        Train the multi-target model with optional hyperparameter tuning
        """
        # Prepare training data
            # Create a temporary dataframe with features and targets to use _prepare_features
            # If X_train is already processed
        # Prepare validation data if provided
        # Hyperparameter tuning
            # Define parameter distributions
            # Use TimeSeriesSplit for temporal data
            # Perform randomized search with MAE as the scoring metric
            # Fit the random search
            # Update model with best parameters
            # Train with default parameters
        # Evaluate the model
    def _calculate_mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        # [Logic Hidden]
        """
        Calculate MAE for each target variable
        """
    def _calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        # [Logic Hidden]
        """
        Calculate RMSE for each target variable
        """
    def _extract_feature_importance(self) -> Dict[str, List[float]]:
        # [Logic Hidden]
        """
        Extract feature importance from each individual regressor
        """
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        # [Logic Hidden]
        """
        Make predictions with post-processing constraints applied
        """
        # Prepare features
            # Create a temporary dataframe to use _prepare_features
            # Add placeholder target columns to satisfy _prepare_features
        # Make predictions
        # Apply post-processing constraints
    def _apply_post_processing_constraints(self, predictions: np.ndarray, X: pd.DataFrame) -> np.ndarray:
        # [Logic Hidden]
        """
        Apply post-processing constraints to ensure:
        - Total calories match TDEE target
        - Macros are proportionally adjusted
        - Allergies are enforced (simulated)
        """
        # Create a copy to avoid modifying original
        # Calculate original total calories per sample
        # Calculate target TDEE for each sample (this would come from user profile in practice)
        # For demonstration, we'll calculate it based on the features
            # Calculate BMR and TDEE based on features
            # Activity multipliers
            # TDEE calculation
            # Adjust based on goal
            # If X is not a DataFrame, use a default approach
        # Adjust meal calories to match TDEE target
                # Apply adjustment to meal calories
        # Now adjust macros proportionally to match the new total calories
        # Calculate new total calories after adjustment
        # Adjust protein, carbs, and fats proportionally
                # Calculate the ratio of each macro to the total
                # Apply the same ratios to the new total calories
                # But ensure they stay within reasonable bounds
        # Apply bounds to ensure realistic values
        # Meal calories bounds
        # Macro bounds
    def save_model(self, model_path: str = None) -> str:
        # [Logic Hidden]
        """
        Save the trained model with versioning
        """
        # Create directory if it doesn't exist
        # Prepare model info
        # Save the model package
    def load_model(self, model_path: str):
        # [Logic Hidden]
        """
        Load a trained model with integrity check
        """
        # Calculate and verify checksum
        # For now, we'll just log the checksum - in production, this would be compared to a known good value
        # Verify required keys exist
    def evaluate(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict:
        # [Logic Hidden]
        """
        Evaluate the model on test data
        """
        # Calculate metrics
        # Calculate MAE and RMSE per target
        # Calculate R score
def create_nutrition_training_pipeline():
    # [Logic Hidden]
    """
    Create and run the complete nutrition model training pipeline
    """
    # Initialize the model
    # Create synthetic training data
    # Prepare features and targets
    # Split the data (time-based split)
    # Further split training for validation
    # Train the model
    # Evaluate on test set
    # Save the model
    # Demonstrate inference
    # Show feature importance for the first target (breakfast calories)
def validation_checks(model: MultiTargetNutritionModel, X_test: pd.DataFrame, y_test: np.ndarray):
    # [Logic Hidden]
    """
    Perform validation checks on the model
    """
    # Make predictions
    # Check 1: Total calories match TDEE target (approximately)
    # Check 2: All values are positive
    # Check 3: Values are within reasonable bounds
    # Check 4: Protein, carbs, and fats sum is approximately equal to total calories
    # Run the complete pipeline
    # Perform validation checks
    # Create test data for validation
```

## backend-python/app/multi_output_xgboost_model.py
```python
"""
Production Multi-Output XGBoost Model for Workout Parameter Prediction
This module implements a multi-target regression model to predict:
- sets
- reps_low
- reps_high
- rest_time
- intensity
With safety layers and production considerations.
"""
class MultiOutputXGBoostModel:
    # [Logic Hidden]
    """
    Production-ready multi-output XGBoost model for workout parameter prediction
    """
    def __init__(self, random_state: int = 42):
        # [Logic Hidden]
        # Safety bounds for predictions
        # Initialize the base model
        # Wrap with MultiOutputRegressor
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        # [Logic Hidden]
        """
        Prepare features from the dataframe
        """
        # Define feature columns (these should match your feature pipeline output)
        # Select features
        X = df[feature_columns].copy()
        # Ensure all values are numeric
        X = X.fillna(0)
        X = X.astype(float)
        # Store feature names
        # Define target columns
    def _create_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        # [Logic Hidden]
        """
        Create synthetic training data for demonstration
        In production, this would be replaced with real user workout history
        """
        # Generate synthetic user profiles
        # Generate realistic target values based on features
        # Sets: More experienced users tend to do more sets
        # Reps: Beginners do higher reps, advanced do lower reps for strength
        # Rest time: More intense workouts need more rest
        # Intensity: Based on experience and recovery
        # Ensure targets are within bounds
    def train(self, 
              X_train: pd.DataFrame, 
              y_train: np.ndarray, 
              X_val: pd.DataFrame = None, 
              y_val: np.ndarray = None,
              hyperparameter_tuning: bool = True,
              cv_folds: int = 3) -> Dict:
        # [Logic Hidden]
        """
        Train the multi-output model with optional hyperparameter tuning
        """
        # Prepare training data
            # If X_train is already processed
        # Prepare validation data if provided
        # Hyperparameter tuning
            # Define parameter grid
            # Use TimeSeriesSplit for temporal data
            # Perform randomized search
            # Fit the random search
            # Update model with best parameters
            # Train with default parameters
        # Evaluate the model
    def _calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        # [Logic Hidden]
        """
        Calculate RMSE for each target variable
        """
    def _extract_feature_importance(self) -> Dict[str, List[float]]:
        # [Logic Hidden]
        """
        Extract feature importance from each individual regressor
        """
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        # [Logic Hidden]
        """
        Make predictions with safety layer applied
        """
        # Prepare features
        # Make predictions
        # Apply safety layer
    def _apply_safety_layer(self, predictions: np.ndarray, X: pd.DataFrame) -> np.ndarray:
        # [Logic Hidden]
        """
        Apply safety constraints to predictions
        """
        # Create a copy to avoid modifying original
        # Clamp each target within safe bounds
        # Apply beginner intensity cap
                # Assuming experience_encoded is at index 5 based on feature order
            # For beginners (experience_encoded == 0), cap intensity at 0.7
        # Apply set bounds based on experience
            # For beginners, cap sets at 4
    def save_model(self, model_path: str = None) -> str:
        # [Logic Hidden]
        """
        Save the trained model with versioning
        """
        # Create directory if it doesn't exist
        # Prepare model info
        # Save the model package
    def load_model(self, model_path: str):
        # [Logic Hidden]
        """
        Load a trained model with integrity check
        """
        # Calculate and verify checksum
        # For now, we'll just log the checksum - in production, this would be compared to a known good value
        # Verify required keys exist
    def evaluate(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict:
        # [Logic Hidden]
        """
        Evaluate the model on test data
        """
        # Calculate metrics
        # Calculate RMSE per target
        # Calculate R score
def create_training_pipeline():
    # [Logic Hidden]
    """
    Create and run the complete training pipeline
    """
    # Initialize the model
    # Create synthetic training data
    # Prepare features and targets
    # Split the data (time-based split)
    # Further split training for validation
    # Train the model
    # Evaluate on test set
    # Save the model
    # Demonstrate inference
    # Show feature importance
def production_notes():
    # [Logic Hidden]
    """
    Production considerations and notes
    """
    """
    print(notes)
if __name__ == "__main__":
    # Run the complete pipeline
    model, training_results, test_evaluation = create_training_pipeline()
    # Print production notes
    production_notes()
    print("\nPipeline completed successfully!")
```

## backend-python/app/nutrition_intelligence.py
```python
"""
Nutrition Intelligence Engine for Elevate Fitness
This module handles intelligent meal planning with hard constraints,
macro balancing, and dietary restrictions compliance.
"""
class NutritionIntelligenceEngine:
    # [Logic Hidden]
    """
    Complete nutrition intelligence engine with constraint satisfaction
    """
    def __init__(self, nutrition_data_path: str = None):
        # [Logic Hidden]
        # Initialize multi-target nutrition model
        # Load nutrition data
            # Fallback data
        # Define macro ratios by goal
        # Activity multipliers
        # Protein requirements (g per kg of body weight)
        # Encode categorical variables for the model
    def validate_user_input(self, user_profile: Dict) -> Dict:
        # [Logic Hidden]
        """
        Validate and sanitize user input
        """
        # Required fields with defaults
        # Validate ranges
    def calculate_derived_metrics(self, user_profile: Dict) -> Dict:
        # [Logic Hidden]
        """
        Calculate derived nutritional metrics with extreme value handling
        """
        # Validate and clamp extreme values
        # BMR calculation (Mifflin-St Jeor Equation)
        # Clamp BMR to reasonable range
        # TDEE calculation
        # Clamp TDEE to reasonable range
        # Calorie target based on goal
        # Clamp calorie target to reasonable range
        # Protein requirement (g per kg body weight)
        # Clamp protein requirement to reasonable range
        # Macro targets based on goal
        # Convert to grams
        # Fiber minimum (25g for women, 38g for men, or 14g per 1000 calories)
    def apply_hard_constraints(self, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        # [Logic Hidden]
        """
        Apply hard constraints to filter foods
        """
        # Exclude allergens (only if column exists)
                # Log warning but continue
        # Dietary preference constraints
        # Food dislikes
        # Remove null calorie entries
    def calculate_meal_splits(self, daily_calories: float) -> Dict[str, float]:
        # [Logic Hidden]
        """
        Calculate calorie splits for different meals
        """
    def select_meals_for_day(self, available_foods: pd.DataFrame,
                           meal_calories: Dict[str, float],
                           user_profile: Dict,
                           previous_days_meals: List[str] = None) -> Dict[str, List[Dict]]:
        # [Logic Hidden]
        """
        Select meals for a single day with diversity and constraint satisfaction
        """
            # Filter by meal type if available
                # Try to match meal type, but fall back to all if none match
            # Avoid recently used meals (3-day rule)
                # Check if 'name' column exists before filtering
            # If no foods left after filtering, use original set
            # If still empty, use fallback foods
            # Select meals that best match target calories
            # If no meals were selected, use fallback
    def _get_fallback_foods(self, meal_type: str) -> pd.DataFrame:
        # [Logic Hidden]
        """
        Get fallback foods when filtering removes all options
        """
        # Create minimal fallback foods based on meal type
    def _get_fallback_meal(self, meal_type: str, target_calories: float) -> List[Dict]:
        # [Logic Hidden]
        """
        Get a fallback meal when no suitable foods are found
        """
    def _select_meals_by_calories(self, foods_df: pd.DataFrame, target_calories: float, meal_type: str) -> List[Dict]:
        # [Logic Hidden]
        """
        Select meals that best match target calories for a meal type
        """
        # Sort by proximity to target calories
            # If this food fits reasonably well
        # If no meals were selected, pick the closest one
    def generate_weekly_plan(self, user_profile: Dict) -> Dict:
        # [Logic Hidden]
        """
        Generate a complete weekly meal plan using multi-target model
        """
        # Validate and derive metrics
        # Prepare features for the multi-target model
        # Use the multi-target model to predict nutrition parameters
            # Extract predictions
            # Fallback to original method
        # Apply hard constraints
        # Create meal splits based on model predictions
        # Generate weekly plan
            # Get previous days' meals for diversity
            # Select meals for this day
            # Add to tracking
        # Calculate weekly consistency score
        # Generate shopping list
        # Create final output
    def _prepare_features_for_model(self, user_profile: Dict) -> pd.DataFrame:
        # [Logic Hidden]
        """
        Prepare user profile features for the multi-target model
        """
        # Create a single-row DataFrame with the user's features
    def _calculate_weekly_consistency(self, weekly_plan: Dict, user_profile: Dict) -> float:
        # [Logic Hidden]
        """
        Calculate how well the weekly plan meets nutritional targets
        """
        # Calculate actual totals
        # Calculate target totals for the week
        # Calculate consistency score (0-1, where 1 is perfect)
        # Average consistency (clamped between 0 and 1)
    def _generate_shopping_list(self, weekly_plan: Dict) -> Dict:
        # [Logic Hidden]
        """
        Generate aggregated shopping list for the week
        """
    def _calculate_weekly_macros(self, weekly_plan: Dict) -> Dict:
        # [Logic Hidden]
        """
        Calculate total macros for the week
        """
    def swap_meal(self, weekly_plan: Dict, day: str, meal_type: str, new_meal: str) -> Dict:
        # [Logic Hidden]
        """
        Swap a specific meal in the weekly plan
        """
        # This would implement meal swapping logic
        # For now, we'll just return the plan unchanged
        # In a full implementation, this would validate the swap against constraints
def explain_nutrition_engine_design():
    # [Logic Hidden]
    """
    Detailed explanation of the nutrition intelligence engine design
    """
    """)
    print("\n" + "=" * 40)
    print("SECTION 2  DERIVED CALCULATIONS")
    print("=" * 40)
    print("""
Exact Formulas:
1. BMR (Mifflin-St Jeor):
   - Male: BMR = 10  weight(kg) + 6.25  height(cm) - 5  age(y) + 5
   - Female: BMR = 10  weight(kg) + 6.25  height(cm) - 5  age(y) - 161
2. TDEE: TDEE = BMR  Activity_Multiplier
   - Sedentary: 1.2, Light: 1.375, Moderate: 1.55, Active: 1.725, Very Active: 1.9
3. Calorie Target: Calorie_Target = TDEE  Goal_Multiplier
   - Weight Loss: 0.85, Fat Loss: 0.80, Muscle Gain: 1.10, Strength: 1.05, Others: 1.00
4. Protein Requirement: Weight(kg)  Protein_G_per_kg
   - Beginners: 1.6g, Intermediate: 1.8g, Advanced: 2.2g
5. Macro Ratios by Goal:
   - Weight Loss: P:35%, C:35%, F:30%
   - Fat Loss: P:40%, C:30%, F:30%
   - Muscle Gain: P:30%, C:50%, F:20%
   - Strength: P:30%, C:55%, F:15%
   - Endurance: P:15%, C:70%, F:15%
   - Maintenance: P:25%, C:50%, F:25%
6. Fiber Minimum: Max(25 for women/38 for men, 14g per 1000 calories)
    """)
    print("\n" + "=" * 40)
    print("SECTION 3  TARGET VARIABLES")
    print("=" * 40)
    print("""
Defined Targets:
- Daily Calorie Target: Calculated from BMR, activity, and goal
- Meal Calorie Splits: Breakfast(25%), Lunch(35%), Dinner(30%), Snacks(10%)
- Macro per Meal: Distributed according to daily targets
- Weekly Consistency Score: 0-1 measure of how well plan meets targets
    """)
    print("\n" + "=" * 40)
    print("SECTION 4  HARD CONSTRAINT ENGINE")
    print("=" * 40)
    print("""
Constraint Logic:
1. Calorie Clamp: All selected meals must fit within daily calorie targets
2. Macro Correction: Adjust selections to meet protein/carb/fat ratios
3. Allergy Exclusion: Foods containing allergens are filtered out completely
4. Dietary Enforcement: Vegetarian/Vegan filters remove animal products
5. Minimum Protein: Ensure protein requirements are always met regardless of other constraints
    """)
    print("\n" + "=" * 40)
    print("SECTION 5  WEEKLY GENERATION LOGIC")
    print("=" * 40)
    print("""
Generation Logic:
1. Diversity Scoring: Track previously selected meals to avoid repetition
2. Repetition Avoidance: 3-day rule prevents same meals within 3 days
3. Cuisine Rotation: Distribute different cuisine types throughout the week
4. Shopping List Aggregation: Combine ingredients needed for the entire week
    """)
    print("\n" + "=" * 40)
    print("SECTION 6  FINAL JSON OUTPUT STRUCTURE")
    print("=" * 40)
    print("""
Example Production JSON:
{
  "user_profile": {
    "age": 28,
    "weight": 75.0,
    "height": 180.0,
    "gender": "Male",
    "goal": "Muscle Gain",
    "daily_calorie_target": 2850.0,
    "protein_requirement_g": 135.0,
    "macro_targets": {
      "protein_calories": 855.0,
      "carb_calories": 1425.0,
      "fat_calories": 570.0
    },
    "macro_targets_g": {
      "protein_g": 213.8,
      "carb_g": 356.3,
      "fat_g": 63.3
    }
  },
  "weekly_plan": {
    "Monday": {
      "breakfast": [
        {
          "name": "Oatmeal",
          "calories": 389,
          "protein": 17,
          "carbs": 66,
          "fat": 6.9,
          "fiber": 10.6,
          "meal_type": "breakfast"
        }
      ],
      "lunch": [...],
      "dinner": [...],
      "snack": [...]
    },
    ...
  },
  "weekly_summary": {
    "total_calories": 19950,
    "weekly_macro_totals": {
      "protein_g": 1493.4,
      "carbs_g": 2492.3,
      "fat_g": 443.1
    },
    "consistency_score": 0.92,
    "shopping_list": {
      "Grilled Chicken Breast": 7,
      "Brown Rice": 7,
      "Broccoli": 7,
      ...
    }
  },
  "generation_timestamp": "2023-12-07T10:30:45.123456"
}
    """)
if __name__ == "__main__":
    # Example usage
    engine = NutritionIntelligenceEngine()
    # Example user profile
    user_profile = {
        'age': 28,
        'weight': 75.0,
        'height': 180.0,
        'gender': 'Male',
        'goal': 'Muscle Gain',
        'activity_level': 'Active',
        'dietary_preference': 'Non-Veg',
        'allergies': ['Shellfish'],
        'food_dislikes': ['Brussels Sprouts'],
        'budget_range': 'Medium',
        'cuisine_preference': 'Mixed'
    }
    # Generate weekly plan
    weekly_plan = engine.generate_weekly_plan(user_profile)
    print(f"Weekly plan generated for {user_profile['goal']} goal")
    print(f"Consistency score: {weekly_plan['weekly_summary']['consistency_score']:.2f}")
    print(f"Total weekly calories: {weekly_plan['weekly_summary']['total_calories']:.0f}")
    # Explain the design
    explain_nutrition_engine_design()
```

## backend-python/app/pose_tracker.py
```python
# --- Import MediaPipe safely ---
    AI_AVAILABLE = True
    AI_AVAILABLE = False
class PoseTracker:
    # [Logic Hidden]
    def __init__(self):
        # [Logic Hidden]
    def process_frame(self, frame):
        # [Logic Hidden]
        # Handle case where AI is not available
            # Return original frame with error message if AI is not available
            # Return original frame with error indication
            # --- 1. BICEP CURL (Arms) ---
            # --- 2. SQUAT (Legs) ---
            # --- 3. PUSH-UP (Chest) ---
                # Calculate Elbow Angle
                # Push-up Logic (Check if body is horizontal roughly)
            # --- CHECK COMPLETION ---
        # ... (Drawing code remains the same)
        # Draw Scoreboard
    def set_exercise(self, exercise_name):
        # [Logic Hidden]
        """Switch the tracking logic based on user selection"""
        # Reset the exercise state before setting a new exercise
        # Set target reps based on exercise type (could be customized per exercise)
    def calculate_angle(self, a, b, c):
        # [Logic Hidden]
        """Calculate angle between three points"""
    def check_form_correctness(self, pose_landmarks):
        # [Logic Hidden]
        """Check if the current pose matches the expected form for the exercise"""
            # Define exercise-specific form checks
                # For bicep curl, check if shoulders are stable and not swinging
                # Check if shoulders are relatively stable (not moving excessively)
                # Check if the elbow is moving in the correct plane
                # Check if the movement is primarily in the sagittal plane (front-back)
                # For bicep curls, the wrist should stay relatively in line with the shoulder
                # For squat, check if knees track over toes and back stays straight
                # Check if knee tracks over ankle (not collapsing inward)
                # Check if hips and shoulders stay aligned
                # For pushup, check if body stays in straight line
                # Check if body is in straight line (shoulder-hip-ankle alignment)
                # For shoulder press, check if core stays engaged and movement is vertical
                # Check if torso remains relatively vertical (not leaning back excessively)
                # For lunge, check if front knee tracks over toe and back leg is stable
                # Check if knee tracks over ankle (not collapsing inward)
            # Default to True if exercise not recognized
    def process_frame(self, frame):
        # [Logic Hidden]
        # Create space for exercise GIF on the left side of the frame
        # Assuming the original frame dimensions
        # Create a new frame with extra space on the left for the GIF
        # Place the original camera frame on the right side
        # Draw a border to separate the GIF area from the camera feed
        # Add exercise name in the GIF area
        # Add instruction text in the GIF area
            # Check if pose detection was successful
                # Handle case where no pose landmarks were detected
                # Return early since there are no landmarks to process
            # Show error message on the frame
            # Determine if the form is correct based on the exercise and current stage
            # Define colors based on form correctness
                # Green for correct form
                # Red for incorrect form
            # Draw Skeleton with color based on form correctness
            # We need to draw each connection individually to control colors
                # --- GET KEY BODY POINTS ---
                # Left Side
                # --- EXERCISE LOGIC SWITCHER ---
                # Define exercise-specific thresholds
                # Only update rep counting if exercise is not completed
                    # 1. BICEP CURL (Arm Angle)
                    # 2. SQUAT (Knee Angle)
                        # Angle between Hip, Knee, Ankle
                    # 3. PUSHUP (Elbow Angle + Body Alignment)
                    # 4. SHOULDER PRESS (Shoulder-Elbow-Wrist, but vertical)
                    # 5. LUNGE (Hip-Knee-Ankle like squat, but different threshold)
                # Check if exercise is completed (after all sets)
                # Assuming target reps are set elsewhere - default to 10 for demo purposes
                    # Exercise completed - show green tick and disable interaction
                    # Keep the skeleton visible but prevent rep counting
                    # Draw a semi-transparent overlay to indicate completion
                    # Draw green tick symbol
                    # Draw a large green tick mark
                    # Add completion text
                    # Add rep count
                    # Mark as completed to prevent further interaction
                    # Still draw the skeleton but don't update rep count
                    # We'll draw the skeleton with a neutral color since the exercise is done
                    # Regular UI when exercise is ongoing
                    # Draw Blue Box for text on the camera feed side
                    # Exercise Name
                    # Counter
                    # Stage
    def handle_camera_error(self, frame, error_message):
        # [Logic Hidden]
        """Handle camera-related errors gracefully"""
            # Show error message on the frame
    def handle_pose_detection_failure(self, frame):
        # [Logic Hidden]
        """Handle pose detection failures gracefully"""
            # Show message indicating pose detection is not working
    def handle_no_pose_landmarks(self, combined_frame, gif_width):
        # [Logic Hidden]
        """Handle case where no pose landmarks are detected"""
        # Show message in the camera area that pose is not detected
    def is_exercise_finished(self):
        # [Logic Hidden]
        """Check if the exercise is completed"""
    def skip_current_exercise(self):
        # [Logic Hidden]
        """Mark the current exercise as skipped"""
    def is_exercise_skipped_flag(self):
        # [Logic Hidden]
        """Check if the current exercise was skipped"""
    def reset_exercise_state(self):
        # [Logic Hidden]
        """Reset the exercise state to allow a new exercise"""
    def start_workout_session(self, workout_plan):
        # [Logic Hidden]
        """Initialize a new workout session with the given plan"""
        # Set the first exercise
    def mark_exercise_completed(self):
        # [Logic Hidden]
        """Mark the current exercise as completed and add to completed list"""
            # Update streak when exercise is completed
            # Log the activity for analytics
    def mark_exercise_skipped(self):
        # [Logic Hidden]
        """Mark the current exercise as skipped and add to skipped list"""
            # Update streak when exercise is skipped
            # Log the activity for analytics
    def is_workout_completed(self):
        # [Logic Hidden]
        """Check if all exercises in the workout have been completed or skipped"""
    def get_current_exercise_index(self):
        # [Logic Hidden]
        """Get the index of the current exercise in the workout plan"""
        # Find the current exercise in the plan
    def get_next_exercise(self):
        # [Logic Hidden]
        """Get the next exercise in the workout plan"""
    def move_to_next_exercise(self):
        # [Logic Hidden]
        """Move to the next exercise in the workout plan"""
    def update_streak(self, workout_completed_today=True):
        # [Logic Hidden]
        """Update the workout streak based on consecutive days"""
            # Increment completed workouts count
            # Increment skipped workouts count
            # First workout
            # Calculate days since last workout
                # Consecutive day - increment streak
                # Same day - no change to streak
                # Break in streak - reset to 1
        # Update intensity based on streak
    def update_intensity_based_on_streak(self):
        # [Logic Hidden]
        """Gradually increase intensity based on streak"""
        # Store previous values to determine if there was a change
        # Increase intensity gradually based on streak
        # Every 3 days of streak, slightly increase intensity
        # Adjust reps and sets based on intensity
        # Cap the increases to ensure safety
        # Generate explanation for intensity change
    def get_intensity_explanation(self):
        # [Logic Hidden]
        """Get explanation for current intensity level"""
    def get_adjusted_workout_params(self):
        # [Logic Hidden]
        """Get the adjusted workout parameters based on streak"""
    def adjust_meal_macros_for_intensity(self, base_macros):
        # [Logic Hidden]
        """Adjust meal plan macros based on workout intensity"""
        # Increase calories and protein based on intensity
        # Increase calories proportionally to intensity
        # Increase protein for muscle recovery based on intensity
        # Slightly adjust carbs and fats based on workout intensity
    def adjust_meal_plan_by_experience_level(self, base_macros):
        # [Logic Hidden]
        """Adjust meal plan based on experience level"""
            # Beginner: Recovery focused - moderate calories, balanced nutrients
            # Add more recovery-focused nutrients
            # Intermediate: Higher protein for muscle building and repair
            # Add more protein-focused nutrients
            # Advanced: Performance focused - higher calories, optimized macros
            # Add performance-focused nutrients
            # Default to base macros if level is unknown
    def get_meal_plan_recommendations(self):
        # [Logic Hidden]
        """Get specific meal plan recommendations based on experience level"""
    def load_exercise_dataset(self):
        # [Logic Hidden]
        """Load the exercise dataset from the data files"""
        # fixed path: backend-python/data (not app/data)
        # Load exercise data
    def validate_exercise_dataset(self):
        # [Logic Hidden]
        """Validate the exercise dataset against current workout execution logic"""
        # Required columns for workout execution logic
        # Additional columns for sets, reps, and difficulty
            # Check required columns exist
            # Check if exercise has the required body keypoints for posture detection
            # This is implicit in MediaPipe - we assume all exercises can use the standard landmarks
            # but we should check if Target_Muscle is properly defined
            # Check if equipment is properly defined
            # Check if difficulty is properly defined
            # Check if exercise has metadata for sets and reps
            # Determine if exercise is valid
        # Prepare validation report
    def evaluate_dataset_sufficiency(self):
        # [Logic Hidden]
        """Evaluate whether the current dataset is sufficient for all supported goals, levels, and exercises"""
        # Load exercise data
        # Load nutrition data
        # Define supported goals
        # Define experience levels
        # Define equipment categories
        # Define target muscle groups
        # Define difficulty levels
        # Evaluate exercise dataset sufficiency
            # Count exercises by goal (based on equipment and muscle groups)
                # For now, we'll count exercises that could support each goal
                # This is a simplified approach - in reality, you'd need more complex logic
            # Count exercises by experience level
                # Get unique difficulties
            # Count exercises by equipment
                # Get unique equipment
            # Count exercises by target muscle
                # Get unique muscles
            # Count exercises by difficulty
        # Evaluate nutrition dataset sufficiency
            # Count meals by dietary preference
            # Count meals by type
            # Get allergen coverage
            # Get calorie ranges
        # Identify gaps in exercise variety
            # Check if all muscle groups are covered
            # Check if all equipment categories are covered
            # Check if all difficulty levels are covered
        # Identify gaps in meal data
            # Check if all dietary preferences are covered
            # Check if all meal types are covered
        # Overall sufficiency assessment
        # Generate recommendations based on gaps
        # Combine all evaluations
    def get_analytics_data(self):
        # [Logic Hidden]
        """Get analytics data for charts based on user activity"""
        # Calculate various metrics for analytics
        # Count meal logs from activity log
        # Prepare analytics data
    def get_last_meal_log(self):
        # [Logic Hidden]
        """Get the most recent meal log from activity log"""
    def calculate_trends(self):
        # [Logic Hidden]
        """Calculate daily, weekly, and overall trends from activity data"""
        # Initialize trend data
        # Get activity log
        # Convert timestamps to datetime objects
                    # If parsing fails, skip this entry
        # Sort by timestamp
        # Calculate daily trends (last 7 days)
            # Only consider last 7 days for daily trends
                # Count workouts
                # Count meals
        # Fill in missing days with 0
        # Calculate weekly trends (last 4 weeks)
            # Calculate week number for i weeks ago
            # Count activities for this week
        # Calculate overall trends
        # Calculate consistency metrics
        # Calculate trend analysis
        # Analyze daily workout trend
        # Analyze weekly workout trend
    def update_activity_log(self, activity_type, details=None):
        # [Logic Hidden]
        """Log user activity for analytics tracking"""
        # Store in a temporary log (in a real app, this would go to a database)
        # Keep only recent activities (last 30 entries)
    def log_meal_completion(self, meal_info, calories_consumed=None):
        # [Logic Hidden]
        """Log meal completion for analytics tracking"""
        # Store in activity log
        # Keep only recent activities (last 30 entries)
    def calculate_skip_rate(self):
        # [Logic Hidden]
        """Calculate the skip rate for the user"""
    def calculate_average_form_accuracy(self):
        # [Logic Hidden]
        """Calculate the average form accuracy based on stored scores"""
    def add_form_accuracy_score(self, score):
        # [Logic Hidden]
        """Add a form accuracy score to the tracking list"""
        # Limit to last 20 scores to keep it recent
    def evaluate_upgrade_readiness(self):
        # [Logic Hidden]
        """Evaluate if user is ready to upgrade from Beginner to Intermediate or Intermediate to Advanced"""
        # Calculate various metrics
        # Define thresholds based on current level
            # Beginner to Intermediate thresholds
            # Intermediate to Advanced thresholds (stricter requirements)
            # Already at highest level or unknown level
        # Calculate readiness score (0-100)
        # Streak contribution (0-40 points)
        # Skip rate contribution (0-30 points)
        # Form accuracy contribution (0-30 points)
        # Store the score and check if upgrade is suggested
        # Check if user meets all criteria for upgrade suggestion
        # Generate explanation for upgrade readiness
            # Explain what's needed to reach the next level
    def suggest_upgrade(self):
        # [Logic Hidden]
        """Return upgrade suggestion if user is ready"""
            # Customize message based on current level
    def draw_styled_landmarks(self, image, pose_landmarks, landmark_color, connection_color):
        # [Logic Hidden]
        """Draw landmarks and connections with custom colors based on form correctness"""
        # Draw connections
            # Get coordinates
            # Convert to pixel coordinates
            # Draw line with specified connection color
        # Draw landmarks
            # Convert to pixel coordinates
            # Draw landmark point with specified landmark color
```

## backend-python/app/profile_change_detection.py
```python
"""
Deterministic Profile Change Detection Engine
This module detects changes in user profiles that trigger workout/nutrition plan regeneration.
Features include threshold logic, cache invalidation, async job processing, and failure handling.
"""
# Configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# Initialize Redis client
# Initialize Celery
class ChangeType(Enum):
    # [Logic Hidden]
    """Types of profile changes that trigger regeneration"""
    GOAL_CHANGED = "goal_changed"
    EXPERIENCE_CHANGED = "experience_changed"
    EQUIPMENT_CHANGED = "equipment_changed"
    INJURY_ADDED = "injury_added"
    INJURY_REMOVED = "injury_removed"
    DAYS_PER_WEEK_CHANGED = "days_per_week_changed"
    WEIGHT_CHANGED = "weight_changed"
    HEIGHT_CHANGED = "height_changed"
    AGE_CHANGED = "age_changed"
@dataclass
class ProfileChange:
    # [Logic Hidden]
    """Represents a detected profile change"""
class ProfileChangeDetector:
    # [Logic Hidden]
    """
    Detects changes in user profiles that require plan regeneration
    """
    def __init__(self):
        # [Logic Hidden]
    def _setup_logging(self) -> logging.Logger:
        # [Logic Hidden]
        """Setup logging for the detector"""
    def _generate_profile_hash(self, profile: Dict) -> str:
        # [Logic Hidden]
        """Generate a hash of the profile for comparison"""
        # Only include fields that matter for regeneration
        # Convert to JSON string and hash
    def _get_cached_profile_hash(self, user_id: str) -> Optional[str]:
        # [Logic Hidden]
        """Retrieve cached profile hash from Redis"""
    def _set_cached_profile_hash(self, user_id: str, profile_hash: str):
        # [Logic Hidden]
        """Store profile hash in Redis"""
        # Cache for 30 days
    def _invalidate_plan_cache(self, user_id: str):
        # [Logic Hidden]
        """Invalidate cached plans for the user"""
    def _get_previous_profile(self, user_id: str) -> Optional[Dict]:
        # [Logic Hidden]
        """Retrieve previous profile from Redis"""
    def _store_current_profile(self, user_id: str, profile: Dict):
        # [Logic Hidden]
        """Store current profile in Redis"""
        # Store for 30 days
    def detect_changes(self, user_id: str, current_profile: Dict) -> List[ProfileChange]:
        # [Logic Hidden]
        """
        Detect changes in user profile that require regeneration
        """
        # Validate the incoming profile data
        # Get previous profile hash
        # If hashes are different, there are changes
            # Get previous profile to determine what changed
                # Compare each field that matters for regeneration
            # Update cached hash and profile
    def _compare_profile_fields(self, user_id: str, old_profile: Dict, new_profile: Dict) -> List[ProfileChange]:
        # [Logic Hidden]
        """Compare profile fields and detect changes"""
        # Compare goal
        # Compare experience
        # Compare equipment
        # Compare injuries
        # Compare days per week
        # Compare weight (with threshold)
        # Compare height
        # Compare age
    def _validate_profile_data(self, profile: Dict) -> Dict:
        # [Logic Hidden]
        """Validate and sanitize profile data"""
        # Validate age range (18-80)
        # Validate weight range (40-200 kg)
        # Validate height range (120-250 cm)
        # Validate days per week (1-7)
        # Validate experience level
        # Validate goal
        # Validate equipment list
        # Validate body issues list
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def trigger_regeneration_task(self, user_id: str, changes: List[Dict]):
    # [Logic Hidden]
    """
    Celery task to trigger plan regeneration
    """
        # Invalidate cache
        # Here you would call the actual regeneration logic
        # For example: regenerate_workout_plan(user_id) or regenerate_nutrition_plan(user_id)
        # This is a placeholder for the actual regeneration logic
        # Update change records to mark as triggered
            # In a real implementation, you would update the database record
            # update_change_record(change)
        # Retry the task
class ProfileChangeManager:
    # [Logic Hidden]
    """
    Manages the profile change detection and regeneration workflow
    """
    def __init__(self):
        # [Logic Hidden]
    def process_profile_update(self, user_id: str, profile: Dict) -> Dict:
        # [Logic Hidden]
        """
        Process a profile update and trigger regeneration if needed
        """
            # Detect changes
            # Convert changes to serializable format
            # Check if regeneration is already in progress
            # Trigger regeneration task
            # Track the job
            # Clean up old job records (keep only recent ones)
    def _cleanup_old_jobs(self):
        # [Logic Hidden]
        """Clean up old job records to prevent memory leaks"""
            # Remove jobs older than 1 hour
    def get_job_status(self, user_id: str) -> Dict:
        # [Logic Hidden]
        """Get the status of a regeneration job for a user"""
# Database Schema Changes
DATABASE_SCHEMA_CHANGES = """
"""
def setup_database():
    """Setup database tables for profile change tracking"""
    # Execute schema changes
def example_usage():
    # [Logic Hidden]
    """
    Example usage of the profile change detection engine
    """
    # Initialize the manager
    # Example user profile
    # Initial profile
    # Process initial profile (should not trigger regeneration)
    # Update profile with significant changes
    # Process updated profile (should trigger regeneration)
        # Show detected changes
    # Try to update again with same profile (should not trigger regeneration)
    # Check job status
    # Setup database
    # Run example
```

## backend-python/app/progression_engine.py
```python
"""
Deterministic Progressive Overload Engine
==========================================
Computes workout progression using:
  progression_delta = base_rate * adherence * recovery * experience_mod
All outputs are clamped by age-based safety caps.
Streak milestones trigger volume or difficulty upgrades.
"""
# ── CONSTANTS ──
BASE_PROGRESSION_RATES = {
EXPERIENCE_MODIFIERS = {
STREAK_VOLUME_THRESHOLD    = 10
STREAK_DIFFICULTY_THRESHOLD = 30
MAX_SETS_ABSOLUTE      = 6
MAX_REPS_ABSOLUTE      = 20
MAX_INTENSITY_ABSOLUTE = 1.0
MIN_SETS               = 2
MIN_REPS               = 3
MIN_INTENSITY          = 0.30
AGE_CAPS = {
class ProgressionMethod(str, Enum):
    # [Logic Hidden]
    VOLUME_INCREASE    = "volume_increase"
    REP_INCREASE       = "rep_increase"
    EXERCISE_UPGRADE   = "exercise_upgrade"
    INTENSITY_INCREASE = "intensity_increase"
    MAINTAIN           = "maintain"
# ── CORE CALCULATIONS ──
def calculate_adherence_score(
    completion_pct: float,
    streak_days: int,
    days_per_week: int = 4,
) -> float:
    # [Logic Hidden]
    """
    adherence = 0.60 * completion_pct + 0.40 * streak_factor
    streak_factor = min(streak_days / (2 * days_per_week), 1.0)
    """
def calculate_recovery_factor(
    sleep_score: float,
    hydration_score: float,
    stress_level: float,
    fatigue_level: float = 5.0,
) -> float:
    # [Logic Hidden]
    """
    recovery = avg(sleep/10, hydration/10, (10-stress)/10, (10-fatigue)/10)
    """
def calculate_progression_delta(
    experience: str,
    adherence: float,
    recovery: float,
) -> float:
    # [Logic Hidden]
    """
    delta = base_rate * adherence * recovery * experience_mod
    Clamped to [0.0, 0.10].
    """
# ── SAFETY OVERRIDES ──
def apply_age_safety_caps(
    age: int,
    sets: int,
    reps_low: int,
    reps_high: int,
    intensity: float,
) -> Tuple[int, int, int, float]:
    # [Logic Hidden]
    """
    Age >= 65 -> max intensity 0.70, max 3 sets, reps 8-15
    Age <  18 -> max intensity 0.80, max 4 sets, reps 10-20
    """
# ── STREAK ADJUSTMENTS ──
def get_streak_adjustments(
    streak_days: int,
    consistency: float,
    current_sets: int,
    experience: str,
) -> Dict:
    # [Logic Hidden]
# ── PROGRESSION METHOD SELECTOR ──
def select_progression_method(
    delta: float,
    streak_days: int,
    current_sets: int,
    current_reps_high: int,
    experience: str,
    recovery: float,
) -> ProgressionMethod:
    # [Logic Hidden]
# ── MAIN ENGINE ──
class ProgressionEngine:
    # [Logic Hidden]
    """Stateless, deterministic progression engine."""
    def compute_progression(
        self,
        user_profile: Dict,
        current_params: Dict,
        workout_stats: Optional[Dict] = None,
    ) -> Dict:
        # [Logic Hidden]
# ── SINGLETON ──
def get_progression_engine() -> ProgressionEngine:
    # [Logic Hidden]
```

## backend-python/app/train_meal_model.py
```python
def train_meal_model():
    # [Logic Hidden]
    """Train XGBoost model for meal recommendations"""
    # Create models directory if not exists
    # Load nutrition data
    # Create synthetic training data for meal recommendations
    # Create features
    # Simulate user profiles
    # Generate training data
        # User target macros
        # Meal macros (from actual data)
        # Intensity and goal
        # Dietary preference match
        # Calculate label (1 = good recommendation, 0 = bad)
        # Good if macros are within 80-120% of target
    # Encode categorical variables
    # Prepare features
    X = train_df[feature_columns]
    # Split data
    # Train XGBoost model
    # Evaluate
    # Save model
    # Save encoders
```

## backend-python/app/train_model.py
```python
# PERFORMANCE SAFETY: Memory-efficient training script for scalable model generation
# SCALABILITY: Designed to handle configurable dataset sizes without memory overflow
# OPTIMIZATION: Uses efficient pandas operations and XGBoost for fast training
# SECURITY NOTE: This training script generates synthetic data for model training
# The actual user data should never be stored or processed in plain text
# All real user data must be handled through secure API endpoints with proper authentication
# Ensure models directory exists
# ==========================================
# 1. GENERATE TRAINING DATA (Simulated)
# ==========================================
# We simulate users to teach the model patterns
# e.g., High BMI + Beginner = Low Intensity
# e.g., Low Age + Muscle Gain = High Intensity
# SCALABILITY CONSIDERATION: Dataset size can be adjusted based on available memory
# For production: Consider increasing data_size for better model generalization
# MEMORY EFFICIENCY: Using numpy arrays for efficient memory usage
# PRIVACY NOTICE: This script uses synthetic/fake data for training only
# No real user data is collected, stored, or processed in this script
# All data is randomly generated and does not represent real individuals
# PERFORMANCE: Efficient data generation using vectorized numpy operations
# SCALABILITY: Vectorized function for efficient label calculation
def determine_intensity_vectorized(df):
    # [Logic Hidden]
    """Vectorized function to calculate intensity levels efficiently"""
    # Calculate BMI for all rows at once
    # Initialize score array
    # Apply age factors efficiently
    # Apply BMI factors efficiently
    # Apply goal factors efficiently
    # Classify based on scores efficiently
# PERFORMANCE: Use vectorized function instead of apply for efficiency
# ==========================================
# 2. PREPROCESS DATA
# ==========================================
# Convert text to numbers (XGBoost only understands numbers)
# PERFORMANCE: Efficient preprocessing using vectorized operations
# SCALABILITY: Encoding happens in-memory without intermediate file storage
# MEMORY EFFICIENCY: Using pandas indexing for efficient column access
# SECURITY NOTE: Data encoding happens locally in memory and is not persisted
# The encoders will be saved securely for use in the prediction pipeline
# PERFORMANCE: Efficient label encoding using pandas vectorized operations
X = df[['age', 'weight', 'height', 'gender_n', 'goal_n']]
# ==========================================
# 3. TRAIN XGBOOST MODEL
# ==========================================
# PERFORMANCE: XGBoost is optimized for speed and memory efficiency
# SCALABILITY: XGBoost handles large datasets efficiently with built-in parallelization
# MEMORY EFFICIENCY: XGBoost uses optimized data structures to minimize memory usage
# SECURITY NOTE: Model training happens in isolated environment
# No sensitive data is transmitted over networks during training
# Model parameters are configured to prevent overfitting to specific user data
# SCALABILITY: XGBoost parameters optimized for performance and generalization
# n_estimators: Number of boosting rounds (balance between performance and speed)
# max_depth: Limits tree depth to prevent overfitting and control memory usage
# learning_rate: Controls step size to ensure stable convergence
# PERFORMANCE: Efficient train-test split with reproducible results
# PERFORMANCE: Calculate accuracy on test set to validate model quality
# ==========================================
# 4. SAVE ARTIFACTS
# ==========================================
# We need to save the model AND the encoders to use them in the real app
# PERFORMANCE: Efficient serialization using joblib for fast loading in production
# SCALABILITY: Model files are compact and can be loaded quickly for predictions
# MEMORY EFFICIENCY: joblib provides efficient compression for model serialization
# SECURITY NOTICE: Model files are saved to local filesystem with restricted access
# These files should be protected with appropriate file system permissions
# The model does not contain personally identifiable information (PII)
# since it was trained on synthetic data
# PERFORMANCE: Use joblib for efficient model serialization
# joblib is optimized for scikit-learn and XGBoost models, providing faster load/save
```

## backend-python/app/workout_engine.py
```python
# -*- coding: utf-8 -*-
# Import progression engine
class WorkoutEngine:
    # [Logic Hidden]
    def __init__(self):
        # [Logic Hidden]
        # Initialize feature pipeline
        # Media URL reliability cache (avoid repeated dead-link checks)
        # Initialize multi-output XGBoost model
        # Initialize progression engine
        # Get base directory
        # Load exercises from CSV or create fallback
                # Standardize column names to TitleCase format to match expected format
                # Standardize column names to TitleCase format to match expected format
                # Fallback exercises
                # Standardize column names for fallback DataFrame too
            # Fill missing values
        # Load ML models
        # Initialize hybrid optimizer (rule-based + ML hooks + user adaptation)
        # Load external workout media index (best-effort; app still works without it)
    def _normalize_exercise_name(self, name: str) -> str:
        # [Logic Hidden]
    def _extract_wger_name(self, exercise: Dict) -> str:
        # [Logic Hidden]
    def _extract_wger_media_url(self, exercise: Dict) -> str:
        # [Logic Hidden]
    def _initialize_wger_media_index(self):
        # [Logic Hidden]
        """Build a local name -> media URL map from WGER API for robust fallback media."""
    def _get_wger_media_for_name(self, exercise_name: str) -> str:
        # [Logic Hidden]
        # Conservative fuzzy fallback: require strong overlap to avoid wrong media.
    def _get_row_value(self, row, candidates: List[str], default=''):
        # [Logic Hidden]
        """Return first matching value from row by trying multiple key styles."""
    def _validate_media_url(self, url: str) -> bool:
        # [Logic Hidden]
        """Validate image/video URL with TTL cache to reduce broken frontend guide media."""
    def _resolve_exercise_media(self, row) -> Dict[str, str]:
        # [Logic Hidden]
        """Pick a working media URL from supported columns and normalize payload fields."""
            # Exact WGER match can be trusted.
            # Dataset URLs are preferred over fuzzy WGER matches.
            # Fuzzy WGER is last to avoid unrelated media.
        # If strict validation fails (provider outage/rate-limit), keep first URL as best-effort.
    def _load_ml_models(self):
        # [Logic Hidden]
        """Load pre-trained ML models (optional)"""
            # Load multiple models for different aspects
    def filter_by_equipment(self, exercises: pd.DataFrame, available_equipment: List[str]) -> pd.DataFrame:
        # [Logic Hidden]
        """Filter exercises by available equipment - RULE-BASED SAFETY LOGIC"""
            # Add variations
            # Always include bodyweight
    def filter_by_injuries(self, exercises: pd.DataFrame, body_issues: List[str]) -> pd.DataFrame:
        # [Logic Hidden]
        """Filter exercises to avoid injuries - RULE-BASED SAFETY LOGIC"""
    def _build_feature_vector(self, profile: dict) -> np.ndarray:
        # [Logic Hidden]
        """Build a comprehensive feature vector using the feature pipeline"""
        # Use the feature pipeline to process the user profile
        # Process through the feature pipeline
    def _get_intensity_adjustment(self, profile: dict) -> float:
        # [Logic Hidden]
        """Get intensity adjustment based on ML model or rules - HYBRID APPROACH"""
        # Try to use multi-output model if available
            # Reshape feature vector for prediction
            # Create a dummy DataFrame with the right column names
            # This would need to match the expected input format of the model
            # Use multi-output model to get all predictions at once
            # Extract intensity from the predictions (assuming it's the 5th element: [sets, reps_low, reps_high, rest_time, intensity])
            # Fall back to original logic
    def _get_optimized_workout_split(self, profile: dict, days_per_week: int) -> List[str]:
        # [Logic Hidden]
        """Get workout split optimized by ML model with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_training_volume(self, profile: dict) -> tuple:
        # [Logic Hidden]
        """Get optimized training volume (sets, reps, rest) using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_sets(self, profile: dict) -> int:
        # [Logic Hidden]
        """Get optimized number of sets using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_reps(self, profile: dict, intensity: float) -> str:
        # [Logic Hidden]
        """Get optimized rep range using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_rest_time(self, profile: dict) -> int:
        # [Logic Hidden]
        """Get optimized rest time using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_frequency(self, profile: dict) -> int:
        # [Logic Hidden]
        """Get optimized training frequency using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_progression(self, profile: dict) -> Dict:
        # [Logic Hidden]
        """Get optimized progression timing using ML with rule-based validation - HYBRID APPROACH"""
    def _generate_dynamic_split(self, days_per_week: int, goal: str) -> List[str]:
        # [Logic Hidden]
        """Generate workout split based on days and goal - RULE-BASED LOGIC"""
    def _calculate_rest_days(self, days_per_week: int, profile: dict = None, intensity: float = None) -> List[int]:
        # [Logic Hidden]
        """Calculate optimal rest days in the week using intensity-aware logic"""
    def _create_optimal_schedule(self, weekly_plan: List[Dict], rest_days: List[int]) -> List[Dict]:
        # [Logic Hidden]
        """Create week schedule with rest days - HYBRID APPROACH"""
    def _calculate_exercise_count(self, experience: str, goal: str) -> int:
        # [Logic Hidden]
        """Calculate number of exercises per workout - RULE-BASED LOGIC"""
    def _calculate_sets(self, experience: str, goal: str) -> int:
        # [Logic Hidden]
        """Calculate number of sets - RULE-BASED LOGIC"""
    def _calculate_reps(self, goal: str, intensity: float) -> str:
        # [Logic Hidden]
        """Calculate rep range based on goal - RULE-BASED LOGIC"""
    def _calculate_rest_time(self, goal: str, experience: str) -> int:
        # [Logic Hidden]
        """Calculate rest time between sets - RULE-BASED LOGIC"""
    def _adjust_reps_for_intensity(self, base_reps: str, intensity: float) -> str:
        # [Logic Hidden]
        """Adjust reps based on intensity - RULE-BASED LOGIC"""
    def _estimate_reps_avg(self, reps_range: str) -> float:
        # [Logic Hidden]
        """Estimate avg reps from a range string like '8-12'"""
    def _apply_age_based_caps(self, profile: dict, sets: int, reps: str, rest_time: int, intensity: float) -> tuple:
        # [Logic Hidden]
        """Apply age-based safety caps to workout parameters - RULE-BASED SAFETY LOGIC"""
        # Log initial values before applying rules
        # Apply age-appropriate limits
            # For older adults, reduce intensity and volume
            # Adjust reps to safer range for older adults
                # Handle cases where reps is not in x-y format
            # Log changes applied by rules
            # For younger individuals, focus on form over heavy loads
            # Higher rep ranges for skill development
                # Handle cases where reps is not in x-y format
            # Log changes applied by rules
    def _filter_biomechanics(self, exercises: pd.DataFrame, profile: dict) -> pd.DataFrame:
        # [Logic Hidden]
        """Filter exercises based on biomechanical safety - RULE-BASED SAFETY LOGIC"""
            # For beginners, filter out complex movements
                # Avoid overly complex exercises for beginners
            # Use Check_Type column if available (e.g., filter out cardio for strength-focused plans)
                # For strength-focused goals, prioritize strength exercises
                    # For endurance-focused goals, include more cardio exercises
            # Use Risk_Level column if available (assuming lower risk is better for beginners)
                    # Filter out high-risk exercises for beginners
                    # For seniors, only allow low-risk exercises
                # If Risk_Level column doesn't exist, create a basic risk assessment based on other factors
            # Additional biomechanical filters based on age
                # Avoid high-impact exercises for seniors
            # Log the results of biomechanical filtering
    def _infer_rest_days_count(self, profile: dict, intensity: float, sets: int, reps: str, num_exercises: int) -> int:
        # [Logic Hidden]
        """Decide rest days based on weekly load + profile (MODEL-DRIVEN LOGIC)"""
    def generate_weekly_plan(self, profile: dict, workout_history: List[Dict] = None) -> List[Dict]:
        # [Logic Hidden]
        """
        Generate weekly workout plan - deterministic with optional Gemini guidance.
        """
        # --- Base Variables ---
        # --- Inject Gemini AI Intelligence Config ---
            # Generate the optimal plan parameters from the AI
            # Store in profile to be consumed by _get_exercise_params
            # --- Fallback: Cap workout days by experience ---
            # Streak-based adjustment: 10+ streak with high consistency -> allow +1 day
        # --- Step 2: Get workout split based on experience ---
        # --- Step 3: Distribute rest days intelligently ---
        # --- Step 4: Build the 7-day schedule ---
    def _get_split_for_experience(self, experience: str, workout_days: int, goal: str) -> List[str]:
        # [Logic Hidden]
        """
        Return the workout focus list for the given experience and day count.
        Deterministic: same inputs always produce same split.
        Beginner -> Varied Full Body emphasis (not identical every day)
        Intermediate -> Upper/Lower alternating
        Advanced -> Push/Pull/Legs cycle
        """
            # Bug #1a Fix: Rotate muscle emphasis so each session has a different focus.
            # This prevents identical workouts every day while keeping Full Body coverage.
            # Fallback: cycle through the 4-day rotation
            # Upper/Lower split - alternating, ensures 48h per group
                # Strength focus: heavier compound days
    def _distribute_rest_days(self, workout_days: int, split: List[str]) -> List[int]:
        # [Logic Hidden]
        """
        Distribute rest days in a 7-day week to maximize recovery.
        Rules:
        - Never place rest days at the very start if possible
        - Space rest days as evenly as possible
        - For PPL: rest after every 3rd day
        - For Upper/Lower: rest after every 2nd day
        - For Full Body: rest between every workout day
        """
            # Many rest days - alternate workout/rest, fill remaining at end
            # e.g., 3 workout days -> W R W R W R R
            # fill any remaining from the end
            # Single rest day - place at position 3 (Wednesday) for mid-week recovery
            # Two rest days - space them out
            # Day 2 (Wednesday) and Day 5 (Saturday) for even distribution
            # Three rest days
            # Distribute: after every 2 workout days
        # Fallback: evenly spaced
    def _build_weekly_plan(self, profile: dict, split: List[str], rest_positions: List[int]) -> List[Dict]:
        # [Logic Hidden]
        """Build the full 7-day plan with exercises for workout days and rest for rest days."""
                # Calculate day intensity score (0-1)
    def _get_warmup_for_focus(self, focus: str) -> List[Dict]:
        # [Logic Hidden]
        """Return a deterministic warm-up block tailored to workout focus."""
        # Bug #1e Fix: 'Brisk Walk / Light Cardio' is non-trackable (time-based, no reps).
        # Mark it trackable=False so the frontend uses a timer instead of a rep counter.
            # Ensure 'trackable' key exists on every warmup entry
    def _get_exercises_for_day(self, focus: str, goal: str, experience: str,
                                equipment: List[str], body_issues: List[str],
                                profile: dict) -> List[Dict]:
        # [Logic Hidden]
        """
        Select exercises deterministically for a given focus day.
        Rules:
        - Filter by equipment compatibility
        - Exclude injury-conflicting exercises
        - Prefer compound movements first (multi-joint)
        - Sort alphabetically for determinism
        - Cap count by experience (Beginner 5-7, Intermediate 6-8, Advanced 7-10)
        - Apply goal-based sets/reps/rest
        - Apply age-based safety caps
        """
        # --- Muscle group mapping ---
        # Bug #1a Fix: Map beginner sub-focus variants to standard muscle groups
        # so the existing muscle_map lookup still works correctly.
        # Compound exercise indicators (multi-joint movements)
        # --- Exercise count by experience ---
        # For Full Body days, use the higher end; for isolation days, use the lower end
        # --- Get exercise parameters based on goal + experience ---
        # --- Filter exercise pool ---
        # Equipment filter
            # Bug #1b Fix: Add comprehensive equipment synonyms to bridge frontend labels
            # (plural/alternate forms) to the dataset's stored singular/specific names.
            # 'gym' is a catch-all — allow all gym equipment
            # Always include bodyweight exercises
        # Injury filter
        # Biomechanical safety filter
        # --- Select exercises per target muscle, compound first ---
            # Get candidates for this muscle
            # Mark compound vs isolation
            # Sort: compound first, then alphabetically for determinism
            # Pick exercises for this muscle (avoid duplicates)
        # If we don't have enough, fill from remaining pool
        # Cap at target_count
        # Sort final list: compound movements first, then isolation
        # Apply age-based safety caps
                # Safely parse rest time
        # Clean internal fields
        # Fallback if still empty
    def _get_exercise_params(self, goal: str, experience: str, profile: dict) -> Dict:
        # [Logic Hidden]
        """
        Return deterministic sets/reps/rest based on goal and experience.
        When ProgressionEngine is available AND the user has history,
        use computed progression; otherwise fall back to static tables.
        """
        # Check Gemini extracted config first
        # Try progression engine first
                # Static baseline
        # Fallback: static tables
        # Bug #1f Fix: Gender-based intensity adjustment.
        # Females tend to have less absolute upper-body strength; add reps for upper body,
        # slightly reduce sets to keep total volume safe. Also bias lower body / glutes.
            # Parse existing reps range and bump up by 2
            # Reduce sets by 1 for upper body exercises (handled at call site via profile)
    def _calculate_day_intensity(self, exercises: List[Dict], experience: str, goal: str) -> float:
        # [Logic Hidden]
        """Calculate a 0-1 intensity score for a workout day."""
        # Base intensity from experience
        # Adjust by exercise count (more exercises = higher intensity)
        # Adjust by goal
    def _get_fallback_exercises(self, params: Dict) -> List[Dict]:
        # [Logic Hidden]
        """Return safe fallback exercises when database filtering yields nothing."""
# ==========================================
# FACTORY FUNCTION
# ==========================================
def get_workout_engine():
    # [Logic Hidden]
    """Get or create the singleton WorkoutEngine instance"""
```

## backend-python/app/__init__.py
```python
"""
Elevate Fitness - Backend Python Package
"""
```

## backend-python/app/models/user.py
```python
class GenderEnum(str, Enum):
    # [Logic Hidden]
class GoalEnum(str, Enum):
    # [Logic Hidden]
class ActivityLevelEnum(str, Enum):
    # [Logic Hidden]
class ExperienceLevelEnum(str, Enum):
    # [Logic Hidden]
class DietaryPreferenceEnum(str, Enum):
    # [Logic Hidden]
class UserBase(BaseModel):
    # [Logic Hidden]
class UserCreate(UserBase):
    # [Logic Hidden]
class UserUpdate(BaseModel):
    # [Logic Hidden]
class UserInDB(UserBase):
    # [Logic Hidden]
class WorkoutHistory(BaseModel):
    # [Logic Hidden]
class MealHistory(BaseModel):
    # [Logic Hidden]
class WorkoutCompletion(BaseModel):
    # [Logic Hidden]
class MealCompletion(BaseModel):
    # [Logic Hidden]
class MealItemTick(BaseModel):
    # [Logic Hidden]
class MealHistoryEntry(BaseModel):
    # [Logic Hidden]
```

## backend-python/app/routes/food_database.py
```python
"""
Food Database API Endpoint
Serves real food data from nutrition.csv
"""
# Load food database
FOOD_DATABASE = None
def load_food_database():
    # [Logic Hidden]
    """Load food database from CSV"""
        # Categorize by meal type
        FOOD_DATABASE = {
            # Map meal types
            # Determine if vegetarian
            # Get swap group
            # Get goal
            # Get allergens
def categorize_food(name: str) -> str:
    # [Logic Hidden]
    """Categorize food based on name"""
@router.get("/food-database")
async def get_food_database():
    # [Logic Hidden]
    """
    Get the complete food database categorized by meal type
    Returns:
    {
        "success": true,
        "data": {
            "breakfast": [...],
            "lunch": [...],
            "dinner": [...],
            "snack": [...]
        }
    }
    """
```

## backend-python/app/routes/meal_tracking.py
```python
def _meal_progress_col():
    # [Logic Hidden]
def _meal_history_col():
    # [Logic Hidden]
class InitDayRequest(BaseModel):
    # [Logic Hidden]
class TickItemRequest(BaseModel):
    # [Logic Hidden]
@router.post("/init-day")
async def init_day_meals(req: InitDayRequest):
    # [Logic Hidden]
    """Initialize a day's meal plan with tickable items"""
@router.post("/tick-item")
async def tick_item(req: TickItemRequest):
    # [Logic Hidden]
    """Tick/untick a meal item. Cannot modify if meal is locked."""
@router.get("/day-progress")
async def get_day_progress(user_id: str, date: str):
    # [Logic Hidden]
@router.get("/history")
async def get_meal_history(user_id: str):
    # [Logic Hidden]
@router.get("/history/{date}")
async def get_meal_history_by_date(user_id: str, date: str):
    # [Logic Hidden]
async def _save_to_history(user_id: str, date: str, meal_type: str, meal: dict):
    # [Logic Hidden]
    # Recalculate total
```

## backend-python/app/routes/profile.py
```python
# Pydantic models
class ProfileUpdateRequest(BaseModel):
    # [Logic Hidden]
    """Profile update request with validation"""
def get_current_user_from_token(x_auth_token: str = Header(..., alias="x-auth-token", description="JWT token")):
    # [Logic Hidden]
    """
    Extract and validate user from JWT token.
    """
        # Node backend signs token as: { user: { id: "..." } }
@router.put("/update")
async def update_profile(
    profile_update: ProfileUpdateRequest,
    x_auth_token: str = Header(..., alias="x-auth-token", description="JWT token"),
    current_user: dict = Depends(get_current_user_from_token)
):
    # [Logic Hidden]
    """
    Update user profile in MongoDB with activity logging
    Requirements:
    - Valid JWT token required
    - Atomic update_one operation
    - Activity logging
    - Write confirmation
    """
        # Get database collections
        # Filter only provided fields (exclude None values)
        # Build MongoDB update query
        # Execute atomic update with safe wrapper
        # Log activity (non-blocking)
            # Don't fail the request
        # Get updated user document
            # Remove sensitive data
@router.get("/me")
async def get_current_user_profile(
    x_auth_token: str = Header(..., alias="x-auth-token", description="JWT token"),
    current_user: dict = Depends(get_current_user_from_token)
):
    # [Logic Hidden]
    """Get current user profile"""
        # Remove sensitive data
```

## backend-python/app/routes/__init__.py
```python
# Routes package
```

## backend-python/app/utils/activity_logger.py
```python
class ActivityType:
    # [Logic Hidden]
    """Activity type constants for consistent logging"""
    PROFILE_UPDATE = "profile_update"
    WORKOUT_COMPLETE = "workout_complete"
    MEAL_COMPLETE = "meal_complete"
    PLAN_REGENERATION = "plan_regeneration"
    GOAL_CHANGE = "goal_change"
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
async def log_user_activity(
    user_id: str,
    activity_type: str,
    metadata: Dict[str, Any],
    source: str = "api",
    version: str = "1.0",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    # [Logic Hidden]
    """
    Log user activity to MongoDB user_activity collection
    Args:
        user_id: User's MongoDB ObjectId (as string)
        activity_type: Type of activity (use ActivityType constants)
        metadata: Activity-specific data
        source: Request source (api/mobile/web)
        version: API version
        ip_address: Client IP (optional)
        user_agent: Client user agent (optional)
    Example:
        await log_user_activity(
            user_id="507f1f77bcf86cd799439011",
            activity_type=ActivityType.PROFILE_UPDATE,
            metadata={"fields_updated": ["goal", "weight"]}
        )
    """
        # Add optional fields
        # Don't raise - logging failure shouldn't break the main operation
```

## backend-python/app/utils/db_safe_write.py
```python
class SafeWriteResult:
    # [Logic Hidden]
    """Result wrapper for safe database operations"""
    def __init__(self, matched_count: int, modified_count: int, upserted_id=None):
        # [Logic Hidden]
async def safe_update_one(
    collection,
    filter_query: dict,
    update_query: dict,
    upsert: bool = False,
    resource_name: str = "document"
) -> SafeWriteResult:
    # [Logic Hidden]
    """
    Safe MongoDB update with confirmation
    Args:
        collection: MongoDB collection
        filter_query: Query to find document
        update_query: Update operation
        upsert: Create if not exists
        resource_name: Name for error messages
    Returns:
        SafeWriteResult with counts
    Raises:
        HTTPException if write fails
    """
        # Verify acknowledgment
        # Log results
        # Check if document was found (when not upserting)
async def safe_insert_one(
    collection,
    document: dict,
    resource_name: str = "document"
) -> ObjectId:
    # [Logic Hidden]
    """
    Safe MongoDB insert with confirmation
    Args:
        collection: MongoDB collection
        document: Document to insert
        resource_name: Name for error messages
    Returns:
        Inserted document ID
    Raises:
        HTTPException if insert fails
    """
async def safe_find_one(
    collection,
    filter_query: dict,
    resource_name: str = "document"
):
    # [Logic Hidden]
    """
    Safe MongoDB find with error handling
    Args:
        collection: MongoDB collection
        filter_query: Query to find document
        resource_name: Name for error messages
    Returns:
        Document or None
    """
def db_operation_handler(max_retries: int = 2, timeout: int = 10):
    # [Logic Hidden]
    """
    Decorator for database operations with retry logic
    Args:
        max_retries: Number of retry attempts
        timeout: Timeout in seconds
    """
    def decorator(func):
        # [Logic Hidden]
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # [Logic Hidden]
                    # Add timeout
                    # Don't retry on certain errors
                # Wait before retry (exponential backoff)
            # All retries failed
```

## backend-python/app/utils/__init__.py
```python
# Utils package
```

## frontend/src/api.js
```javascript
// ===== API CONFIGURATION =====
// Auth endpoints (login/register) are on Node.js backend (port 5000)
// Workout/Nutrition endpoints are on Python backend (port 8000)
const VITE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const VITE_PYTHON_API_URL = import.meta.env.VITE_PYTHON_API_URL || 'http://localhost:8000';
const VITE_POSE_TRACKING_URL = import.meta.env.VITE_POSE_TRACKING_URL || 'http://localhost:5001';
// Export base URLs for use in components
export const API_BASE_URL = VITE_API_URL;
export const PYTHON_API_URL = VITE_PYTHON_API_URL;
export const POSE_TRACKING_BASE_URL = VITE_POSE_TRACKING_URL;
// Create axios instance for AUTH endpoints (Node.js backend)
// Create axios instance for WORKOUT/NUTRITION endpoints (Python backend)
// Request interceptor for Auth API
// Request interceptor for Fitness API
// ===== AUTH ENDPOINTS (Node.js backend - port 5000) =====
export const registerUser = (userData) => AuthAPI.post('/auth/register', userData);
export const loginUser = (userData) => AuthAPI.post('/auth/login', userData);
export const loginWithGoogle = (tokenId) => AuthAPI.post('/auth/google', { token: tokenId });
  // [Logic Hidden]
export const loginUser = (userData) => AuthAPI.post('/auth/login', userData);
export const loginWithGoogle = (tokenId) => AuthAPI.post('/auth/google', { token: tokenId });
  // [Logic Hidden]
export const loginWithGoogle = (tokenId) => AuthAPI.post('/auth/google', { token: tokenId });
  // [Logic Hidden]
export const logoutUser = () => AuthAPI.post('/auth/logout');
// ===== PROFILE ENDPOINTS (Node.js backend - port 5000) =====
export const getProfile = () => AuthAPI.get('/profile');
export const saveProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveUserProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveTrends = (trendData) => AuthAPI.post('/profile/trends', trendData);
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
  // [Logic Hidden]
// ===== PROFILE ENDPOINTS (Node.js backend - port 5000) =====
export const getProfile = () => AuthAPI.get('/profile');
export const saveProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveUserProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveTrends = (trendData) => AuthAPI.post('/profile/trends', trendData);
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
  // [Logic Hidden]
export const saveProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveUserProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveTrends = (trendData) => AuthAPI.post('/profile/trends', trendData);
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
  // [Logic Hidden]
export const saveUserProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveTrends = (trendData) => AuthAPI.post('/profile/trends', trendData);
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
  // [Logic Hidden]
export const saveTrends = (trendData) => AuthAPI.post('/profile/trends', trendData);
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
  // [Logic Hidden]
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
  // [Logic Hidden]
export const saveUserWorkoutToNode = (workoutData) => AuthAPI.post('/users/workout/save', workoutData);
export const saveUserMealToNode = (mealData) => AuthAPI.post('/users/meals/save', mealData);
// ===== WORKOUT/NUTRITION ENDPOINTS (Python backend - port 8000) =====
export const updateProfileAndRegenerateWorkouts = (profileData) =>
    FitnessAPI.put('/profile/update-with-plans', profileData);
export const clearWorkoutPlanCache = () => {
  // [Logic Hidden]
export const saveUserMealToNode = (mealData) => AuthAPI.post('/users/meals/save', mealData);
// ===== WORKOUT/NUTRITION ENDPOINTS (Python backend - port 8000) =====
export const updateProfileAndRegenerateWorkouts = (profileData) =>
    FitnessAPI.put('/profile/update-with-plans', profileData);
export const clearWorkoutPlanCache = () => {
  // [Logic Hidden]
// ===== WORKOUT/NUTRITION ENDPOINTS (Python backend - port 8000) =====
export const updateProfileAndRegenerateWorkouts = (profileData) =>
    FitnessAPI.put('/profile/update-with-plans', profileData);
export const clearWorkoutPlanCache = () => {
  // [Logic Hidden]
export const clearWorkoutPlanCache = () => {
  // [Logic Hidden]
export const suggestDailyMeals = (profileData, intensityFocus) => 
    FitnessAPI.post('/nutrition/daily', { profile: profileData, intensity_focus: intensityFocus });
  // [Logic Hidden]
export const sendChatbotMessage = (message, profile, history) => 
    FitnessAPI.post('/api/chat', { message, profile, history }, { timeout: 30000 });
  // [Logic Hidden]
export const generateAIPlan = (profileData) =>
    FitnessAPI.post('/generate-plan', profileData);
export const saveWorkoutPlan = (workoutData) =>
    AuthAPI.post('/users/workout/save', workoutData);
export const saveWorkoutCompletion = (workoutData) =>
    FitnessAPI.post('/workout-completion', workoutData);
export const getWorkoutHistory = () =>
    AuthAPI.get('/profile/workout-history');
export const saveWorkoutHistory = (data) =>
    AuthAPI.post('/profile/workout-history', data);
export const saveMealPlan = (mealData) =>
    AuthAPI.post('/users/meals/save', mealData);
export const saveMealCompletion = (mealData) =>
    FitnessAPI.post('/meal-completion', mealData);
export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const saveWorkoutPlan = (workoutData) =>
    AuthAPI.post('/users/workout/save', workoutData);
export const saveWorkoutCompletion = (workoutData) =>
    FitnessAPI.post('/workout-completion', workoutData);
export const getWorkoutHistory = () =>
    AuthAPI.get('/profile/workout-history');
export const saveWorkoutHistory = (data) =>
    AuthAPI.post('/profile/workout-history', data);
export const saveMealPlan = (mealData) =>
    AuthAPI.post('/users/meals/save', mealData);
export const saveMealCompletion = (mealData) =>
    FitnessAPI.post('/meal-completion', mealData);
export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const saveWorkoutCompletion = (workoutData) =>
    FitnessAPI.post('/workout-completion', workoutData);
export const getWorkoutHistory = () =>
    AuthAPI.get('/profile/workout-history');
export const saveWorkoutHistory = (data) =>
    AuthAPI.post('/profile/workout-history', data);
export const saveMealPlan = (mealData) =>
    AuthAPI.post('/users/meals/save', mealData);
export const saveMealCompletion = (mealData) =>
    FitnessAPI.post('/meal-completion', mealData);
export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const getWorkoutHistory = () =>
    AuthAPI.get('/profile/workout-history');
export const saveWorkoutHistory = (data) =>
    AuthAPI.post('/profile/workout-history', data);
export const saveMealPlan = (mealData) =>
    AuthAPI.post('/users/meals/save', mealData);
export const saveMealCompletion = (mealData) =>
    FitnessAPI.post('/meal-completion', mealData);
export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const saveWorkoutHistory = (data) =>
    AuthAPI.post('/profile/workout-history', data);
export const saveMealPlan = (mealData) =>
    AuthAPI.post('/users/meals/save', mealData);
export const saveMealCompletion = (mealData) =>
    FitnessAPI.post('/meal-completion', mealData);
export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const saveMealPlan = (mealData) =>
    AuthAPI.post('/users/meals/save', mealData);
export const saveMealCompletion = (mealData) =>
    FitnessAPI.post('/meal-completion', mealData);
export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const saveMealCompletion = (mealData) =>
    FitnessAPI.post('/meal-completion', mealData);
export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');
  // [Logic Hidden]
```

## frontend/src/App.jsx
```javascript
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ProfileSetup = lazy(() => import('./pages/ProfileSetup'));
const Workout = lazy(() => import('./pages/Workout'));
const Nutrition = lazy(() => import('./pages/Nutrition'));
const Chatbot = lazy(() => import('./pages/Chatbot'));
export default function App() {
  // [Logic Hidden]
const Register = lazy(() => import('./pages/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ProfileSetup = lazy(() => import('./pages/ProfileSetup'));
const Workout = lazy(() => import('./pages/Workout'));
const Nutrition = lazy(() => import('./pages/Nutrition'));
const Chatbot = lazy(() => import('./pages/Chatbot'));
export default function App() {
  // [Logic Hidden]
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ProfileSetup = lazy(() => import('./pages/ProfileSetup'));
const Workout = lazy(() => import('./pages/Workout'));
const Nutrition = lazy(() => import('./pages/Nutrition'));
const Chatbot = lazy(() => import('./pages/Chatbot'));
export default function App() {
  // [Logic Hidden]
const ProfileSetup = lazy(() => import('./pages/ProfileSetup'));
const Workout = lazy(() => import('./pages/Workout'));
const Nutrition = lazy(() => import('./pages/Nutrition'));
const Chatbot = lazy(() => import('./pages/Chatbot'));
export default function App() {
  // [Logic Hidden]
const Workout = lazy(() => import('./pages/Workout'));
const Nutrition = lazy(() => import('./pages/Nutrition'));
const Chatbot = lazy(() => import('./pages/Chatbot'));
export default function App() {
  // [Logic Hidden]
const Nutrition = lazy(() => import('./pages/Nutrition'));
const Chatbot = lazy(() => import('./pages/Chatbot'));
export default function App() {
  // [Logic Hidden]
const Chatbot = lazy(() => import('./pages/Chatbot'));
export default function App() {
  // [Logic Hidden]
export default function App() {
  // [Logic Hidden]
    // Bug #6a: Use authReady to defer routing until after the first mount.
    // Without this, React renders a flash of the redirect destination before
    // the synchronous localStorage read has been used to set isAuthenticated.
    // Sync auth state from localStorage
    const syncAuthState = () => {
      // [Logic Hidden]
        // Initial auth check — runs synchronously after mount
        const onStorage = (event) => {
          // [Logic Hidden]
        const onFocus = () => syncAuthState();
        window.addEventListener('storage', onStorage);
        window.addEventListener('focus', onFocus);
        return () => {
          // [Logic Hidden]
    // Logout function
    const handleLogout = () => {
      // [Logic Hidden]
    // Don't render routes until we've confirmed auth state from localStorage
```

## frontend/src/main.jsx
```javascript

```

## frontend/src/components/ConfirmDialog.jsx
```javascript
const ConfirmDialog = ({ show, message, onConfirm, onCancel }) => {
  // [Logic Hidden]
      // Lock background scroll
      // Unlock background scroll
    // Cleanup function
```

## frontend/src/components/NotificationProvider.jsx
```javascript
/* eslint-disable react-refresh/only-export-components */
export const useNotification = () => {
  // [Logic Hidden]
export const NotificationProvider = ({ children }) => {
  // [Logic Hidden]
  const showNotification = useCallback((message, type = 'info', duration = 4000) => {
    // [Logic Hidden]
    // Auto-remove notification after duration
  const showError = useCallback((message, duration = 5000) => {
    // [Logic Hidden]
  const showSuccess = useCallback((message, duration = 4000) => {
    // [Logic Hidden]
  const showWarning = useCallback((message, duration = 4000) => {
    // [Logic Hidden]
  const showInfo = useCallback((message, duration = 4000) => {
    // [Logic Hidden]
  const removeNotification = useCallback((id) => {
    // [Logic Hidden]
const NotificationList = ({ notifications, removeNotification }) => {
  // [Logic Hidden]
const NotificationItem = ({ notification, onClose }) => {
  // [Logic Hidden]
  const getNotificationStyles = () => {
    // [Logic Hidden]
```

## frontend/src/components/PoseDetector.jsx
```javascript
// ─── COMPREHENSIVE MOVEMENT PATTERNS ──
// Pattern mapping for 1300+ exercise dataset via keyword matching
const MOVEMENT_PATTERNS = {
const getMovementPattern = (name) => {
  // [Logic Hidden]
// ─── Speed category for adaptive smoothing & frame skip ──
const SPEED_CATEGORY = {
// ─── ANGLE MATH ──
const calcAngle = (a, b, c) => {
  // [Logic Hidden]
// ─── Adaptive EMA smoother ──
// Fast exercises (curls): high alpha (0.50) = more responsive to quick movement
// Slow exercises (squats): low alpha (0.25) = smoother, less jitter
const emaSmooth = (prev, curr, alpha) => ({
  // [Logic Hidden]
const getAlpha = (pattern) => {
  // [Logic Hidden]
const getFrameSkip = (pattern) => {
  // [Logic Hidden]
// Minimum visibility threshold for reliable angle calculations
const MIN_VISIBILITY = 0.40;
const TRACK_STALE_MS = 180;
const getPrimaryVisibility = (pattern, pts) => {
  // [Logic Hidden]
const smoothPoint = (prev, curr, alpha) => {
  // [Logic Hidden]
// ─── FORM SAFETY RULES per pattern ──
const checkForm = (pattern, angles) => {
  // [Logic Hidden]
// ─── REP COUNTING CONFIG with ROM validation ──
const REP_CONFIG = {
// Hysteresis band to avoid jitter-based double counting
const HYSTERESIS = 8;
export default function PoseDetector({
  // [Logic Hidden]
  // EMA smoothed landmarks
  // Frame counter for skip logic
  // Track the last warning to avoid repeating the same message
  // Rep state — 3-phase state machine
    // Calf-specific: track ankle Y position
    // Hold detection for isometric exercises
    // Stabilize brief landmark dropouts
  // ─── Initialise MediaPipe ──
  // ─── Reset state on exercise change ──
  // ─────────────────────────────────────
  //  MAIN ANALYSIS & DRAWING
  // ─────────────────────────────────────
  const analyzeAndDraw = useCallback((rawLandmarks, canvas, isPredictionStale = false) => {
    // [Logic Hidden]
    const toPoint = (idx) => ({
      // [Logic Hidden]
    // Extract raw points
    // Apply adaptive EMA smoothing based on exercise speed
    // Calculate all angles
    // ─── FORM CHECK with dedup ──
    // Only fire feedback if: different warning than last, and enough time passed
    // ─── CONFIDENCE GATE ──
    // ─── REP COUNTING — 3-phase state machine with ROM validation ──
      // ── CALF RAISE: Use ankle Y-position delta instead of angle ──
      // Detect upward movement (heel raise = Y decreases)
        // Coming back down
      // ── Standard angle-based rep counting ──
      // Track angle extremes during the rep for ROM validation
        // "Normal" — angle starts high (rest), goes low (contracted), back to high
        // rest → contracting (angle drops below down threshold)
        // contracting → extended (angle rises above up threshold) → count rep if ROM valid
          // Validate ROM before counting
            // Partial rep — reset without counting
            // Feedback for partial reps (debounced)
        // "Inverted" — angle starts high, drops to contracted, rises back
      // ── HOLD DETECTION for planks/isometric core ──
          // Report every 5 seconds held
    // ─── DRAWING ──
    const drawLine = (a, b) => {
      // [Logic Hidden]
    // Skeleton connections
    // ─── ANGLE ARC + TEXT on key joints ──
    const drawAngleArc = (a, b, c, angle, label) => {
      // [Logic Hidden]
      // Arc
      // Text background
    // Show key angles per pattern
    // ─── Draw JOINT NODES ──
    // ─── Rep stage indicator (small HUD) ──
  // ─── Processing loop with adaptive frame skipping ──
    const processVideo = () => {
      // [Logic Hidden]
          // Adaptive frame skip based on exercise speed
            // Skip broken frames
```

## frontend/src/components/UserProfile.jsx
```javascript
const UserProfile = () => {
  // [Logic Hidden]
    const handleChange = (e) => {
      // [Logic Hidden]
    const handleSubmit = async (e) => {
      // [Logic Hidden]
```

## frontend/src/data/quotes.js
```javascript
export const QUOTES = [
  // --- THE DAVID GOGGINS / JOCKO WILLINK TIER (Extreme Discipline) ---
  // --- THE STOIC / BRUTAL TRUTH TIER ---
  // --- THE BODYBUILDING / IRON TIER ---
  // --- THE "DARK MOTIVATION" TIER ---
  // --- SHORT & PUNCHY (For Mobile Layouts) ---
  // --- CONTINUATION (To ensure zero repeats for months) ---
```

## frontend/src/pages/Chatbot.jsx
```javascript
// ===== STYLES =====
  // --- CHAT LAYOUT ---
  // --- CHAT HEADER ---
  // --- MESSAGES ---
  // --- WELCOME SCREEN ---
  // --- INPUT AREA ---
  // --- ERROR BANNER ---
// ===== QUICK SUGGESTION CHIPS =====
const SUGGESTIONS = [
const MAX_INPUT_LENGTH = 2000;
// ===== SIMPLE MARKDOWN RENDERER =====
function renderMarkdown(text) {
  // [Logic Hidden]
  // Split into lines and process
  const flushList = () => {
    // [Logic Hidden]
  const processInline = (line) => {
    // [Logic Hidden]
    // Bold
    // Bullet list
    // Numbered list
    // End of list
    // Empty line
    // Heading-like (### or **)
    // Normal paragraph
  // Flush any remaining list
// ===== TYPING INDICATOR =====
function TypingIndicator() {
  // [Logic Hidden]
// ===== MAIN COMPONENT =====
function Chatbot() {
  // [Logic Hidden]
  // Load profile on mount
    const loadProfile = async () => {
      // [Logic Hidden]
    // Load saved chat from sessionStorage (persists within tab)
  // Save chat to sessionStorage whenever messages change
  // Auto-scroll
  // Clear error after 5s
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);
  const sendMessage = useCallback(async (text) => {
        // [Logic Hidden]
  const sendMessage = useCallback(async (text) => {
    // [Logic Hidden]
    // Clear any previous error
    // Add user message
    // Cooldown to prevent spam
      // Focus input after response
  const handleSubmit = (e) => {
    // [Logic Hidden]
  const handleKeyDown = (e) => {
    // [Logic Hidden]
  const clearChat = () => {
    // [Logic Hidden]
  const handleLogout = () => {
    // [Logic Hidden]
        /* Messages area scrollbar */
        /* Mobile responsive */
```

## frontend/src/pages/Dashboard.jsx
```javascript
// --- FULL PREMIUM STYLES (JS Object - Static Only) ---
// --- RESPONSIVE CSS STRING (Animations, Media Queries, Hover States) ---
  /* ===== HOVER EFFECTS ===== */
  /* ===== ANIMATIONS ===== */
  /* ===== SCROLLBAR ===== */
  /* ===== ANIMATIONS (Entry/Exit) ===== */
  /* ===== RESPONSIVE MEDIA QUERIES ===== */
  /* Extra Small Mobile (320px - 480px) */
  /* Small Mobile (481px - 768px) */
  /* Tablet (769px - 1024px) */
  /* Desktop (1025px+) */
// --- CHART COMPONENT ---
const ActivityChart = React.memo(({ data, mode, period, xLabels: propXLabels }) => {
  // [Logic Hidden]
  const getPoint = (i) => {
    // [Logic Hidden]
// --- DEFAULT HISTORY ---
const DEFAULT_HISTORY = [];
function Dashboard() {
  // [Logic Hidden]
  // --- STATE DECLARATIONS ---
  // ✅ FIX 2: Cross-page macro update — called when meal is saved from Nutrition page
  // Sets absolute macro values (not incremental) from today's totals returned by the backend
  const _setMacrosFromTotals = (totals) => {
    // [Logic Hidden]
  const _updateMacrosFromMeal = (mealData) => {
    // [Logic Hidden]
  const currentQuote = useMemo(() => {
    // [Logic Hidden]
  const getWorkoutPlanForDate = (dateObj) => {
    // [Logic Hidden]
  const isRestDayForDate = (dateObj) => {
    // [Logic Hidden]
    // 1. Explicit type from backend engine
    // 2. Focus field
    // 3. Label / note
    // 4. No exercises and not explicitly a workout
  const normalizeMealEntries = (rawMeals = []) => {
    // [Logic Hidden]
  // --- EFFECTS & LIFECYCLE ---
  // Fetch user and init dashboard
    const fetchUserData = async () => {
      // [Logic Hidden]
        // ✅ BACKEND SYNC: Parse MongoDB history instead of localStorage
        // Normalize meal history because backend can return either grouped day objects
        // or flat meal entries depending on write path.
        // Calculate exact macros eaten TODAY from MongoDB
        const mealsToday = normalizedMeals.filter(m => {
          // [Logic Hidden]
        // ✅ FIX: Round all macro values to integers
        const mealsDoneToday = ['breakfast', 'lunch', 'dinner'].every((type) =>
          completedMealTypesToday.has(type)
        );
        if (mealsDoneToday) {
          // [Logic Hidden]
            // On rest day, meal completion is sufficient to mark day as completed.
        // ✅ FIX 1: Macro targets from nutrition plan's daily_target (computed by Python TDEE engine)
        // Priority: cached nutrition plan → goal-based defaults
        // ✅ Avatar Sync
        // ✅ State Sync from DB Trends (Water, Sleep, Streak)
           // Synchronize today's latest data points
           const todayRecord = data.trends.find(t => String(t.date).startsWith(todayStr));
           if (todayRecord) {
             // [Logic Hidden]
           // ✅ FIX: Advanced Streak Calculation incorporating Rest Days
           // A day is "completed" if meal_completed AND (workout_completed OR isRestDay)
           // Build a map: date-string -> trend entry (pick latest if duplicates)
           // Walk backwards from today, day by day
           // ✅ FIX: Build weekly progress from backend trends data
           const weekData = days.map((day, index) => {
             // [Logic Hidden]
           // Fallback to workout count
           const uniqueDays = new Set(workouts.map(w => (w.date || '').split('T')[0]));
           setStats((prev) => ({ ...prev, streak: uniqueDays.size }));
             // [Logic Hidden]
           // ✅ FIX: Still build weekly progress even without trends
        // Derive definitive status
        const todayRecordForStatus = data.trends && Array.isArray(data.trends) ? data.trends.find(t => String(t.date).startsWith(todayStr)) : null;
        let finalWorkoutDone = todayRecordForStatus ? !!todayRecordForStatus.workout_completed : false;
        let finalMealDone = todayRecordForStatus ? !!todayRecordForStatus.meal_completed : false;
        // Fallback calculations if trend data is lagging
        const workoutsTodayArray = (data.workouts || []).filter(w => String(w.completedAt || w.date).startsWith(todayStr));
        if (workoutsTodayArray.length > 0) finalWorkoutDone = true;
        if (mealsDoneToday) finalMealDone = true;
        if (finalWorkoutDone) {
          // [Logic Hidden]
        // Fallback calculations if trend data is lagging
        const workoutsTodayArray = (data.workouts || []).filter(w => String(w.completedAt || w.date).startsWith(todayStr));
        if (workoutsTodayArray.length > 0) finalWorkoutDone = true;
        if (mealsDoneToday) finalMealDone = true;
        if (finalWorkoutDone) {
          // [Logic Hidden]
      // Run daily reset AFTER backend data is loaded.
      // NOTE: checkDailyReset no longer zeroes macros — DB values are authoritative.
      // ✅ FIX: Call checkDayReset to properly set workout→meal→done status flow
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // Session recovery on mount
    const recoverSession = () => {
      // [Logic Hidden]
        // ✅ UPDATED: Use storage utility
          // ✅ UPDATED: Use storage utility
  // ✅ UPDATED: Daily reset logic with storage utilities
  const checkDailyReset = async () => {
    // [Logic Hidden]
        // ✅ FIX: Do NOT call resetDailyMacros() here!
        // Macros are loaded from MongoDB by fetchUserData() and are authoritative.
        // Zeroing them would overwrite the real data from the database.
        // Clear notification flags
  // ✅ FIX 2: Cross-page macro sync — re-fetch today's data when user returns to Dashboard
    const handlePageVisibilityChange = async () => {
      // [Logic Hidden]
          // Re-fetch profile to get updated meal data (e.g., after completing meals on Nutrition page)
          const mealsToday = normalizedMeals.filter(m => {
            // [Logic Hidden]
          // ✅ PA-6: Also refresh the chart so it reflects latest data
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // ✅ BUG FIX: Listen for macro sync from Nutrition page via localStorage 'storage' event
    const handleStorageSync = (e) => {
      // [Logic Hidden]
  const addNotification = useCallback((message, type = 'info') => {
    // [Logic Hidden]
  const dismissNotification = (id) =>
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  const handleClickOutside = (event) => {
    // [Logic Hidden]
  const handleClickOutside = (event) => {
    // [Logic Hidden]
  // ✅ UPDATED: logActivity uses storage utility
  const logActivity = (type, name, details) => {
    // [Logic Hidden]
  const removeLastLog = (type) => {
    // [Logic Hidden]
      const index = prev.findIndex((item) => item.type === type);
      if (index !== -1) {
        // [Logic Hidden]
  // ✅ UPDATED: Notification tracking with storage utilities
  const hasNotificationBeenShownToday = (notificationId) => {
    // [Logic Hidden]
  const markNotificationAsShownToday = (notificationId) => {
    // [Logic Hidden]
  const checkWaterThresholdNotifications = useCallback((oldWater, newWater) => {
    // [Logic Hidden]
  const checkSleepThresholdNotifications = useCallback((oldSleep, newSleep) => {
    // [Logic Hidden]
  // ✅ UPDATED: Reminder tracking with storage utilities
  const hasDailyReminderBeenShown = (reminderType) => {
    // [Logic Hidden]
  const markDailyReminderAsShown = (reminderType) => {
    // [Logic Hidden]
  const checkDailyReminders = () => {
    // [Logic Hidden]
            const exists = prev.some((n) => n.id === newNotification.id);
            if (exists) return prev;
            markDailyReminderAsShown('sleep');
            return [...prev, newNotification].slice(-5);
          });
        } else {
              // [Logic Hidden]
      // Morning hydration reminder
            const exists = prev.some((n) => n.id === newNotification.id);
            if (exists) return prev;
            markDailyReminderAsShown('water');
            return [...prev, newNotification].slice(-5);
          });
        } else {
              // [Logic Hidden]
      // Afternoon hydration check
            const exists = prev.some((n) => n.id === newNotification.id);
            if (exists) return prev;
            markDailyReminderAsShown('water-afternoon');
            return [...prev, newNotification].slice(-5);
          });
        } else {
              // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
    const handleResize = () => {};
      // [Logic Hidden]
  const checkInterruptedSessions = () => {
    // [Logic Hidden]
      // ✅ UPDATED: Use storage utility
  // ✅ UPDATED: Workout session management with storage utilities
  const startWorkoutSession = (sessionDetails = null) => {
    // [Logic Hidden]
  const endWorkoutSession = () => {
    // [Logic Hidden]
    // updateChart is intentionally excluded to avoid effect loops from function identity changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // Separate lightweight local-only chart update for water/sleep live changes
  // ✅ BACKEND PERSISTENCE: Debounce-sync water & sleep to MongoDB trends
    // Don't sync on initial mount (values are 0)
    const timer = setTimeout(() => {
      // [Logic Hidden]
  const updateRecoveryScore = (currentWater, currentSleep) => {
    // [Logic Hidden]
   // ✅ FIX 4: Use StorageKeys for water persistence
   const handleWaterAdd = useCallback(() => {
     // [Logic Hidden]
  const handleWaterRemove = useCallback(() => {
    // [Logic Hidden]
  // ✅ UPDATED: useCallback for sleep handlers
  // ✅ FIX 4: Use StorageKeys for sleep persistence
  const handleSleepAdd = useCallback(() => {
    // [Logic Hidden]
  const handleSleepRemove = useCallback(() => {
    // [Logic Hidden]
  const fetchExternalNutritionData = async (foodQuery) => {
    // [Logic Hidden]
      // Using USDA FoodData Central API (Requires API key)
        // Return mock nutrition data as fallback
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(
        `https://api.nal.usda.gov/fdc/v1/foods/search?query=${encodeURIComponent(foodQuery)}&pageSize=1&api_key=${apiKey}`,
        // [Logic Hidden]
        // Return fallback data if API fails
      // Extract nutrients from USDA format
      const getNutrient = (nutrientId) => {
        // [Logic Hidden]
      // USDA Nutrient IDs:
      // 1008 = Energy (kcal)
      // 1003 = Protein (g)
      // 1005 = Carbohydrate (g)
      // 1004 = Fat (g)
      // 1079 = Fiber (g)
      // Return fallback data on error
  const fetchExternalExerciseData = async (exerciseQuery) => {
    // [Logic Hidden]
        // Return mock exercise data as fallback
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(
        `https://api.api-ninjas.com/v1/exercises?muscle=${encodeURIComponent(exerciseQuery)}`,
        // [Logic Hidden]
        // Return fallback data if API fails
      // Return fallback data on error
  const enrichDataWithExternalAPIs = async () => {
    // [Logic Hidden]
  // ✅ UPDATED: Cached data uses storage utilities
  const getCachedEnrichedData = async () => {
    // [Logic Hidden]
    const maybeEnrich = async () => {
      // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  const updateChart = async (mode, period) => {
    // [Logic Hidden]
        // --- MONTH VIEW: Group into 4 weeks ---
        const series = weekBuckets.map((bucket) => {
          // [Logic Hidden]
            const totalCal = bucket.reduce((s, e) => s + (e?.calories || 0), 0);
            return bucket.length > 0 ? Math.round(totalCal / bucket.length) : 0;
          }
          if (mode === 'water') {
              // [Logic Hidden]
            const total = bucket.reduce((s, e) => s + (e?.water_intake || e?.water_glasses || 0), 0);
            return parseFloat((total / bucket.length).toFixed(1));
          }
          if (mode === 'sleep') {
              // [Logic Hidden]
            const total = bucket.reduce((s, e) => s + (e?.sleep_duration || e?.sleep_hours || 0), 0);
            return parseFloat((total / bucket.length).toFixed(1));
          }
          return 0;
        });
        setChartXLabels(weekLabels);
        setChartData(series);
      } else {
              // [Logic Hidden]
        // --- WEEK VIEW: 7-day slots Mon-Sun ---
        // For water/sleep, ensure today's slot reflects live state
  const saveTrendsToBackend = async (trendData) => {
    // [Logic Hidden]
  // ✅ UPDATED: Trends uses storage utilities
  const _updateTrends = async () => {
    // [Logic Hidden]
      // ✅ UPDATED: Use storage utilities
      // ✅ FIX: Send flat macro fields instead of nested `macros` object.
      // The Mongoose schema now expects top-level `calories`, `protein`, `carbs`, `fat`.
  const updateLocalTrendData = (trendData) => {
    // [Logic Hidden]
  // ✅ UPDATED: Day reset uses deriving from backend or fallback to storage
  const checkDayReset = async (forceWorkoutDone, forceMealDone) => {
    // [Logic Hidden]
      // Streak is now computed from backend trends in fetchUserData.
      // Do NOT override with stale localStorage values.
      // ✅ UPDATED: Use storage utility
  const handleAction = async () => {
    // [Logic Hidden]
  const showConfirmDialog = (message, onConfirm) =>
    setConfirmDialog({ show: true, message, onConfirm });
    // [Logic Hidden]
  const handleConfirm = () => {
    // [Logic Hidden]
  const handleCancelConfirm = () => {
    // [Logic Hidden]
  // ✅ FIX: Logout uses logoutSafe (selective clear) instead of clearAllStorage (nuclear)
  const handleLogout = () => {
    // [Logic Hidden]
        // Disable all interactions immediately
        // Selective clear — preserves cached data for faster re-login
        // Navigate immediately without waiting
        // Re-enable after navigation completes
  // ✅ BUG FIX 1: Listen for macro sync signals from Nutrition page
  // When user switches back to Dashboard tab, read _macroSync from localStorage
    const handleVisibilityChange = () => {
      // [Logic Hidden]
            // Only apply if the signal is recent (within last 5 minutes)
            // Clear the signal after consuming it
```

## frontend/src/pages/Login.jsx
```javascript
const clearUserScopedCache = () => {
  // [Logic Hidden]
const syncUserSession = (newUser) => {
  // [Logic Hidden]
function Login({ setIsAuthenticated }) {
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  const handleGoogleResponse = async (response) => {
    // [Logic Hidden]
  const handleChange = (e) => {
    // [Logic Hidden]
  const handleSubmit = async (e) => {
    // [Logic Hidden]
```

## frontend/src/pages/Nutrition.jsx
```javascript
// Local-timezone date string helper is now imported from storage.js
function Nutrition() {
  // [Logic Hidden]
  // Swap state
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // ✅ BUG FIX 2: Backend Persistence to Frontend
      const dayPlan = weeklyPlan.days.find((d) => d.date === dayEntry.date);
      if (!dayPlan) return;
      Object.values(dayEntry.meals).forEach((mealData) => {
        // [Logic Hidden]
        const planMeal = dayPlan.meals.find((m) => m.meal_type === mealData.meal_type);
        if (!planMeal) return;
        const lockMealName = mealData.name || planMeal.name;
        const mealLockKey = `${dayEntry.date}-${lockMealName}`;
          // [Logic Hidden]
            const planFood = planMeal.foods.find((f) => f.name === food.name);
            if (!planFood) return;
            const checkKey = `${dayEntry.date}-${planFood.id}`;
              // [Logic Hidden]
  const getTodayWorkoutIntensity = (workoutPlan = []) => {
    // [Logic Hidden]
    const todayPlan = workoutPlan.find((d) => (d?.day_of_week ?? -1) === todayIdx) || workoutPlan[todayIdx];
    if (!todayPlan) return "moderate";
    const label = `${todayPlan.day || todayPlan.focus || ""}`.toLowerCase();
      // [Logic Hidden]
    const totalSets = exercises.reduce((sum, ex) => {
      // [Logic Hidden]
  const getWorkoutPlanForNutrition = async (profile) => {
    // [Logic Hidden]
  const isTodayRestDay = () => {
    // [Logic Hidden]
      const todayPlan = workoutPlan.find((d) => (d?.day_of_week ?? -1) === todayIdx) || workoutPlan[todayIdx];
      if (!todayPlan) return false;
      // 1. Explicit type from backend engine
      if (todayPlan.type === 'rest') return true;
      // 2. Focus field
      const focus = `${todayPlan.focus || ""}`.toLowerCase();
        // [Logic Hidden]
      // 1. Explicit type from backend engine
      // 2. Focus field
      // 3. Label / note
      // 4. No exercises and not explicitly a workout
  /* ──────────────────────────────────────────
   *  FETCH — builds 7-day plan from backend
   *  ✅ FIX 7: Date-aware caching with profile hash
   *  ✅ FIX 8: Cache invalidation on profile change
   * ────────────────────────────────────────── */
  const fetchNutritionPlan = async () => {
    // [Logic Hidden]
      // ✅ FIX 7+8: Check if we have a valid cached plan for today with same profile
      // ✅ PA-7: Use LOCAL timezone for consistent date across pages
        // Use cached plan — no network request needed
      // Clear invalidation flag since we're fetching fresh
        // Save daily target
        // Build 7-day display from weekly_plan the backend now returns
          // Get the matching day from the backend weekly plan
          // Build meals array from the backend day object
            const foods = items.map((item, idx) => ({
              // [Logic Hidden]
          // Daily totals = sum of all meal totals
        // ✅ FIX 9: Sync daily_target to localStorage for Dashboard macro targets
  /* ──────────────────────────────────────────
   *  CHECKING / LOCKING meals
   * ────────────────────────────────────────── */
  const loadHistory = async () => {
    // [Logic Hidden]
      // ✅ Populate lockedMeals directly from backed up daily history
      const todayEntry = historyData.find(d => d.date === todayDate);
      if (todayEntry && todayEntry.meals) {
        // [Logic Hidden]
      // Fallback
  const loadCheckedFoods = () => setCheckedFoods(JSON.parse(localStorage.getItem("checkedFoods") || "{}"));
    // [Logic Hidden]
  const handleCheckFood = (foodId, mealName, dayIdx) => {
    // [Logic Hidden]
    // Check if ALL items in this meal are now ticked
      const meal = selectedDay.meals.find(m => m.name === mealName);
      if (meal) {
        // [Logic Hidden]
        const allChecked = meal.foods.every(f => newChecked[`${today}-${f.id}`]);
          // [Logic Hidden]
          let dateEntry = updatedHistory.find(e => e.date === today);
          if (!dateEntry) { dateEntry = { date: today, meals: {}, total_calories: 0, total_protein: 0, total_carbs: 0, total_fat: 0 }; updatedHistory.unshift(dateEntry); }
            // [Logic Hidden]
          // Sync with Node Database & consume todayTotals for Dashboard macro update
            // ✅ BUG FIX: Consume todayTotals from backend to signal Dashboard
          // ✅ FIX 6: Snacks are OPTIONAL for day completion
          // Only Breakfast + Lunch + Dinner are required — Snack is bonus calories
          const allMealsDone = requiredMeals.every((mealType) => Boolean(dateEntry.meals?.[mealType]));
          const water = parseInt(String(getFromStorage(StorageKeys.WATER_INTAKE, 0) || 0), 10) || 0;
          const sleep = parseFloat(String(getFromStorage(StorageKeys.SLEEP_HOURS, 0) || 0)) || 0;
          const restDay = isTodayRestDay();
          const workoutDone = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === "true";
          // Keep trend/graph state in sync after every completed meal.
          saveTrends({
            // [Logic Hidden]
          // Keep trend/graph state in sync after every completed meal.
  /* ──────────────────────────────────────────
   *  SWAP — fetches alternatives from backend
   * ────────────────────────────────────────── */
  const openSwapModal = async (food, mealType, dayIdx) => {
    // [Logic Hidden]
  const confirmSwap = () => {
    // [Logic Hidden]
    const updatedDays = weeklyPlan.days.map((day, i) => {
      // [Logic Hidden]
      const updatedMeals = day.meals.map(meal => {
        // [Logic Hidden]
        const updatedFoods = meal.foods.map(f => {
          // [Logic Hidden]
  /* ──────────────────────────────────────────
   *  RENDER
   * ────────────────────────────────────────── */
  // ✅ BUG FIX 4: Logout confirmation handler for Navbar
  const handleLogout = () => {
    // [Logic Hidden]
  const selectedDayConsumedTotals = (() => {
    // [Logic Hidden]
    const dayEntry = mealHistory.find((e) => e.date === selectedDay.date);
    return {
      // [Logic Hidden]
            const checkedCount = meal.foods.filter(f => checkedFoods[`${selectedDay.date}-${f.id}`] || isLocked).length;
              // [Logic Hidden]
            // Default action: logout
/* ═══════════════════════════════════════════
 *  CHILD COMPONENTS
 * ═══════════════════════════════════════════ */
function Navbar({ navigate, setShowHistory, onLogout }) {
  // [Logic Hidden]
function MacroStat({ value, label, color, icon }) {
  // [Logic Hidden]
function MealCard({ meal, isLocked, checkedFoods, tickTimes, today, checkedCount, totalCount, onCheckFood, onSwapFood, dayIndex, isFutureDay }) {
  // [Logic Hidden]
function HistoryPanel({ mealHistory, expandedDates, setExpandedDates, expandedMeals, setExpandedMeals, onClose, today }) {
  // [Logic Hidden]
```

## frontend/src/pages/ProfileSetup.jsx
```javascript
// --- STYLES ---
  // NEW: Cancel Button Style
const MultiSelect = ({ name, options, value, onChange, isOpen, onToggle, isNoneChecked }) => {
  // [Logic Hidden]
function ProfileSetup() {
  // [Logic Hidden]
  // State for regeneration timing dialog
  // Function to clear workout plan cache to force regeneration
  const _clearWorkoutPlanCache = () => {
    // [Logic Hidden]
      // Bug #5 Fix: Use the exact keys Workout.jsx reads to ensure invalidation works.
      // Legacy keys (in case any old code wrote them)
  // Function to clear meal plan cache to force regeneration
  const _clearMealPlanCache = () => {
    // [Logic Hidden]
      // Bug #5 Fix: Use the exact keys Nutrition.jsx reads to ensure cache invalidation works.
      // Volatile daily state that belongs to the old plan
      // Legacy keys (in case any old code wrote them)
  const getMondayIndexToday = () => {
    // [Logic Hidden]
  const getPlanItemIndex = (item, fallbackIdx) => {
    // [Logic Hidden]
  const mergeWorkoutPlanFromToday = (currentPlan, regeneratedPlan) => {
    // [Logic Hidden]
    // 1. BLOCK BACK BUTTON
    const handlePopState = () => {
      // [Logic Hidden]
    // 2. LOAD EXISTING DATA
    const loadData = async () => {
      // [Logic Hidden]
            // Determine if user is editing based on existing profile data
            // If editing, prefill form
            // Check if user has Google avatar
    // 3. LOAD AVATAR
    // eslint-disable-next-line react-hooks/exhaustive-deps
    const handleClickOutside = (event) => {
      // [Logic Hidden]
  const handleImageUpload = (event) => {
    // [Logic Hidden]
  const handleRemoveImage = (e) => {
    // [Logic Hidden]
  const handleChange = (e) => {
    // [Logic Hidden]
  const handleCheckbox = (e, type) => {
    // [Logic Hidden]
  const handleSubmit = async (e) => {
    // [Logic Hidden]
    // Build profile update payload
    // Compare against server-loaded baseline profile, not cached local profile.
    // Check what changes affect workout regeneration
    // If changes affect plans, ask timing for existing users.
    // No plan-impacting changes (e.g. name/avatar only), update directly without regeneration.
  /**
   * Handle regeneration timing choice
   */
  const handleRegenerateChoice = async (choice) => {
    // [Logic Hidden]
  /**
   * Perform the actual profile update
   * @param {Object} profileUpdate - The profile data to update
   * @param {string} timing - 'immediate' or 'next_week'
   */
  const performProfileUpdate = async (profileUpdate, timing, options = {}) => {
    // [Logic Hidden]
      // ✅ CRITICAL FIX: Save profile to Node backend (port 5000 / MongoDB) FIRST.
      // The Dashboard reads from Node via getProfile(). If we skip this step,
      // the Dashboard sees no goal/weight and instantly redirects back to /profile-setup.
        // Log but don't block — Python plan generation can still proceed
        // Call the Python backend to regenerate workout/nutrition plans
        // ✅ FIX 10: Invalidate nutrition cache so Nutrition page fetches fresh plan
        // Also set profile update timestamp for cross-page awareness
        // ✅ Persist regenerated nutrition plan with proper StorageKeys
        // Wrap raw plan in cache-compatible format that Nutrition.jsx expects
          // ✅ FIX PA-5: profileHash MUST match the format Nutrition.jsx uses at line 185:
          //    `${profile.weight}-${profile.height}-${profile.goal}-${profile.dietary_preference || ''}-${profile.age}`
          // ✅ PA-7: Use local timezone date, same format as Dashboard/Nutrition
        // Update user data in localStorage
        // Show success notification
        // Redirect to dashboard after short delay
```

## frontend/src/pages/Register.jsx
```javascript
const clearUserScopedCache = () => {
  // [Logic Hidden]
const syncUserSession = (newUser) => {
  // [Logic Hidden]
const Register = () => {
  // [Logic Hidden]
    // Initialize Google SDK after component mounts
            // Hide notification after 5 seconds
        // eslint-disable-next-line react-hooks/exhaustive-deps
    const handleGoogleResponse = async (response) => {
      // [Logic Hidden]
            // Send the Google token to our backend
            // Save token and user info
            // Since Google users are already registered, redirect to profile setup or dashboard
    const handleChange = (e) => {
      // [Logic Hidden]
    const handleRegister = async (e) => {
      // [Logic Hidden]
            // 1. Call Node.js Backend
            // 2. SUCCESS: Show stylish message instead of alert
            // 3. Wait 2 seconds, then go to Login
```

## frontend/src/pages/Workout.jsx
```javascript
// Define full weekday names array
// --- STYLES (Your Exact Styles Preserved) ---
// History dynamically fetched from node
const getTodayIdx = () => {
  // [Logic Hidden]
  // Use IST to stay aligned with date handling across the app/backend.
const isRestDay = (day) => {
  // [Logic Hidden]
  // 1. Explicit type field from backend engine (most reliable)
  // 2. Focus field containing 'rest' (e.g. "Rest Day", "Rest", "Active Recovery")
  // 3. Day label or note containing 'rest'
  // 4. No exercises AND type is not 'workout' → treat as rest
const getDayStatus = (day, todayIdx, completedIds = new Set()) => {
  // [Logic Hidden]
const Workout = () => {
  // [Logic Hidden]
  // State declarations
  // Posture processing state
  const showConfirmDialog = (message, onConfirm) => {
    // [Logic Hidden]
  const handleConfirm = () => {
    // [Logic Hidden]
  const handleCancelConfirm = () => {
    // [Logic Hidden]
  const getExerciseMediaCandidates = (exercise) => {
    // [Logic Hidden]
  const isVideoUrl = (url) => {
    // [Logic Hidden]
  const getMovementCue = (exerciseName = '') => {
    // [Logic Hidden]
  const renderAnimatedGuideFallback = (exerciseName) => (
    <div style={{ ...styles.gifLarge, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '10px', background: '#0f0f12' }}>
    // [Logic Hidden]
  const renderActiveExerciseMedia = () => {
    // [Logic Hidden]
    const handleClickOutside = (event) => {
      // [Logic Hidden]
  const saveLog = async (name, details) => {
    // [Logic Hidden]
    // Save to node backend instead of localstorage
  // ===== HELPER FUNCTIONS =====
  /**
   * Create fallback workout plan if backend returns empty
   */
  const createFallbackPlan = () => {
    // [Logic Hidden]
  /**
   * Normalize plan to always have 7 days
   */
  const normalizeToSevenDays = (plan) => {
    // [Logic Hidden]
    // Pad with rest days if less than 7
    // Trim if more than 7
    // Track if component is mounted to prevent state updates after unmount
    const fetchWorkoutPlan = async (forceRefresh = false, profileData = null) => {
      // [Logic Hidden]
        // ✅ FIX: Use fresh profile from API instead of stale localStorage.user
        // localStorage.user only has {id, name, email} — no fitness profile fields!
        // **Check if cached plan exists and is not expired**
          // Cache valid for 24 hours
        // **Fetch new plan from server using FULL profile data**
        // ===== VALIDATE RESPONSE STRUCTURE =====
        // Backend returns: { success: true, workout: [...], exercises_count: number }
        // Check for workout array (could be at response.data.workout OR response.data.data.workout)
          // ✅ Correct structure: { success: true, workout: [...] }
          // Fallback for alternative structure: { success: true, data: { weekly_plan: [...] } }
        // Validate workout plan is not empty
          // Don't throw - use fallback
        // Validate plan has 7 days
          // **Cache the new plan**
        // Classify error for better user feedback
          // Network error - backend not reachable
    const checkAndFetchPlan = async () => {
      // [Logic Hidden]
        // Always fetch profile first to get latest data
        // Normalize arrays for comparison (sort to ensure consistent order)
        const normalizeForComparison = (obj) => {
          // [Logic Hidden]
          // ✅ FIX: Pass the fresh profile to fetchWorkoutPlan
    const fetchHistory = async () => {
      // [Logic Hidden]
    // Cleanup function to prevent state updates on unmount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  const normalizeWeeklyPlan = (rawPlan = []) => {
    // [Logic Hidden]
    // Create a map from the backend response
    // Map all 7 days, filling missing ones with placeholders
  const handleDayClick = (dayIdx) => {
    // [Logic Hidden]
  const startCamera = async () => {
    // [Logic Hidden]
      // Optimized camera constraints for smoother MediaPipe processing
  const stopCamera = () => {
    // [Logic Hidden]
  const handleExerciseSelect = (ex) => {
    // [Logic Hidden]
  const handleExerciseComplete = () => {
    // [Logic Hidden]
     const currentIndex = activeDay.exercises.findIndex(e => e.name === activeExercise.name);
     if (currentIndex >= 0 && currentIndex < activeDay.exercises.length - 1) {
       // [Logic Hidden]
  const handleRepUpdate = (repsCount) => {
    // [Logic Hidden]
  const finishSession = async () => {
    // [Logic Hidden]
      // ✅ FIX: Sync workout_completed to backend trends so Dashboard streak works
  const handleLogout = () => {
    // [Logic Hidden]
```

## frontend/src/services/profileApi.js
```javascript
// API service for profile updates with plan regeneration
// Points to Python backend (port 8000) where regeneration logic exists
// Use environment variable for consistency with rest of app
const API_BASE_URL = import.meta.env.VITE_PYTHON_API_URL || 'http://localhost:8000';
// Request timeout in milliseconds
const REQUEST_TIMEOUT = 15000;
/**
 * Get auth token from localStorage
 */
const getAuthToken = () => {
  // [Logic Hidden]
/**
 * Get headers with auth token
 */
const getHeaders = () => {
  // [Logic Hidden]
/**
 * Create axios instance with custom configuration
 */
/**
 * Request interceptor - Attach auth token
 */
/**
 * Response interceptor - Global error handling
 */
    // Log error for debugging
/**
 * Classify error types for better handling
 */
export const classifyError = (error) => {
  // [Logic Hidden]
  // Network error (no response from server)
  // HTTP error responses
/**
 * Update user profile and regenerate workout/meal plans if needed
 * Uses the safe endpoint with graceful degradation
 */
export const updateProfileWithRegeneration = async (profileData, options = {}) => {
  // [Logic Hidden]
      // Health check before making the request (optional, can be disabled)
          // Continue anyway - backend might still respond
      // Retry delay (exponential backoff)
      // Make the request with timeout
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      const response = await apiClient.put('/profile/update-safe', profileData, {
        // [Logic Hidden]
      // Don't retry for certain error types
      // If this was the last attempt, break and throw
  // All retries failed, throw formatted error
/**
 * Alternative endpoint for basic profile update (no regeneration)
 */
export const updateProfileBasic = async (profileData) => {
  // [Logic Hidden]
/**
 * Get available profile endpoints from backend
 */
export const getProfileEndpoints = async () => {
  // [Logic Hidden]
/**
 * Check backend health
 */
export const checkBackendHealth = async () => {
  // [Logic Hidden]
```

## frontend/src/utils/googleAuth.js
```javascript
// Reusable Google Auth Utility Functions
// Common Google SDK loading function
export const loadGoogleSDK = (buttonId, onSuccess, onError) => {
  // [Logic Hidden]
    // Load Google SDK script
            // Use environment variable instead of hardcoded ID
                // Show visible error in the button container
// Common Google login initialization function
export const initializeGoogleLogin = (containerId, onSuccessCallback, onErrorCallback, clientIdOverride = null) => {
  // [Logic Hidden]
            // Try both Vite and React App environment variable names
            // Use override if provided, otherwise use environment variable
                // Show a warning if the client ID is not configured
            // Validate client ID format (should end with '.googleusercontent.com')
            // Check if the button container exists before rendering
                // Clear the container first to ensure no conflicts
                // Apply custom styling after the button is rendered
            // Show fallback button if initialization fails
```

## frontend/src/utils/storage.js
```javascript
/**
 * Centralized localStorage management
 * Provides type-safe key constants and error-handling wrappers
 */
  // Activity & History
  // User Profile
  // Streak & Progress
  // Daily Tracking
  // Workout Sessions
  // Water & Sleep
  // Nutrition Cache
  // Profile Change Tracking
  // Cached Data
  // Notification Tracking
  // Dynamic notification keys (helper function below)
/**
 * Returns a formatted date string (YYYY-MM-DD) strictly in Indian Standard Time (Asia/Kolkata)
 */
export const getLocalDateStr = (d = new Date()) => {
  // [Logic Hidden]
  const year = parts.find(p => p.type === 'year').value;
  const month = parts.find(p => p.type === 'month').value;
  const day = parts.find(p => p.type === 'day').value;
  return `${year}-${month}-${day}`;
    // [Logic Hidden]
  const month = parts.find(p => p.type === 'month').value;
  const day = parts.find(p => p.type === 'day').value;
  return `${year}-${month}-${day}`;
    // [Logic Hidden]
  const day = parts.find(p => p.type === 'day').value;
  return `${year}-${month}-${day}`;
    // [Logic Hidden]
/**
 * Returns today's date in YYYY-MM-DD format strictly in Indian Standard Time (Asia/Kolkata)
 */
export const getTodayStr = () => getLocalDateStr();
/**
 * Safe retrieval from localStorage with error handling
 * @param {string} key - Storage key
  // [Logic Hidden]
/**
 * Safe retrieval from localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if key not found
 * @returns {any} Retrieved value or defaultValue
 */
export const getFromStorage = (key, defaultValue = null) => {
  // [Logic Hidden]
    // Try to parse as JSON, otherwise return as string
      // If parsing fails, return the raw string (for simple values)
/**
 * Safe storage to localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} value - Value to store (will be JSON stringified)
 * @returns {boolean} Success status
 */
export const setToStorage = (key, value) => {
  // [Logic Hidden]
/**
 * Safe removal from localStorage
 * @param {string} key - Storage key to remove
 * @returns {boolean} Success status
 */
export const removeFromStorage = (key) => {
  // [Logic Hidden]
/**
 * Clear all localStorage data
 * @returns {boolean} Success status
 */
export const clearAllStorage = () => {
  // [Logic Hidden]
/**
 * Safe logout — removes auth-related and volatile session keys only.
 * Preserves non-sensitive cached data (nutrition plan, workout plan, etc.)
 * so a re-login restores state instantly without extra API calls.
 *
 * Call this INSTEAD of localStorage.clear() on logout.
 * @returns {boolean} Success status
 */
export const logoutSafe = () => {
  // [Logic Hidden]
    // Auth tokens
    // Volatile daily state that should reset on logout
      // Nutrition volatile keys
      // Cached plans (different user may have different profile)
    // Also clear any dynamic workout_done_* and notification_* keys
    // Clear sessionStorage (chat history etc.)
    // Fallback: nuclear clear if selective removal fails
/**
 * Get multiple values at once
 * @param {string[]} keys - Array of storage keys
 * @returns {object} Object with key-value pairs
 */
export const getMultipleFromStorage = (keys) => {
  // [Logic Hidden]
/**
 * Set multiple values at once
 * @param {object} entries - Object with key-value pairs
 * @returns {boolean} Success status (all or nothing)
 */
export const setMultipleToStorage = (entries) => {
  // [Logic Hidden]
/**
 * Check if a key exists in storage
 * @param {string} key - Storage key
 * @returns {boolean} True if key exists
 */
export const keyExistsInStorage = (key) => {
  // [Logic Hidden]
/**
 * Get storage size (approximate, in characters)
 * @returns {number} Total size of localStorage
 */
export const getStorageSize = () => {
  // [Logic Hidden]
```

## Bug Categories Mapping

### 1. Workout Engine
- ackend-python/app/workout_engine.py
- ackend-python/app/hybrid_volume_optimizer.py
- ackend-python/app/progression_engine.py

### 2. Media
- rontend/src/pages/Workout.jsx
- rontend/src/components/ExerciseCard.jsx (if exists)
- rontend/src/components/MediaViewer.jsx (if exists)

### 3. Meals
- ackend-python/app/meal_engine.py
- ackend-python/app/deterministic_meal_engine.py
- ackend-python/app/nutrition_intelligence.py
- rontend/src/pages/Meals.jsx

### 4. Gemini API
- ackend-python/app/gemini_service.py

### 5. Profile
- ackend-node/routes/profile.js
- ackend-node/routes/users.js
- ackend-node/models/User.js
- ackend-python/app/profile_change_detection.py
- rontend/src/pages/Profile.jsx

### 6. Persistence
- ackend-python/app/db.py
- ackend-node/server.js
- ackend-node/models/User.js
- rontend/src/services/api.js

### 7. Flickering
- rontend/src/App.jsx
- rontend/src/main.jsx
- rontend/src/api.js or Auth Context components