import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDiary } from '../context/DiaryContext.jsx';

const DiaryHistory = () => {
  const navigate = useNavigate();
  const { entries, loading, error, loadEntries } = useDiary();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEmotion, setSelectedEmotion] = useState('');
  const [dateFilter, setDateFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [filteredEntries, setFilteredEntries] = useState([]);

  useEffect(() => {
    loadEntries();
  }, []);

  useEffect(() => {
    filterAndSortEntries();
  }, [entries, searchTerm, selectedEmotion, dateFilter, sortBy]);

  const filterAndSortEntries = () => {
    let filtered = [...(entries || [])];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(entry => 
        entry.ai_summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        entry.responses?.some(response => 
          response.response_text?.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Filter by emotion
    if (selectedEmotion) {
      filtered = filtered.filter(entry =>
        entry.emotions?.some(emotion => 
          emotion.emotion_name.toLowerCase() === selectedEmotion.toLowerCase()
        )
      );
    }

    // Filter by date
    const now = new Date();
    if (dateFilter !== 'all') {
      filtered = filtered.filter(entry => {
        const entryDate = new Date(entry.entry_date);
        const daysDiff = Math.floor((now - entryDate) / (1000 * 60 * 60 * 24));
        
        switch (dateFilter) {
          case 'week': return daysDiff <= 7;
          case 'month': return daysDiff <= 30;
          case '3months': return daysDiff <= 90;
          default: return true;
        }
      });
    }

    // Sort entries
    filtered.sort((a, b) => {
      const dateA = new Date(a.entry_date);
      const dateB = new Date(b.entry_date);
      
      switch (sortBy) {
        case 'oldest': return dateA - dateB;
        case 'happiness_high': return b.happiness_score - a.happiness_score;
        case 'happiness_low': return a.happiness_score - b.happiness_score;
        default: return dateB - dateA; // newest first
      }
    });

    setFilteredEntries(filtered);
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
    const date = new Date(dateString);
    const today = new Date();
    const diffTime = today - date;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedEmotion('');
    setDateFilter('all');
    setSortBy('newest');
  };

  const uniqueEmotions = [...new Set(
    entries?.flatMap(entry => 
      entry.emotions?.map(emotion => emotion.emotion_name) || []
    ) || []
  )];

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-base-content mb-2">Diary History</h1>
          <p className="text-base-content/60">
            {entries?.length || 0} entries • {filteredEntries.length} showing
          </p>
        </div>

        {/* Search and Filters */}
        <div className="card bg-base-100 border border-base-300">
          <div className="card-body p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              
              {/* Search */}
              <div>
                <label className="label label-text font-medium">Search</label>
                <input
                  type="text"
                  placeholder="Search entries..."
                  className="input input-bordered input-sm w-full"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              {/* Emotion Filter */}
              <div>
                <label className="label label-text font-medium">Emotion</label>
                <select
                  className="select select-bordered select-sm w-full"
                  value={selectedEmotion}
                  onChange={(e) => setSelectedEmotion(e.target.value)}
                >
                  <option value="">All emotions</option>
                  {uniqueEmotions.map(emotion => (
                    <option key={emotion} value={emotion}>
                      {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date Filter */}
              <div>
                <label className="label label-text font-medium">Time Period</label>
                <select
                  className="select select-bordered select-sm w-full"
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                >
                  <option value="all">All time</option>
                  <option value="week">Last week</option>
                  <option value="month">Last month</option>
                  <option value="3months">Last 3 months</option>
                </select>
              </div>

              {/* Sort */}
              <div>
                <label className="label label-text font-medium">Sort by</label>
                <select
                  className="select select-bordered select-sm w-full"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="newest">Newest first</option>
                  <option value="oldest">Oldest first</option>
                  <option value="happiness_high">Highest happiness</option>
                  <option value="happiness_low">Lowest happiness</option>
                </select>
              </div>
            </div>

            {/* Clear Filters */}
            {(searchTerm || selectedEmotion || dateFilter !== 'all' || sortBy !== 'newest') && (
              <div className="mt-4">
                <button
                  onClick={clearFilters}
                  className="btn btn-ghost btn-sm"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Entries List */}
        {loading ? (
          <div className="flex justify-center py-8">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        ) : error ? (
          <div className="alert alert-error">
            <span>{error}</span>
          </div>
        ) : filteredEntries.length > 0 ? (
          <div className="space-y-4">
            {filteredEntries.map((entry) => (
              <div
                key={entry.id}
                className="card bg-base-100 border border-base-300 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate(`/diary/entries/${entry.id}`)}
              >
                <div className="card-body p-6">
                  <div className="flex justify-between items-start mb-3">
                    <div className="text-sm font-medium text-base-content/80">
                      {formatDate(entry.entry_date)}
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`text-xl ${getHappinessColor(entry.happiness_score)}`}>
                        {getHappinessEmoji(entry.happiness_score)}
                      </span>
                      <span className="font-bold text-sm">
                        {entry.happiness_score}/10
                      </span>
                    </div>
                  </div>

                  {/* AI Summary */}
                  {entry.ai_summary && (
                    <p className="text-base-content/80 mb-3 line-clamp-2">
                      {entry.ai_summary}
                    </p>
                  )}

                  {/* Emotions */}
                  {entry.emotions && entry.emotions.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {entry.emotions.slice(0, 4).map((emotion, index) => (
                        <span
                          key={index}
                          className="badge badge-outline badge-sm"
                        >
                          {emotion.emotion_name}
                        </span>
                      ))}
                      {entry.emotions.length > 4 && (
                        <span className="badge badge-outline badge-sm">
                          +{entry.emotions.length - 4} more
                        </span>
                      )}
                    </div>
                  )}

                  {/* Entry Stats */}
                  <div className="flex justify-between items-center text-xs text-base-content/60">
                    <span>{entry.responses?.length || 0} responses</span>
                    <span>
                      {entry.created_at !== entry.entry_date && 
                        `Created ${formatDate(entry.created_at)}`
                      }
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card bg-base-100 border border-base-300">
            <div className="card-body p-8 text-center">
              <div className="text-4xl mb-4">📝</div>
              <h3 className="font-medium mb-2">
                {entries?.length === 0 ? 'No entries yet' : 'No entries match your filters'}
              </h3>
              <p className="text-sm text-base-content/60 mb-4">
                {entries?.length === 0 
                  ? 'Start your journey with your first reflection'
                  : 'Try adjusting your search or filter criteria'
                }
              </p>
              {entries?.length === 0 && (
                <button
                  onClick={() => navigate('/diary/session')}
                  className="btn btn-primary btn-sm"
                >
                  Create First Entry
                </button>
              )}
            </div>
          </div>
        )}

        {/* Back Button */}
        <div className="text-center">
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-ghost"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default DiaryHistory;
