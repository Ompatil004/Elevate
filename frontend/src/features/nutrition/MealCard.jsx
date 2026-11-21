import React from 'react';
import { styles } from './nutritionStyles';
import { getFallbackServing } from './nutritionServing';

export default function MealCard({
  meal,
  isLocked,
  isSequenceLocked,
  unlockMessage,
  checkedFoods,
  tickTimes,
  today,
  checkedCount,
  totalCount,
  onCheckFood,
  onSwapFood,
  dayIndex,
  isFutureDay,
}) {
  const isDisabled = isFutureDay || isLocked || isSequenceLocked;
  return (
    <div
      className="meal-card meal-card-hover"
      style={{
        ...styles.mealCard,
        ...(isLocked ? styles.mealCardCompleted : {}),
        ...(isSequenceLocked
          ? {
              opacity: 0.55,
              cursor: "not-allowed",
              border: "1px dashed rgba(255,255,255,0.12)",
            }
          : {}),
      }}
    >
      {isLocked && <div style={styles.completedBadge}>✓ Completed</div>}
      {isSequenceLocked && (
        <div style={{
          position: "absolute",
          top: "15px",
          right: "15px",
          background: "rgba(113, 113, 122, 0.22)",
          color: "var(--app-text-muted)",
          padding: "6px 14px",
          borderRadius: "20px",
          fontSize: "11px",
          fontWeight: "700",
          border: "1px solid rgba(113, 113, 122, 0.35)",
        }}>
          Locked
        </div>
      )}

      <div style={styles.mealHeader} className="meal-header">
        <div style={{ display: "flex", alignItems: "center" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center" }}>
              <div style={styles.mealName}>{meal.name}</div>
              {meal.meal_type.toLowerCase() === "snack" && <span style={styles.optionalBadge}>Always Open</span>}
            </div>
            <div style={{ fontSize: "13px", color: isLocked ? "#22c55e" : "#6366f1", fontWeight: "700", textTransform: "uppercase", marginTop: "4px", letterSpacing: "1px" }}>{meal.meal_type}</div>
            {isSequenceLocked && unlockMessage && (
              <div style={{ fontSize: "12px", color: "var(--app-text-muted)", marginTop: "6px" }}>{unlockMessage}</div>
            )}
          </div>
        </div>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <div style={{ fontSize: "13px", fontWeight: "700", fontFamily: "monospace", color: isLocked ? "#22c55e" : checkedCount > 0 ? "#818cf8" : "#52525b" }}>
            {isLocked ? "✓ All" : `${checkedCount}/${totalCount}`}
          </div>
          <div style={{ width: "60px", height: "4px", background: "var(--app-surface2)", borderRadius: "4px", overflow: "hidden" }}>
            <div style={{ width: `${totalCount > 0 ? (checkedCount / totalCount) * 100 : 0}%`, height: "100%", background: isLocked ? "#22c55e" : "#6366f1", borderRadius: "4px", transition: "width 0.3s ease" }} />
          </div>
        </div>
      </div>

      <div className="food-table-scroll">
      <div style={styles.foodTableHeader} className="food-table-header">
        <div></div><div>Food</div><div style={{ textAlign: "center", color: "#a78bfa" }}>Portion</div><div style={{ textAlign: "center" }}>Cal</div>
        <div style={{ textAlign: "center" }}>Pro</div><div style={{ textAlign: "center" }}>Carb</div>
        <div style={{ textAlign: "center" }}>Fat</div><div></div>
      </div>

      <div style={styles.foodList}>
        {(meal.foods || []).map((food) => {
          const checkKey = `${today}-${food.id}`;
          const isChecked = !!checkedFoods[checkKey] || isLocked;
          const itemTickTime = tickTimes[checkKey];
          return (
            <div key={food.id} className="food-row-hover" style={{
              ...styles.foodItemRow,
              opacity: isChecked ? (isLocked ? 0.5 : 0.7) : 1,
              background: isChecked ? "rgba(34, 197, 94, 0.04)" : "rgba(255,255,255,0.02)",
              ...(isSequenceLocked ? { pointerEvents: "none", opacity: 0.5 } : {}),
            }}>
              {/* Col 1: Checkbox */}
              <div onClick={() => !isDisabled && onCheckFood(food.id, meal.name, meal.meal_type, dayIndex)} style={{
                ...styles.checkbox, ...(isChecked ? styles.checkboxChecked : {}),
                ...(isDisabled && !isChecked ? { opacity: 0.3, cursor: "not-allowed" } : {}),
              }} role="checkbox" aria-checked={isChecked} aria-label={`Mark ${food.name} as eaten`}>
                {isChecked && "✓"}
              </div>
              {/* Col 2: Food name */}
              <div style={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
                <span style={{ fontWeight: "600", color: isChecked ? "var(--app-text-muted)" : "var(--app-text)", textDecoration: isChecked ? "line-through" : "none", overflowWrap: "break-word" }}>{food.name}</span>
                {isChecked && itemTickTime && <span style={{ fontSize: "10px", color: "#22c55e", fontFamily: "monospace", marginTop: "2px" }}>✓ {itemTickTime}</span>}
              </div>
              {/* Col 3: Portion (desktop) */}
              <div style={{ textAlign: "center" }}>
                <span style={{
                  fontSize: "12px", fontWeight: "700", color: "#a78bfa",
                  background: "rgba(167,139,250,0.10)", borderRadius: "8px",
                  padding: "3px 7px", fontFamily: "monospace",
                  whiteSpace: "nowrap",
                }}>
                  {(!food.serving || String(food.serving).match(/^(~?\d+(?:\.\d+)?)(g|ml)$/i)) ? getFallbackServing(food.name, food.calories) : food.serving}
                </span>
              </div>
              {/* Col 4-7: Macros (desktop) */}
              <div style={{ textAlign: "center", color: "var(--app-text)", fontWeight: "600", fontFamily: "monospace", fontSize: "13px" }}>{food.calories}</div>
              <div style={{ textAlign: "center", color: "#10b981", fontFamily: "monospace", fontSize: "13px" }}>{food.protein_g}g</div>
              <div style={{ textAlign: "center", color: "#3b82f6", fontFamily: "monospace", fontSize: "13px" }}>{food.carbs_g}g</div>
              <div style={{ textAlign: "center", color: "#f59e0b", fontFamily: "monospace", fontSize: "13px" }}>{food.fat_g}g</div>
              {/* Col 8: Swap button */}
              <button className="swap-btn-hover" onClick={() => !isDisabled && onSwapFood(food, meal.meal_type, dayIndex)} disabled={isDisabled} aria-label={`Swap ${food.name}`} style={{ ...styles.swapBtn, ...(isDisabled ? { opacity: 0.3, cursor: "not-allowed" } : {}) }}>🔄</button>
              {/* Mobile macro metadata */}
              <div className="food-macro-meta" style={{ display: "none" }}>
                <span style={{ fontSize: "11px", color: "#a78bfa", fontWeight: "700" }}>
                  {(!food.serving || food.serving.match(/^(~?\d+(?:\.\d+)?)(g|ml)$/i)) ? getFallbackServing(food.name, food.calories) : food.serving}
                </span>
                <span style={{ fontSize: "11px", color: "var(--app-text)", fontWeight: "700", fontFamily: "monospace" }}>{food.calories} cal</span>
                <span style={{ fontSize: "11px", color: "#10b981", fontFamily: "monospace" }}>P: {food.protein_g}g</span>
                <span style={{ fontSize: "11px", color: "#3b82f6", fontFamily: "monospace" }}>C: {food.carbs_g}g</span>
                <span style={{ fontSize: "11px", color: "#f59e0b", fontFamily: "monospace" }}>F: {food.fat_g}g</span>
              </div>
            </div>
          );
        })}
      </div>
      </div>

      <div style={styles.mealMacroTotal} className="meal-macro-total">
        <div style={{ fontSize: "13px", fontWeight: "800", color: "var(--app-text)", fontFamily: "monospace" }}>{meal.totals?.calories || 0} cal</div>
        <div style={{ fontSize: "13px", fontWeight: "700", color: "#10b981", fontFamily: "monospace" }}>{meal.totals?.protein_g || 0}g pro</div>
        <div style={{ fontSize: "13px", fontWeight: "700", color: "#3b82f6", fontFamily: "monospace" }}>{meal.totals?.carbs_g || 0}g carb</div>
        <div style={{ fontSize: "13px", fontWeight: "700", color: "#f59e0b", fontFamily: "monospace" }}>{meal.totals?.fat_g || 0}g fat</div>
      </div>
    </div>
  );
}
