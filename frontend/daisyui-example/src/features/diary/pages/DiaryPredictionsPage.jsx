import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../../shared/services/api.js';

const DiaryPredictionsPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [predictionDays, setPredictionDays] = useState(7);

  useEffect(() => {
    loadPredictions();
  }, []);

  const loadPredictions = async (days = 7) => {
    try {
      setLoading(true);
      const response = await apiService.diary.predictMood({ prediction_days: days });
      
      if (response.data.success) {
        setPredictions(response.data);
      } else {
        setError(response.data.message || 'Failed to generate predictions');
      }
    } catch (err) {
      console.error('Error loading predictions:', err);
      setError('Failed to load mood predictions');
    } finally {
      setLoading(false);
    }
  };

  const handleDaysChange = (days) => {
    setPredictionDays(days);
    loadPredictions(days);
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

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-success';
    if (confidence >= 0.6) return 'text-warning';
    return 'text-error';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-200 flex items-center justify-center">
        <div className="text-center">
          <span className="loading loading-spinner loading-lg"></span>
          <p className="mt-4">Generating predictions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">🔮 Mood Predictions</h1>
            <p className="text-base-content/60">AI-powered forecasting based on your patterns</p>
          </div>
          <button
            onClick={() => navigate('/diary')}
            className="btn btn-ghost"
          >
            ← Back
          </button>
        </div>

        {/* Prediction Controls */}
        <div className="card bg-base-100">
          <div className="card-body">
            <h2 className="card-title">Forecast Period</h2>
            <div className="flex gap-2">
              {[3, 7, 14].map((days) => (
                <button
                  key={days}
                  onClick={() => handleDaysChange(days)}
                  className={`btn btn-sm ${predictionDays === days ? 'btn-primary' : 'btn-outline'}`}
                >
                  {days} Days
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Predictions Display */}
        {predictions && predictions.predictions.length > 0 ? (
          <>
            {/* Confidence Indicator */}
            <div className="card bg-base-100">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="card-title">Prediction Confidence</h2>
                    <p className="text-sm text-base-content/60">
                      Based on {predictions.historical_entries} diary entries
                    </p>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${getConfidenceColor(predictions.confidence)}`}>
                      {(predictions.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="text-sm text-base-content/60">Confidence</div>
                  </div>
                </div>
                
                <div className="mt-4">
                  <progress 
                    className={`progress w-full ${
                      predictions.confidence >= 0.8 ? 'progress-success' :
                      predictions.confidence >= 0.6 ? 'progress-warning' : 'progress-error'
                    }`}
                    value={predictions.confidence * 100} 
                    max="100"
                  ></progress>
                </div>
              </div>
            </div>

            {/* Predictions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {predictions.predictions.map((prediction, index) => (
                <div key={index} className="card bg-base-100 border border-base-300">
                  <div className="card-body p-4">
                    <div className="text-center mb-3">
                      <div className="text-sm font-medium text-base-content/60">
                        {new Date(prediction.date).toLocaleDateString('en-US', { 
                          weekday: 'long',
                          month: 'short', 
                          day: 'numeric' 
                        })}
                      </div>
                      <div className="flex items-center justify-center space-x-2 mt-2">
                        <span className={`text-3xl ${getHappinessColor(prediction.predicted_happiness)}`}>
                          {getHappinessEmoji(prediction.predicted_happiness)}
                        </span>
                        <span className={`text-xl font-bold ${getHappinessColor(prediction.predicted_happiness)}`}>
                          {prediction.predicted_happiness}/10
                        </span>
                      </div>
                    </div>

                    {prediction.likely_emotions && prediction.likely_emotions.length > 0 && (
                      <div>
                        <div className="text-xs text-base-content/60 mb-2">Likely emotions:</div>
                        <div className="flex flex-wrap gap-1">
                          {prediction.likely_emotions.slice(0, 3).map((emotion, i) => (
                            <span key={i} className="badge badge-outline badge-xs">
                              {emotion.emotion} ({emotion.predicted_intensity})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Confidence Factors */}
                    {prediction.confidence_factors && (
                      <div className="mt-3 text-xs text-base-content/50">
                        <div>Base: {prediction.confidence_factors.base_pattern?.toFixed(1)}</div>
                        {prediction.confidence_factors.trend_adjustment !== 0 && (
                          <div>Trend: {prediction.confidence_factors.trend_adjustment > 0 ? '+' : ''}{prediction.confidence_factors.trend_adjustment?.toFixed(1)}</div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Insights */}
            <div className="card bg-base-100">
              <div className="card-body">
                <h2 className="card-title">📊 Prediction Insights</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div className="bg-base-200 rounded-lg p-4">
                    <h3 className="font-medium mb-2">Average Predicted Happiness</h3>
                    <div className="text-2xl font-bold text-primary">
                      {(predictions.predictions.reduce((sum, p) => sum + p.predicted_happiness, 0) / predictions.predictions.length).toFixed(1)}/10
                    </div>
                  </div>
                  
                  <div className="bg-base-200 rounded-lg p-4">
                    <h3 className="font-medium mb-2">Prediction Range</h3>
                    <div className="text-sm">
                      <div>Highest: <span className="font-bold text-success">
                        {Math.max(...predictions.predictions.map(p => p.predicted_happiness))}/10
                      </span></div>
                      <div>Lowest: <span className="font-bold text-warning">
                        {Math.min(...predictions.predictions.map(p => p.predicted_happiness))}/10
                      </span></div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-info/10 rounded-lg">
                  <div className="text-sm">
                    <strong>How it works:</strong> Our AI analyzes your diary patterns from the last 60 days, 
                    including weekly trends, emotional patterns, and happiness trajectories to predict your 
                    likely mood for upcoming days. Higher confidence means more consistent historical data.
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="card bg-base-100">
            <div className="card-body text-center py-12">
              <div className="text-4xl mb-4">📝</div>
              <h3 className="font-medium mb-2">Insufficient Data</h3>
              <p className="text-base-content/60 mb-4">
                {error || 'We need at least a week of diary entries to generate accurate mood predictions.'}
              </p>
              <button
                onClick={() => navigate('/diary/session')}
                className="btn btn-primary"
              >
                Create Diary Entry
              </button>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="alert alert-error">
            <span>{error}</span>
            <button 
              onClick={() => setError(null)}
              className="btn btn-ghost btn-sm"
            >
              Dismiss
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default DiaryPredictionsPage;
