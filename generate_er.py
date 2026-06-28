import base64
import urllib.request
import zlib

def make_node(id, title, color, fields):
    rows = ""
    for field in fields:
        if field.startswith("[PK]"):
            rows += f"<b style='color:#d84315; font-size:15px;'>[PK]</b> <span style='font-size:15px;'>{field[4:]}</span><hr style='border:1px solid #ddd;margin:6px 0;'>"
        elif field.startswith("[FK]"):
            rows += f"<b style='color:#1d57e5; font-size:15px;'>[FK]</b> <span style='font-size:15px;'>{field[4:]}</span><br>"
        else:
            rows += f"<span style='color:{color}; font-size:18px;'>\u2022</span> <span style='font-size:15px;color:#333;'>{field}</span><br>"
            
    html = f"\"<table style='border-collapse:collapse;border:2px solid {color};'><tr><td bgcolor='{color}' style='background-color:{color};color:white;font-weight:bold;font-size:16px;padding:12px;text-align:center;width:240px;'>{title}</td></tr><tr><td bgcolor='#ffffff' style='background-color:white;color:black;padding:12px;text-align:left;'>{rows}</td></tr></table>\""
    return f"{id}[{html}]"

def lbl(text, color):
    return f"\"<table style='border-collapse:collapse;margin:0;padding:0;'><tr><td bgcolor='{color}' style='color:white;font-weight:bold;font-size:12px;padding:2px 6px;border:none;'>{text}</td></tr></table>\""

mermaid_code = f"""
graph LR
    classDef rel_blue fill:#fff,stroke:#2a3f94,stroke-width:2px,color:#2a3f94,font-weight:bold,font-size:14px;
    classDef rel_teal fill:#fff,stroke:#11987d,stroke-width:2px,color:#11987d,font-weight:bold,font-size:14px;
    classDef rel_orange fill:#fff,stroke:#d67600,stroke-width:2px,color:#d67600,font-weight:bold,font-size:14px;
    classDef rel_red fill:#fff,stroke:#db221d,stroke-width:2px,color:#db221d,font-weight:bold,font-size:14px;
    classDef rel_green fill:#fff,stroke:#008d53,stroke-width:2px,color:#008d53,font-weight:bold,font-size:14px;
    classDef rel_purple fill:#fff,stroke:#7b43e8,stroke-width:2px,color:#7b43e8,font-weight:bold,font-size:14px;
    classDef rel_blue2 fill:#fff,stroke:#255cef,stroke-width:2px,color:#255cef,font-weight:bold,font-size:14px;

    {make_node("USER", "USER", "#2a3f94", ["[PK] user_id", "age", "weight_kg", "height_cm", "gender", "goal", "experience_level"])}
    {make_node("DATASET", "KAGGLE_DATASET", "#11987d", ["[PK] record_id", "age", "weight", "height", "experience_level", "target_muscle", "sets_reps"])}
    {make_node("MODEL", "ELEVATE_AI_ENGINE", "#7b43e8", ["[PK] model_id", "XGBoost (Workout)", "XGBoost (Nutrition)", "Google Gemini (NLP)", "Scikit-Learn (Scaler)"])}
    
    {make_node("WORKOUT", "WORKOUT_ROUTINE", "#d67600", ["[PK] routine_id", "[FK] user_id", "target_muscle", "predicted_sets", "predicted_reps", "intensity_level"])}
    
    {make_node("MEAL", "MEAL_PLAN", "#db221d", ["[PK] plan_id", "[FK] routine_id", "total_calories", "protein_g", "carbs_g", "fat_g"])}
    {make_node("LOG", "DAILY_HEALTH_LOG", "#255cef", ["[PK] log_id", "[FK] plan_id", "calories_consumed", "protein_consumed", "sleep_score", "hydration_score"])}
    {make_node("TRACKING", "PROGRESS_TRACKING", "#008d53", ["[PK] tracking_id", "[FK] routine_id", "workout_completion", "streak_days", "consistency_score"])}

    R1{{Matches}}:::rel_blue
    R2{{Trains}}:::rel_teal
    R3{{Requests}}:::rel_orange
    R4{{Powered_By}}:::rel_purple
    R5{{Pairs_With}}:::rel_red
    R6{{Yields}}:::rel_green
    R7{{Tracked_Via}}:::rel_blue2

    USER ---|{lbl("1", "#2a3f94")}| R1
    R1 ---|{lbl("N", "#11987d")}| DATASET
    
    DATASET ---|{lbl("N", "#11987d")}| R2
    R2 ---|{lbl("1", "#7b43e8")}| MODEL

    USER ---|{lbl("1", "#2a3f94")}| R3
    R3 ---|{lbl("N", "#d67600")}| WORKOUT
    
    WORKOUT ---|{lbl("N", "#d67600")}| R4
    R4 ---|{lbl("1", "#7b43e8")}| MODEL

    WORKOUT ---|{lbl("1", "#d67600")}| R5
    R5 ---|{lbl("1", "#db221d")}| MEAL
    
    WORKOUT ---|{lbl("1", "#d67600")}| R6
    R6 ---|{lbl("1", "#008d53")}| TRACKING
    
    MEAL ---|{lbl("1", "#db221d")}| R7
    R7 ---|{lbl("N", "#255cef")}| LOG
"""

compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
url = f"https://kroki.io/mermaid/png/{encoded}"

print("Fetching ER Diagram...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open('er_diagram.png', 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print("Successfully saved er_diagram.png")
except Exception as e:
    print(f"Error: {e}")
