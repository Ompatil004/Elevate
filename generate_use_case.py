import base64
import urllib.request
import zlib

plantuml_code = """
@startuml
!theme plain
left to right direction
skinparam packageStyle rectangle

' Scale up the entire diagram resolution by 2x for ultra-sharp PPT rendering
scale 2

' Make the entire diagram background transparent
skinparam backgroundColor transparent

' Massive font sizes for PPT visibility
skinparam usecase {
  BackgroundColor #fdfdfd
  BorderColor #555555
  ArrowColor #333333
  FontSize 32
  FontName sans-serif
}
skinparam actor {
  BackgroundColor<<Primary>> #a9dfbf
  BackgroundColor<<Admin>> #f5b7b1
  BackgroundColor<<AI>> #d4b4f5
  BorderColor #333333
  FontSize 32
  FontName sans-serif
}
skinparam rectangle {
  BorderColor #000000
  FontSize 42
  FontStyle bold
  FontName sans-serif
}

' Define our Actors
actor "Registered User" as User <<Primary>>
actor "System Administrator" as Admin <<Admin>>
actor "Elevate AI Engine" as AI <<AI>>

' Define the System Boundary
rectangle "Elevate System" {
  usecase "Register / Login Account" as UC1
  usecase "Update Biometrics\\n(Sleep/Water)" as UC2
  usecase "View Workout & Meal\\nDashboard" as UC3
  usecase "Generate Personalized\\nML Plan" as UC4
  usecase "Execute Real-time\\nCamera Workout" as UC5
  
  usecase "View System Logs" as UC6
  usecase "Suspend Malicious Users" as UC7
}

' Connect Primary Actors (Left Side)
User -[thickness=3]-> UC1
User -[thickness=3]-> UC2
User -[thickness=3]-> UC3
User -[thickness=3]-> UC4
User -[thickness=3]-> UC5

Admin -[thickness=3]-> UC6
Admin -[thickness=3]-> UC7

' Connect Secondary Actor (Right Side)
UC4 <-[thickness=3]- AI
UC5 <-[thickness=3]- AI
@enduml
"""

compressed = zlib.compress(plantuml_code.encode('utf-8'), 9)
encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
url = f"https://kroki.io/plantuml/png/{encoded}"

print("Fetching UML Use Case Diagram...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open('uml_use_case_diagram.png', 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print("Successfully saved uml_use_case_diagram.png")
except Exception as e:
    print(f"Error: {e}")
