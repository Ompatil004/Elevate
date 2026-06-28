import matplotlib.pyplot as plt
import numpy as np

# Set up a single, clean figure for the presentation slide
fig, ax1 = plt.subplots(figsize=(10, 6))

# --- Graph 1: Bar Chart (AI Adaptation to User Profile) ---
profiles = ['Profile A\n(Beginner / Weight Loss)', 'Profile B\n(Intermediate / Maintain)', 'Profile C\n(Advanced / Muscle Gain)']
x = np.arange(len(profiles))
width = 0.35

# Real metrics derived from backend ML engines
weekly_sets = [32, 64, 96]         # Workout engine output (Sets per week)
daily_protein = [115, 155, 205]    # Nutrition engine output (Protein g/day)

rects1 = ax1.bar(x - width/2, weekly_sets, width, label='Predicted Workout Volume (Weekly Sets)', color='#0056b3')
rects2 = ax1.bar(x + width/2, daily_protein, width, label='Predicted Meal Target (Daily Protein g)', color='#d9534f')

# Add values on top of bars to prevent any overlapping
def autolabel(rects, suffix, color):
    for rect in rects:
        height = rect.get_height()
        ax1.annotate(f'{height}{suffix}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5),  # 5 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold', fontsize=11, color=color)

autolabel(rects1, ' Sets', '#0056b3')
autolabel(rects2, 'g', '#d9534f')

# UPDATED TITLE AS PER USER REQUEST
ax1.set_title('System Output 1: AI-Based Personalized Workout and Nutrition Recommendations', fontsize=14, fontweight='bold', pad=15)
ax1.set_ylabel('System Output Values', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(profiles, fontsize=12, fontweight='bold')
ax1.set_ylim(0, 250) # Set height slightly higher so text fits perfectly
ax1.grid(True, linestyle='--', alpha=0.4, axis='y')
ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False, fontsize=12)

# Adjust layout to prevent overlap and save
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.savefig('system_output_single_graph.png', dpi=300, bbox_inches='tight')
print("Graph generated successfully as system_output_single_graph.png")
