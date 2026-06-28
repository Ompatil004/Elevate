import requests
try:
    r = requests.get('https://api.github.com/repos/wrkout/exercises.json/git/trees/master?recursive=1', timeout=5)
    data = r.json()
    if 'tree' in data:
        files = [t['path'] for t in data['tree'] if t['path'].endswith('.json') and 'exercises/' in t['path']]
        print(f"Found {len(files)} exercise json files in wrkout")
        if files:
            sample_url = f"https://raw.githubusercontent.com/wrkout/exercises.json/master/{files[0]}"
            print(f"Sample: {sample_url}")
            r2 = requests.get(sample_url)
            print(r2.text[:200])
except Exception as e:
    print(e)
