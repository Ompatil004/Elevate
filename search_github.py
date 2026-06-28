import requests
import json
import time

headers = {'Accept': 'application/vnd.github.v3+json'}
url = 'https://api.github.com/search/code?q=filename:exercises.json+"gifUrl"'
r = requests.get(url, headers=headers)
data = r.json()
if 'items' in data:
    for item in data['items'][:5]:
        repo = item['repository']['full_name']
        path = item['path']
        raw_url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
        print(f"Found: {raw_url}")
else:
    print(data)
