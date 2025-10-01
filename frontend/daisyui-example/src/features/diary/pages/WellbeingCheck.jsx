import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDiary } from '../context/DiaryContext.jsx';
import { useAuth } from '../../../core/auth/AuthContext.jsx';

const WellbeingCheck = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    wellbeingData,
    loading,
    error,
    loadWellbeingCheck,
    clearError,
  } = useDiary();

  const [insights, setInsights] = useState(null);

  useEffect(() => {
    loadWellbeingCheck();
  }, []);

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

  const getTrendEmoji = (trend) => {
    if (trend?.includes('improving') || trend?.includes('better')) return '📈';
    if (trend?.includes('declining') || trend?.includes('worse')) return '📉';
    return '📊';
  };

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-base-content mb-2">
            How Am I Doing Recently?
          </h1>
          <p className="text-base-content/60">
            AI-powered insights from your diary patterns
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        ) : wellbeingData ? (
          <>
            {/* Overall Summary */}
            <div className="card bg-base-100 border border-base-300">
              <div className="card-body p-6">
                <h2 className="card-title text-lg mb-4">Overall Wellbeing</h2>
                
                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      <span className={`text-3xl ${getHappinessColor(wellbeingData.average_happiness)}`}>
                        {getHappinessEmoji(wellbeingData.average_happiness)}
                      </span>
                      <span className="text-2xl font-bold">
                        {wellbeingData.average_happiness?.toFixed(1) || 'N/A'}
                      </span>
                    </div>
                    <div className="text-sm text-base-content/60">Average Happiness</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary mb-2">
                      {wellbeingData.recent_entries_count || 0}
                    </div>
                    <div className="text-sm text-base-content/60">Recent Entries</div>
                  </div>
                </div>

                {wellbeingData.analysis_text && (
                  <div className="bg-base-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className="text-2xl">
                        {getTrendEmoji(wellbeingData.analysis_text)}
                      </div>
                      <div>
                        <h3 className="font-medium mb-1">Trend Analysis</h3>
                        <p className="text-sm text-base-content/80">
                          {wellbeingData.analysis_text}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="card bg-base-100 border border-base-300">
            <div className="card-body p-8 text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="font-medium mb-2">No Data Yet</h3>
              <p className="text-sm text-base-content/60 mb-6">
                Complete a few diary entries to see your wellbeing insights
              </p>
              <button
                onClick={() => navigate('/diary/session')}
                className="btn btn-primary"
              >
                Start Your First Entry
              </button>
            </div>
          </div>
        )}

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

        {/* Actions */}
        <div className="flex space-x-4">
          <button
            onClick={() => navigate('/diary/session')}
            className="btn btn-primary flex-1"
          >
            New Entry
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-outline flex-1"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default WellbeingCheck;
