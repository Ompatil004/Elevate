import { Link, useLocation } from 'react-router-dom';
import { Activity, Home, Utensils, TrendingUp, Dumbbell } from 'lucide-react';

export function Navbar() {
  const location = useLocation();
  
  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/workout', icon: Dumbbell, label: 'Workout' },
    { path: '/meal-plan', icon: Utensils, label: 'Meals' },
    { path: '/analytics', icon: TrendingUp, label: 'Progress' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/dashboard" className="flex items-center gap-2">
            <Activity className="w-8 h-8 text-[#22C55E]" />
            <span className="text-xl" style={{ fontFamily: 'var(--font-poppins)' }}>Elevate</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-6">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-[#22C55E]/10 text-[#22C55E]' 
                      : 'text-gray-600 hover:text-[#22C55E]'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Mobile Navigation */}
          <div className="md:hidden flex gap-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`${
                    isActive ? 'text-[#22C55E]' : 'text-gray-600'
                  }`}
                >
                  <Icon className="w-6 h-6" />
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
