import { Link } from 'react-router-dom';
import { Dumbbell, Utensils, TrendingUp, Flame, Target, Clock, ChevronRight } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export function Dashboard() {
  const calorieData = [
    { name: 'Consumed', value: 1850, color: '#22C55E' },
    { name: 'Remaining', value: 450, color: '#E5E7EB' }
  ];

  const weeklyProgress = [
    { day: 'Mon', calories: 2100 },
    { day: 'Tue', calories: 2250 },
    { day: 'Wed', calories: 2000 },
    { day: 'Thu', calories: 2300 },
    { day: 'Fri', calories: 2150 },
    { day: 'Sat', calories: 1850 },
    { day: 'Sun', calories: 2200 }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl mb-2" style={{ fontFamily: 'var(--font-poppins)' }}>
            Welcome back, Alex! 👋
          </h1>
          <p className="text-gray-600">Here's your fitness summary for today</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Calories', value: '1,850', unit: 'kcal', icon: Flame, color: '#F97316' },
            { label: 'Workouts', value: '3', unit: 'this week', icon: Dumbbell, color: '#3B82F6' },
            { label: 'Weight', value: '68.5', unit: 'kg', icon: Target, color: '#22C55E' },
            { label: 'Streak', value: '12', unit: 'days', icon: Clock, color: '#8B5CF6' }
          ].map((stat, index) => (
            <div key={index} className="bg-white rounded-2xl p-6 shadow-sm">
              <div 
                className="w-12 h-12 rounded-xl flex items-center justify-center mb-3"
                style={{ backgroundColor: `${stat.color}15` }}
              >
                <stat.icon className="w-6 h-6" style={{ color: stat.color }} />
              </div>
              <p className="text-2xl mb-1">{stat.value}</p>
              <p className="text-sm text-gray-600">{stat.label}</p>
              <p className="text-xs text-gray-400">{stat.unit}</p>
            </div>
          ))}
        </div>

        {/* Main Cards */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Today's Workout */}
          <Link to="/workout" className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>
                Today's Workout
              </h3>
              <Dumbbell className="w-6 h-6 text-[#3B82F6]" />
            </div>
            <div className="space-y-3 mb-4">
              {[
                { name: 'Push-ups', sets: '3 sets × 15 reps' },
                { name: 'Squats', sets: '4 sets × 12 reps' },
                { name: 'Plank', sets: '3 sets × 45 sec' }
              ].map((exercise, index) => (
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

          {/* Today's Meals */}
          <Link to="/meal-plan" className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>
                Today's Meals
              </h3>
              <Utensils className="w-6 h-6 text-[#22C55E]" />
            </div>
            <div className="space-y-3 mb-4">
              {[
                { meal: 'Breakfast', name: 'Protein Oatmeal', calories: '450 kcal' },
                { meal: 'Lunch', name: 'Grilled Chicken Salad', calories: '650 kcal' },
                { meal: 'Dinner', name: 'Salmon & Vegetables', calories: '750 kcal' }
              ].map((meal, index) => (
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
                <span className="text-sm">1,850 / 2,300</span>
              </div>
              <ResponsiveContainer width="100%" height={120}>
                <PieChart>
                  <Pie
                    data={calorieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={60}
                    dataKey="value"
                  >
                    {calorieData.map((entry, index) => (
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
                <LineChart data={weeklyProgress}>
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
            {[
              { label: 'Steps', current: 8500, goal: 10000, color: '#3B82F6' },
              { label: 'Water', current: 6, goal: 8, color: '#22C55E', unit: 'glasses' },
              { label: 'Sleep', current: 7, goal: 8, color: '#8B5CF6', unit: 'hours' }
            ].map((goal, index) => {
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
