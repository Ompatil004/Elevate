import base64
import urllib.request
import zlib

mermaid_code = """
graph TD
    classDef user fill:#ede7f6,stroke:#7e57c2,stroke-width:2px,color:#000;
    classDef presentation fill:#1e88e5,stroke:#0d47a1,stroke-width:2px,color:#fff;
    classDef logic fill:#00897b,stroke:#004d40,stroke-width:2px,color:#fff;
    classDef ml fill:#e65100,stroke:#bf360c,stroke-width:2px,color:#fff;
    classDef db fill:#3949ab,stroke:#1a237e,stroke-width:2px,color:#fff;
    classDef external fill:#37474f,stroke:#263238,stroke-width:2px,color:#fff;

    style PresentationLayer fill:#fffde7,stroke:#cddc39,stroke-width:1px,stroke-dasharray: 5 5
    style LogicLayer fill:#fffde7,stroke:#cddc39,stroke-width:1px,stroke-dasharray: 5 5
    style MLLayer fill:#fffde7,stroke:#cddc39,stroke-width:1px,stroke-dasharray: 5 5
    style StorageLayer fill:#fffde7,stroke:#cddc39,stroke-width:1px,stroke-dasharray: 5 5

    %% 1. Top Level
    Users(["Users (Fitness Enthusiasts)"]):::user

    %% 2. Presentation Layer
    subgraph PresentationLayer ["Presentation Layer (React + Vite)"]
        UI_Prof["User Profile<br>& Auth"]:::presentation
        UI_Dash["Dashboards<br>& Workouts"]:::presentation
        UI_Cam["MediaPipe<br>Camera View"]:::presentation
    end

    Users -- "Interacts" --> UI_Dash

    %% 3. Logic Layer
    subgraph LogicLayer ["Logic Layer (Node.js + Express)"]
        L_API["API Routes<br>(Auth, Data, Plans)"]:::logic
        L_Core["Core Services<br>(Analytics, Context)"]:::logic
        L_API --> L_Core
    end

    UI_Prof -- "Uploads Data" --> L_API
    UI_Dash -- "Requests Insights" --> L_API
    UI_Cam -- "Pose Metrics" --> L_API

    %% 4. Bottom Layers (Side-by-Side)
    subgraph MLLayer ["Machine Learning Layer (FastAPI)"]
        M_API["ML API Endpoints<br>(/predict, /coach)"]:::ml
        M_Work["Workout AI Model<br>(XGBoost)"]:::ml
        M_Nut["Nutrition AI Model<br>(XGBoost)"]:::ml
        
        M_API -- "Predicts Sets/Reps" --> M_Work
        M_API -- "Predicts Macros" --> M_Nut
        
        M_Work ~~~ M_Nut
    end

    subgraph StorageLayer ["Storage & External APIs"]
        S_DB[("MongoDB<br>(Users, Datasets)")]:::db
        S_Ext(("Google Gemini<br>API")):::external
        %% Force side-by-side or stacked in storage
        S_DB ~~~ S_Ext
    end

    L_Core -- "Triggers Training<br>& Prediction" --> M_API
    L_Core -- "Read / Write" --> S_DB
    
    %% Cross-layer call
    M_API -- "Generates NLP" --> S_Ext
"""

compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
url = f"https://kroki.io/mermaid/png/{encoded}"

print(f"Fetching from {url}")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open('system_architecture.png', 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print("Successfully saved structured layered system_architecture.png")
except Exception as e:
    print(f"Error: {e}")
