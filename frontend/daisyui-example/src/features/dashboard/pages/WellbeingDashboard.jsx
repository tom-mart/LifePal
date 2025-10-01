import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../core/auth/AuthContext.jsx';
import { apiService } from '../../../shared/services/api.js';

const WellbeingDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [entries, setEntries] = useState([]);
  const [wellbeingData, setWellbeingData] = useState(null);
  const [chartData, setChartData] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadWellbeingData();
  }, []);

  const loadWellbeingData = async () => {
    try {
      setLoading(true);
      
      // Load recent entries
      const entriesResponse = await apiService.diary.getEntries(1, 10);
      setEntries(entriesResponse.data.entries || []);
      
      // Load wellbeing check
      const wellbeingResponse = await apiService.diary.getWellbeingCheck();
      setWellbeingData(wellbeingResponse.data);
      
      // Load dashboard charts
      const chartsResponse = await apiService.diary.charts.getDashboard();
      setChartData(chartsResponse.data || {});
      
      // Load recommendations
      try {
        const recResponse = await apiService.diary.getRecommendations();
        if (recResponse.data.success) {
          setRecommendations(recResponse.data.recommendations || []);
        }
      } catch (recError) {
        console.log('Recommendations not available:', recError);
      }
      
    } catch (error) {
      console.error('Failed to load wellbeing data:', error);
      setError('Failed to load wellbeing data');
    } finally {
      setLoading(false);
    }
  };

  const diaryTools = [
    {
      id: 'new-entry',
      title: 'New Diary Entry',
      description: 'Start a new reflection session',
      icon: '✍️',
      color: 'btn-primary',
      action: () => navigate('/diary/session')
    },
    {
      id: 'history',
      title: 'Entry History',
      description: 'Browse and search past entries',
      icon: '📚',
      color: 'btn-secondary',
      action: () => navigate('/diary/history')
    },
    {
      id: 'analytics',
      title: 'Analytics',
      description: 'Detailed mood and pattern analysis',
      icon: '📊',
      color: 'btn-accent',
      action: () => navigate('/diary/analytics')
    },
    {
      id: 'predictions',
      title: 'Mood Predictions',
      description: 'AI-powered mood forecasting',
      icon: '🔮',
      color: 'btn-info',
      action: () => navigate('/diary/predictions')
    },
    {
      id: 'wellbeing-check',
      title: 'Wellbeing Check',
      description: 'Quick mental health assessment',
      icon: '🎯',
      color: 'btn-success',
      action: () => navigate('/diary/wellbeing')
    }
  ];

  const getHappinessColor = (score) => {
    if (score >= 8) return 'text-success';
    if (score >= 6) return 'text-warning';
    return 'text-error';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-200 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Breadcrumb */}
        <div className="breadcrumbs text-sm">
          <ul>
            <li><a onClick={() => navigate('/dashboard')} className="cursor-pointer">Dashboard</a></li>
            <li>Diary</li>
          </ul>
        </div>

        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-base-content mb-2">
            Diary Dashboard
          </h1>
          <p className="text-base-content/60">
            Your complete mental health toolkit
          </p>
        </div>

        {/* Diary Tools */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title text-xl mb-4">🧠 Diary Tools</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {diaryTools.map((tool) => (
                <button
                  key={tool.id}
                  onClick={tool.action}
                  className={`btn ${tool.color} h-20 flex-col`}
                >
                  <div className="text-2xl mb-1">{tool.icon}</div>
                  <div className="text-center">
                    <div className="font-medium">{tool.title}</div>
                    <div className="text-xs opacity-80">{tool.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="stat bg-base-100 rounded-xl shadow">
            <div className="stat-figure text-primary">
              <span className="text-2xl">😊</span>
            </div>
            <div className="stat-title">Current Happiness</div>
            <div className="stat-value text-primary">
              {wellbeingData?.current_happiness || 'N/A'}
              {wellbeingData?.current_happiness && '/10'}
            </div>
            <div className="stat-desc">Latest entry</div>
          </div>
          
          <div className="stat bg-base-100 rounded-xl shadow">
            <div className="stat-figure text-secondary">
              <span className="text-2xl">📈</span>
            </div>
            <div className="stat-title">7-Day Average</div>
            <div className="stat-value text-secondary">
              {chartData.happiness_trend?.average_7_days?.toFixed(1) || 'N/A'}
              {chartData.happiness_trend?.average_7_days && '/10'}
            </div>
            <div className="stat-desc">
              {chartData.happiness_trend?.trend === 'improving' && '↗️ Improving'}
              {chartData.happiness_trend?.trend === 'declining' && '↘️ Declining'}
              {chartData.happiness_trend?.trend === 'stable' && '→ Stable'}
            </div>
          </div>
          
          <div className="stat bg-base-100 rounded-xl shadow">
            <div className="stat-figure text-accent">
              <span className="text-2xl">📝</span>
            </div>
            <div className="stat-title">Recent Entries</div>
            <div className="stat-value text-accent">{entries.length}</div>
            <div className="stat-desc">Last 10 entries</div>
          </div>
        </div>

        {/* AI Recommendations */}
        {recommendations.length > 0 && (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-xl mb-4">🤖 AI Recommendations</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendations.slice(0, 4).map((rec, index) => (
                  <div key={index} className="bg-base-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">{rec.category === 'mindfulness' ? '🧘' : 
                                                   rec.category === 'social' ? '👥' : 
                                                   rec.category === 'lifestyle' ? '🌟' : '💭'}</div>
                      <div>
                        <h4 className="font-medium capitalize">{rec.category}</h4>
                        <p className="text-sm text-base-content/70 mt-1">{rec.recommendation}</p>
                        <div className="text-xs text-base-content/50 mt-2">
                          Priority: {rec.priority}/10
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Recent Entries */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <h2 className="card-title text-xl">📚 Recent Entries</h2>
              <button 
                onClick={() => navigate('/diary/history')}
                className="btn btn-ghost btn-sm"
              >
                View All →
              </button>
            </div>
            
            {entries.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📝</div>
                <p className="text-base-content/60 mb-4">No diary entries yet</p>
                <button 
                  onClick={() => navigate('/diary/session')}
                  className="btn btn-primary"
                >
                  Start Your First Entry
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {entries.slice(0, 5).map((entry) => (
                  <div 
                    key={entry.id} 
                    className="flex items-center gap-4 p-3 bg-base-200 rounded-lg cursor-pointer hover:bg-base-300 transition-colors"
                    onClick={() => navigate(`/diary/entries/${entry.id}`)}
                  >
                    <div className="text-2xl">📝</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">Diary Entry</span>
                        {entry.happiness_score !== null && entry.happiness_score !== undefined && (
                          <span className={`text-sm font-medium ${getHappinessColor(entry.happiness_score)}`}>
                            😊 {entry.happiness_score}/10
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-base-content/60">
                        {entry.summary_preview || 'Entry completed'}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-base-content/50">
                        {formatDate(entry.created_at)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Emotion Overview */}
        {chartData.emotion_distribution && (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-xl mb-4">🎭 Recent Emotions</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {chartData.emotion_distribution.emotions?.slice(0, 8).map((emotion, index) => (
                  <div key={index} className="text-center p-3 bg-base-200 rounded-lg">
                    <div className="text-2xl mb-2">{emotion.emoji || '😊'}</div>
                    <div className="font-medium text-sm">{emotion.name}</div>
                    <div className="text-xs text-base-content/60">{emotion.count} times</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WellbeingDashboard;
