import re

with open('src/pages/Dashboard.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

helper = """
const getDynamicWaterGoal = (weight, sleepHours, workoutCompleted) => {
  let base = parseFloat(((weight || 70) * 0.033).toFixed(2));
  if (workoutCompleted) base += 0.5; // +500ml for workout
  if (sleepHours > 0 && sleepHours < 7) base += 0.25; // +250ml for recovery
  return parseFloat(Math.min(base, 5.0).toFixed(1));
};
"""

if 'getDynamicWaterGoal' not in content:
    content = content.replace('function Dashboard() {', helper + '\nfunction Dashboard() {')

# Find all occurrences of waterGoal calculations and replace them
content = re.sub(
    r'const waterGoal = parseFloat\(\(userWeight \* 0\.033\)\.toFixed\(\d+\)\)(?: \|\| 2\.3)?;',
    r'const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);\n    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);',
    content
)

with open('src/pages/Dashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
