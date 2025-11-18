import { useState } from 'react';
import { TrendingUp, TrendingDown, ChevronLeft, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

export function Analytics() {
  const [timeRange, setTimeRange] = useState('month');

  const weightData = [
    { date: 'Jan 1', weight: 72.5, bmi: 23.8 },
    { date: 'Jan 8', weight: 72.0, bmi: 23.6 },
    { date: 'Jan 15', weight: 71.5, bmi: 23.4 },
    { date: 'Jan 22', weight: 71.0, bmi: 23.2 },
    { date: 'Jan 29', weight: 70.5, bmi: 23.1 },
    { date: 'Feb 5', weight: 70.0, bmi: 22.9 },
    { date: 'Feb 12', weight: 69.5, bmi: 22.7 },
    { date: 'Feb 19', weight: 69.0, bmi: 22.6 },
    { date: 'Feb 26', weight: 68.5, bmi: 22.4 }
  ];

  const calorieData = [
    { date: 'Mon', consumed: 2100, burned: 2400, target: 2300 },
    { date: 'Tue', consumed: 2250, burned: 2350, target: 2300 },
    { date: 'Wed', consumed: 2000, burned: 2500, target: 2300 },
    { date: 'Thu', consumed: 2300, burned: 2400, target: 2300 },
    { date: 'Fri', consumed: 2150, burned: 2300, target: 2300 },
    { date: 'Sat', consumed: 1850, burned: 2200, target: 2300 },
    { date: 'Sun', consumed: 2200, burned: 2450, target: 2300 }
  ];

  const workoutData = [
    { day: 'Mon', duration: 45, calories: 350 },
    { day: 'Tue', duration: 60, calories: 450 },
    { day: 'Wed', duration: 30, calories: 250 },
    { day: 'Thu', duration: 50, calories: 400 },
    { day: 'Fri', duration: 55, calories: 420 },
    { day: 'Sat', duration: 70, calories: 550 },
    { day: 'Sun', duration: 40, calories: 300 }
  ];

  const macroData = [
    { day: 'Mon', protein: 150, carbs: 220, fats: 65 },
    { day: 'Tue', protein: 165, carbs: 200, fats: 70 },
    { day: 'Wed', protein: 140, carbs: 180, fats: 60 },
    { day: 'Thu', protein: 170, carbs: 230, fats: 68 },
    { day: 'Fri', protein: 155, carbs: 210, fats: 65 },
    { day: 'Sat', protein: 145, carbs: 190, fats: 55 },
    { day: 'Sun', protein: 160, carbs: 215, fats: 72 }
  ];

  const stats = [
    {
      label: 'Weight Lost',
      value: '4.0 kg',
      change: '-5.5%',
      trend: 'down',
      color: '#22C55E'
    },
    {
      label: 'BMI',
      value: '22.4',
      change: '-1.4',
      trend: 'down',
      color: '#3B82F6'
    },
    {
      label: 'Avg Calories',
      value: '2,122',
      change: '+150',
      trend: 'up',
      color: '#F97316'
    },
    {
      label: 'Workout Days',
      value: '24',
      change: '+8',
      trend: 'up',
      color: '#8B5CF6'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Link to="/dashboard" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <ChevronLeft className="w-5 h-5" />
            Back to Dashboard
          </Link>
          <div className="flex items-center gap-2 bg-white rounded-lg p-1 shadow-sm">
            {(['week', 'month', 'year']).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-md transition-colors capitalize ${
                  timeRange === range
                    ? 'bg-[#22C55E] text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>

        <h1 className="text-3xl mb-2" style={{ fontFamily: 'var(--font-poppins)' }}>
          Progress Analytics
        </h1>
        <p className="text-gray-600 mb-8">Track your fitness journey over time</p>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-2xl p-6 shadow-lg">
              <p className="text-sm text-gray-600 mb-2">{stat.label}</p>
              <p className="text-3xl mb-2" style={{ fontFamily: 'var(--font-poppins)' }}>
                {stat.value}
              </p>
              <div className="flex items-center gap-1">
                {stat.trend === 'down' ? (
                  <TrendingDown className="w-4 h-4 text-[#22C55E]" />
                ) : (
                  <TrendingUp className="w-4 h-4 text-[#3B82F6]" />
                )}
                <span className={`text-sm ${stat.trend === 'down' ? 'text-[#22C55E]' : 'text-[#3B82F6]'}`}>
                  {stat.change}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Weight & BMI Chart */}
        <div className="bg-white rounded-2xl p-6 shadow-lg mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>
              Weight & BMI Trend
            </h3>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>Last 2 months</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={weightData}>
              <defs>
                <linearGradient id="colorWeight" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22C55E" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22C55E" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorBMI" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem'
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="weight"
                stroke="#22C55E"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorWeight)"
                name="Weight (kg)"
              />
              <Area
                type="monotone"
                dataKey="bmi"
                stroke="#3B82F6"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorBMI)"
                name="BMI"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Calories Chart */}
        <div className="bg-white rounded-2xl p-6 shadow-lg mb-8">
          <h3 className="text-xl mb-6" style={{ fontFamily: 'var(--font-poppins)' }}>
            Calories: Consumed vs Burned
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={calorieData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem'
                }}
              />
              <Legend />
              <Bar dataKey="consumed" fill="#22C55E" name="Consumed" radius={[8, 8, 0, 0]} />
              <Bar dataKey="burned" fill="#F97316" name="Burned" radius={[8, 8, 0, 0]} />
              <Line type="monotone" dataKey="target" stroke="#3B82F6" strokeWidth={2} name="Target" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Workout Stats */}
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <h3 className="text-xl mb-6" style={{ fontFamily: 'var(--font-poppins)' }}>
              Workout Duration & Calories
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={workoutData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="day" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem'
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="duration"
                  stroke="#3B82F6"
                  strokeWidth={3}
                  name="Duration (min)"
                  dot={{ r: 5 }}
                />
                <Line
                  type="monotone"
                  dataKey="calories"
                  stroke="#F97316"
                  strokeWidth={3}
                  name="Calories Burned"
                  dot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Macros Breakdown */}
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <h3 className="text-xl mb-6" style={{ fontFamily: 'var(--font-poppins)' }}>
              Macronutrient Breakdown
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={macroData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="day" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.5rem'
                  }}
                />
                <Legend />
                <Bar dataKey="protein" stackId="a" fill="#3B82F6" name="Protein (g)" radius={[0, 0, 0, 0]} />
                <Bar dataKey="carbs" stackId="a" fill="#22C55E" name="Carbs (g)" radius={[0, 0, 0, 0]} />
                <Bar dataKey="fats" stackId="a" fill="#F59E0B" name="Fats (g)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Achievements */}
        <div className="bg-gradient-to-r from-[#22C55E] to-[#3B82F6] rounded-2xl p-8 mt-8 text-white">
          <h3 className="text-2xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
            Recent Achievements 🎉
          </h3>
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { title: '10-Day Streak', description: 'Logged meals for 10 consecutive days' },
              { title: 'Weight Milestone', description: 'Lost 5kg since starting' },
              { title: 'Workout Warrior', description: 'Completed 25 workouts this month' }
            ].map((achievement, index) => (
              <div key={index} className="bg-white/20 backdrop-blur-sm rounded-xl p-4">
                <p className="text-lg mb-1">{achievement.title}</p>
                <p className="text-sm opacity-90">{achievement.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}