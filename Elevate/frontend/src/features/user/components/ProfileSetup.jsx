import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext.jsx';
import { Ruler, Weight, Calendar, Activity, Utensils, Heart, Dumbbell, Home, Briefcase, Clock, UtensilsCrossed, ChefHat, Apple, HeartPulse, ChevronRight } from 'lucide-react';
import { toast } from 'sonner';

export function ProfileSetup() {
  const [formData, setFormData] = useState({
    height: '',
    weight: '',
    age: '',
    activityLevel: 'moderate',
    dietaryPreferences: ['balanced'],
    fitnessGoals: ['maintenance'], // Keep as array for compatibility
    gender: 'other',
    healthConditions: [], // Optional: for any health conditions
    // Additional fields for ML model
    experienceLevel: 'beginner', // For workout recommendations
    equipmentAvailable: [], // Equipment at home/gym for workouts
    timeAvailable: 30, // Minutes available for workouts
    targetMuscleGroup: 'full-body', // Primary muscle group to target
    injuryHistory: [], // Past injuries to avoid
    preferredExerciseType: 'cardio', // Type of exercises preferred
    intensityLevel: 'moderate', // Workout intensity
    frequencyPerWeek: 3, // Workout sessions per week
    focusArea: 'strength', // Focus area (strength, hypertrophy, etc.)
    gymOrHome: 'home', // Where they prefer to workout
    allergies: [], // Food allergies
    mealTime: 'moderate', // Time available for meal prep
    budget: 15, // Budget per meal
    proteinTarget: 25, // Daily protein target
    carbTarget: 45, // Daily carb target
    fatTarget: 15, // Daily fat target
    preferredCuisine: 'italian', // Preferred cuisine type
    cookingSkill: 'intermediate', // Cooking skill level
    ingredients: [], // Ingredients they like
    avoidIngredients: [], // Ingredients to avoid
    spiceLevel: 3, // Spice tolerance (1-5)
    prepTime: 30, // Maximum prep time in minutes
  });
  const [loading, setLoading] = useState(false);
  const { user, completeProfile } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Prepare profile completion data according to backend schema
      const profileData = {
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
        age: parseInt(formData.age),
        activityLevel: formData.activityLevel,
        dietaryPreferences: formData.dietaryPreferences,
        fitnessGoals: formData.fitnessGoals,
        gender: formData.gender,
        healthConditions: formData.healthConditions,
        // Additional ML fields
        experienceLevel: formData.experienceLevel,
        equipmentAvailable: formData.equipmentAvailable,
        timeAvailable: formData.timeAvailable,
        targetMuscleGroup: formData.targetMuscleGroup,
        injuryHistory: formData.injuryHistory,
        preferredExerciseType: formData.preferredExerciseType,
        intensityLevel: formData.intensityLevel,
        frequencyPerWeek: formData.frequencyPerWeek,
        focusArea: formData.focusArea,
        gymOrHome: formData.gymOrHome,
        allergies: formData.allergies,
        mealTime: formData.mealTime,
        budget: formData.budget,
        proteinTarget: formData.proteinTarget,
        carbTarget: formData.carbTarget,
        fatTarget: formData.fatTarget,
        preferredCuisine: formData.preferredCuisine,
        cookingSkill: formData.cookingSkill,
        ingredients: formData.ingredients,
        avoidIngredients: formData.avoidIngredients,
        spiceLevel: formData.spiceLevel,
        prepTime: formData.prepTime,
        profileCompleted: true // Mark profile as completed
      };

      // Submit profile completion to backend
      await completeProfile(profileData);
      toast.success('Profile setup completed successfully!');
      navigate('/dashboard');
    } catch (error) {
      console.error('Profile setup failed:', error);
      toast.error('Profile setup failed: ' + (error.response?.data?.msg || error.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const updateSelectArray = (arrayName, value, add) => {
    setFormData(prev => ({
      ...prev,
      [arrayName]: add
        ? [...prev[arrayName], value]
        : prev[arrayName].filter(item => item !== value)
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FAFAFA] to-[#F0F9FF] py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-3xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>Profile Setup</h1>
            <p className="text-gray-600">Complete your profile to get personalized recommendations</p>
          </div>

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
                  <Weight className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#3B82F6]" />
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
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#3B82F6]" />
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

            {/* Gender Selection */}
            <div>
              <label className="block mb-3 text-gray-700">Gender</label>
              <div className="grid grid-cols-3 gap-3">
                {['male', 'female', 'other'].map((gender) => (
                  <button
                    key={gender}
                    type="button"
                    onClick={() => setFormData({ ...formData, gender })}
                    className={`py-4 px-4 border-2 rounded-xl capitalize transition-all ${
                      formData.gender === gender
                        ? 'border-[#22C55E] bg-[#22C55E]/10'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {gender}
                  </button>
                ))}
              </div>
            </div>

            {/* Activity Level */}
            <div>
              <label className="block mb-3 text-gray-700">Activity Level</label>
              <div className="grid grid-cols-3 gap-3">
                {['sedentary', 'moderate', 'active'].map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setFormData({ ...formData, activityLevel: level })}
                    className={`py-4 px-4 border-2 rounded-xl capitalize transition-all ${
                      formData.activityLevel === level
                        ? 'border-[#22C55E] bg-[#22C55E]/10'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            {/* Fitness Goals */}
            <div>
              <label className="block mb-3 text-gray-700">Fitness Goals</label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {['weight-loss', 'muscle-gain', 'maintenance', 'endurance', 'flexibility'].map((goal) => (
                  <button
                    key={goal}
                    type="button"
                    onClick={() => updateSelectArray('fitnessGoals', goal, !formData.fitnessGoals.includes(goal))}
                    className={`py-4 px-4 border-2 rounded-xl capitalize transition-all ${
                      formData.fitnessGoals.includes(goal)
                        ? 'border-[#22C55E] bg-[#22C55E]/10'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {goal.replace('-', ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Dietary Preferences */}
            <div>
              <label className="block mb-3 text-gray-700">Dietary Preferences</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {['balanced', 'high-protein', 'low-carb', 'keto', 'vegan', 'vegetarian', 'paleo', 'mediterranean'].map((pref) => (
                  <button
                    key={pref}
                    type="button"
                    onClick={() => updateSelectArray('dietaryPreferences', pref, !formData.dietaryPreferences.includes(pref))}
                    className={`py-4 px-4 border-2 rounded-xl capitalize transition-all ${
                      formData.dietaryPreferences.includes(pref)
                        ? 'border-[#22C55E] bg-[#22C55E]/10'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {pref}
                  </button>
                ))}
              </div>
            </div>

            {/* Health Conditions */}
            <div>
              <label className="block mb-3 text-gray-700">Health Conditions (Optional)</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {['diabetes', 'hypertension', 'heart-disease', 'arthritis', 'asthma', 'none'].map((condition) => (
                  <label key={condition} className="flex items-center gap-2 p-3 border border-gray-300 rounded-xl cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.healthConditions.includes(condition)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFormData({
                            ...formData,
                            healthConditions: [...formData.healthConditions, condition]
                          });
                        } else {
                          setFormData({
                            ...formData,
                            healthConditions: formData.healthConditions.filter(item => item !== condition)
                          });
                        }
                      }}
                      className="w-4 h-4 text-[#22C55E]"
                    />
                    <span className="capitalize">{condition.replace('-', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Workout Preferences */}
            <div className="border-t pt-8">
              <h3 className="text-xl mb-6 flex items-center gap-2" style={{ fontFamily: 'var(--font-poppins)' }}>
                <Dumbbell className="w-6 h-6 text-[#22C55E]" />
                Workout Preferences
              </h3>

              {/* Experience Level */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Experience Level</label>
                <div className="grid grid-cols-3 gap-3">
                  {['beginner', 'intermediate', 'advanced'].map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setFormData({ ...formData, experienceLevel: level })}
                      className={`py-4 px-4 border-2 rounded-xl capitalize transition-all ${
                        formData.experienceLevel === level
                          ? 'border-[#22C55E] bg-[#22C55E]/10'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              {/* Equipment Available */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Equipment Available</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['dumbbells', 'barbell', 'resistance-bands', 'gym', 'bodyweight-only'].map((equip) => (
                    <label key={equip} className="flex items-center gap-2 p-3 border border-gray-300 rounded-xl cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.equipmentAvailable.includes(equip)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              equipmentAvailable: [...formData.equipmentAvailable, equip]
                            });
                          } else {
                            setFormData({
                              ...formData,
                              equipmentAvailable: formData.equipmentAvailable.filter(item => item !== equip)
                            });
                          }
                        }}
                        className="w-4 h-4 text-[#22C55E]"
                      />
                      <span className="capitalize">{equip.replace('-', ' ')}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Time Available for Workouts */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Time Available for Workouts (minutes per session)</label>
                <input
                  type="range"
                  min="10"
                  max="120"
                  value={formData.timeAvailable}
                  onChange={(e) => setFormData({ ...formData, timeAvailable: parseInt(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-gray-500 mt-1">
                  <span>10 min</span>
                  <span className="font-medium">{formData.timeAvailable} min</span>
                  <span>120 min</span>
                </div>
              </div>

              {/* Target Muscle Group */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Primary Target Muscle Group</label>
                <select
                  value={formData.targetMuscleGroup}
                  onChange={(e) => setFormData({ ...formData, targetMuscleGroup: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                >
                  <option value="full-body">Full Body</option>
                  <option value="chest">Chest</option>
                  <option value="back">Back</option>
                  <option value="legs">Legs</option>
                  <option value="arms">Arms</option>
                  <option value="shoulders">Shoulders</option>
                  <option value="core">Core</option>
                </select>
              </div>

              {/* Preferred Exercise Type */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Preferred Exercise Type</label>
                <select
                  value={formData.preferredExerciseType}
                  onChange={(e) => setFormData({ ...formData, preferredExerciseType: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                >
                  <option value="cardio">Cardio</option>
                  <option value="strength">Strength Training</option>
                  <option value="flexibility">Flexibility/Mobility</option>
                  <option value="hiit">HIIT</option>
                  <option value="yoga">Yoga</option>
                  <option value="pilates">Pilates</option>
                </select>
              </div>

              {/* Intensity Level */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Intensity Level</label>
                <select
                  value={formData.intensityLevel}
                  onChange={(e) => setFormData({ ...formData, intensityLevel: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                >
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="high">High</option>
                  <option value="extreme">Extreme</option>
                </select>
              </div>

              {/* Workout Frequency */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Workout Frequency per Week</label>
                <select
                  value={formData.frequencyPerWeek}
                  onChange={(e) => setFormData({ ...formData, frequencyPerWeek: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                >
                  {[1, 2, 3, 4, 5, 6, 7].map((freq) => (
                    <option key={freq} value={freq}>{freq} days</option>
                  ))}
                </select>
              </div>

              {/* Focus Area */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Focus Area</label>
                <select
                  value={formData.focusArea}
                  onChange={(e) => setFormData({ ...formData, focusArea: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                >
                  <option value="strength">Strength</option>
                  <option value="hypertrophy">Hypertrophy (Muscle Growth)</option>
                  <option value="endurance">Endurance</option>
                  <option value="fat-loss">Fat Loss</option>
                </select>
              </div>

              {/* Gym or Home */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Workout Location</label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'gym', icon: <Activity className="w-5 h-5" />, label: 'Gym' },
                    { value: 'home', icon: <Home className="w-5 h-5" />, label: 'Home' },
                    { value: 'outdoor', icon: <Activity className="w-5 h-5" />, label: 'Outdoor' },
                    { value: 'any', icon: <Activity className="w-5 h-5" />, label: 'Any' }
                  ].map((location) => (
                    <button
                      key={location.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, gymOrHome: location.value })}
                      className={`flex flex-col items-center justify-center p-4 border-2 rounded-xl transition-all ${
                        formData.gymOrHome === location.value
                          ? 'border-[#22C55E] bg-[#22C55E]/10'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="text-[#22C55E] mb-2">{location.icon}</div>
                      <span>{location.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Injury History */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Injury History (Optional)</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['knee', 'shoulder', 'back', 'elbow', 'wrist', 'ankle', 'hip'].map((injury) => (
                    <label key={injury} className="flex items-center gap-2 p-3 border border-gray-300 rounded-xl cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.injuryHistory.includes(injury)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              injuryHistory: [...formData.injuryHistory, injury]
                            });
                          } else {
                            setFormData({
                              ...formData,
                              injuryHistory: formData.injuryHistory.filter(item => item !== injury)
                            });
                          }
                        }}
                        className="w-4 h-4 text-[#EF4444]"
                      />
                      <span className="capitalize">{injury}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Nutrition Preferences */}
            <div className="border-t pt-8">
              <h3 className="text-xl mb-6 flex items-center gap-2" style={{ fontFamily: 'var(--font-poppins)' }}>
                <Utensils className="w-6 h-6 text-[#22C55E]" />
                Nutrition Preferences
              </h3>

              {/* Food Allergies */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Food Allergies (Optional)</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['nuts', 'shellfish', 'soy', 'wheat', 'dairy', 'eggs'].map((allergy) => (
                    <label key={allergy} className="flex items-center gap-2 p-3 border border-gray-300 rounded-xl cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.allergies.includes(allergy)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({
                              ...formData,
                              allergies: [...formData.allergies, allergy]
                            });
                          } else {
                            setFormData({
                              ...formData,
                              allergies: formData.allergies.filter(item => item !== allergy)
                            });
                          }
                        }}
                        className="w-4 h-4 text-[#EF4444]"
                      />
                      <span className="capitalize">{allergy}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Preferred Cuisine */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Preferred Cuisine</label>
                <select
                  value={formData.preferredCuisine}
                  onChange={(e) => setFormData({ ...formData, preferredCuisine: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                >
                  <option value="italian">Italian</option>
                  <option value="asian">Asian</option>
                  <option value="mexican">Mexican</option>
                  <option value="american">American</option>
                  <option value="mediterranean">Mediterranean</option>
                  <option value="indian">Indian</option>
                </select>
              </div>

              {/* Cooking Skill */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Cooking Skill Level</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['beginner', 'intermediate', 'advanced'].map((skill) => (
                    <label key={skill} className={`flex items-center justify-center p-4 border-2 rounded-xl cursor-pointer transition-all ${
                      formData.cookingSkill === skill
                        ? 'border-[#22C55E] bg-[#22C55E]/5'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <input
                        type="radio"
                        name="cookingSkill"
                        value={skill}
                        checked={formData.cookingSkill === skill}
                        onChange={(e) => setFormData({ ...formData, cookingSkill: e.target.value })}
                        className="sr-only"
                      />
                      <span className="capitalize">{skill}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Meal Prep Time */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Time Available for Meal Prep (minutes)</label>
                <input
                  type="range"
                  min="5"
                  max="60"
                  value={formData.prepTime}
                  onChange={(e) => setFormData({ ...formData, prepTime: parseInt(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-gray-500 mt-1">
                  <span>5 min</span>
                  <span className="font-medium">{formData.prepTime} min</span>
                  <span>60 min</span>
                </div>
              </div>

              {/* Preferred Ingredients */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Ingredients You Like (Optional)</label>
                <input
                  type="text"
                  value={formData.ingredients.join(', ')}
                  placeholder="Enter ingredients separated by commas (e.g., chicken, rice, broccoli)"
                  onChange={(e) => {
                    const ingredients = e.target.value.split(',').map(ing => ing.trim()).filter(ing => ing);
                    setFormData({ ...formData, ingredients });
                  }}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                />
              </div>

              {/* Avoid Ingredients */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Ingredients to Avoid (Optional)</label>
                <input
                  type="text"
                  value={formData.avoidIngredients.join(', ')}
                  placeholder="Enter ingredients separated by commas (e.g., mushrooms, tomatoes, onions)"
                  onChange={(e) => {
                    const avoidIngredients = e.target.value.split(',').map(ing => ing.trim()).filter(ing => ing);
                    setFormData({ ...formData, avoidIngredients });
                  }}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                />
              </div>

              {/* Spice Level */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Preferred Spice Level (1-5)</label>
                <div className="flex items-center gap-4">
                  {[1, 2, 3, 4, 5].map((level) => (
                    <label key={level} className={`flex flex-col items-center justify-center p-4 border-2 rounded-xl cursor-pointer transition-all ${
                      formData.spiceLevel === level
                        ? 'border-[#F97316] bg-[#F97316]/10'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <input
                        type="radio"
                        name="spiceLevel"
                        value={level}
                        checked={formData.spiceLevel === level}
                        onChange={(e) => setFormData({ ...formData, spiceLevel: parseInt(e.target.value) })}
                        className="sr-only"
                      />
                      <span className="text-lg font-bold">{level}</span>
                      <span className="text-sm mt-1">
                        {level === 1 ? 'Mild' : level === 2 ? 'Light' : level === 3 ? 'Medium' : level === 4 ? 'Spicy' : 'Hot'}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Budget per Meal */}
              <div className="mb-6">
                <label className="block mb-3 text-gray-700">Budget per Meal (USD)</label>
                <input
                  type="range"
                  min="5"
                  max="50"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-gray-500 mt-1">
                  <span>$5</span>
                  <span className="font-medium">${formData.budget.toFixed(2)}</span>
                  <span>$50</span>
                </div>
              </div>

              {/* Daily Macro Targets */}
              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <label className="block mb-2 text-gray-700">Daily Protein Target (g)</label>
                  <input
                    type="number"
                    value={formData.proteinTarget}
                    onChange={(e) => setFormData({ ...formData, proteinTarget: parseFloat(e.target.value) })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                    placeholder="25"
                  />
                </div>

                <div>
                  <label className="block mb-2 text-gray-700">Daily Carb Target (g)</label>
                  <input
                    type="number"
                    value={formData.carbTarget}
                    onChange={(e) => setFormData({ ...formData, carbTarget: parseFloat(e.target.value) })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                    placeholder="45"
                  />
                </div>

                <div>
                  <label className="block mb-2 text-gray-700">Daily Fat Target (g)</label>
                  <input
                    type="number"
                    value={formData.fatTarget}
                    onChange={(e) => setFormData({ ...formData, fatTarget: parseFloat(e.target.value) })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                    placeholder="15"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-4 rounded-xl transition-colors flex items-center justify-center gap-2 ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-[#F97316] hover:bg-[#EA580C] text-white'
              }`}
            >
              {loading ? (
                <span>Saving...</span>
              ) : (
                <>
                  <span>Continue to Dashboard</span>
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}