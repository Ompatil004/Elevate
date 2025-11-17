import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Ruler, Weight, Calendar, Activity, Utensils, ChevronRight } from 'lucide-react';

interface ProfileSetupProps {
  onComplete: () => void;
}

export function ProfileSetup({ onComplete }: ProfileSetupProps) {
  const [formData, setFormData] = useState({
    height: '',
    weight: '',
    age: '',
    activityLevel: 'moderate',
    dietPreference: 'balanced'
  });
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onComplete();
    navigate('/dashboard');
  };

  const activityLevels = [
    { value: 'sedentary', label: 'Sedentary', description: 'Little to no exercise' },
    { value: 'light', label: 'Light', description: '1-3 days/week' },
    { value: 'moderate', label: 'Moderate', description: '3-5 days/week' },
    { value: 'active', label: 'Active', description: '6-7 days/week' },
    { value: 'very-active', label: 'Very Active', description: 'Intense daily exercise' }
  ];

  const dietPreferences = [
    { value: 'balanced', label: 'Balanced', icon: '🥗' },
    { value: 'low-carb', label: 'Low Carb', icon: '🥑' },
    { value: 'high-protein', label: 'High Protein', icon: '🍗' },
    { value: 'vegetarian', label: 'Vegetarian', icon: '🥦' },
    { value: 'vegan', label: 'Vegan', icon: '🌱' },
    { value: 'keto', label: 'Keto', icon: '🥓' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-3xl shadow-xl p-8 md:p-12">
          <h2 className="text-3xl mb-2 text-center" style={{ fontFamily: 'var(--font-poppins)' }}>
            Complete Your Profile
          </h2>
          <p className="text-center text-gray-600 mb-8">
            Help us personalize your fitness experience
          </p>

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Metrics */}
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <label className="block mb-2 text-gray-700">Height (cm)</label>
                <div className="relative">
                  <Ruler className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#3B82F6]" />
                  <input
                    type="number"
                    value={formData.height}
                    onChange={(e) => setFormData({ ...formData, height: e.target.value })}
                    className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                    placeholder="170"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block mb-2 text-gray-700">Weight (kg)</label>
                <div className="relative">
                  <Weight className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#22C55E]" />
                  <input
                    type="number"
                    value={formData.weight}
                    onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                    className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                    placeholder="70"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block mb-2 text-gray-700">Age</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#F97316]" />
                  <input
                    type="number"
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                    className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                    placeholder="25"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Activity Level */}
            <div>
              <label className="flex items-center gap-2 mb-4 text-gray-700">
                <Activity className="w-5 h-5 text-[#3B82F6]" />
                Activity Level
              </label>
              <div className="space-y-3">
                {activityLevels.map((level) => (
                  <label
                    key={level.value}
                    className={`flex items-center justify-between p-4 border-2 rounded-xl cursor-pointer transition-all ${
                      formData.activityLevel === level.value
                        ? 'border-[#22C55E] bg-[#22C55E]/5'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <input
                        type="radio"
                        name="activityLevel"
                        value={level.value}
                        checked={formData.activityLevel === level.value}
                        onChange={(e) => setFormData({ ...formData, activityLevel: e.target.value })}
                        className="w-5 h-5 text-[#22C55E]"
                      />
                      <div>
                        <p>{level.label}</p>
                        <p className="text-sm text-gray-500">{level.description}</p>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Diet Preference */}
            <div>
              <label className="flex items-center gap-2 mb-4 text-gray-700">
                <Utensils className="w-5 h-5 text-[#22C55E]" />
                Diet Preference
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {dietPreferences.map((diet) => (
                  <label
                    key={diet.value}
                    className={`flex flex-col items-center justify-center p-6 border-2 rounded-xl cursor-pointer transition-all ${
                      formData.dietPreference === diet.value
                        ? 'border-[#22C55E] bg-[#22C55E]/5'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="dietPreference"
                      value={diet.value}
                      checked={formData.dietPreference === diet.value}
                      onChange={(e) => setFormData({ ...formData, dietPreference: e.target.value })}
                      className="sr-only"
                    />
                    <span className="text-3xl mb-2">{diet.icon}</span>
                    <span className="text-center">{diet.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-4 bg-[#F97316] text-white rounded-xl hover:bg-[#EA580C] transition-colors flex items-center justify-center gap-2"
            >
              Continue to Dashboard
              <ChevronRight className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
