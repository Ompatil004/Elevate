import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_exercises_data(file_path):
    """
    Analyze exercises data for quality issues and insights
    """
    print("="*60)
    print("EXERCISES DATA ANALYSIS")
    print("="*60)
    
    try:
        df = pd.read_csv(file_path)
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print()
        
        # 1. Missing Values Analysis
        print("1. MISSING VALUES ANALYSIS")
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        missing_df = pd.DataFrame({
            'Missing Count': missing_data,
            'Percentage': missing_percent
        })
        print(missing_df[missing_df['Missing Count'] > 0])
        print()
        
        # 2. Duplicate Analysis
        print("2. DUPLICATE ANALYSIS")
        duplicates = df.duplicated().sum()
        print(f"Total duplicate rows: {duplicates}")
        if duplicates > 0:
            print("Duplicate rows detected - consider removing or investigating")
        print()
        
        # 3. Data Types and Consistency
        print("3. DATA TYPES AND CONSISTENCY")
        print(df.dtypes)
        print()
        
        # 4. Categorical Variable Analysis
        print("4. CATEGORICAL VARIABLES ANALYSIS")
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            print(f"\n{col.upper()} Distribution:")
            value_counts = df[col].value_counts()
            print(value_counts.head(10))  # Top 10 values
            print(f"Unique values: {df[col].nunique()}")
            
            # Check for inconsistent entries (potential typos)
            if df[col].dtype == 'object':
                unique_vals = df[col].unique()
                suspicious_entries = [val for val in unique_vals if pd.notna(val) and 
                                    (isinstance(val, str) and (val.strip() != val or val.lower() != val))]
                if suspicious_entries:
                    print(f"Suspicious entries in {col}: {suspicious_entries[:5]}")
        print()
        
        # 5. Numerical Variables Summary
        print("5. NUMERICAL VARIABLES SUMMARY")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(df[numeric_cols].describe())
        else:
            print("No numerical columns found")
        print()
        
        # 6. Equipment Analysis
        print("6. EQUIPMENT ANALYSIS")
        if 'equipment' in df.columns:
            equipment_dist = df['equipment'].value_counts()
            print(f"Equipment types: {len(equipment_dist)}")
            print("Top equipment types:")
            print(equipment_dist.head(10))
        print()
        
        # 7. Target Muscle Analysis
        print("7. TARGET MUSCLE ANALYSIS")
        if 'Target_Muscle' in df.columns:
            muscle_dist = df['Target_Muscle'].value_counts()
            print(f"Muscle groups: {len(muscle_dist)}")
            print("Top muscle groups:")
            print(muscle_dist.head(10))
        print()
        
        # 8. Difficulty Level Analysis
        print("8. DIFFICULTY LEVEL ANALYSIS")
        if 'Difficulty' in df.columns:
            difficulty_dist = df['Difficulty'].value_counts()
            print("Difficulty distribution:")
            print(difficulty_dist)
        print()
        
        # 9. Potential Issues Summary
        print("9. POTENTIAL ISSUES IDENTIFIED")
        issues = []
        
        if 'equipment' in df.columns:
            if df['equipment'].isnull().sum() > len(df) * 0.1:  # More than 10% missing
                issues.append("High percentage of missing equipment data")
                
        if 'Target_Muscle' in df.columns:
            if df['Target_Muscle'].isnull().sum() > len(df) * 0.1:
                issues.append("High percentage of missing target muscle data")
                
        if 'Difficulty' in df.columns:
            if df['Difficulty'].nunique() < 2:
                issues.append("Insufficient variation in difficulty levels")
        
        if 'Name' in df.columns:
            if df['Name'].duplicated().sum() > 0:
                issues.append("Duplicate exercise names detected")
        
        if issues:
            for issue in issues:
                print(f"- {issue}")
        else:
            print("No major issues detected in exercises data")
        
        print()
        return df
        
    except Exception as e:
        print(f"Error analyzing exercises data: {str(e)}")
        return None

def analyze_nutrition_data(file_path):
    """
    Analyze nutrition data for quality issues and insights
    """
    print("="*60)
    print("NUTRITION DATA ANALYSIS")
    print("="*60)
    
    try:
        df = pd.read_csv(file_path)
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print()
        
        # 1. Missing Values Analysis
        print("1. MISSING VALUES ANALYSIS")
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        missing_df = pd.DataFrame({
            'Missing Count': missing_data,
            'Percentage': missing_percent
        })
        print(missing_df[missing_df['Missing Count'] > 0])
        print()
        
        # 2. Duplicate Analysis
        print("2. DUPLICATE ANALYSIS")
        duplicates = df.duplicated().sum()
        print(f"Total duplicate rows: {duplicates}")
        if duplicates > 0:
            print("Duplicate rows detected - consider removing or investigating")
        print()
        
        # 3. Data Types and Consistency
        print("3. DATA TYPES AND CONSISTENCY")
        print(df.dtypes)
        print()
        
        # 4. Categorical Variable Analysis
        print("4. CATEGORICAL VARIABLES ANALYSIS")
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            print(f"\n{col.upper()} Distribution:")
            value_counts = df[col].value_counts()
            print(value_counts.head(10))
            print(f"Unique values: {df[col].nunique()}")
        print()
        
        # 5. Nutritional Values Analysis
        print("5. NUTRITIONAL VALUES ANALYSIS")
        nutritional_cols = ['calories', 'protein', 'carbohydrate', 'total_fat', 'Carbs', 'Protein', 'Fats', 'Calories']
        available_nutritional = [col for col in nutritional_cols if col in df.columns]
        
        if available_nutritional:
            nutri_df = df[available_nutritional].select_dtypes(include=[np.number])
            if not nutri_df.empty:
                print("Nutritional values summary:")
                print(nutri_df.describe())
                
                # Check for negative values (invalid)
                for col in nutri_df.columns:
                    neg_vals = (nutri_df[col] < 0).sum()
                    if neg_vals > 0:
                        print(f"WARNING: {neg_vals} negative values found in {col}")
                        
                # Check for extremely high values (potential outliers)
                for col in nutri_df.columns:
                    Q3 = nutri_df[col].quantile(0.75)
                    Q1 = nutri_df[col].quantile(0.25)
                    IQR = Q3 - Q1
                    upper_bound = Q3 + 3 * IQR  # Using 3*IQR for extreme outliers
                    extreme_outliers = (nutri_df[col] > upper_bound).sum()
                    if extreme_outliers > 0:
                        print(f"WARNING: {extreme_outliers} extreme outliers found in {col} (> {upper_bound:.2f})")
        else:
            print("No standard nutritional columns found")
        print()
        
        # 6. Meal Type Analysis
        print("6. MEAL TYPE ANALYSIS")
        meal_type_cols = ['Type', 'type']
        meal_col = None
        for col in meal_type_cols:
            if col in df.columns:
                meal_col = col
                break
                
        if meal_col:
            meal_dist = df[meal_col].value_counts()
            print(f"Meal types: {len(meal_dist)}")
            print("Meal type distribution:")
            print(meal_dist)
        else:
            print("No meal type column found")
        print()
        
        # 7. Dietary Tags Analysis
        print("7. DIETARY TAGS ANALYSIS")
        tag_cols = ['Tags', 'dietary_tags', 'dietary_preference']
        for col in tag_cols:
            if col in df.columns:
                tag_dist = df[col].value_counts()
                print(f"{col} distribution:")
                print(tag_dist.head(10))
        print()
        
        # 8. Potential Issues Summary
        print("8. POTENTIAL ISSUES IDENTIFIED")
        issues = []
        
        if 'calories' in df.columns or 'Calories' in df.columns:
            cal_col = 'calories' if 'calories' in df.columns else 'Calories'
            zero_cal = (df[cal_col] == 0).sum()
            if zero_cal > len(df) * 0.5:  # More than 50% have zero calories
                issues.append(f"High percentage ({zero_cal/len(df)*100:.1f}%) of zero calorie entries")
        
        if 'protein' in df.columns or 'Protein' in df.columns:
            prot_col = 'protein' if 'protein' in df.columns else 'Protein'
            high_prot = (df[prot_col] > 100).sum()  # Unusually high protein content
            if high_prot > 0:
                issues.append(f"{high_prot} entries with unusually high protein content (>100g)")
        
        if issues:
            for issue in issues:
                print(f"- {issue}")
        else:
            print("No major issues detected in nutrition data")
        
        print()
        return df
        
    except Exception as e:
        print(f"Error analyzing nutrition data: {str(e)}")
        return None

def analyze_class_imbalance(df, column_name):
    """
    Analyze class imbalance for a categorical column
    """
    if column_name not in df.columns:
        print(f"Column '{column_name}' not found in dataset")
        return
    
    value_counts = df[column_name].value_counts()
    total_count = len(df)
    
    print(f"\nCLASS IMBALANCE ANALYSIS FOR '{column_name}':")
    print("-" * 50)
    
    for value, count in value_counts.items():
        percentage = (count / total_count) * 100
        print(f"{value}: {count} ({percentage:.2f}%)")
        
        # Flag highly imbalanced classes (less than 5% or more than 70%)
        if percentage < 5:
            print(f"    WARNING: '{value}' class is significantly underrepresented (<5%)")
        elif percentage > 70:
            print(f"    WARNING: '{value}' class dominates the dataset (>70%)")
    
    print()


def analyze_feature_gaps(user_profile_example=None):
    """
    Analyze potential gaps in feature representation
    """
    print("="*60)
    print("FEATURE GAP ANALYSIS")
    print("="*60)

    print("Analyzing potential gaps between user profile features and dataset features...")
    print()

    # Define expected user profile features
    expected_user_features = [
        'age', 'weight', 'height', 'gender', 'fitness_level',
        'goal', 'experience', 'equipment', 'body_issues',
        'days_per_week', 'dietary_preference', 'allergies', 'activity_level'
    ]

    print("Expected user profile features:")
    for feat in expected_user_features:
        print(f"- {feat}")
    print()

    # Potential gaps in current datasets
    print("POTENTIAL FEATURE GAPS:")
    gaps = [
        "Age-appropriate exercise scaling not directly represented in exercises data",
        "Gender-specific exercise recommendations not explicitly modeled",
        "User experience progression path not clearly defined in data",
        "Equipment availability matching could be improved",
        "Injury prevention logic needs stronger integration",
        "Metabolic rate calculation not directly tied to nutrition data",
        "User preference learning not captured in current datasets",
        "Temporal patterns (time of day, seasonality) not considered"
    ]

    for gap in gaps:
        print(f"- {gap}")
    print()

    # Recommend new columns to add
    print("RECOMMENDED NEW COLUMNS TO ADD:")
    new_columns = [
        "age_group (for age-appropriate recommendations)",
        "gender_specific (for gender-specific exercises)",
        "experience_progression_path (for progression tracking)",
        "equipment_availability_score (for equipment matching)",
        "injury_risk_score (for injury prevention)",
        "metabolic_efficiency (for metabolic rate calculation)",
        "preference_score (for preference learning)",
        "seasonal_factor (for temporal patterns)"
    ]

    for col in new_columns:
        print(f"- {col}")
    print()

def generate_comprehensive_report(exercises_df, nutrition_df):
    """
    Generate a comprehensive health report
    """
    print("="*60)
    print("COMPREHENSIVE DATA HEALTH REPORT")
    print("="*60)
    print(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if exercises_df is not None:
        print("EXERCISES DATASET SUMMARY:")
        print(f"- Total exercises: {len(exercises_df)}")
        print(f"- Total features: {len(exercises_df.columns)}")
        print(f"- Missing data percentage: {(exercises_df.isnull().sum().sum() / (len(exercises_df) * len(exercises_df.columns))) * 100:.2f}%")
        print(f"- Memory usage: {exercises_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print()
    
    if nutrition_df is not None:
        print("NUTRITION DATASET SUMMARY:")
        print(f"- Total food items: {len(nutrition_df)}")
        print(f"- Total features: {len(nutrition_df.columns)}")
        print(f"- Missing data percentage: {(nutrition_df.isnull().sum().sum() / (len(nutrition_df) * len(nutrition_df.columns))) * 100:.2f}%")
        print(f"- Memory usage: {nutrition_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print()
    
    print("RECOMMENDATIONS FOR MODEL IMPROVEMENT:")
    recommendations = [
        "1. Implement feature engineering to create user-exercise compatibility scores",
        "2. Develop nutritional density calculations for better food recommendations",
        "3. Create exercise progression pathways based on difficulty and user level",
        "4. Add seasonal/temporal features for better personalization",
        "5. Implement user feedback loops to improve recommendation accuracy",
        "6. Create synthetic features combining multiple data points for better predictions",
        "7. Add safety constraints to prevent inappropriate exercise recommendations",
        "8. Implement nutritional balance algorithms for meal planning"
    ]
    
    for rec in recommendations:
        print(rec)
    print()
    
    print("INTERPRETATION GUIDE:")
    interpretation = [
        "High missing data percentages (>10%) may indicate data quality issues",
        "Duplicate entries should be investigated and removed if appropriate",
        "Outliers in nutritional data may indicate data entry errors",
        "Limited variation in categorical variables may reduce model effectiveness",
        "Feature gaps can lead to poor personalization and recommendations",
        "Memory usage should be monitored for performance optimization"
    ]
    
    for interp in interpretation:
        print(f"- {interp}")

def generate_data_cleaning_strategy(exercises_df, nutrition_df):
    """
    Generate a data cleaning strategy based on identified issues
    """
    print("="*60)
    print("DATA CLEANING STRATEGY")
    print("="*60)
    
    print("Based on the analysis, here is the recommended data cleaning strategy:\n")
    
    strategies = [
        "1. Handle missing values:",
        "   - For exercises: Fill missing 'Target_Muscle' with 'General' if not available",
        "   - For exercises: Fill missing 'equipment' with 'Body Weight' as default",
        "   - For nutrition: Fill missing nutritional values with column means",
        "",
        "2. Remove or merge duplicate entries:",
        "   - Identify and remove exact duplicate rows",
        "   - For near-duplicates with slight variations, standardize the entries",
        "",
        "3. Standardize categorical values:",
        "   - Normalize equipment names ('Dumbell' → 'Dumbbell', 'dumb bell' → 'Dumbbell')",
        "   - Normalize target muscle groups ('Chest ' → 'Chest', 'chest' → 'Chest')",
        "   - Normalize difficulty levels ('beginner' → 'Beginner', 'BEG' → 'Beginner')",
        "",
        "4. Correct inconsistent units:",
        "   - Ensure all weights are in consistent units (grams, kg, etc.)",
        "   - Standardize measurement formats across the dataset",
        "",
        "5. Address outliers:",
        "   - Cap extreme nutritional values at reasonable thresholds",
        "   - Investigate and validate outlier exercise durations or intensities",
        "",
        "6. Validate data types:",
        "   - Ensure numeric columns contain only numeric values",
        "   - Convert incorrectly typed columns to appropriate data types",
        "",
        "7. Enforce data integrity:",
        "   - Add validation rules for minimum/maximum acceptable values",
        "   - Create constraints to prevent invalid combinations of values"
    ]
    
    for strategy in strategies:
        print(strategy)
    print()

def main():
    """
    Main function to run the complete analysis
    """
    from pathlib import Path

    # BUG-P9 fix: use __file__-relative paths so this script works regardless
    # of the current working directory. Previously used hardcoded relative paths
    # like 'backend-python/data/...' which broke when run from any other directory.
    _script_dir = Path(__file__).resolve().parent
    _data_dir = _script_dir.parent / 'data'

    print("ELEVATE FITNESS APPLICATION - DATA HEALTH ANALYSIS")
    print("=" * 60)

    # Analyze exercises data
    exercises_df = analyze_exercises_data(str(_data_dir / 'exercises_processed.csv'))

    # Analyze nutrition data
    nutrition_df = analyze_nutrition_data(str(_data_dir / 'nutrition_processed.csv'))

    # Perform class imbalance analysis if dataframes exist
    if exercises_df is not None:
        print("PERFORMING CLASS IMBALANCE ANALYSIS ON EXERCISES DATA...")
        # Common categorical columns in exercises data
        exercise_categorical_cols = ['Difficulty', 'Target_Muscle', 'equipment', 'Name']
        for col in exercise_categorical_cols:
            if col in exercises_df.columns:
                analyze_class_imbalance(exercises_df, col)

    if nutrition_df is not None:
        print("PERFORMING CLASS IMBALANCE ANALYSIS ON NUTRITION DATA...")
        # Common categorical columns in nutrition data
        nutrition_categorical_cols = ['Type', 'Tags', 'Name']
        for col in nutrition_categorical_cols:
            if col in nutrition_df.columns:
                analyze_class_imbalance(nutrition_df, col)

    # Analyze feature gaps
    analyze_feature_gaps()

    # Generate data cleaning strategy
    generate_data_cleaning_strategy(exercises_df, nutrition_df)

    # Generate comprehensive report
    generate_comprehensive_report(exercises_df, nutrition_df)

    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("Review the findings above to identify areas for improvement")
    print("in your model training and data preparation process.")


if __name__ == "__main__":
    main()