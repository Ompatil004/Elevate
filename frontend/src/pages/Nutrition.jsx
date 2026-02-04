import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../components/NotificationProvider";
import { getProfile } from "../api";
import ConfirmDialog from "../components/ConfirmDialog";
import axios from "axios";

const styles = {
  page: {
    background: "#09090b",
    minHeight: "100vh",
    color: "#e4e4e7",
    fontFamily: "'Inter', sans-serif",
    position: "relative",
  },
  navbar: {
    display: "flex",
    alignItems: "center",
    padding: "0 40px",
    height: "80px",
    borderBottom: "1px solid rgba(255,255,255,0.08)",
    background: "rgba(9, 9, 11, 0.6)",
    backdropFilter: "blur(16px)",
    position: "sticky",
    top: 0,
    zIndex: 1000,
  },
  brand: {
    flex: 1,
    fontSize: "22px",
    fontWeight: "900",
    letterSpacing: "-1px",
    background: "linear-gradient(to right, #fff, #a5b4fc)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  navCenter: {
    display: "flex",
    gap: "8px",
    height: "100%",
    alignItems: "center",
    justifyContent: "center",
  },
  navLink: {
    display: "flex",
    alignItems: "center",
    padding: "8px 20px",
    fontSize: "13px",
    fontWeight: "600",
    color: "#a1a1aa",
    cursor: "pointer",
    borderRadius: "20px",
    transition: "all 0.2s",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    border: "1px solid transparent",
  },
  navLinkActive: {
    background: "rgba(255,255,255,0.1)",
    color: "#fff",
    boxShadow: "0 0 20px rgba(255,255,255,0.05)",
    border: "1px solid rgba(255,255,255,0.05)",
  },
  navRight: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    gap: "24px",
    justifyContent: "flex-end",
  },
  dateDisplay: {
    fontSize: "13px",
    fontWeight: "600",
    color: "#a1a1aa",
    fontFamily: "sans-serif",
    letterSpacing: "0.5px",
    marginRight: "8px",
  },
  brandDot: {
    width: "8px",
    height: "8px",
    background: "#6366f1",
    borderRadius: "50%",
    boxShadow: "0 0 15px #6366f1",
  },
  iconButton: {
    width: "42px",
    height: "42px",
    borderRadius: "12px",
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.08)",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    fontSize: "18px",
    transition: "all 0.2s",
    position: "relative",
  },
  notifDropdown: {
    position: "absolute",
    top: "60px",
    right: "0px",
    width: "340px",
    background: "#18181b",
    border: "1px solid rgba(255,255,255,0.1)",
    borderRadius: "16px",
    padding: "16px",
    zIndex: 2000,
    boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
  },
  notifItem: {
    padding: "12px 16px",
    borderBottom: "1px solid rgba(255,255,255,0.05)",
    fontSize: "13px",
    color: "#d4d4d8",
  },
  logoutBtn: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "0 20px",
    borderRadius: "12px",
    background: "rgba(239, 68, 68, 0.1)",
    border: "1px solid rgba(239, 68, 68, 0.2)",
    color: "#ef4444",
    cursor: "pointer",
    transition: "all 0.2s ease",
    height: "42px",
  },
  logoutText: {
    fontSize: "12px",
    fontWeight: "700",
    letterSpacing: "0.5px",
    textTransform: "uppercase",
  },
  container: { maxWidth: "1200px", margin: "0 auto", padding: "40px" },
  h1: {
    fontSize: "36px",
    fontWeight: "800",
    marginBottom: "40px",
    color: "#fff",
    letterSpacing: "-1px",
  },
  card: {
    background: "#18181b",
    borderRadius: "24px",
    padding: "32px",
    border: "1px solid rgba(255,255,255,0.05)",
    height: "100%",
    boxShadow: "0 20px 40px rgba(0,0,0,0.2)",
    transition: "all 0.3s ease",
    position: "relative",
    overflow: "hidden",
  },
  cardCompleted: {
    border: "1px solid #22c55e",
    background:
      "linear-gradient(145deg, #18181b 0%, rgba(34, 197, 94, 0.05) 100%)",
  },
  completedBadge: {
    position: "absolute",
    top: 15,
    right: 15,
    background: "rgba(34, 197, 94, 0.1)",
    color: "#22c55e",
    padding: "4px 10px",
    borderRadius: "20px",
    fontSize: "11px",
    fontWeight: "800",
    border: "1px solid #22c55e",
  },
  title: {
    fontSize: "20px",
    fontWeight: "800",
    marginBottom: "20px",
    textTransform: "uppercase",
    letterSpacing: "1px",
  },
  itemRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "14px 12px",
    borderBottom: "1px solid rgba(255,255,255,0.05)",
    transition: "background 0.2s ease",
    borderRadius: "8px",
  },
  itemLeft: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    flex: 1,
    cursor: "pointer",
  },
  checkbox: {
    width: "20px",
    height: "20px",
    borderRadius: "6px",
    border: "2px solid #52525b",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "all 0.2s",
  },
  checkboxChecked: { background: "#22c55e", borderColor: "#22c55e" },
  itemText: {
    fontSize: "14px",
    fontWeight: "500",
    color: "#e4e4e7",
    transition: "all 0.2s",
  },
  itemTextDone: { color: "#52525b", textDecoration: "line-through" },
  swapBtn: {
    background: "transparent",
    border: "none",
    color: "#6366f1",
    cursor: "pointer",
    fontSize: "16px",
    opacity: 0.5,
    transition: "all 0.2s",
  },
  modalBackdrop: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    background: "rgba(0,0,0,0.6)",
    backdropFilter: "blur(8px)",
    zIndex: 2000,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  modalCard: {
    background: "#18181b",
    padding: "32px",
    borderRadius: "24px",
    width: "400px",
    border: "1px solid rgba(255,255,255,0.1)",
    boxShadow: "0 25px 50px rgba(0,0,0,0.5)",
    textAlign: "center",
  },
  modalTitle: {
    fontSize: "20px",
    fontWeight: "800",
    color: "#fff",
    marginBottom: "10px",
  },
  modalText: {
    fontSize: "14px",
    color: "#a1a1aa",
    marginBottom: "24px",
    lineHeight: "1.5",
  },
  modalBtnRow: { display: "flex", gap: "12px" },
  modalBtnCancel: {
    flex: 1,
    padding: "12px",
    borderRadius: "12px",
    background: "#27272a",
    color: "#fff",
    border: "none",
    fontWeight: "700",
    cursor: "pointer",
  },
  modalBtnConfirm: {
    flex: 1,
    padding: "12px",
    borderRadius: "12px",
    background: "#6366f1",
    color: "#fff",
    border: "none",
    fontWeight: "700",
    cursor: "pointer",
  },
  historyPanel: {
    position: "fixed",
    top: "80px",
    right: "0",
    width: "400px",
    height: "calc(100vh - 80px)",
    background: "#09090b",
    borderLeft: "1px solid rgba(255,255,255,0.1)",
    zIndex: 1500,
    padding: "24px",
    overflowY: "auto",
    boxShadow: "-20px 0 50px rgba(0,0,0,0.5)",
  },
  historyItem: {
    background: "#18181b",
    borderRadius: "16px",
    padding: "20px",
    marginBottom: "16px",
    border: "1px solid rgba(255,255,255,0.05)",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  historyDate: {
    fontSize: "14px",
    fontWeight: "700",
    color: "#fff",
    marginBottom: "12px",
  },
  historyLabel: {
    fontSize: "11px",
    color: "#a5b4fc",
    fontWeight: "700",
    textTransform: "uppercase",
    marginBottom: "4px",
  },
  historyList: { fontSize: "13px", color: "#a1a1aa", lineHeight: "1.4" },
};

const ALTERNATIVES = [
  "Protein Smoothie",
  "Tofu Scramble",
  "Turkey Sandwich",
  "Lentil Soup",
  "Cottage Cheese Bowl",
];

function Nutrition() {
  const navigate = useNavigate();
  const notifRef = useRef(null);
  const { showError, showSuccess } = useNotification();
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    message: "",
    onConfirm: null,
  });
  const [plan, setPlan] = useState({});
  const [completedItems, setCompletedItems] = useState({});
  const [userProfile, setUserProfile] = useState(null);
  const [showNotif, setShowNotif] = useState(false);
  const [swapTarget, setSwapTarget] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [mealHistory, setMealHistory] = useState([]);

  const showConfirmDialog = (message, onConfirm) => {
    setConfirmDialog({ show: true, message, onConfirm });
  };

  const handleConfirm = () => {
    if (confirmDialog.onConfirm) confirmDialog.onConfirm(true);
    setConfirmDialog({ show: false, message: "", onConfirm: null });
  };

  const handleCancelConfirm = () => {
    if (confirmDialog.onConfirm) confirmDialog.onConfirm(false);
    setConfirmDialog({ show: false, message: "", onConfirm: null });
  };

  const todayDate = new Date().toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotif(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const saveLog = (name, details) => {
    const newLog = {
      name: name,
      date: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      details: details,
      type: "meal",
      fullDate: new Date().toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      }),
    };
    const currentHistory = JSON.parse(
      localStorage.getItem("activityHistory") || "[]",
    );
    localStorage.setItem(
      "activityHistory",
      JSON.stringify([newLog, ...currentHistory]),
    );
    loadMealHistory();
  };

  const loadMealHistory = () => {
    const activityHistory = JSON.parse(
      localStorage.getItem("activityHistory") || "[]",
    );
    const mealLogs = activityHistory.filter((log) => log.type === "meal");

    if (mealLogs.length === 0) {
      setMealHistory([]);
      return;
    }

    const groupedByDate = {};
    mealLogs.forEach((log) => {
      const dateKey = log.fullDate || log.date;
      if (!groupedByDate[dateKey]) {
        groupedByDate[dateKey] = [];
      }
      groupedByDate[dateKey].push(log.name);
    });

    const historyArray = Object.entries(groupedByDate)
      .sort((a, b) => new Date(b[0]) - new Date(a[0]))
      .map(([date, meals]) => ({
        date,
        meals,
        status: "Logged",
      }));

    setMealHistory(historyArray);
  };

  useEffect(() => {
    const lastDate = localStorage.getItem("lastMealDate");
    const today = new Date().toDateString();

    if (lastDate !== today) {
      setCompletedItems({});
      localStorage.setItem("lastMealDate", today);
      localStorage.removeItem("todayMealsDone");
    }

    loadMealHistory();

    const fetchNutritionPlan = async () => {
      try {
        console.log("🔍 Step 1: Fetching user profile...");
        const profileRes = await getProfile();
        const profile = profileRes.data;
        console.log("✅ Profile:", profile);
        setUserProfile(profile);

        const apiBase =
          import.meta.env.VITE_PY_BACKEND || "http://localhost:8000";
        console.log("🔍 Step 2: Calling backend at:", apiBase);

        const response = await axios.post(`${apiBase}/nutrition`, {
          age: profile.age,
          weight: profile.weight,
          height: profile.height,
          gender: profile.gender,
          goal: profile.goal,
          dietary_preference: profile.dietary_preference || "Non-Veg",
          allergies: profile.allergies || [],
        });

        console.log("✅ Backend response:", response.data);

        if (!response.data?.success) {
          throw new Error(
            response.data?.error || "Failed to generate nutrition",
          );
        }

        const nutrition = response.data.nutrition;
        console.log("🔍 Step 3: Nutrition data:", nutrition);
        console.log("🔍 Step 4: Meals array:", nutrition.meals);

        const normalizedPlan = {
          breakfast: [],
          lunch: [],
          dinner: [],
          snack: [],
        };

        if (nutrition.meals && Array.isArray(nutrition.meals)) {
          console.log(
            `🔍 Step 5: Processing ${nutrition.meals.length} meals...`,
          );

          nutrition.meals.forEach((meal, idx) => {
            const category = (meal.meal_type || "snack").toLowerCase();
            console.log(`   Meal ${idx}: ${meal.name} → ${category}`);

            if (!normalizedPlan[category]) {
              normalizedPlan[category] = [];
            }

            normalizedPlan[category].push({
              id: `${category}-${idx}`,
              item: meal.name || "Meal",
              calories: meal.calories || 0,
              protein: meal.protein || 0,
              carbs: meal.carbs || 0,
              fat: meal.fat || 0,
              swapped: false,
            });
          });
        } else {
          console.error("❌ nutrition.meals is not an array:", nutrition.meals);
        }

        console.log("✅ Final normalized plan:", normalizedPlan);
        setPlan(normalizedPlan);
        localStorage.setItem("nutritionPlan", JSON.stringify(normalizedPlan));
        showSuccess(`✅ Meal plan generated!`, 3000);
      } catch (error) {
        console.error("❌ Full error:", error);
        console.error("❌ Error response:", error.response?.data);
        showError(
          "Failed to generate nutrition plan. Ensure Python backend is running on port 8000.",
          4000,
        );
      }
    };

    const storedPlan = localStorage.getItem("nutritionPlan");
    if (storedPlan) {
      try {
        const parsed = JSON.parse(storedPlan);
        setPlan(parsed);
      } catch (e) {
        fetchNutritionPlan();
      }
    } else {
      fetchNutritionPlan();
    }
  }, []); // Empty dependency array since getProfile is stable and won't change

  useEffect(() => {
    if (Object.keys(plan).length === 0) return;
    const mainMeals = ["breakfast", "lunch", "dinner"];
    const allMainMealsDone = mainMeals.every((category) => {
      if (!plan[category] || !Array.isArray(plan[category])) return true;
      return plan[category].every((item) => completedItems[item.id]);
    });

    if (allMainMealsDone) {
      localStorage.setItem("todayMealsDone", "true");
    } else {
      localStorage.setItem("todayMealsDone", "false");
    }
  }, [completedItems, plan]);

  const handleLogout = () => {
    showConfirmDialog("Log out?", (confirmed) => {
      if (confirmed) {
        localStorage.clear();
        navigate("/login");
      }
    });
  };

  const toggleItem = (itemId, itemName) => {
    const newState = !completedItems[itemId];
    setCompletedItems((prev) => ({ ...prev, [itemId]: newState }));

    if (newState) {
      console.log(`✅ Meal logged: ${itemName}`);
      saveLog(itemName, `Consumed - ${new Date().toLocaleString()}`);
    } else {
      console.log(`❌ Meal unchecked: ${itemName}`);
    }
  };

  const isCategoryComplete = (categoryKey) => {
    const categoryPlan = plan[categoryKey];
    if (!categoryPlan || !Array.isArray(categoryPlan)) return false;
    return categoryPlan.every((item) => completedItems[item.id]);
  };

  const initiateSwap = (category, index, item) => {
    if (completedItems[item.id]) return;
    setSwapTarget({ category, index, item });
  };

  const confirmSwap = () => {
    if (!swapTarget) return;
    const { category, index } = swapTarget;
    const randomNew =
      ALTERNATIVES[Math.floor(Math.random() * ALTERNATIVES.length)];
    setPlan((prevPlan) => {
      const newCategoryList = [...prevPlan[category]];
      newCategoryList[index] = {
        ...newCategoryList[index],
        item: randomNew,
        swapped: true,
      };
      return { ...prevPlan, [category]: newCategoryList };
    });
    setSwapTarget(null);
    showSuccess("✅ Meal swapped!", 2000);
  };

  const categoryOrder = ["breakfast", "lunch", "dinner", "snack"];
  const categoryIcons = {
    breakfast: "🌅",
    lunch: "🍽️",
    snack: "🥜",
    dinner: "🌙",
  };
  const categoryColors = {
    breakfast: "#fcd34d",
    lunch: "#34d399",
    snack: "#60a5fa",
    dinner: "#f472b6",
  };

  return (
    <>
      <div style={styles.page}>
        <style>{`
          @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
          @keyframes scaleUp { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
          @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
          .icon-hover:hover { background: rgba(255,255,255,0.1) !important; }
          .logout-btn:hover { background: rgba(239, 68, 68, 0.2) !important; transform: translateY(-2px); }
          .swap-btn:hover { opacity: 1 !important; }
          .item-row:hover { background: rgba(255,255,255,0.02); }
          .history-card:hover { border-color: #6366f1 !important; background: rgba(255,255,255,0.05) !important; }
        `}</style>

        <nav style={styles.navbar}>
          <div style={styles.brand}>
            <div style={styles.brandDot}></div> ELEVATE
          </div>
          <div style={styles.navCenter}>
            <div style={styles.navLink} onClick={() => navigate("/dashboard")}>
              Dashboard
            </div>
            <div style={styles.navLink} onClick={() => navigate("/workout")}>
              Workout
            </div>
            <div style={{ ...styles.navLink, ...styles.navLinkActive }}>
              Nutrition
            </div>
            <div style={styles.navLink} onClick={() => navigate("/chatbot")}>
              ChatBot
            </div>
          </div>
          <div style={styles.navRight}>
            <div style={styles.dateDisplay}>{todayDate}</div>
            <button
              style={styles.iconButton}
              className="icon-hover"
              onClick={() => setShowHistory(!showHistory)}
              title="Past Meals"
            >
              🕒
            </button>
            <div style={{ position: "relative" }} ref={notifRef}>
              <button
                style={styles.iconButton}
                className="icon-hover"
                onClick={() => setShowNotif(!showNotif)}
              >
                🔔
              </button>
              {showNotif && (
                <div style={styles.notifDropdown}>
                  <div
                    style={{
                      fontSize: "14px",
                      fontWeight: "700",
                      color: "#fff",
                      marginBottom: "12px",
                    }}
                  >
                    Notifications
                  </div>
                  <div style={styles.notifItem}>🔥 You're on a streak!</div>
                  <div style={styles.notifItem}>
                    🥗 Don't forget to log meals.
                  </div>
                </div>
              )}
            </div>
            <button
              style={styles.logoutBtn}
              className="logout-btn"
              onClick={handleLogout}
            >
              <span style={styles.logoutText}>LOGOUT</span>
            </button>
          </div>
        </nav>

        <div style={styles.container}>
          <h1 style={styles.h1}>Your Daily Nutrition</h1>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap: "24px",
            }}
          >
            {categoryOrder.map((category) => {
              const categoryMeals = plan[category] || [];
              const isComplete = isCategoryComplete(category);
              const accentColor = categoryColors[category];
              const icon = categoryIcons[category];

              return (
                <div
                  key={`meal-${category}`}
                  style={{
                    ...styles.card,
                    ...(isComplete ? styles.cardCompleted : {}),
                  }}
                >
                  {isComplete && (
                    <div style={styles.completedBadge}>✓ COMPLETED</div>
                  )}
                  <h2 style={{ ...styles.title, color: accentColor }}>
                    {icon}{" "}
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </h2>
                  {categoryMeals.length > 0 ? (
                    categoryMeals.map((food, idx) => {
                      const isChecked = !!completedItems[food.id];
                      return (
                        <div
                          key={food.id}
                          style={styles.itemRow}
                          className="item-row"
                        >
                          <div
                            style={styles.itemLeft}
                            onClick={() => toggleItem(food.id, food.item)}
                          >
                            <div
                              style={{
                                ...styles.checkbox,
                                ...(isChecked ? styles.checkboxChecked : {}),
                              }}
                            >
                              {isChecked && (
                                <span
                                  style={{
                                    color: "#fff",
                                    fontSize: "12px",
                                    fontWeight: "bold",
                                  }}
                                >
                                  ✓
                                </span>
                              )}
                            </div>
                            <div
                              style={{
                                ...styles.itemText,
                                ...(isChecked ? styles.itemTextDone : {}),
                              }}
                            >
                              {food.item}
                              {food.swapped && (
                                <span
                                  style={{
                                    fontSize: "10px",
                                    color: accentColor,
                                    marginLeft: "8px",
                                    border: `1px solid ${accentColor}`,
                                    padding: "2px 4px",
                                    borderRadius: "4px",
                                  }}
                                >
                                  AI SWAP
                                </span>
                              )}
                            </div>
                          </div>
                          {!isChecked && (
                            <button
                              style={styles.swapBtn}
                              className="swap-btn"
                              onClick={() => initiateSwap(category, idx, food)}
                            >
                              🔄
                            </button>
                          )}
                        </div>
                      );
                    })
                  ) : (
                    <div
                      style={{
                        color: "#52525b",
                        fontSize: "13px",
                        padding: "12px",
                      }}
                    >
                      No meal assigned
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {showHistory && (
        <div style={styles.historyPanel}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "24px",
            }}
          >
            <div style={{ fontSize: "20px", fontWeight: "800", color: "#fff" }}>
              Meal History
            </div>
            <button
              onClick={() => setShowHistory(false)}
              style={{
                background: "none",
                border: "none",
                color: "#fff",
                fontSize: "20px",
                cursor: "pointer",
              }}
            >
              ✕
            </button>
          </div>
          {mealHistory.length > 0 ? (
            mealHistory.map((historyEntry, i) => (
              <div
                key={i}
                style={styles.historyItem}
                className="history-card"
                onClick={() =>
                  setSelectedHistory(selectedHistory === i ? null : i)
                }
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div style={styles.historyDate}>{historyEntry.date}</div>
                  <div
                    style={{
                      fontSize: "12px",
                      fontWeight: "700",
                      color: "#22c55e",
                    }}
                  >
                    {historyEntry.status}
                  </div>
                </div>
                {selectedHistory === i && (
                  <div
                    style={{
                      marginTop: "15px",
                      paddingTop: "15px",
                      borderTop: "1px solid rgba(255,255,255,0.1)",
                    }}
                  >
                    <div style={styles.historyLabel}>Meals Logged:</div>
                    <div style={styles.historyList}>
                      {historyEntry.meals.map((meal, idx) => (
                        <div key={idx} style={{ marginBottom: "4px" }}>
                          • {meal}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div
              style={{ textAlign: "center", padding: "40px", color: "#52525b" }}
            >
              No meal history yet
            </div>
          )}
        </div>
      )}

      {swapTarget && (
        <div style={styles.modalBackdrop}>
          <div style={styles.modalCard}>
            <div style={{ fontSize: "40px", marginBottom: "15px" }}>🍲</div>
            <div style={styles.modalTitle}>Swap Meal Item?</div>
            <div style={styles.modalText}>
              Do you want to swap <strong>"{swapTarget.item.item}"</strong>?
              <br />
              Our AI will find a nutritionally equivalent alternative.
            </div>
            <div style={styles.modalBtnRow}>
              <button
                style={styles.modalBtnCancel}
                onClick={() => setSwapTarget(null)}
              >
                No, Keep it
              </button>
              <button style={styles.modalBtnConfirm} onClick={confirmSwap}>
                Yes, Swap it
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        show={confirmDialog.show}
        message={confirmDialog.message}
        onConfirm={handleConfirm}
        onCancel={handleCancelConfirm}
      />
    </>
  );
}


export default Nutrition;