import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../../core/auth/AuthContext.jsx';
import { apiService } from '../../../shared/services/api.js';
// NotificationSettings removed - using MDN implementation in Settings page

const MainDashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [recentEvents, setRecentEvents] = useState([]);
  const [quickStats, setQuickStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showSuccessBanner, setShowSuccessBanner] = useState(false);
  // Notification settings moved to Settings page

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Show success banner if redirected after completing a session
  useEffect(() => {
    if (location.state?.sessionComplete) {
      setShowSuccessBanner(true);
      // Clear router state to prevent banner from reappearing on back/refresh
      navigate(location.pathname, { replace: true, state: {} });
      const timer = setTimeout(() => setShowSuccessBanner(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [location.state, location.pathname, navigate]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load recent diary entries
      console.log('🔍 Loading diary entries...');
      let recentEntries = [];
      try {
        const entriesResponse = await apiService.diary.getEntries(1, 5);
        console.log('📊 Entries API Response:', entriesResponse);
        console.log('📊 Entries Data:', entriesResponse.data);
        
        recentEntries = entriesResponse.data.entries || [];
        console.log('📝 Recent Entries:', recentEntries);
        console.log('📝 Entries Count:', recentEntries.length);
      } catch (entriesError) {
        console.error('❌ Failed to load diary entries:', entriesError);
        console.error('❌ Error details:', entriesError.response?.data);
        recentEntries = [];
      }
      
      // Load user stats with fallback
      let stats = { total_entries: 0, current_streak: 0 };
      try {
        console.log('📈 Loading diary stats...');
        const statsResponse = await apiService.diary.getStats();
        console.log('📊 Stats API Response:', statsResponse);
        stats = statsResponse.data;
        console.log('📊 Stats Data:', stats);
      } catch (error) {
        console.warn('⚠️ Failed to load stats, using fallback:', error.message);
        // Fallback: use entry count from recent entries
        stats.total_entries = recentEntries.length;
        stats.current_streak = recentEntries.length > 0 ? 1 : 0;
      }
      
      // Use API average happiness if provided; respect 0 values as valid
      const apiAvg = typeof stats.average_happiness === 'number' ? stats.average_happiness : null;
      // Fallback: Calculate from recent entries using happiness_score returned by API
      let computedAvg = null;
      const entriesWithHappiness = recentEntries.filter(entry => typeof entry.happiness_score === 'number');
      if (entriesWithHappiness.length > 0) {
        const sum = entriesWithHappiness.reduce((acc, entry) => acc + entry.happiness_score, 0);
        computedAvg = Math.round((sum / entriesWithHappiness.length) * 10) / 10;
      }
      
      // Choose display average: if API returns 0 but we have computed average from entries, use computed
      const displayAvg = (apiAvg === 0 && computedAvg !== null) ? computedAvg : (apiAvg ?? computedAvg ?? 0);

      console.log('🎯 Happiness Calculation Debug:');
      console.log('  Full stats object:', stats);
      console.log('  API average_happiness:', stats.average_happiness);
      console.log('  Type of average_happiness:', typeof stats.average_happiness);
      console.log('  Is truthy?:', !!stats.average_happiness);
      console.log('  Using average:', displayAvg);
      console.log('  Setting quickStats.avg_happiness to:', displayAvg);
      
      console.log('🔥 DIRECT FIX: Using stats.average_happiness directly when available:', stats.average_happiness);
      
      setQuickStats({
        total_entries: stats.total_entries || recentEntries.length,
        avg_happiness: displayAvg,
        current_streak: stats.current_streak || (recentEntries.length > 0 ? 1 : 0),
        entries_this_week: recentEntries.length
      });
      
      // Format recent events
      const events = recentEntries.map(entry => ({
        id: entry.id,
        type: 'diary',
        title: 'New diary entry',
        description: entry.summary_preview || 'Diary entry completed',
        timestamp: entry.created_at,
        happiness_score: entry.happiness_score,
        icon: '✍️'
      }));
      
      console.log('🎯 Formatted Events:', events);
      setRecentEvents(events);
      
    } catch (error) {
      console.error('❌ Failed to load dashboard data:', error);
      console.error('❌ Error details:', error.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  const availableTools = [
    {
      id: 'wellbeing',
      title: 'Diary',
      description: 'Diary tools, analytics & insights',
      icon: '🧠',
      color: 'bg-primary',
      path: '/dashboard/wellbeing'
    },
    {
      id: 'finance',
      title: 'Finance',
      description: 'Budget & expense tracking',
      icon: '💰',
      color: 'bg-success',
      path: '/finance',
      comingSoon: true
    },
    {
      id: 'kitchen',
      title: 'Kitchen',
      description: 'Meal planning & pantry',
      icon: '🍳',
      color: 'bg-warning',
      path: '/kitchen',
      comingSoon: true
    },
    {
      id: 'projects',
      title: 'Projects',
      description: 'Task & project management',
      icon: '📋',
      color: 'bg-info',
      path: '/projects',
      comingSoon: true
    },
    {
      id: 'schedule',
      title: 'Schedule',
      description: 'Calendar & time management',
      icon: '📅',
      color: 'bg-secondary',
      path: '/schedule',
      comingSoon: true
    }
  ];

  const quickActions = [
    {
      title: 'New Diary Entry',
      icon: '✍️',
      action: () => navigate('/diary/session'),
      color: 'btn-primary'
    },
    {
      title: 'Relationships',
      icon: '🤝',
      action: () => navigate('/relationships'),
      color: 'btn-success'
    },
    {
      title: 'Home',
      icon: '🏠',
      action: () => navigate('/home'),
      color: 'btn-warning'
    },
    {
      title: 'Settings',
      icon: '⚙️',
      action: () => navigate('/settings'),
      color: 'btn-info'
    },
    {
      title: 'View Profile',
      icon: '👤',
      action: () => navigate('/dashboard/profile'),
      color: 'btn-secondary'
    }
  ];

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
        {showSuccessBanner && (
          <div className="alert alert-success shadow">
            <span>Session successfully saved.</span>
          </div>
        )}
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-base-content mb-2">
            {getGreeting()}, {user?.first_name || 'friend'}!
          </h1>
          <p className="text-base-content/60">
            Welcome to your LifePal dashboard
          </p>
        </div>


        {/* Quick Actions */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title text-xl mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={action.action}
                  className={`btn ${action.color} h-16 flex-col`}
                >
                  <div className="text-2xl mb-1">{action.icon}</div>
                  <span className="text-sm">{action.title}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="stat bg-base-100 rounded-xl shadow">
            <div className="stat-figure text-primary">
              <span className="text-2xl">📝</span>
            </div>
            <div className="stat-title">Total Entries</div>
            <div className="stat-value text-primary">{quickStats.total_entries || 0}</div>
            <div className="stat-desc">All time</div>
          </div>
          
          <div className="stat bg-base-100 rounded-xl shadow">
            <div className="stat-figure text-secondary">
              <span className="text-2xl">😊</span>
            </div>
            <div className="stat-title">Avg Happiness</div>
            <div className="stat-value text-secondary">{quickStats.avg_happiness || 0}/10</div>
            <div className="stat-desc">This month</div>
          </div>
          
          <div className="stat bg-base-100 rounded-xl shadow">
            <div className="stat-figure text-accent">
              <span className="text-2xl">🔥</span>
            </div>
            <div className="stat-title">Current Streak</div>
            <div className="stat-value text-accent">{quickStats.current_streak || 0}</div>
            <div className="stat-desc">Days in a row</div>
          </div>
          
          <div className="stat bg-base-100 rounded-xl shadow">
            <div className="stat-figure text-success">
              <span className="text-2xl">🎯</span>
            </div>
            <div className="stat-title">This Week</div>
            <div className="stat-value text-success">{quickStats.entries_this_week || 0}</div>
            <div className="stat-desc">Entries logged</div>
          </div>
        </div>

        {/* Available Tools */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h2 className="card-title text-xl mb-4">Available Tools</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableTools.map((tool) => (
                <div
                  key={tool.id}
                  className={`card ${tool.comingSoon ? 'opacity-60' : 'cursor-pointer hover:shadow-lg'} transition-all`}
                  onClick={() => !tool.comingSoon && navigate(tool.path)}
                >
                  <div className="card-body p-4">
                    <div className={`w-12 h-12 ${tool.color} rounded-xl flex items-center justify-center text-white text-2xl mb-3`}>
                      {tool.icon}
                    </div>
                    <h3 className="font-bold text-lg">{tool.title}</h3>
                    <p className="text-sm text-base-content/60 mb-2">{tool.description}</p>
                    {tool.comingSoon && (
                      <div className="badge badge-outline">Coming Soon</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Events */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <h2 className="card-title text-xl">Recent Activity</h2>
              <button 
                onClick={() => navigate('/dashboard/wellbeing')}
                className="btn btn-ghost btn-sm"
              >
                View All →
              </button>
            </div>
            
            {recentEvents.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📝</div>
                <p className="text-base-content/60">No recent activity</p>
                <button 
                  onClick={() => navigate('/diary/session')}
                  className="btn btn-primary btn-sm mt-4"
                >
                  Start Your First Entry
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {recentEvents.map((event) => (
                  <div key={event.id} className="flex items-center gap-4 p-3 bg-base-200 rounded-lg">
                    <div className="text-2xl">{event.icon}</div>
                    <div className="flex-1">
                      <h4 className="font-medium">{event.title}</h4>
                      <p className="text-sm text-base-content/60">{event.description}</p>
                    </div>
                    <div className="text-right">
                      {event.happiness_score && (
                        <div className="text-sm font-medium">
                          😊 {event.happiness_score}/10
                        </div>
                      )}
                      <div className="text-xs text-base-content/50">
                        {formatDate(event.timestamp)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Notification settings moved to Settings page */}
    </div>
  );
};

export default MainDashboard;
