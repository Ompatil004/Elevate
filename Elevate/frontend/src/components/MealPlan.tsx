import { useState } from 'react';
import { RefreshCw, Flame, ChevronLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ImageWithFallback } from './figma/ImageWithFallback';

export function MealPlan() {
  const [meals, setMeals] = useState([
    {
      id: 1,
      type: 'Breakfast',
      name: 'Protein Oatmeal Bowl',
      image: 'https://images.unsplash.com/photo-1563438962385-0d3dd8319200?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm90ZWluJTIwYnJlYWtmYXN0fGVufDF8fHx8MTc2MTkzMDY1Mnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      calories: 450,
      protein: 25,
      carbs: 55,
      fats: 12
    },
    {
      id: 2,
      type: 'Morning Snack',
      name: 'Greek Yogurt & Berries',
      image: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwbWVhbHxlbnwxfHx8fDE3NjE5MzA2NTF8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      calories: 200,
      protein: 15,
      carbs: 25,
      fats: 3
    },
    {
      id: 3,
      type: 'Lunch',
      name: 'Grilled Chicken Salad',
      image: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzYWxhZCUyMGJvd2x8ZW58MXx8fHwxNzYxOTI5MjIzfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      calories: 650,
      protein: 45,
      carbs: 40,
      fats: 28
    },
    {
      id: 4,
      type: 'Afternoon Snack',
      name: 'Protein Smoothie',
      image: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwbWVhbHxlbnwxfHx8fDE3NjE5MzA2NTF8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      calories: 300,
      protein: 30,
      carbs: 35,
      fats: 5
    },
    {
      id: 5,
      type: 'Dinner',
      name: 'Grilled Salmon & Vegetables',
      image: 'https://images.unsplash.com/photo-1712579733874-c3a79f0f9d12?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxncmlsbGVkJTIwY2hpY2tlbnxlbnwxfHx8fDE3NjE5MzA2NTJ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      calories: 750,
      protein: 55,
      carbs: 45,
      fats: 35
    },
    {
      id: 6,
      type: 'Evening Snack',
      name: 'Almonds & Dark Chocolate',
      image: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwbWVhbHxlbnwxfHx8fDE3NjE5MzA2NTF8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      calories: 250,
      protein: 8,
      carbs: 20,
      fats: 18
    }
  ]);

  const totalCalories = meals.reduce((sum, meal) => sum + meal.calories, 0);
  const totalProtein = meals.reduce((sum, meal) => sum + meal.protein, 0);
  const totalCarbs = meals.reduce((sum, meal) => sum + meal.carbs, 0);
  const totalFats = meals.reduce((sum, meal) => sum + meal.fats, 0);

  const handleSwap = (mealId: number) => {
    // In a real app, this would fetch a new meal from the API
    alert(`Swapping meal ${mealId} with an alternative...`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Link to="/dashboard" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <ChevronLeft className="w-5 h-5" />
            Back to Dashboard
          </Link>
        </div>

        <h1 className="text-3xl mb-2" style={{ fontFamily: 'var(--font-poppins)' }}>
          Today's Meal Plan
        </h1>
        <p className="text-gray-600 mb-8">Personalized nutrition for your fitness goals</p>

        {/* Daily Summary */}
        <div className="bg-white rounded-2xl p-6 shadow-lg mb-8">
          <h3 className="text-xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
            Daily Nutrition Summary
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#F97316]/10 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Flame className="w-5 h-5 text-[#F97316]" />
                <span className="text-sm text-gray-600">Calories</span>
              </div>
              <p className="text-2xl">{totalCalories}</p>
              <p className="text-sm text-gray-600">kcal</p>
            </div>
            <div className="bg-[#3B82F6]/10 rounded-xl p-4">
              <span className="text-sm text-gray-600">Protein</span>
              <p className="text-2xl">{totalProtein}g</p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div className="h-2 bg-[#3B82F6] rounded-full" style={{ width: '75%' }} />
              </div>
            </div>
            <div className="bg-[#22C55E]/10 rounded-xl p-4">
              <span className="text-sm text-gray-600">Carbs</span>
              <p className="text-2xl">{totalCarbs}g</p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div className="h-2 bg-[#22C55E] rounded-full" style={{ width: '65%' }} />
              </div>
            </div>
            <div className="bg-[#F59E0B]/10 rounded-xl p-4">
              <span className="text-sm text-gray-600">Fats</span>
              <p className="text-2xl">{totalFats}g</p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div className="h-2 bg-[#F59E0B] rounded-full" style={{ width: '80%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Meal Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {meals.map((meal) => (
            <div key={meal.id} className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
              <div className="relative h-48">
                <ImageWithFallback 
                  src={meal.image}
                  alt={meal.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-3 left-3 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-full text-sm">
                  {meal.type}
                </div>
              </div>
              <div className="p-5">
                <h3 className="text-xl mb-3" style={{ fontFamily: 'var(--font-poppins)' }}>
                  {meal.name}
                </h3>
                
                {/* Macros */}
                <div className="grid grid-cols-4 gap-2 mb-4">
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 mb-1">
                      <Flame className="w-4 h-4 text-[#F97316]" />
                    </div>
                    <p className="text-sm">{meal.calories}</p>
                    <p className="text-xs text-gray-600">kcal</p>
                  </div>
                  <div className="text-center">
                    <div className="w-3 h-3 bg-[#3B82F6] rounded-full mx-auto mb-1" />
                    <p className="text-sm">{meal.protein}g</p>
                    <p className="text-xs text-gray-600">protein</p>
                  </div>
                  <div className="text-center">
                    <div className="w-3 h-3 bg-[#22C55E] rounded-full mx-auto mb-1" />
                    <p className="text-sm">{meal.carbs}g</p>
                    <p className="text-xs text-gray-600">carbs</p>
                  </div>
                  <div className="text-center">
                    <div className="w-3 h-3 bg-[#F59E0B] rounded-full mx-auto mb-1" />
                    <p className="text-sm">{meal.fats}g</p>
                    <p className="text-xs text-gray-600">fats</p>
                  </div>
                </div>

                <button
                  onClick={() => handleSwap(meal.id)}
                  className="w-full py-2 border-2 border-[#22C55E] text-[#22C55E] rounded-xl hover:bg-[#22C55E] hover:text-white transition-colors flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Swap Meal
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Tips Section */}
        <div className="bg-gradient-to-r from-[#22C55E] to-[#3B82F6] rounded-2xl p-8 mt-8 text-white">
          <h3 className="text-2xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
            Nutrition Tips
          </h3>
          <ul className="space-y-2">
            <li>✓ Drink at least 8 glasses of water throughout the day</li>
            <li>✓ Eat within 30 minutes after your workout for optimal recovery</li>
            <li>✓ Include a protein source in every meal to support muscle growth</li>
            <li>✓ Plan your meals in advance to stay on track with your goals</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
