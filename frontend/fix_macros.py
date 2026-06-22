import re

with open('src/pages/Dashboard.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add getMealHistory to api imports
content = re.sub(
    r'import \{ ([^\}]+) \} from \'../api\';',
    lambda m: f"import {{ {m.group(1)}, getMealHistory }} from '../api';" if 'getMealHistory' not in m.group(1) else m.group(0),
    content
)

injection = '''
        // Fetch real macros from DB
        try {
          const mealRes = await getMealHistory();
          if (mealRes && mealRes.data) {
            const todayStr = getLocalDateStr(new Date());
            const todaysMeals = mealRes.data.filter(m => String(m.date).startsWith(todayStr));
            let tCal = 0, tPro = 0, tCarb = 0, tFat = 0;
            todaysMeals.forEach(m => {
              tCal += Number(m.calories) || 0;
              tPro += Number(m.protein) || 0;
              tCarb += Number(m.carbs) || 0;
              tFat += Number(m.fat) || 0;
            });
            setMacros(prev => ({
              ...prev,
              calories: Math.round(tCal),
              p: Math.round(tPro),
              c: Math.round(tCarb),
              f: Math.round(tFat),
              remaining: Math.max(0, prev.calMax - Math.round(tCal))
            }));
          }
        } catch(e) {
          console.warn('Failed to fetch meal history on load:', e);
        }
'''

content = content.replace('// ? Fallback to local storage', injection + '\n        // ? Fallback to local storage')

with open('src/pages/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
