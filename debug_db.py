import pandas as pd
import requests

try:
    resp = requests.get('https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json', timeout=15)
    db_data = resp.json()
    print("Remote DB sample:")
    for ex in db_data[:3]:
        print(ex.get('name'))
except Exception as e:
    print(e)
