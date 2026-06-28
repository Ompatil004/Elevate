import base64
import urllib.request
import zlib

def get_table(name, attrs, methods):
    attrs_html = "<br>".join([f"- {a}" for a in attrs])
    methods_html = "<br>".join([f"- {m}" for m in methods])
    # GIGANTIC font sizes for PPT visibility: title to 48px, text to 36px. Expanded width to 900px to fit.
    return f"\"<table style='border-collapse:collapse;border:3px solid black;background:white;width:900px;font-family:sans-serif;'><tr style='border-bottom:3px solid black;'><td bgcolor='white' style='text-align:center;font-weight:bold;padding:24px;font-size:48px;color:black;'>{name}</td></tr><tr style='border-bottom:3px solid black;'><td bgcolor='white' style='text-align:left;padding:24px;font-size:36px;color:black;line-height:1.5;'>{attrs_html}</td></tr><tr><td bgcolor='white' style='text-align:left;padding:24px;font-size:36px;color:black;line-height:1.5;'>{methods_html}</td></tr></table>\""

react_node = get_table("ReactFrontend", 
                       ["Tailwind CSS: UserInterface:", "Recharts: DataVisualization:"],
                       ["submitUserProfile()", "requestWorkoutPlan()", "viewProgressTracking()"])

express_node = get_table("NodeExpressBackend",
                         ["JWT AuthMiddleware:", "WorkoutController", "NutritionController"],
                         ["validateUserProfile()", "calculateFitnessGoals()"])

mongo_node = get_table("MongoDBDatabase",
                       ["UserSchema", "RoutineSchema"],
                       ["storeFitnessData()", "retrieveWorkoutHistory()"])

fastapi_node = get_table("FastAPIMicroservice",
                         ["Gemini_NLP_Logic", "XGBoost_Engine"],
                         ["trainModel()", "predictRoutine()", "evaluateAccuracy()"])

mermaid_code = f"""
graph TD
    classDef plain fill:none,stroke:none;
    
    RF[{react_node}]:::plain
    NE[{express_node}]:::plain
    MD[{mongo_node}]:::plain
    FA[{fastapi_node}]:::plain

    %% Gigantic edge label font size to 36px with larger padding
    RF -->|"<div style='font-size:36px;color:black;background:white;padding:12px;font-weight:bold;'>REST API (HTTP/JSON)</div>"| NE
    NE -->|"<div style='font-size:36px;color:black;background:white;padding:12px;font-weight:bold;'>Mongoose ORM</div>"| MD
    NE -->|"<div style='font-size:36px;color:black;background:white;padding:12px;font-weight:bold;'>HTTP POST (Model Trigger)</div>"| FA

    %% Even thicker lines to match the scaled-up boxes and text
    linkStyle 0 stroke:#007bff,stroke-width:8px;
    linkStyle 1 stroke:#007bff,stroke-width:8px;
    linkStyle 2 stroke:#007bff,stroke-width:8px;
"""

compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
url = f"https://kroki.io/mermaid/png/{encoded}"

print("Fetching UML Component Diagram...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open('uml_component_diagram.png', 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print("Successfully saved uml_component_diagram.png")
except Exception as e:
    print(f"Error: {e}")
