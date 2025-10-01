import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../../shared/services/api.js';

const DiaryAnalyticsPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [moodPrediction, setMoodPrediction] = useState(null);
  const [chartData, setChartData] = useState({});

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Load recommendations
      const recResponse = await apiService.diary.getRecommendations();
      if (recResponse.data.success) {
        setRecommendations(recResponse.data.recommendations);
      }

      // Load mood prediction
      const predResponse = await apiService.diary.predictMood({ prediction_days: 7 });
      if (predResponse.data.success) {
        setMoodPrediction(predResponse.data);
      }

      // Load basic chart data (happiness trend)
      const chartResponse = await apiService.diary.charts.getHappinessTrend(30);
      setChartData(chartResponse.data);

    } catch (err) {
      console.error('Error loading analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (format) => {
    try {
      const response = await apiService.diary.exportData({ format_type: format });
      if (response.data.success) {
        // Create download link
        const blob = new Blob([response.data.data], { 
          type: response.data.content_type 
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.data.filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Export failed:', err);
      setError('Failed to export data');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'badge-error';
      case 'medium': return 'badge-warning';
      case 'low': return 'badge-info';
      default: return 'badge-ghost';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'emotional_regulation': return '🧘';
      case 'mindfulness': return '🌸';
      case 'social_connection': return '👥';
      case 'physical_wellness': return '🏃';
      case 'lifestyle': return '🌱';
      default: return '💡';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-200 flex items-center justify-center">
        <div className="text-center">
          <span className="loading loading-spinner loading-lg"></span>
          <p className="mt-4">Loading analytics...</p>
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
            <h1 className="text-2xl font-bold">📈 Analytics Dashboard</h1>
            <p className="text-base-content/60">AI-powered insights from your diary</p>
          </div>
          <button
            onClick={() => navigate('/diary')}
            className="btn btn-ghost"
          >
            ← Back
          </button>
        </div>

        {/* Quick Stats */}
        {chartData.statistics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="stat bg-base-100 rounded-lg">
              <div className="stat-title">Average Happiness</div>
              <div className="stat-value text-primary">{chartData.statistics.average}</div>
            </div>
            <div className="stat bg-base-100 rounded-lg">
              <div className="stat-title">Total Entries</div>
              <div className="stat-value text-secondary">{chartData.statistics.total_entries}</div>
            </div>
            <div className="stat bg-base-100 rounded-lg">
              <div className="stat-title">Highest Score</div>
              <div className="stat-value text-success">{chartData.statistics.maximum}</div>
            </div>
            <div className="stat bg-base-100 rounded-lg">
              <div className="stat-title">Lowest Score</div>
              <div className="stat-value text-warning">{chartData.statistics.minimum}</div>
            </div>
          </div>
        )}

        {/* Mood Prediction */}
        {moodPrediction && moodPrediction.predictions.length > 0 && (
          <div className="card bg-base-100">
            <div className="card-body">
              <h2 className="card-title">🔮 7-Day Mood Prediction</h2>
              <p className="text-sm text-base-content/60 mb-4">
                Based on your patterns (Confidence: {(moodPrediction.confidence * 100).toFixed(0)}%)
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {moodPrediction.predictions.slice(0, 6).map((prediction, index) => (
                  <div key={index} className="bg-base-200 rounded-lg p-3">
                    <div className="flex justify-between items-center">
                      <div className="text-sm font-medium">
                        {new Date(prediction.date).toLocaleDateString('en-US', { 
                          weekday: 'short', 
                          month: 'short', 
                          day: 'numeric' 
                        })}
                      </div>
                      <div className="text-lg font-bold text-primary">
                        {prediction.predicted_happiness}/10
                      </div>
                    </div>
                    {prediction.likely_emotions.length > 0 && (
                      <div className="mt-2">
                        <div className="text-xs text-base-content/60 mb-1">Likely emotions:</div>
                        <div className="flex flex-wrap gap-1">
                          {prediction.likely_emotions.slice(0, 2).map((emotion, i) => (
                            <span key={i} className="badge badge-outline badge-xs">
                              {emotion.emotion}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Personalized Recommendations */}
        {recommendations.length > 0 && (
          <div className="card bg-base-100">
            <div className="card-body">
              <h2 className="card-title">💡 Personalized Recommendations</h2>
              <p className="text-sm text-base-content/60 mb-4">
                AI-generated suggestions based on your diary patterns
              </p>
              
              <div className="space-y-4">
                {recommendations.map((rec, index) => (
                  <div key={index} className="border border-base-300 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-xl">{getCategoryIcon(rec.category)}</span>
                        <h3 className="font-medium">{rec.title}</h3>
                      </div>
                      <div className="flex space-x-2">
                        <span className={`badge badge-sm ${getPriorityColor(rec.priority)}`}>
                          {rec.priority}
                        </span>
                        {rec.personalized && (
                          <span className="badge badge-primary badge-sm">Personalized</span>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-base-content/80">{rec.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Chart Placeholder */}
        <div className="card bg-base-100">
          <div className="card-body">
            <h2 className="card-title">📊 Happiness Trend</h2>
            <div className="bg-base-200 rounded-lg p-8 text-center">
              <div className="text-4xl mb-4">📈</div>
              <p className="text-base-content/60">
                Chart visualization will be implemented with Chart.js
              </p>
              <p className="text-sm text-base-content/40 mt-2">
                Data is ready from API: {chartData.title || 'Happiness Trend Chart'}
              </p>
            </div>
          </div>
        </div>

        {/* Data Export */}
        <div className="card bg-base-100">
          <div className="card-body">
            <h2 className="card-title">📥 Export Your Data</h2>
            <p className="text-sm text-base-content/60 mb-4">
              Download your diary entries for backup or analysis
            </p>
            
            <div className="flex gap-4">
              <button
                onClick={() => exportData('json')}
                className="btn btn-outline"
              >
                📄 Export as JSON
              </button>
              <button
                onClick={() => exportData('csv')}
                className="btn btn-outline"
              >
                📊 Export as CSV
              </button>
            </div>
          </div>
        </div>

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

export default DiaryAnalyticsPage;
