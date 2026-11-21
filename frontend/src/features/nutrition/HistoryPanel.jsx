import React from 'react';
import { styles } from './nutritionStyles';

export default function HistoryPanel({
  mealHistory,
  expandedDates,
  setExpandedDates,
  expandedMeals,
  setExpandedMeals,
  onClose,
  today,
}) {
  const mealTypeIcons = { breakfast: "☀️", lunch: "🌤️", dinner: "🌙", snack: "🍎" };
  const mealTypeColors = { breakfast: "#f59e0b", lunch: "#3b82f6", dinner: "#8b5cf6", snack: "#10b981" };

  return (
    <div style={styles.historyPanel} className="nutrition-history-panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <div style={{ fontSize: "20px", fontWeight: "800", color: "var(--app-text)" }}>Meal History</div>
          <div style={{ fontSize: "12px", color: "#71717a", marginTop: "4px" }}>{mealHistory.length} day{mealHistory.length !== 1 ? "s" : ""} tracked</div>
        </div>
        <button
          onClick={onClose}
          style={{
            background: "var(--app-border)",
            border: "1px solid var(--app-border)",
            color: "var(--app-text)",
            fontSize: "16px",
            cursor: "pointer",
            width: "36px",
            height: "36px",
            borderRadius: "10px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}
        >
          ✕
        </button>
      </div>

      {mealHistory.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#3f3f46" }}>
          <div style={{ fontSize: "48px", marginBottom: "12px" }}>📋</div>
          <div style={{ fontSize: "16px", fontWeight: "700", color: "#52525b" }}>No meals completed yet</div>
          <div style={{ fontSize: "13px", color: "#3f3f46", marginTop: "8px" }}>Tick all items in a meal to save it here</div>
        </div>
      ) : (
        mealHistory.map((dayEntry) => {
          const dateObj = new Date(dayEntry.date + "T00:00:00");
          const dayName = dateObj.toLocaleDateString("en-US", { weekday: "long" });
          const dateText = dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
          const isToday = dayEntry.date === today;
          const isExpanded = !!expandedDates[dayEntry.date];
          const mealCount = Object.keys(dayEntry.meals || {}).length;

          return (
            <div key={dayEntry.date} style={{ marginBottom: "12px", borderRadius: "16px", overflow: "hidden", border: "1px solid rgba(255,255,255,0.06)" }}>
              <div
                onClick={() => setExpandedDates((prev) => ({ ...prev, [dayEntry.date]: !prev[dayEntry.date] }))}
                style={{
                  background: isToday ? "linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%)" : "var(--quote-bg)",
                  padding: "16px 20px",
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  borderBottom: isExpanded ? "1px solid rgba(255,255,255,0.06)" : "none",
                }}
              >
                <div>
                  <div style={{ fontSize: "11px", fontWeight: "800", color: isToday ? "#818cf8" : "#71717a", textTransform: "uppercase", letterSpacing: "1px", marginBottom: "4px" }}>{isToday ? "⭐ Today" : dayName}</div>
                  <div style={{ fontSize: "15px", fontWeight: "700", color: "var(--app-text)" }}>{dateText}</div>
                  <div style={{ fontSize: "11px", color: "#52525b", marginTop: "4px" }}>{mealCount} meal{mealCount !== 1 ? "s" : ""} completed</div>
                </div>
                <div style={{ textAlign: "right", display: "flex", alignItems: "center", gap: "16px" }}>
                  <div>
                    <div style={{ fontSize: "20px", fontWeight: "800", color: "var(--app-text)", fontFamily: "monospace" }}>{dayEntry.total_calories}</div>
                    <div style={{ fontSize: "10px", color: "#71717a", textTransform: "uppercase", letterSpacing: "1px" }}>calories</div>
                  </div>
                  <div style={{ fontSize: "14px", color: "#52525b", transition: "transform 0.3s", transform: isExpanded ? "rotate(0deg)" : "rotate(-90deg)" }}>▼</div>
                </div>
              </div>

              {isExpanded && (
                <div style={{ background: "rgba(0,0,0,0.2)" }}>
                  {["breakfast", "lunch", "dinner", "snack"].map((mealType) => {
                    const meal = dayEntry.meals?.[mealType];
                    if (!meal) return null;
                    const mealKey = `${dayEntry.date}-${mealType}`;
                    const isMealExpanded = !!expandedMeals[mealKey];
                    return (
                      <div key={mealType} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                        <div
                          onClick={() => setExpandedMeals((prev) => ({ ...prev, [mealKey]: !prev[mealKey] }))}
                          style={{
                            padding: "14px 20px",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            cursor: "pointer",
                          }}
                        >
                          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                            <div style={{ width: "36px", height: "36px", borderRadius: "10px", background: (mealTypeColors[mealType] || "#6366f1") + "15", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px" }}>
                              {mealTypeIcons[mealType] || "🍽️"}
                            </div>
                            <div>
                              <div style={{ fontSize: "13px", fontWeight: "700", color: "var(--app-text)", textTransform: "capitalize" }}>{mealType}</div>
                            </div>
                          </div>
                          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                            <div style={{ background: "rgba(34, 197, 94, 0.15)", color: "#22c55e", padding: "4px 10px", borderRadius: "10px", fontSize: "12px", fontWeight: "700", fontFamily: "monospace" }}>{meal.calories} cal</div>
                            <div style={{ fontSize: "12px", color: "#3f3f46", transition: "transform 0.3s", transform: isMealExpanded ? "rotate(0deg)" : "rotate(-90deg)" }}>▼</div>
                          </div>
                        </div>
                        {isMealExpanded && (
                          <div style={{ padding: "0 20px 14px 68px" }}>
                            <div style={{ display: "flex", gap: "16px", marginBottom: "10px", padding: "8px 12px", background: 'var(--app-surface-hover, rgba(255,255,255,0.02))', borderRadius: "10px" }}>
                              <span style={{ fontSize: "11px", color: "#10b981", fontWeight: "700", fontFamily: "monospace" }}>P: {meal.protein}g</span>
                              <span style={{ fontSize: "11px", color: "#3b82f6", fontWeight: "700", fontFamily: "monospace" }}>C: {meal.carbs}g</span>
                              <span style={{ fontSize: "11px", color: "#f59e0b", fontWeight: "700", fontFamily: "monospace" }}>F: {meal.fat}g</span>
                            </div>
                            {(meal.foods || []).map((food, fIdx) => (
                              <div key={fIdx} style={{ display: "flex", alignItems: "center", padding: "8px 0", borderBottom: fIdx < (meal.foods || []).length - 1 ? "1px solid rgba(255,255,255,0.03)" : "none" }}>
                                <div style={{ width: "20px", height: "20px", borderRadius: "6px", background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)", display: "flex", alignItems: "center", justifyContent: "center", marginRight: "10px", fontSize: "10px", color: "var(--app-text)", flexShrink: 0 }}>✓</div>
                                <div style={{ flex: 1 }}>
                                  <div style={{ fontSize: "13px", fontWeight: "600", color: "#d4d4d8" }}>{food.name}</div>
                                  <div style={{ fontSize: "11px", color: "#52525b" }}>{food.calories} cal</div>
                                </div>
                                {food.tick_time && <div style={{ fontSize: "10px", color: "#71717a", background: "rgba(255,255,255,0.04)", padding: "3px 8px", borderRadius: "8px", fontFamily: "monospace" }}>🕐 {food.tick_time}</div>}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}
