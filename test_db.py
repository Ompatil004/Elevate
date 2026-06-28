import requests
urls = [
    'https://raw.githubusercontent.com/alr-lab/test-exercises/master/exercises.json',
    'https://raw.githubusercontent.com/skylake/exercisedb/master/exercises.json',
    'https://raw.githubusercontent.com/nabil6391/exercisedb/main/exercises.json'
]
for url in urls:
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data and 'gifUrl' in data[0]:
                print(f"FOUND: {url}")
                break
            else:
                print(f"No gifUrl in {url}")
    except:
        pass
