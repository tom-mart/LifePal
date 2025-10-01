import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useDiary } from '../context/DiaryContext.jsx';
import { useAuth } from '../../../core/auth/AuthContext.jsx';

const DiaryDashboardPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const {
    entries,
    wellbeingData,
    loading,
    error,
    loadEntries,
    loadWellbeingCheck,
    clearError,
  } = useDiary();

  const [showSessionComplete, setShowSessionComplete] = useState(false);
  const [sessionResults, setSessionResults] = useState(null);

  useEffect(() => {
    // Load initial data
    loadEntries();
    loadWellbeingCheck();

    // Check if we just completed a session
    if (location.state?.sessionComplete) {
      setShowSessionComplete(true);
      setSessionResults({
        summary: location.state.summary,
        happiness_score: location.state.happiness_score,
      });
      
      // Clear the state to prevent showing again on refresh
      window.history.replaceState({}, document.title);
    }
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getHappinessColor = (score) => {
    if (score >= 8) return 'text-success';
    if (score >= 6) return 'text-warning';
    if (score >= 4) return 'text-info';
    return 'text-error';
  };

  const getHappinessEmoji = (score) => {
    if (score >= 8) return '😊';
    if (score >= 6) return '🙂';
    if (score >= 4) return '😐';
    return '😔';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatRelativeDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const diffTime = today - date;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Session Complete Modal */}
        {showSessionComplete && sessionResults && (
          <div className="modal modal-open">
            <div className="modal-box">
              <h3 className="font-bold text-lg mb-4">Reflection Complete! ✨</h3>
              
              <div className="space-y-4">
                <div className="bg-base-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">Happiness Score</span>
                    <div className="flex items-center space-x-2">
                      <span className={`text-2xl ${getHappinessColor(sessionResults.happiness_score)}`}>
                        {getHappinessEmoji(sessionResults.happiness_score)}
                      </span>
                      <span className="font-bold text-lg">
                        {sessionResults.happiness_score}/10
                      </span>
                    </div>
                  </div>
                </div>

                {sessionResults.summary && (
                  <div className="bg-base-200 rounded-lg p-4">
                    <h4 className="font-medium mb-2">AI Insights</h4>
                    <p className="text-sm text-base-content/80">
                      {sessionResults.summary}
                    </p>
                  </div>
                )}
              </div>

              <div className="modal-action">
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowSessionComplete(false)}
                >
                  Continue
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-base-content mb-2">
            {getGreeting()}, {user?.first_name || 'friend'}
          </h1>
          <p className="text-base-content/60">
            How are you feeling today?
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <button
            onClick={() => navigate('/diary/session')}
            className="btn btn-primary h-20 flex-col"
          >
            <div className="text-2xl mb-1">✍️</div>
            <span>New Entry</span>
          </button>
          
          <button
            onClick={() => navigate('/diary/wellbeing')}
            className="btn btn-outline h-20 flex-col"
          >
            <div className="text-2xl mb-1">📊</div>
            <span>Wellbeing</span>
          </button>
        </div>

        {/* Phase 3 Features */}
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => navigate('/diary/analytics')}
            className="btn btn-secondary h-20 flex-col"
          >
            <div className="text-2xl mb-1">📈</div>
            <span>Analytics</span>
          </button>
          
          <button
            onClick={() => navigate('/relationships')}
            className="btn btn-accent h-20 flex-col"
          >
            <div className="text-2xl mb-1">🤝</div>
            <span>Relationships</span>
          </button>
        </div>

        {/* Secondary Actions */}
        <div className="grid grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/diary/history')}
            className="btn btn-ghost h-16 flex-col"
          >
            <div className="text-xl mb-1">🔍</div>
            <span className="text-sm">Search</span>
          </button>
          
          <button
            onClick={() => navigate('/diary/predictions')}
            className="btn btn-ghost h-16 flex-col"
          >
            <div className="text-xl mb-1">🔮</div>
            <span className="text-sm">Predictions</span>
          </button>
          
          <button
            onClick={() => navigate('/dashboard/settings')}
            className="btn btn-ghost h-16 flex-col"
          >
            <div className="text-xl mb-1">⚙️</div>
            <span className="text-sm">Settings</span>
          </button>
        </div>

        {/* Wellbeing Summary */}
        {wellbeingData && (
          <div className="card bg-base-100 border border-base-300">
            <div className="card-body p-6">
              <h2 className="card-title text-lg mb-4">Recent Wellbeing</h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary mb-1">
                    {wellbeingData.average_happiness?.toFixed(1) || 'N/A'}
                  </div>
                  <div className="text-sm text-base-content/60">Avg Happiness</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-secondary mb-1">
                    {wellbeingData.recent_entries_count || 0}
                  </div>
                  <div className="text-sm text-base-content/60">Entries</div>
                </div>
              </div>

              {wellbeingData.analysis_text && (
                <div className="mt-4 p-3 bg-base-200 rounded-lg">
                  <div className="text-sm font-medium mb-1">Trend Analysis</div>
                  <div className="text-sm text-base-content/80">
                    {wellbeingData.analysis_text}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Recent Entries */}
        <div className="card bg-base-100 border border-base-300">
          <div className="card-body p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="card-title text-lg">Recent Entries</h2>
              <div className="flex gap-2">
                <button 
                  onClick={() => navigate('/diary/history')}
                  className="btn btn-ghost btn-sm"
                >
                  🔍 Search
                </button>
                <button 
                  onClick={() => navigate('/diary/history')}
                  className="btn btn-ghost btn-sm"
                >
                  View All
                </button>
              </div>
            </div>

            {loading ? (
              <div className="flex justify-center py-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : entries && entries.length > 0 ? (
              <div className="space-y-3">
                {entries.slice(0, 3).map((entry) => (
                  <div
                    key={entry.id}
                    className="border border-base-300 rounded-lg p-4 cursor-pointer hover:bg-base-50 transition-colors"
                    onClick={() => navigate(`/diary/entries/${entry.id}`)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="text-sm font-medium">
                        {formatRelativeDate(entry.entry_date)}
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-lg ${getHappinessColor(entry.happiness_score)}`}>
                          {getHappinessEmoji(entry.happiness_score)}
                        </span>
                        <span className="text-sm font-medium">
                          {entry.happiness_score}/10
                        </span>
                      </div>
                    </div>
                    
                    {entry.ai_summary && (
                      <p className="text-sm text-base-content/70 line-clamp-2">
                        {entry.ai_summary}
                      </p>
                    )}

                    {entry.emotions && entry.emotions.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {entry.emotions.slice(0, 3).map((emotion, index) => (
                          <span
                            key={index}
                            className="badge badge-outline badge-sm"
                          >
                            {emotion.emotion_name}
                          </span>
                        ))}
                        {entry.emotions.length > 3 && (
                          <span className="badge badge-outline badge-sm">
                            +{entry.emotions.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📝</div>
                <h3 className="font-medium mb-2">No entries yet</h3>
                <p className="text-sm text-base-content/60 mb-4">
                  Start your journey with your first reflection
                </p>
                <button
                  onClick={() => navigate('/diary/session')}
                  className="btn btn-primary btn-sm"
                >
                  Create First Entry
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="alert alert-error">
            <span>{error}</span>
            <button 
              onClick={clearError}
              className="btn btn-ghost btn-sm"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Motivational Quote */}
        <div className="card bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/20">
          <div className="card-body p-6 text-center">
            <div className="text-2xl mb-2">🌱</div>
            <p className="text-sm italic text-base-content/80">
              "The unexamined life is not worth living." - Socrates
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiaryDashboardPage;
