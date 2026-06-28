import requests
import json
try:
    print("Fetching Wger videos...")
    r = requests.get('https://wger.de/api/v2/video/?limit=1000', timeout=10)
    data = r.json()
    print(f"Total videos on Wger: {data.get('count', 0)}")
    if data.get('results'):
        print("Sample:", json.dumps(data['results'][0], indent=2))
except Exception as e:
    print("Error:", e)
