import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Activity, Mail, Lock, User } from 'lucide-react';
import { ImageWithFallback } from '@/components/figma/ImageWithFallback';
import { toast } from 'sonner';

export function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    fitnessGoal: 'weight-loss'
  });
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        // Login
        await login(formData.email, formData.password);
        toast.success('Login successful!');
        navigate('/profile-setup');
      } else {
        // Register
        await register({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          fitnessGoal: formData.fitnessGoal
        });
        toast.success('Registration successful!');
        navigate('/profile-setup');
      }
    } catch (error: any) {
      console.error('Authentication error:', error);
      toast.error(error || (isLogin ? 'Login failed' : 'Registration failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="flex items-center justify-center gap-2 mb-8">
            <Activity className="w-10 h-10 text-[#22C55E]" />
            <span className="text-2xl" style={{ fontFamily: 'var(--font-poppins)' }}>Elevate</span>
          </div>

          <h2 className="text-3xl text-center mb-8" style={{ fontFamily: 'var(--font-poppins)' }}>
            {isLogin ? 'Welcome Back' : 'Start Your Journey'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block mb-2 text-gray-700">Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                    placeholder="Your name"
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block mb-2 text-gray-700">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                  placeholder="your@email.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block mb-2 text-gray-700">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {!isLogin && (
              <div>
                <label className="block mb-2 text-gray-700">Fitness Goal</label>
                <select
                  value={formData.fitnessGoal}
                  onChange={(e) => setFormData({ ...formData, fitnessGoal: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#22C55E] focus:border-transparent"
                >
                  <option value="weight-loss">Weight Loss</option>
                  <option value="muscle-gain">Muscle Gain</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="endurance">Endurance Training</option>
                  <option value="flexibility">Flexibility & Mobility</option>
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-xl transition-colors ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-[#F97316] hover:bg-[#EA580C] text-white'
              }`}
            >
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </form>

          <p className="text-center mt-6 text-gray-600">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-[#22C55E] hover:underline"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>

      {/* Right side - Motivational Background */}
      <div className="hidden lg:block flex-1 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-[#22C55E]/90 to-[#3B82F6]/90" />
        <ImageWithFallback 
          src="https://images.unsplash.com/photo-1506126613408-eca07ce68773?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx5b2dhJTIwbWVkaXRhdGlvbnxlbnwxfHx8fDE3NjE5MTkzMjJ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Yoga meditation"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 flex items-center justify-center text-white text-center p-12">
          <div>
            <h2 className="text-4xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
              Transform Your Life
            </h2>
            <p className="text-xl opacity-90">
              Your journey to a healthier, stronger you starts here
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
