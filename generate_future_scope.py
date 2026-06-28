import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis('off')

# Background
fig.patch.set_facecolor('#F8F9FA')

cards = [
    {'x': 0.5, 'y': 3.7, 'title': '01. IoT Biometric Sync', 'text': 'Apple Health & Google Fit integration\nfor automatic fatigue & sleep tracking.', 'color': '#4361EE'},
    {'x': 6.2, 'y': 3.7, 'title': '02. Track Lifting Speed', 'text': 'Using the camera to track how fast\nyou lift to maximize muscle growth.', 'color': '#F72585'},
    {'x': 0.5, 'y': 0.5, 'title': '03. CV Dietary Logging', 'text': 'Image-recognition AI to instantly\nestimate and log macros from a photo.', 'color': '#3A0CA3'},
    {'x': 6.2, 'y': 0.5, 'title': '04. Grocery API', 'text': 'One-click Instacart integration\nfor automated AI meal plan delivery.', 'color': '#7209B7'}
]

for card in cards:
    # Draw card background shadow
    shadow = patches.Rectangle((card['x'] + 0.05, card['y'] - 0.05), 5.3, 2.8, facecolor='#E9ECEF', edgecolor='none', zorder=0)
    ax.add_patch(shadow)
    
    # Draw card background
    rect = patches.Rectangle((card['x'], card['y']), 5.3, 2.8, facecolor='white', edgecolor='#DEE2E6', linewidth=1, zorder=1)
    ax.add_patch(rect)
    
    # Draw color accent line on the left
    accent = patches.Rectangle((card['x'], card['y']), 0.15, 2.8, facecolor=card['color'], zorder=2)
    ax.add_patch(accent)
    
    # Draw Title
    ax.text(card['x'] + 0.4, card['y'] + 2.1, card['title'], fontsize=18, fontweight='bold', color='#212529', fontfamily='sans-serif', zorder=3)
    
    # Draw Underline
    ax.plot([card['x'] + 0.4, card['x'] + 1.2], [card['y'] + 1.8, card['y'] + 1.8], color=card['color'], linewidth=4, zorder=3)
    
    # Draw Text
    ax.text(card['x'] + 0.4, card['y'] + 1.4, card['text'], fontsize=14, color='#495057', fontfamily='sans-serif', linespacing=1.6, verticalalignment='top', zorder=3)

plt.savefig('future_scope_infographic.png', bbox_inches='tight', dpi=300)
print("Infographic successfully generated: future_scope_infographic.png")
