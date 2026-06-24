import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'nutrition_production_final_v2.csv')
CLEAN_CSV_PATH = os.path.join(BASE_DIR, 'data', 'nutrition_production_final_v3.csv')

def run_purge():
    print("Starting Final Dietary Suitability Audit...")
    df = pd.read_csv(CSV_PATH)
    initial_count = len(df)
    
    # We must be careful with 'kheer' to not match 'kheere' (cucumber). 
    # We will use word boundaries for short/ambiguous words
    short_words = ['kheer', 'cake', 'swan', 'donut', 'peda', 'candy', 'syrup']
    long_words = [
        'rasgulla', 'rasmalai', 'jalebi', 'ladoo', 'payasam', 'halwa', 'barfi', 
        'mysore pak', 'gulab jamun', 'cham cham', 'sandesh', 'kalakand', 'rabri', 
        'shrikhand', 'malpua', 'imarti', 'balushahi', 'milk cake', 'soan papdi', 
        'chocolate', 'ice cream', 'pudding', 'custard', 'pastry', 'brownie', 
        'muffin', 'cupcake', 'cookie', 'dessert', 'sweet bakery',
        'confectionery', 'frozen dessert', 'butterscotch', 'squash', 'choux'
    ]
    
    patterns = []
    for w in short_words:
        patterns.append(r'\b' + re.escape(w) + r'\b')
    for w in long_words:
        patterns.append(re.escape(w))
    
    combined_pattern = re.compile('|'.join(patterns), re.IGNORECASE)
    
    deleted_rows = []
    
    def is_unhealthy(name):
        return bool(combined_pattern.search(str(name)))
        
    df['is_unhealthy'] = df['food_name'].apply(is_unhealthy)
    
    deleted_df = df[df['is_unhealthy'] == True]
    
    # Build report
    for i, row in deleted_df.iterrows():
        name = row['food_name']
        # find the matched word for the reason
        match = combined_pattern.search(str(name).lower())
        reason = f"Matches unhealthy pattern: '{match.group()}'" if match else "Unhealthy"
        deleted_rows.append((name, reason))
        
    # Drop rows
    df = df[df['is_unhealthy'] == False]
    df = df.drop(columns=['is_unhealthy'])
    
    final_count = len(df)
    
    df.to_csv(CLEAN_CSV_PATH, index=False)
    
    print("=" * 60)
    print("FINAL DIETARY SUITABILITY AUDIT REPORT")
    print("=" * 60)
    print(f"Total foods audited   : {initial_count}")
    print(f"Total foods removed   : {len(deleted_rows)}")
    print(f"Total foods remaining : {final_count}")
    print("-" * 60)
    print("Sample of Removed Foods & Reasons:")
    for name, reason in deleted_rows[:20]:
        print(f" - {name} ({reason})")
    print("=" * 60)
    print(f"Dataset successfully saved to: {CLEAN_CSV_PATH}")

if __name__ == '__main__':
    run_purge()
