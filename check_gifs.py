import pandas as pd
df = pd.read_csv('backend-python/data/exercises_processed_repaired.csv')
home_eq = {'body weight', 'bodyweight', 'dumbbell', 'band', 'resistance band', 'none', 'no equipment'}
df_home = df[df['Equipment'].astype(str).str.lower().str.strip().isin(home_eq)]

def has_gif(row):
    urls = [str(row.get('Video_URL', '')), str(row.get('Wger_Image_URL', '')), str(row.get('Media_URL', ''))]
    for url in urls:
        url = url.lower()
        if 'http' in url and (url.endswith('.gif') or 'giphy' in url or 'gfycat' in url):
            return True
    return False

df_home['has_gif'] = df_home.apply(has_gif, axis=1)
print(f"Total home exercises: {len(df_home)}")
print(f"Has GIF: {df_home['has_gif'].sum()}")
print(f"Missing GIF: {len(df_home) - df_home['has_gif'].sum()}")
