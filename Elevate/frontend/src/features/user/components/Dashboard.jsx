import { Link } from 'react-router-dom';
import { Dumbbell, Utensils, TrendingUp, Flame, Target, Clock, ChevronRight, RotateCcw, Sparkles } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';
import { useAuth } from '@/contexts/AuthContext.jsx';
import { useState, useEffect } from 'react';
import { mlAPI } from '@/services/api.js';
import { toast } from 'sonner';

export function Dashboard() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState({
    calorieData: [
      { name: 'Consumed', value: 1850, color: '#22C55E' },
      { name: 'Remaining', value: 450, color: '#E5E7EB' }
    ],
    weeklyProgress: [
      { day: 'Mon', calories: 2100 },
      { day: 'Tue', calories: 2250 },
      { day: 'Wed', calories: 2000 },
      { day: 'Thu', calories: 2300 },
      { day: 'Fri', calories: 2150 },
      { day: 'Sat', calories: 1850 },
      { day: 'Sun', calories: 2200 }
    ],
    quickStats: [
      { label: 'Calories', value: '1,850', unit: 'kcal', icon: Flame, color: '#F97316' },
      { label: 'Workouts', value: '3', unit: 'this week', icon: Dumbbell, color: '#3B82F6' },
      { label: 'Weight', value: '68.5', unit: 'kg', icon: Target, color: '#22C55E' },
      { label: 'Streak', value: '12', unit: 'days', icon: Clock, color: '#8B5CF6' }
    ],
    todayWorkout: [
      { name: 'Push-ups', sets: '3 sets × 15 reps' },
      { name: 'Squats', sets: '4 sets × 12 reps' },
      { name: 'Plank', sets: '3 sets × 45 sec' }
    ],
    todayMeals: [
      { meal: 'Breakfast', name: 'Protein Oatmeal', calories: '450 kcal' },
      { meal: 'Lunch', name: 'Grilled Chicken Salad', calories: '650 kcal' },
      { meal: 'Dinner', name: 'Salmon & Vegetables', calories: '750 kcal' }
    ],
    dailyGoals: [
      { label: 'Steps', current: 8500, goal: 10000, color: '#3B82F6' },
      { label: 'Water', current: 6, goal: 8, color: '#22C55E', unit: 'glasses' },
      { label: 'Sleep', current: 7, goal: 8, color: '#8B5CF6', unit: 'hours' }
    ]
  });

  const [mlRecommendations, setMlRecommendations] = useState({
    workout: null,
    meal: null
  });
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  // Load personalized data based on user profile
  useEffect(() => {
    if (user) {
      // Update dashboard data based on user profile
      const updatedData = {
        ...dashboardData,
        quickStats: [
          { label: 'Calories', value: user?.weight ? `${Math.round(user.weight * 22)}-${Math.round(user.weight * 25)}` : '2000', unit: 'kcal', icon: Flame, color: '#F97316' },
          { label: 'Workouts', value: '3', unit: 'this week', icon: Dumbbell, color: '#3B82F6' },
          { label: user?.weight ? 'Weight' : 'Target', value: user?.weight ? `${user.weight} kg` : '68.5 kg', unit: user?.height ? `${user.height} cm` : '170 cm', icon: Target, color: '#22C55E' },
          { label: 'Streak', value: '12', unit: 'days', icon: Clock, color: '#8B5CF6' }
        ],
        dailyGoals: [
          { label: 'Steps', current: 8500, goal: user?.activityLevel === 'sedentary' ? 7000 : user?.activityLevel === 'light' ? 8000 : user?.activityLevel === 'moderate' ? 10000 : user?.activityLevel === 'active' ? 12000 : user?.activityLevel === 'very-active' ? 15000 : 10000, color: '#3B82F6' },
          { label: 'Water', current: 6, goal: user?.weight ? Math.ceil(user.weight / 0.453592 / 8) : 8, color: '#22C55E', unit: 'glasses' },
          { label: 'Sleep', current: 7, goal: 8, color: '#8B5CF6', unit: 'hours' }
        ]
      };

      setDashboardData(updatedData);

      // Load ML recommendations when dashboard loads
      fetchMLRecommendations();
    }
  }, [user]);

  const fetchMLRecommendations = async () => {
    if (!user) return;

    setLoadingRecommendations(true);
    try {
      const response = await mlAPI.getPersonalizedRecommendations({});
      setMlRecommendations({
        workout: response.data.workout,
        meal: response.data.meal
      });
      toast.success('AI recommendations loaded!');
    } catch (error) {
      console.error('Error fetching ML recommendations:', error);
      toast.error('Failed to load AI recommendations');
    } finally {
      setLoadingRecommendations(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl mb-2" style={{ fontFamily: 'var(--font-poppins)' }}>
                Welcome back, {user?.name || 'User'}! 👋
              </h1>
              <p className="text-gray-600">
                {user?.fitnessGoals?.length
                  ? `Here's your fitness summary for today based on your goal: ${user.fitnessGoals.join(', ')}.`
                  : "Here's your fitness summary for today"}
              </p>
            </div>
            <button
              onClick={fetchMLRecommendations}
              disabled={loadingRecommendations}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                loadingRecommendations
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-[#22C55E] hover:bg-[#16A34A] text-white'
              }`}
            >
              {loadingRecommendations ? (
                <>
                  <RotateCcw className="w-4 h-4 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Refresh AI Recommendations
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {dashboardData.quickStats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="bg-white rounded-2xl p-6 shadow-sm">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center mb-3"
                  style={{ backgroundColor: `${stat.color}15` }}
                >
                  <Icon className="w-6 h-6" style={{ color: stat.color }} />
                </div>
                <p className="text-2xl mb-1">{stat.value}</p>
                <p className="text-sm text-gray-600">{stat.label}</p>
                <p className="text-xs text-gray-400">{stat.unit}</p>
              </div>
            );
          })}
        </div>

        {/* AI Recommendations Section */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* AI Workout Recommendation */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Dumbbell className="w-6 h-6 text-[#3B82F6]" />
                <h3 className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>
                  AI Workout Recommendation
                </h3>
              </div>
              <span className="text-xs bg-[#3B82F6]/10 text-[#3B82F6] px-2 py-1 rounded-full">AI-Powered</span>
            </div>

            {mlRecommendations.workout ? (
              <div>
                {mlRecommendations.workout.error ? (
                  <div className="text-center py-8">
                    <div className="text-gray-400 mb-2">⚠️ No workout recommendation available</div>
                    <p className="text-sm text-gray-500">Complete your profile to get personalized workout suggestions</p>
                  </div>
                ) : (
                  <>
                    <div className="mb-4">
                      <h4 className="font-semibold text-lg">{mlRecommendations.workout.title || 'Personalized Workout'}</h4>
                    </div>
                    <div className="space-y-3">
                      {mlRecommendations.workout.exercises && mlRecommendations.workout.exercises.slice(0, 3).map((exercise, index) => (
                        <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                          <span>{exercise.name || exercise.exercise}</span>
                          <span className="text-sm text-gray-600">{exercise.sets || exercise.reps}</span>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                {loadingRecommendations ? 'AI is analyzing your profile...' : 'Click "Refresh AI Recommendations" to see AI workout suggestions'}
              </div>
            )}
          </div>

          {/* AI Meal Recommendation */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Utensils className="w-6 h-6 text-[#22C55E]" />
                <h3 className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>
                  AI Meal Recommendation
                </h3>
              </div>
              <span className="text-xs bg-[#22C55E]/10 text-[#22C55E] px-2 py-1 rounded-full">AI-Powered</span>
            </div>

            {mlRecommendations.meal ? (
              <div>
                {mlRecommendations.meal.error ? (
                  <div className="text-center py-8">
                    <div className="text-gray-400 mb-2">⚠️ No meal recommendation available</div>
                    <p className="text-sm text-gray-500">Complete your profile to get personalized meal suggestions</p>
                  </div>
                ) : (
                  <>
                    <div className="mb-4">
                      <h4 className="font-semibold text-lg">{mlRecommendations.meal.title || 'Personalized Meal'}</h4>
                    </div>
                    <div className="space-y-3">
                      {mlRecommendations.meal.meals && mlRecommendations.meal.meals.slice(0, 3).map((meal, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded-xl">
                          <div className="flex justify-between items-center mb-1">
                            <span>{meal.name || meal.food}</span>
                            <span className="text-sm text-gray-600">{meal.calories || meal.calories} kcal</span>
                          </div>
                          <div className="flex text-xs text-gray-500 gap-4">
                            <span>Protein: {meal.protein || meal.protein_g || 0}g</span>
                            <span>Carbs: {meal.carbohydrate || meal.carbs_g || 0}g</span>
                            <span>Fat: {meal.fat || meal.fat_g || 0}g</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                {loadingRecommendations ? 'AI is analyzing your profile...' : 'Click "Refresh AI Recommendations" to see AI meal suggestions'}
              </div>
            )}
          </div>
        </div>

        {/* Main Cards */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Today's Workout - personalized based on fitness goals */}
          <Link to="/workout" className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>
                Today's Workout
              </h3>
              <Dumbbell className="w-6 h-6 text-[#3B82F6]" />
            </div>
            <div className="space-y-3 mb-4">
              {(user?.fitnessGoals?.includes('muscle-gain')
                ? [
                    { name: 'Bench Press', sets: '4 sets × 8 reps' },
                    { name: 'Squats', sets: '4 sets × 10 reps' },
                    { name: 'Pull-ups', sets: '3 sets × 6 reps' }
                  ]
                : user?.fitnessGoals?.includes('weight-loss')
                  ? [
                      { name: 'Running', sets: '30 mins cardio' },
                      { name: 'Squats', sets: '3 sets × 15 reps' },
                      { name: 'Lunges', sets: '3 sets × 12 reps each' }
                    ]
                  : user?.fitnessGoals?.includes('endurance')
                    ? [
                        { name: 'Cycling', sets: '45 mins' },
                        { name: 'Swimming', sets: '30 mins' },
                        { name: 'HIIT', sets: '20 mins' }
                      ]
                    : dashboardData.todayWorkout
              ).map((exercise, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                  <span>{exercise.name}</span>
                  <span className="text-sm text-gray-600">{exercise.sets}</span>
                </div>
              ))}
            </div>
            <button className="w-full py-3 bg-[#3B82F6] text-white rounded-xl hover:bg-[#2563EB] transition-colors flex items-center justify-center gap-2">
              Start Workout
              <ChevronRight className="w-5 h-5" />
            </button>
          </Link>

          {/* Today's Meals - personalized based on dietary preferences */}
          <Link to="/meal-plan" className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>
                Today's Meals
              </h3>
              <Utensils className="w-6 h-6 text-[#22C55E]" />
            </div>
            <div className="space-y-3 mb-4">
              {(user?.dietaryPreferences?.includes('vegetarian')
                ? [
                    { meal: 'Breakfast', name: 'Vegetable Omelette', calories: '350 kcal' },
                    { meal: 'Lunch', name: 'Quinoa Salad', calories: '450 kcal' },
                    { meal: 'Dinner', name: 'Tofu Stir-fry', calories: '500 kcal' }
                  ]
                : user?.dietaryPreferences?.includes('vegan')
                  ? [
                      { meal: 'Breakfast', name: 'Oatmeal with Fruits', calories: '300 kcal' },
                      { meal: 'Lunch', name: 'Chickpea Salad', calories: '400 kcal' },
                      { meal: 'Dinner', name: 'Lentil Curry', calories: '450 kcal' }
                    ]
                  : user?.dietaryPreferences?.includes('keto')
                    ? [
                        { meal: 'Breakfast', name: 'Avocado & Eggs', calories: '450 kcal' },
                        { meal: 'Lunch', name: 'Chicken Salad', calories: '500 kcal' },
                        { meal: 'Dinner', name: 'Salmon with Veggies', calories: '600 kcal' }
                      ]
                    : user?.dietaryPreferences?.includes('high-protein')
                      ? [
                          { meal: 'Breakfast', name: 'Protein Pancakes', calories: '400 kcal' },
                          { meal: 'Lunch', name: 'Grilled Chicken', calories: '550 kcal' },
                          { meal: 'Dinner', name: 'Protein Shake', calories: '300 kcal' }
                        ]
                      : dashboardData.todayMeals
              ).map((meal, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-xl">
                  <div className="flex justify-between items-center mb-1">
                    <span>{meal.meal}</span>
                    <span className="text-sm text-gray-600">{meal.calories}</span>
                  </div>
                  <p className="text-sm text-gray-600">{meal.name}</p>
                </div>
              ))}
            </div>
            <button className="w-full py-3 bg-[#22C55E] text-white rounded-xl hover:bg-[#16A34A] transition-colors flex items-center justify-center gap-2">
              View Meal Plan
              <ChevronRight className="w-5 h-5" />
            </button>
          </Link>

          {/* Progress Summary */}
          <Link to="/analytics" className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>
                Progress Summary
              </h3>
              <TrendingUp className="w-6 h-6 text-[#F97316]" />
            </div>

            {/* Calorie Chart */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Daily Calories</span>
                <span className="text-sm">
                  {user?.weight ? `${Math.round(user.weight * 22) - 500}` : '1,850'}
                  /
                  {user?.weight ? `${Math.round(user.weight * 22)}` : '2,300'}
                </span>
              </div>
              <ResponsiveContainer width="100%" height={120}>
                <PieChart>
                  <Pie
                    data={dashboardData.calorieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={60}
                    dataKey="value"
                  >
                    {dashboardData.calorieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Weekly Chart */}
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">Weekly Calories</p>
              <ResponsiveContainer width="100%" height={80}>
                <LineChart data={dashboardData.weeklyProgress}>
                  <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                  <Line type="monotone" dataKey="calories" stroke="#22C55E" strokeWidth={2} dot={false} />
                  <Tooltip />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <button className="w-full py-3 bg-[#F97316] text-white rounded-xl hover:bg-[#EA580C] transition-colors flex items-center justify-center gap-2">
              View Analytics
              <ChevronRight className="w-5 h-5" />
            </button>
          </Link>
        </div>

        {/* Daily Goals */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <h3 className="text-xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
            Daily Goals
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            {dashboardData.dailyGoals.map((goal, index) => {
              const percentage = (goal.current / goal.goal) * 100;
              return (
                <div key={index}>
                  <div className="flex justify-between mb-2">
                    <span>{goal.label}</span>
                    <span className="text-sm text-gray-600">
                      {goal.current} / {goal.goal} {goal.unit || ''}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="h-3 rounded-full transition-all"
                      style={{ width: `${percentage}%`, backgroundColor: goal.color }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}