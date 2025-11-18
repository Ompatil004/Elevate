import { Link } from 'react-router-dom';
import { Activity, Target, TrendingUp, Users, Zap, Heart, Utensils } from 'lucide-react';
import { ImageWithFallback } from '@/components/figma/ImageWithFallback.jsx';

export function Landing() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Activity className="w-8 h-8 text-[#22C55E]" />
              <span className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>Elevate</span>
            </div>
            <Link
              to="/auth"
              className="px-6 py-2 bg-[#F97316] text-white rounded-full hover:bg-[#EA580C] transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl mb-6" style={{ fontFamily: 'var(--font-poppins)' }}>
              Elevate Your Fitness Journey
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              Your AI-powered fitness companion that personalizes workouts, meal plans, and tracks your progress towards your health goals.
            </p>
            <Link
              to="/auth"
              className="inline-block px-8 py-4 bg-[#F97316] text-white rounded-full hover:bg-[#EA580C] transition-colors"
            >
              Get Started
            </Link>
          </div>
          <div className="relative">
            <div className="rounded-3xl overflow-hidden shadow-2xl">
              <ImageWithFallback
                src="https://images.unsplash.com/photo-1534258936925-c58bed479fcb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmaXRuZXNzJTIwdHJhaW5pbmd8ZW58MXx8fHwxNzYxOTMxNDc5fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                alt="Fitness training"
                className="w-full h-auto"
              />
            </div>
            <div className="absolute -bottom-6 -left-6 bg-white rounded-2xl shadow-xl p-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-[#22C55E]/10 rounded-full flex items-center justify-center">
                  <Target className="w-6 h-6 text-[#22C55E]" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Weekly Goal</p>
                  <p className="text-xl">95% Complete</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-gray-50 py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl text-center mb-16" style={{ fontFamily: 'var(--font-poppins)' }}>
            Everything You Need to Succeed
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Zap,
                title: 'AI-Powered Workouts',
                description: 'Personalized exercise routines that adapt to your fitness level and goals',
                color: '#3B82F6'
              },
              {
                icon: Utensils,
                title: 'Custom Meal Plans',
                description: 'Nutrition tailored to your dietary preferences and fitness objectives',
                color: '#22C55E'
              },
              {
                icon: TrendingUp,
                title: 'Progress Tracking',
                description: 'Comprehensive analytics to visualize your fitness journey',
                color: '#F97316'
              },
              {
                icon: Heart,
                title: 'Form Detection',
                description: 'Real-time pose detection to ensure proper exercise technique',
                color: '#3B82F6'
              },
              {
                icon: Users,
                title: 'Community Support',
                description: 'Connect with others on similar fitness journeys',
                color: '#22C55E'
              },
              {
                icon: Target,
                title: 'Goal Setting',
                description: 'Set and track specific, measurable fitness milestones',
                color: '#F97316'
              }
            ].map((feature, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
                <div
                  className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4"
                  style={{ backgroundColor: `${feature.color}15` }}
                >
                  <feature.icon className="w-7 h-7" style={{ color: feature.color }} />
                </div>
                <h3 className="text-xl mb-3" style={{ fontFamily: 'var(--font-poppins)' }}>
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <div className="bg-gradient-to-r from-[#22C55E] to-[#3B82F6] rounded-3xl p-12 md:p-16 text-center text-white">
          <h2 className="text-3xl md:text-4xl mb-6" style={{ fontFamily: 'var(--font-poppins)' }}>
            Ready to Transform Your Life?
          </h2>
          <p className="text-lg mb-8 opacity-90">
            Join thousands of users who have already elevated their fitness journey
          </p>
          <Link
            to="/auth"
            className="inline-block px-8 py-4 bg-white text-[#22C55E] rounded-full hover:bg-gray-100 transition-colors"
          >
            Start Your Journey Today
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Activity className="w-6 h-6 text-[#22C55E]" />
            <span className="text-lg" style={{ fontFamily: 'var(--font-poppins)' }}>Elevate</span>
          </div>
          <p className="text-gray-400">© 2025 Elevate. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}