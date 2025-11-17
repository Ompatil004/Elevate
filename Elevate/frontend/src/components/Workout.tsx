import { useState, useRef, useEffect } from 'react';
import { Play, Pause, RotateCcw, Check, AlertCircle, ChevronLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export function Workout() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentExercise, setCurrentExercise] = useState(0);
  const [reps, setReps] = useState(0);
  const [timer, setTimer] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const exercises = [
    {
      name: 'Push-ups',
      sets: 3,
      reps: 15,
      hints: ['Keep your back straight', 'Lower chest to ground', 'Push through palms', 'Engage core throughout']
    },
    {
      name: 'Squats',
      sets: 4,
      reps: 12,
      hints: ['Feet shoulder-width apart', 'Knees behind toes', 'Lower until thighs parallel', 'Keep chest up']
    },
    {
      name: 'Plank',
      sets: 3,
      reps: 45,
      hints: ['Straight line from head to heels', 'Engage core muscles', 'Don\'t let hips sag', 'Breathe steadily']
    }
  ];

  const currentEx = exercises[currentExercise];

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimer((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleReset = () => {
    setTimer(0);
    setReps(0);
    setIsPlaying(false);
  };

  const handleNextExercise = () => {
    if (currentExercise < exercises.length - 1) {
      setCurrentExercise(currentExercise + 1);
      handleReset();
    }
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
          <div className="flex items-center gap-2">
            <span className="px-4 py-2 bg-[#22C55E]/10 text-[#22C55E] rounded-full">
              Exercise {currentExercise + 1} of {exercises.length}
            </span>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Video Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              {/* Video Placeholder with Skeleton Overlay */}
              <div className="relative aspect-video bg-gray-900">
                <video
                  ref={videoRef}
                  className="w-full h-full object-cover opacity-50"
                  poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect fill='%23111827' width='100' height='100'/%3E%3C/svg%3E"
                >
                  <source src="#" type="video/mp4" />
                </video>
                
                {/* Skeleton Overlay */}
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 640 480">
                  {/* Head */}
                  <circle cx="320" cy="100" r="30" fill="none" stroke="#22C55E" strokeWidth="3" />
                  
                  {/* Body */}
                  <line x1="320" y1="130" x2="320" y2="280" stroke="#22C55E" strokeWidth="3" />
                  
                  {/* Arms */}
                  <line x1="320" y1="160" x2="260" y2="220" stroke="#3B82F6" strokeWidth="3" />
                  <line x1="260" y1="220" x2="240" y2="280" stroke="#3B82F6" strokeWidth="3" />
                  <line x1="320" y1="160" x2="380" y2="220" stroke="#3B82F6" strokeWidth="3" />
                  <line x1="380" y1="220" x2="400" y2="280" stroke="#3B82F6" strokeWidth="3" />
                  
                  {/* Legs */}
                  <line x1="320" y1="280" x2="280" y2="360" stroke="#F97316" strokeWidth="3" />
                  <line x1="280" y1="360" x2="270" y2="440" stroke="#F97316" strokeWidth="3" />
                  <line x1="320" y1="280" x2="360" y2="360" stroke="#F97316" strokeWidth="3" />
                  <line x1="360" y1="360" x2="370" y2="440" stroke="#F97316" strokeWidth="3" />
                  
                  {/* Joints */}
                  <circle cx="320" cy="160" r="6" fill="#22C55E" />
                  <circle cx="260" cy="220" r="6" fill="#3B82F6" />
                  <circle cx="380" cy="220" r="6" fill="#3B82F6" />
                  <circle cx="320" cy="280" r="6" fill="#22C55E" />
                  <circle cx="280" cy="360" r="6" fill="#F97316" />
                  <circle cx="360" cy="360" r="6" fill="#F97316" />
                </svg>

                {/* Camera Placeholder Text */}
                <div className="absolute top-4 left-4 bg-black/50 text-white px-4 py-2 rounded-lg backdrop-blur-sm">
                  📹 Camera Feed (Pose Detection Ready)
                </div>
              </div>

              {/* Exercise Info */}
              <div className="p-6">
                <h2 className="text-2xl mb-2" style={{ fontFamily: 'var(--font-poppins)' }}>
                  {currentEx.name}
                </h2>
                <p className="text-gray-600 mb-4">
                  {currentEx.sets} sets × {currentEx.reps} {currentEx.name === 'Plank' ? 'seconds' : 'reps'}
                </p>

                {/* Controls */}
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="flex items-center justify-center w-14 h-14 bg-[#F97316] text-white rounded-full hover:bg-[#EA580C] transition-colors"
                  >
                    {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-1" />}
                  </button>
                  <button
                    onClick={handleReset}
                    className="flex items-center justify-center w-14 h-14 bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300 transition-colors"
                  >
                    <RotateCcw className="w-6 h-6" />
                  </button>
                  {currentExercise < exercises.length - 1 && (
                    <button
                      onClick={handleNextExercise}
                      className="flex items-center gap-2 px-6 py-3 bg-[#22C55E] text-white rounded-full hover:bg-[#16A34A] transition-colors ml-auto"
                    >
                      Next Exercise
                      <Check className="w-5 h-5" />
                    </button>
                  )}
                  {currentExercise === exercises.length - 1 && reps >= currentEx.reps && (
                    <Link
                      to="/dashboard"
                      className="flex items-center gap-2 px-6 py-3 bg-[#22C55E] text-white rounded-full hover:bg-[#16A34A] transition-colors ml-auto"
                    >
                      Complete Workout
                      <Check className="w-5 h-5" />
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* Rep Counter */}
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <h3 className="text-xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
                Rep Counter
              </h3>
              <div className="text-center mb-6">
                <div className="text-6xl mb-2" style={{ fontFamily: 'var(--font-poppins)' }}>
                  {reps}
                </div>
                <p className="text-gray-600">of {currentEx.reps} {currentEx.name === 'Plank' ? 'seconds' : 'reps'}</p>
              </div>
              <button
                onClick={() => setReps(Math.min(reps + 1, currentEx.reps))}
                className="w-full py-3 bg-[#3B82F6] text-white rounded-xl hover:bg-[#2563EB] transition-colors"
              >
                Count Rep
              </button>
              <div className="mt-4 w-full bg-gray-200 rounded-full h-3">
                <div
                  className="h-3 bg-[#22C55E] rounded-full transition-all"
                  style={{ width: `${(reps / currentEx.reps) * 100}%` }}
                />
              </div>
            </div>

            {/* Timer */}
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <h3 className="text-xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
                Timer
              </h3>
              <div className="text-5xl text-center" style={{ fontFamily: 'var(--font-poppins)' }}>
                {formatTime(timer)}
              </div>
            </div>

            {/* Form Hints */}
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <h3 className="flex items-center gap-2 text-xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
                <AlertCircle className="w-5 h-5 text-[#F97316]" />
                Form Tips
              </h3>
              <ul className="space-y-3">
                {currentEx.hints.map((hint, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-[#22C55E] flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{hint}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Exercise List */}
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <h3 className="text-xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
                Today's Routine
              </h3>
              <div className="space-y-2">
                {exercises.map((exercise, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-xl flex items-center justify-between ${
                      index === currentExercise
                        ? 'bg-[#22C55E]/10 border-2 border-[#22C55E]'
                        : index < currentExercise
                        ? 'bg-gray-50 opacity-50'
                        : 'bg-gray-50'
                    }`}
                  >
                    <span>{exercise.name}</span>
                    {index < currentExercise && (
                      <Check className="w-5 h-5 text-[#22C55E]" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
