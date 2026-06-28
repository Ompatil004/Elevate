import requests
import json
try:
    resp = requests.get('https://raw.githubusercontent.com/justcalitme/exercisedb-json/main/exercises.json', timeout=15)
    data = resp.json()
    print("Fetched successfully. Entries:", len(data))
    if len(data) > 0:
        print(json.dumps(data[0], indent=2))
except Exception as e:
    print(e)
