import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDiary } from '../context/DiaryContext.jsx';
import { useAuth } from '../../../core/auth/AuthContext.jsx';
import { apiService } from '../../../shared/services/api.js';
// NotificationSettings removed - using MDN implementation in Settings page

const DiarySessionPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    sessionActive,
    currentQuestion,
    currentQuestionIndex,
    questions,
    sessionProgress,
    isLastQuestion,
    loading,
    error,
    startSession,
    submitResponse,
    completeSession,
    clearError,
    resetSession,
    loadEntries,
  } = useDiary();

  const [sessionMode, setSessionMode] = useState('text');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]); // Today's date
  const [currentResponse, setCurrentResponse] = useState('');
  const [sessionStarted, setSessionStarted] = useState(false);
  const [existingEntries, setExistingEntries] = useState([]);
  const [entriesLoaded, setEntriesLoaded] = useState(false);
  
  // Voice-related state
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioRef = useRef(null);
  const recordingIntervalRef = useRef(null);

  useEffect(() => {
    // Reset session when component mounts
    if (!sessionActive) {
      resetSession();
    }
    
    // Load existing entries to check availability
    const loadExistingEntries = async () => {
      const result = await loadEntries(1);
      if (result.success) {
        setExistingEntries(result.entries || []);
      } else {
        setExistingEntries([]);
      }
      setEntriesLoaded(true);
    };
    
    loadExistingEntries();
    
    // Cleanup on unmount
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  // Update selected date when existing entries are loaded
  useEffect(() => {
    if (entriesLoaded) {
      const availableDates = getAvailableDates();
      if (availableDates.length > 0) {
        // Set to first available date if current selection is not available
        const currentDateAvailable = availableDates.some(date => date.value === selectedDate);
        if (!currentDateAvailable) {
          setSelectedDate(availableDates[0].value);
        }
      }
    }
  }, [entriesLoaded, selectedDate]);

  // Helper functions for date handling
  const getAvailableDates = () => {
    const dates = [];
    const today = new Date();
    
    // Allow entries for today and up to 3 days back (matching backend limit)
    for (let i = 0; i < 4; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      const dateString = date.toISOString().split('T')[0];
      
      // Check if this date already has a completed entry
      const hasCompletedEntry = existingEntries?.some(entry => 
        entry.entry_date === dateString && entry.is_completed
      ) || false;
      
      if (!hasCompletedEntry) {
        dates.push({
          value: dateString,
          label: i === 0 ? 'Today' : 
                 i === 1 ? 'Yesterday' : 
                 date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }),
          available: true
        });
      }
    }
    return dates;
  };

  // Helper function to get unavailable dates for display
  const getUnavailableDates = () => {
    const unavailableDates = [];
    const today = new Date();
    
    for (let i = 0; i < 4; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      const dateString = date.toISOString().split('T')[0];
      
      const hasCompletedEntry = existingEntries?.some(entry => 
        entry.entry_date === dateString && entry.is_completed
      ) || false;
      
      if (hasCompletedEntry) {
        unavailableDates.push({
          value: dateString,
          label: i === 0 ? 'Today' : 
                 i === 1 ? 'Yesterday' : 
                 date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })
        });
      }
    }
    return unavailableDates;
  };

  const handleStartSession = async () => {
    const result = await startSession({
      mode: sessionMode,
      entry_date: selectedDate
    });
    if (result.success) {
      setSessionStarted(true);
      clearError();
    }
  };

  const handleSubmitResponse = async () => {
    if (!currentResponse.trim()) return;

    console.log('🎯 Attempting to submit response:', {
      sessionActive,
      currentQuestion,
      currentQuestionIndex: currentQuestionIndex,
      questionsLength: questions?.length || 0,
      responseText: currentResponse.substring(0, 50) + '...'
    });

    // Check if this is the last question BEFORE submitting
    const isLastQuestionBeforeSubmit = isLastQuestion;

    const result = await submitResponse(currentResponse);
    if (result.success) {
      setCurrentResponse('');
      
      // If this was the last question, complete the session automatically
      if (isLastQuestionBeforeSubmit) {
        console.log('🎉 Last question completed, auto-completing session...');
        handleCompleteSession();
      }
    }
  };

  const handleCompleteSession = async () => {
    console.log('🚀 Starting session completion...');
    try {
      const result = await completeSession();
      console.log('📊 Session completion result:', result);
      
      if (result.success) {
        console.log('✅ Session completed successfully, navigating to dashboard...');
        // Navigate to success page or dashboard with results
        navigate('/dashboard', { 
          state: { 
            sessionComplete: true,
            summary: result.summary,
            happiness_score: result.happiness_score,
            emotions: result.emotions || []
          }
        });
      } else {
        console.error('❌ Session completion failed:', result.error);
      }
    } catch (error) {
      console.error('💥 Session completion error:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSubmitResponse();
    }
  };

  // Voice functionality
  const startRecording = async () => {
    try {
      // Check if we're on HTTPS or localhost (required for microphone access)
      if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
        alert('Microphone access requires HTTPS. Please use a secure connection or access via http://localhost:3000 for testing.');
        return;
      }

      // Request microphone permission explicitly (if supported)
      if (navigator.permissions) {
        try {
          const permissions = await navigator.permissions.query({ name: 'microphone' });
          if (permissions.state === 'denied') {
            alert('Microphone access is denied. Please enable microphone permissions in your browser settings.');
            return;
          }
        } catch (e) {
          console.log('Permissions API not fully supported, proceeding with getUserMedia');
        }
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      
      let errorMessage = 'Unable to access microphone. ';
      
      if (error.name === 'NotAllowedError') {
        errorMessage += 'Please allow microphone access in your browser and try again.';
      } else if (error.name === 'NotFoundError') {
        errorMessage += 'No microphone found. Please connect a microphone and try again.';
      } else if (error.name === 'NotSupportedError') {
        errorMessage += 'Your browser does not support audio recording.';
      } else {
        errorMessage += 'Please check your microphone settings and try again.';
      }
      
      alert(errorMessage);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  };

  const transcribeAudio = async () => {
    if (!audioBlob) return;
    
    try {
      console.log('🎤 Starting transcription...', { blobSize: audioBlob.size });
      
      const response = await apiService.voice.transcribeAudio(audioBlob);
      
      console.log('📝 Transcription response:', response.data);
      
      if (response.data.transcription) {
        setCurrentResponse(response.data.transcription);
        setAudioBlob(null); // Clear the audio after transcription
      } else {
        alert('No transcription received. Please try speaking more clearly.');
      }
    } catch (error) {
      console.error('Transcription error:', error);
      alert(`Failed to transcribe audio: ${error.response?.data?.error || error.message}`);
    }
  };

  const playQuestionAudio = () => {
    if (currentQuestion?.audio_file_url && !isPlaying) {
      console.log('🔊 Attempting to play audio:', currentQuestion.audio_file_url);
      
      // Construct full URL - audio files are served by Django backend (port 8000)
      const audioUrl = currentQuestion.audio_file_url.startsWith('http') 
        ? currentQuestion.audio_file_url 
        : `http://${window.location.hostname}:8000${currentQuestion.audio_file_url}`;
      
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      
      audio.onplay = () => {
        console.log('▶️ Audio started playing');
        setIsPlaying(true);
      };
      audio.onended = () => {
        console.log('⏹️ Audio finished playing');
        setIsPlaying(false);
      };
      audio.onerror = (error) => {
        console.error('❌ Audio error:', error, 'URL:', audioUrl);
        setIsPlaying(false);
        alert('Unable to play question audio. The audio file may not be available.');
      };
      
      audio.play().catch(error => {
        console.error('❌ Audio play error:', error);
        setIsPlaying(false);
        alert('Failed to play audio. Please check your browser audio settings.');
      });
    }
  };

  const stopQuestionAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Session mode selection screen
  if (!sessionStarted && !sessionActive) {
    return (
      <div className="min-h-screen bg-base-200 p-4">
        <div className="max-w-md mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-base-content mb-2">
              Daily Reflection
            </h1>
            <p className="text-base-content/60">
              Welcome back, {user?.first_name || 'friend'}. How would you like to share today?
            </p>
          </div>

          {/* Date Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-base-content mb-2">
              Which day would you like to write about?
            </label>
            
            {getAvailableDates().length > 0 ? (
              <>
                <select
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="select select-bordered w-full"
                >
                  {getAvailableDates().map((date) => (
                    <option key={date.value} value={date.value}>
                      {date.label}
                    </option>
                  ))}
                </select>
                
                {/* Show unavailable dates if any */}
                {getUnavailableDates().length > 0 && (
                  <div className="mt-2 p-2 bg-base-200 rounded text-xs">
                    <span className="text-base-content/60">Already completed: </span>
                    <span className="text-base-content/80">
                      {getUnavailableDates().map(date => date.label).join(', ')}
                    </span>
                  </div>
                )}
                
                <div className="text-xs text-base-content/50 mt-1">
                  You can write entries for today and up to 3 days back
                </div>
              </>
            ) : (
              <div className="bg-warning/10 border border-warning/20 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">✅</div>
                <h3 className="font-medium text-warning-content mb-1">All caught up!</h3>
                <p className="text-sm text-warning-content/80">
                  You've completed diary entries for all available dates. Come back tomorrow for a new entry!
                </p>
              </div>
            )}
          </div>

          {/* Mode Selection - Text Only */}
          <div className="space-y-4 mb-8">
            <div className="card bg-base-100 border-2 border-primary bg-primary/5">
              <div className="card-body p-4">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">✍️</div>
                  <div>
                    <h3 className="font-semibold">Text Entry</h3>
                    <p className="text-sm text-base-content/60">Type your thoughts and reflections</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Notification settings available in Settings page */}

          {/* Start Button */}
          {getAvailableDates().length > 0 && (
            <button
              onClick={handleStartSession}
              disabled={loading}
              className="btn btn-primary w-full mb-4"
            >
              {loading ? (
                <>
                  <span className="loading loading-spinner loading-sm"></span>
                  Starting...
                </>
              ) : (
                'Begin Reflection'
              )}
            </button>
          )}

          {/* Error Display */}
          {error && (
            <div className="alert alert-error">
              <span>{error}</span>
            </div>
          )}

          {/* Back Button */}
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-ghost w-full"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }


  // Main session screen
  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-md mx-auto">
        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-base-content/60 mb-2">
            <span>Question {Math.min((currentQuestionIndex + 1), questions.length)} of {questions.length}</span>
            <span>{Math.round(sessionProgress)}%</span>
          </div>
          <progress 
            className="progress progress-primary w-full" 
            value={sessionProgress} 
            max="100"
          ></progress>
        </div>

        {/* Question Card */}
        {currentQuestion && (
          <div className="card bg-base-100 border border-base-300 mb-6">
            <div className="card-body p-6">
              <div className="flex items-start space-x-3 mb-4">
                <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-content font-bold text-sm">
                  {currentQuestionIndex + 1}
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold mb-2">
                    {currentQuestion.question_text}
                  </h2>
                  {currentQuestion.question_type === 'dynamic' && (
                    <div className="badge badge-primary badge-sm">
                      Personalized for you
                    </div>
                  )}
                </div>
              </div>


              {/* Response Input */}
              <div className="space-y-4">
                <textarea
                  value={currentResponse}
                  onChange={(e) => setCurrentResponse(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Share your thoughts..."
                  className="textarea textarea-bordered w-full h-32 resize-none"
                  disabled={loading}
                />
                
                <div className="flex justify-between items-center">
                  <div className="text-xs text-base-content/50">
                    Press Ctrl+Enter to submit
                  </div>
                  <div className="text-xs text-base-content/50">
                    {currentResponse.length} characters
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={handleSubmitResponse}
            disabled={!currentResponse.trim() || loading}
            className="btn btn-primary w-full"
          >
            {loading ? (
              <>
                <span className="loading loading-spinner loading-sm"></span>
                Submitting...
              </>
            ) : isLastQuestion ? (
              'Complete Reflection'
            ) : (
              'Next Question'
            )}
          </button>

          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-ghost w-full"
          >
            Save & Exit
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="alert alert-error mt-4">
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiarySessionPage;
