import base64
import urllib.request
import zlib

mermaid_code = """
classDiagram
    %% Apply custom styles
    classDef user fill:#2a3f94,stroke:#1a285e,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef engine fill:#7b43e8,stroke:#512ca8,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef workout fill:#d67600,stroke:#9c5600,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef meal fill:#db221d,stroke:#991713,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef tracking fill:#008d53,stroke:#006139,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef log fill:#255cef,stroke:#163a9c,stroke-width:2px,color:#ffffff,font-weight:bold;

    class User {
        -String userId
        -String name
        -int age
        -float weight_kg
        -float height_cm
        -String fitnessGoal
        +register() void
        +login() boolean
        +updateProfile() void
        +requestWorkout() WorkoutRoutine
    }
    
    class AIEngine {
        -String modelId
        -String version
        -boolean isTrained
        +loadModels() void
        +trainModel(Dataset data) void
        +predictWorkout(User user) WorkoutRoutine
        +predictNutrition(User user) MealPlan
    }
    
    class WorkoutRoutine {
        -String routineId
        -String targetMuscle
        -int predictedSets
        -int predictedReps
        -String intensityLevel
        +displayRoutine() void
        +startWorkout() void
        +markCompleted() void
    }
    
    class MealPlan {
        -String planId
        -int totalCalories
        -int proteinGrams
        -int carbsGrams
        -int fatGrams
        +displayMeals() void
        +updateMacros() void
    }
    
    class HealthLog {
        -String logId
        -Date date
        -int caloriesConsumed
        -int sleepScore
        -int hydrationLevel
        +addLog() void
        +getWeeklyAverage() float
    }
    
    class ProgressTracker {
        -String trackingId
        -int streakDays
        -float consistencyScore
        -float weightChange
        +calculateProgress() float
        +generateReport() String
    }

    User "1" --> "1..*" WorkoutRoutine : requests
    AIEngine "1" --> "*" WorkoutRoutine : generates
    AIEngine "1" --> "*" MealPlan : generates
    WorkoutRoutine "1" *-- "1" MealPlan : includes
    User "1" *-- "1" ProgressTracker : owns
    User "1" --> "*" HealthLog : creates
    ProgressTracker "1" o-- "*" HealthLog : analyzes

    class User user
    class AIEngine engine
    class WorkoutRoutine workout
    class MealPlan meal
    class ProgressTracker tracking
    class HealthLog log
"""

compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
url = f"https://kroki.io/mermaid/png/{encoded}"

print("Fetching UML Diagram...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open('uml_class_diagram.png', 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print("Successfully saved uml_class_diagram.png")
except Exception as e:
    print(f"Error: {e}")
