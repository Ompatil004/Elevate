import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { mlAPI } from '@/services/api';
import { toast } from 'sonner';
import { Play, Pause, RotateCcw, Check, AlertCircle, ChevronLeft, Camera } from 'lucide-react';

const PoseDetection: React.FC = () => {
  const [isTracking, setIsTracking] = useState(false);
  const [reps, setReps] = useState(0);
  const [feedback, setFeedback] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exerciseName, setExerciseName] = useState<string>('Push-ups');
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Get exercise name from navigation state
  useEffect(() => {
    if (location.state && (location.state as any).exerciseName) {
      setExerciseName((location.state as any).exerciseName);
    }
  }, [location.state]);

  // Initialize camera when component mounts
  useEffect(() => {
    const initCamera = async () => {
      setLoading(true);
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          } 
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
        }
      } catch (err) {
        console.error('Error accessing camera:', err);
        setError('Could not access camera. Please check permissions.');
        toast.error('Camera access denied');
      } finally {
        setLoading(false);
      }
    };

    initCamera();

    // Clean up on unmount
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startTracking = async () => {
    if (!exerciseName) {
      toast.error('No exercise selected for tracking');
      return;
    }

    setLoading(true);
    try {
      // Initialize tracking with the backend
      const trackingData = {
        exercise_name: exerciseName,
        camera_index: 0
      };

      // In a real implementation, this would start the tracking session
      // For now, we'll simulate the tracking process
      console.log(`Starting tracking for exercise: ${exerciseName}`);
      
      setIsTracking(true);
      toast.success(`Started tracking for ${exerciseName}`);
    } catch (err: any) {
      console.error('Error starting tracking:', err);
      setError(err.message || 'Error starting pose tracking');
      toast.error('Failed to start pose tracking');
    } finally {
      setLoading(false);
    }
  };

  const stopTracking = () => {
    setIsTracking(false);
    if (onSessionComplete) {
      onSessionComplete(reps, feedback);
    }
    toast.success('Tracking session completed');
  };

  const handleRepCount = () => {
    setReps(prev => prev + 1);
    toast.success('Rep counted!');
  };

  const resetSession = () => {
    setReps(0);
    setFeedback('');
    setIsTracking(false);
    toast.info('Session reset');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ChevronLeft className="w-5 h-5" />
            Back
          </button>
          <h1 className="text-2xl font-bold text-center">Pose Detection for {exerciseName}</h1>
          <div className="w-24"></div> {/* Spacer for alignment */}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video Feed */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="relative aspect-video bg-gray-900">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
                
                {/* Status overlay */}
                <div className="absolute top-4 left-4 bg-black/50 text-white px-4 py-2 rounded-lg backdrop-blur-sm">
                  {loading ? 'Initializing camera...' : 'Camera Ready'}
                </div>
                
                {/* Exercise info overlay */}
                <div className="absolute top-4 right-4 bg-black/50 text-white px-4 py-2 rounded-lg backdrop-blur-sm">
                  <div className="text-sm">{exerciseName}</div>
                </div>
                
                {/* Camera icon */}
                <div className="absolute bottom-4 left-4 flex items-center gap-2 bg-black/50 text-white px-3 py-2 rounded-lg backdrop-blur-sm">
                  <Camera className="w-4 h-4" />
                  <span>Camera ON</span>
                </div>
              </div>

              {/* Controls */}
              <div className="p-4 bg-gray-50">
                <div className="flex flex-wrap gap-3">
                  {!isTracking ? (
                    <button
                      onClick={startTracking}
                      disabled={loading}
                      className="flex items-center gap-2 px-6 py-3 bg-[#22C55E] text-white rounded-xl hover:bg-[#16A34A] transition-colors disabled:opacity-50"
                    >
                      <Play className="w-5 h-5" />
                      Start Tracking
                    </button>
                  ) : (
                    <button
                      onClick={stopTracking}
                      className="flex items-center gap-2 px-6 py-3 bg-[#F97316] text-white rounded-xl hover:bg-[#EA580C] transition-colors"
                    >
                      <Pause className="w-5 h-5" />
                      Stop Tracking
                    </button>
                  )}
                  
                  <button
                    onClick={handleRepCount}
                    disabled={!isTracking}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl transition-colors ${
                      isTracking
                        ? 'bg-[#3B82F6] text-white hover:bg-[#2563EB]'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    <Check className="w-5 h-5" />
                    Count Rep
                  </button>
                  
                  <button
                    onClick={resetSession}
                    className="flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors"
                  >
                    <RotateCcw className="w-5 h-5" />
                    Reset
                  </button>
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
                <p className="text-gray-600">Total Reps Completed</p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="h-3 bg-[#22C55E] rounded-full transition-all"
                  style={{ width: `${Math.min(100, reps * 5)}%` }} // Just for visualization
                />
              </div>
            </div>

            {/* Exercise Info */}
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <h3 className="text-xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
                Exercise Info
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Exercise:</span>
                  <span className="font-medium">{exerciseName}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-medium ${isTracking ? 'text-[#22C55E]' : 'text-gray-500'}`}>
                    {isTracking ? 'Tracking' : 'Idle'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Camera:</span>
                  <span className="font-medium">Active</span>
                </div>
              </div>
            </div>

            {/* Form Tips */}
            <div className="bg-white rounded-2xl p-6 shadow-lg">
              <h3 className="flex items-center gap-2 text-xl mb-4" style={{ fontFamily: 'var(--font-poppins)' }}>
                <AlertCircle className="w-5 h-5 text-[#F97316]" />
                Form Tips
              </h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-[#22C55E] mt-0.5 flex-shrink-0" />
                  <span>Keep the full body visible in the camera frame</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-[#22C55E] mt-0.5 flex-shrink-0" />
                  <span>Ensure good lighting for better detection</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-[#22C55E] mt-0.5 flex-shrink-0" />
                  <span>Move slowly to allow for proper rep counting</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 text-[#22C55E] mt-0.5 flex-shrink-0" />
                  <span>Maintain proper form for safety and effectiveness</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export { PoseDetection };