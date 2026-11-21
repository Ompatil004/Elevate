import React from 'react';
import { styles } from './nutritionStyles';
import { getFallbackServing } from './nutritionServing';

export default function MealSwapModal({
  show,
  food,
  swapLoading,
  swapOptions,
  selectedSwap,
  setSelectedSwap,
  onClose,
  onConfirmSwap,
}) {
  if (!show) return null;

  return (
    <div
      style={styles.swapModal}
      className="swap-modal-backdrop"
      onClick={onClose}
    >
      <div
        style={styles.swapModalCard}
        className="swap-modal-card"
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "var(--app-text)", letterSpacing: "-0.5px" }}>Swap Food</div>
          <button
            onClick={onClose}
            style={{
              background: "var(--app-border)",
              borderRadius: "50%",
              width: "36px",
              height: "36px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--app-text-muted)",
              border: "1px solid var(--app-border)",
              fontSize: "16px",
              cursor: "pointer",
              transition: "all 0.2s ease"
            }}
            className="icon-hover"
          >
            ✕
          </button>
        </div>
        <div style={{ fontSize: "15px", color: "var(--app-text-muted)", marginBottom: "24px", lineHeight: "1.5" }}>
          Looking for alternatives to <strong style={{ color: "var(--app-text)" }}>{food?.name}</strong>? Choose an option below.
        </div>

        {swapLoading ? (
          <div style={{ textAlign: "center", padding: "60px 20px", color: "#71717a", flex: 1 }}>
            <div style={{ fontSize: "32px", marginBottom: "16px", animation: "pulse 1.5s infinite" }}>🔄</div>
            <div style={{ fontSize: "15px", fontWeight: "600" }}>Searching dataset for alternatives...</div>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginBottom: "24px", overflowY: "auto", flex: 1, paddingRight: "8px" }} className="custom-scroll">
            {swapOptions.length === 0 ? (
              <div style={{ textAlign: "center", padding: "40px", color: "#52525b", fontSize: "15px", background: 'var(--app-surface-hover, rgba(255,255,255,0.02))', borderRadius: "16px" }}>No similar swap options found.</div>
            ) : (
              swapOptions.map((option, i) => {
                const optName = option.food_name || option.name;
                const selName = selectedSwap?.food_name || selectedSwap?.name;
                const isSelected = selName === optName;
                return (
                  <div
                    key={i}
                    onClick={() => setSelectedSwap(option)}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "16px 20px",
                      background: isSelected ? "rgba(99, 102, 241, 0.15)" : "var(--quote-bg)",
                      borderRadius: "16px",
                      border: isSelected ? "2px solid #6366f1" : "1px solid var(--app-border)",
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                      boxShadow: isSelected ? "0 4px 15px rgba(99, 102, 241, 0.2)" : "none"
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "16px", fontWeight: "700", color: isSelected ? "var(--app-text)" : "var(--app-text)" }}>{optName}</div>
                      <div style={{ fontSize: "13px", color: "var(--app-text-muted)", marginTop: "4px" }}>
                        {(!option.serving || String(option.serving).match(/^(~?\d+(?:\.\d+)?)(g|ml)$/i)) ? getFallbackServing(optName, option.calories) : option.serving}
                      </div>
                      <div style={{ display: "flex", gap: "12px", marginTop: "8px" }}>
                        <span style={{ fontSize: "12px", color: "#10b981", fontWeight: "600", fontFamily: "monospace" }}>P: {option.protein}g</span>
                        <span style={{ fontSize: "12px", color: "#3b82f6", fontWeight: "600", fontFamily: "monospace" }}>C: {option.carbs}g</span>
                        <span style={{ fontSize: "12px", color: "#f59e0b", fontWeight: "600", fontFamily: "monospace" }}>F: {option.fat}g</span>
                      </div>
                    </div>
                    <div style={{ fontSize: "16px", fontWeight: "800", color: "var(--app-text)", fontFamily: "monospace", background: "var(--app-border)", padding: "6px 12px", borderRadius: "12px" }}>
                      {option.calories} cal
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}

        <div style={{ display: "flex", gap: "12px" }}>
          <button
            onClick={onClose}
            style={{
              flex: 1,
              padding: "14px",
              borderRadius: "14px",
              background: "var(--app-surface2)",
              color: "var(--app-text)",
              border: "1px solid var(--app-border)",
              fontWeight: "700",
              cursor: "pointer",
              fontSize: "14px"
            }}
          >
            Cancel
          </button>
          <button
            onClick={onConfirmSwap}
            disabled={!selectedSwap}
            style={{
              flex: 1,
              padding: "14px",
              borderRadius: "14px",
              background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
              color: "var(--app-text)",
              border: "none",
              fontWeight: "700",
              cursor: "pointer",
              fontSize: "14px",
              opacity: selectedSwap ? 1 : 0.4,
              boxShadow: selectedSwap ? "0 4px 20px rgba(99, 102, 241, 0.4)" : "none"
            }}
          >
            Swap Food
          </button>
        </div>
      </div>
    </div>
  );
}
