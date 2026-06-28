import requests
try:
    r = requests.get('https://api.github.com/repos/XZE3N/ExerciseGifDownloader/git/trees/master?recursive=1', timeout=5)
    data = r.json()
    if 'tree' in data:
        files = [t['path'] for t in data['tree'] if t['path'].endswith('.json')]
        for f in files:
            print(f"JSON: {f}")
            if 'exercise' in f.lower():
                url = f"https://raw.githubusercontent.com/XZE3N/ExerciseGifDownloader/master/{f}"
                print(f"Fetching {url}")
                r2 = requests.get(url)
                if r2.status_code == 200:
                    print(r2.text[:200])
except Exception as e:
    print(e)
