export const styles = {
  page: { background: "transparent", minHeight: "100dvh", color: "var(--app-text)", fontFamily: "'Inter', sans-serif", overflowX: "hidden", position: "relative", zIndex: 1, paddingTop: "clamp(64px, 9vw, 80px)" },
  navbar: { display: "flex", alignItems: "center", padding: "0 clamp(12px, 4vw, 40px)", height: "clamp(64px, 9vw, 80px)", gap: "clamp(8px, 2vw, 18px)", borderBottom: "1px solid var(--app-border)", background: 'var(--app-nav-bg, rgba(9, 9, 11, 0.6))', backdropFilter: "blur(16px)", position: "fixed", top: 0, left: 0, right: 0, zIndex: 1000, overflowX: "auto" },
  brand: { flex: 1, fontSize: "22px", fontWeight: "900", letterSpacing: "-1px", background: "var(--brand-grad, linear-gradient(to right, #ffffff, #a5b4fc))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", display: "flex", alignItems: "center", gap: "10px" },
  navCenter: { display: "flex", gap: "clamp(4px, 1.5vw, 8px)", height: "100%", alignItems: "center", justifyContent: "center" },
  navLink: { display: "flex", alignItems: "center", padding: "8px clamp(10px, 2vw, 20px)", fontSize: "clamp(11px, 1.7vw, 13px)", fontWeight: "600", color: "var(--app-text-muted)", cursor: "pointer", borderRadius: "20px", transition: "all 0.2s", textTransform: "uppercase", letterSpacing: "0.5px", border: "1px solid transparent" },
  navLinkActive: { background: "var(--app-border)", color: "var(--app-text)", boxShadow: "0 0 20px var(--app-border)", border: "1px solid var(--app-border)" },
  navRight: { flex: 1, display: "flex", alignItems: "center", gap: "clamp(8px, 2vw, 24px)", justifyContent: "flex-end" },
  brandDot: { width: "8px", height: "8px", background: "#6366f1", borderRadius: "50%", boxShadow: "0 0 15px #6366f1" },
  iconButton: { width: "clamp(36px, 6vw, 42px)", height: "clamp(36px, 6vw, 42px)", borderRadius: "12px", background: "var(--quote-bg)", border: "1px solid var(--app-border)", color: "var(--app-text)", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "18px", transition: "all 0.2s" },
  logoutBtn: { display: "flex", alignItems: "center", gap: "8px", padding: "0 clamp(10px, 2vw, 20px)", borderRadius: "12px", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", color: "#ef4444", cursor: "pointer", transition: "all 0.2s ease", height: "clamp(36px, 6vw, 42px)" },
  logoutText: { fontSize: "12px", fontWeight: "700", letterSpacing: "0.5px", textTransform: "uppercase" },
  container: { maxWidth: "1400px", margin: "0 auto", padding: "clamp(12px, 4vw, 40px)" },
  header: { fontSize: "clamp(28px, 5vw, 42px)", fontWeight: "800", color: "var(--app-text)", marginBottom: "clamp(18px, 3vw, 40px)", letterSpacing: "-1px", background: "var(--h1-grad)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", filter: "drop-shadow(0 4px 20px rgba(99, 102, 241, 0.3))" },
  daySelectorBar: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(90px, 1fr))", gap: "10px", marginBottom: "20px" },
  dayCard: { background: "var(--app-surface)", border: "1px solid var(--app-border)", borderRadius: "16px", padding: "clamp(8px, 1.8vw, 12px)", cursor: "pointer", transition: "all 0.3s ease", textAlign: "center", position: "relative", overflow: "hidden" },
  dayCardSelected: { background: 'var(--day-card-selected-bg, linear-gradient(145deg, #1e1b4b 0%, #312e81 100%))', border: "2px solid #6366f1", transform: "scale(1.05)", boxShadow: "0 0 30px rgba(99, 102, 241, 0.2)" },
  dayCardToday: { borderColor: "#10b981", boxShadow: "0 0 15px rgba(16, 185, 129, 0.15)" },
  dayName: { fontSize: "12px", fontWeight: "700", color: "var(--app-text-muted)", marginBottom: "4px", textTransform: "uppercase", letterSpacing: "1px" },
  dailySummaryCard: { background: "var(--app-surface)", borderRadius: "20px", padding: "clamp(12px, 2vw, 20px)", marginBottom: "20px", border: "1px solid var(--app-border)", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "clamp(10px, 2vw, 16px)", position: "relative", overflow: "hidden" },
  macroStat: { textAlign: "center", padding: "10px", borderRadius: "14px", background: 'var(--app-surface-hover, rgba(255,255,255,0.02))', border: "1px solid rgba(255,255,255,0.04)", transition: "all 0.2s ease" },
  macroValue: { fontSize: "clamp(18px, 3vw, 26px)", fontWeight: "800", color: "var(--app-text)", marginBottom: "2px", fontFamily: "'Inter', sans-serif" },
  macroLabel: { fontSize: "11px", color: "#71717a", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: "700" },
  mealList: { display: "grid", gap: "20px" },
  mealCard: { background: "var(--app-surface)", borderRadius: "20px", padding: "clamp(14px, 2.8vw, 28px)", border: "1px solid var(--app-border)", transition: "all 0.3s ease", position: "relative", overflowX: "auto", overflowY: "hidden" },
  mealCardCompleted: { border: "1px solid rgba(34, 197, 94, 0.4)", background: "var(--app-card-bg)" },
  completedBadge: { position: "absolute", top: "15px", right: "15px", background: "rgba(34, 197, 94, 0.1)", color: "#22c55e", padding: "6px 14px", borderRadius: "20px", fontSize: "11px", fontWeight: "800", border: "1px solid rgba(34, 197, 94, 0.3)" },
  mealHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", paddingBottom: "16px", borderBottom: '1px solid var(--app-border)', gap: "12px", flexWrap: "wrap" },
  mealName: { fontSize: "20px", fontWeight: "800", color: "var(--app-text)", letterSpacing: "-0.5px" },
  foodTableHeader: { display: "grid", gridTemplateColumns: "30px minmax(140px, 2fr) minmax(80px, 1fr) repeat(4, minmax(54px, 1fr)) 44px", gap: "10px", minWidth: "660px", padding: "0 16px 12px", fontSize: "11px", fontWeight: "700", color: "#52525b", textTransform: "uppercase", letterSpacing: "1px" },
  foodList: { display: "grid", gap: "8px" },
  foodItemRow: { display: "grid", gridTemplateColumns: "30px minmax(140px, 2fr) minmax(80px, 1fr) repeat(4, minmax(54px, 1fr)) 44px", gap: "10px", minWidth: "660px", padding: "14px 16px", background: 'var(--app-surface-hover, rgba(255,255,255,0.02))', borderRadius: "14px", alignItems: "center", fontSize: "14px", border: '1px solid var(--app-border)', transition: "all 0.2s ease" },
  checkbox: { width: "22px", height: "22px", borderRadius: "8px", border: "2px solid var(--app-border)", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", transition: "all 0.2s", background: "transparent", fontSize: "12px" },
  checkboxChecked: { background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)", borderColor: "#22c55e", boxShadow: "0 0 10px rgba(34, 197, 94, 0.3)", color: "#ffffff" },
  swapBtn: { background: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.2)", color: "#818cf8", cursor: "pointer", fontSize: "16px", padding: "6px", borderRadius: "10px", transition: "all 0.2s", width: "34px", height: "34px", display: "flex", alignItems: "center", justifyContent: "center" },
  mealMacroTotal: { display: "flex", justifyContent: "flex-end", gap: "24px", marginTop: "16px", paddingTop: "16px", borderTop: '1px solid var(--app-border)', flexWrap: "wrap" },
  historyPanel: { position: "fixed", top: "80px", right: "0", width: "min(96vw, 480px)", height: "calc(100dvh - 80px)", background: "var(--app-bg)", borderLeft: "1px solid var(--app-border)", zIndex: 1500, padding: "clamp(14px, 2.5vw, 24px)", overflowY: "auto", animation: "slideInRight 0.3s ease-out", boxShadow: "-20px 0 50px rgba(0,0,0,0.5)" },
  swapModal: { position: "fixed", top: 0, left: 0, width: "100%", height: "100%", background: "rgba(0,0,0,0.75)", backdropFilter: "blur(12px)", zIndex: 3000, display: "flex", alignItems: "center", justifyContent: "center", transition: "opacity 0.3s ease" },
  swapModalCard: { background: "var(--app-surface)", padding: "clamp(16px, 3vw, 32px)", borderRadius: "24px", width: "min(96vw, 480px)", maxWidth: "480px", border: "1px solid rgba(99, 102, 241, 0.2)", boxShadow: "0 20px 60px rgba(0,0,0,0.6), 0 0 40px rgba(99, 102, 241, 0.1)", animation: "scaleIn 0.3s ease-out", maxHeight: "84dvh", display: "flex", flexDirection: "column" },
  optionalBadge: { background: "rgba(245, 158, 11, 0.1)", color: "#f59e0b", padding: "4px 10px", borderRadius: "12px", fontSize: "10px", fontWeight: "800", border: "1px solid rgba(245, 158, 11, 0.3)", marginLeft: "10px", textTransform: "uppercase" },
};

export const nutritionAnimations = `
  @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
  @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
  @keyframes scaleIn { from { transform: scale(0.95) translateY(20px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.08); } 100% { transform: scale(1); } }
  .day-card-hover:hover { transform: translateY(-3px) !important; border-color: rgba(99, 102, 241, 0.3) !important; box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important; }
  .food-row-hover:hover { background: rgba(255,255,255,0.04) !important; border-color: var(--app-border) !important; }
  .meal-card-hover:hover { border-color: rgba(99, 102, 241, 0.15) !important; box-shadow: 0 8px 30px rgba(0,0,0,0.2) !important; }
  .swap-btn-hover:hover { background: rgba(99, 102, 241, 0.2) !important; transform: scale(1.1); box-shadow: 0 0 12px rgba(99, 102, 241, 0.3); }
  .macro-stat-hover:hover { background: rgba(255,255,255,0.04) !important; transform: scale(1.03); }
  .icon-hover:hover { background: var(--app-border) !important; }
  .logout-btn:hover { background: rgba(239, 68, 68, 0.2) !important; }
  @media (max-width: 640px) {
    .meal-card { overflow-x: hidden !important; }
    .meal-header { padding-right: 120px !important; }
    .food-table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  }
`;
