import requests
import json
resp = requests.get('https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json', timeout=15)
data = resp.json()
print(json.dumps(data[0], indent=2))
