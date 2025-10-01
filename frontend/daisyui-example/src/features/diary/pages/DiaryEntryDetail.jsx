import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDiary } from '../context/DiaryContext.jsx';
import { apiService } from '../../../shared/services/api.js';

const DiaryEntryDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { loading, error } = useDiary();
  
  const [entry, setEntry] = useState(null);
  const [entryLoading, setEntryLoading] = useState(true);
  const [entryError, setEntryError] = useState(null);
  const [regenerating, setRegenerating] = useState(false);
  const [regenerateSuccess, setRegenerateSuccess] = useState(false);
  
  // Happiness score correction
  const [editingHappiness, setEditingHappiness] = useState(false);
  const [newHappinessScore, setNewHappinessScore] = useState(0);
  const [updatingHappiness, setUpdatingHappiness] = useState(false);
  const [happinessUpdateSuccess, setHappinessUpdateSuccess] = useState(false);
  
  // Response editing
  const [editingResponses, setEditingResponses] = useState({});
  const [editedResponses, setEditedResponses] = useState({});
  const [updatingResponse, setUpdatingResponse] = useState(false);
  const [responseUpdateSuccess, setResponseUpdateSuccess] = useState('');
  
  // Response visibility
  const [responsesVisible, setResponsesVisible] = useState(false);

  useEffect(() => {
    loadEntryDetail();
  }, [id]);

  const loadEntryDetail = async () => {
    try {
      setEntryLoading(true);
      setEntryError(null);
      
      console.log('Loading entry detail for ID:', id);
      const response = await apiService.diary.getEntryDetail(id);
      console.log('Entry detail response:', response.data);
      
      setEntry(response.data);
    } catch (error) {
      console.error('Failed to load entry detail:', error);
      if (error.response?.status === 404) {
        setEntryError('Diary entry not found');
      } else {
        setEntryError('Failed to load diary entry');
      }
    } finally {
      setEntryLoading(false);
    }
  };

  const getHappinessColor = (score) => {
    if (score >= 8) return 'text-success';
    if (score >= 6) return 'text-warning';
    if (score >= 4) return 'text-info';
    return 'text-error';
  };

  const handleRegenerateSummary = async () => {
    try {
      setRegenerating(true);
      setRegenerateSuccess(false);
      
      await apiService.diary.regenerateSummary(id);
      
      // Reload the entry to get the new summary
      await loadEntryDetail();
      
      setRegenerateSuccess(true);
      setTimeout(() => setRegenerateSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to regenerate summary:', error);
      alert('Failed to regenerate summary. Please try again.');
    } finally {
      setRegenerating(false);
    }
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

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleEditHappiness = () => {
    setNewHappinessScore(entry.happiness_score || 5);
    setEditingHappiness(true);
  };

  const handleUpdateHappiness = async () => {
    try {
      setUpdatingHappiness(true);
      
      await apiService.diary.updateHappinessScore(id, newHappinessScore);
      
      // Update the entry locally
      setEntry(prev => ({ ...prev, happiness_score: newHappinessScore }));
      
      setEditingHappiness(false);
      setHappinessUpdateSuccess(true);
      setTimeout(() => setHappinessUpdateSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to update happiness score:', error);
      alert('Failed to update happiness score. Please try again.');
    } finally {
      setUpdatingHappiness(false);
    }
  };

  const handleCancelHappinessEdit = () => {
    setEditingHappiness(false);
    setNewHappinessScore(entry.happiness_score || 5);
  };

  const isEntryEditable = () => {
    if (!entry) return false;
    const entryDate = new Date(entry.entry_date);
    const today = new Date();
    const diffTime = Math.abs(today - entryDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 3;
  };

  const handleEditResponse = (responseId, currentText) => {
    setEditingResponses(prev => ({ ...prev, [responseId]: true }));
    setEditedResponses(prev => ({ ...prev, [responseId]: currentText }));
  };

  const handleCancelResponseEdit = (responseId) => {
    setEditingResponses(prev => ({ ...prev, [responseId]: false }));
    setEditedResponses(prev => {
      const newState = { ...prev };
      delete newState[responseId];
      return newState;
    });
  };

  const handleSaveResponse = async (responseId) => {
    try {
      setUpdatingResponse(true);
      
      // Call API to update response
      await apiService.diary.updateResponse(responseId, editedResponses[responseId]);
      
      // Update local state
      setEntry(prev => ({
        ...prev,
        responses: prev.responses.map(resp => 
          resp.id === responseId 
            ? { ...resp, response_text: editedResponses[responseId] }
            : resp
        )
      }));
      
      // Clear editing state
      setEditingResponses(prev => ({ ...prev, [responseId]: false }));
      setEditedResponses(prev => {
        const newState = { ...prev };
        delete newState[responseId];
        return newState;
      });
      
      setResponseUpdateSuccess(responseId);
      setTimeout(() => setResponseUpdateSuccess(''), 3000);
      
    } catch (error) {
      console.error('Failed to update response:', error);
      alert('Failed to update response. Please try again.');
    } finally {
      setUpdatingResponse(false);
    }
  };

  const handleResponseTextChange = (responseId, newText) => {
    setEditedResponses(prev => ({ ...prev, [responseId]: newText }));
  };

  if (entryLoading) {
    return (
      <div className="min-h-screen bg-base-200 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="flex justify-center py-8">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        </div>
      </div>
    );
  }

  if (entryError || !entry) {
    return (
      <div className="min-h-screen bg-base-200 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="alert alert-error">
            <span>{entryError || 'Entry not found'}</span>
          </div>
          <div className="mt-4 text-center">
            <button
              onClick={() => navigate('/diary/history')}
              className="btn btn-ghost"
            >
              ← Back to History
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-bold text-base-content mb-2">
            Diary Entry
          </h1>
          <p className="text-base-content/60">
            {formatDate(entry.entry_date)}
          </p>
        </div>

        {/* Entry Overview */}
        <div className="card bg-base-100 border border-base-300">
          <div className="card-body p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-lg font-semibold mb-1">
                  {formatDate(entry.entry_date)}
                </h2>
                <p className="text-sm text-base-content/60">
                  Created at {formatTime(entry.created_at)}
                </p>
              </div>
              <div className="text-center">
                {editingHappiness ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-center space-x-2">
                      <input
                        type="range"
                        min="0"
                        max="10"
                        step="0.5"
                        value={newHappinessScore}
                        onChange={(e) => setNewHappinessScore(parseFloat(e.target.value))}
                        className="range range-primary range-sm"
                      />
                    </div>
                    <div className="flex items-center justify-center space-x-2 mb-1">
                      <span className={`text-2xl ${getHappinessColor(newHappinessScore)}`}>
                        {getHappinessEmoji(newHappinessScore)}
                      </span>
                      <span className="font-bold text-lg">
                        {newHappinessScore}/10
                      </span>
                    </div>
                    <div className="flex gap-2 justify-center">
                      <button
                        onClick={handleUpdateHappiness}
                        disabled={updatingHappiness}
                        className={`btn btn-xs btn-success ${updatingHappiness ? 'loading' : ''}`}
                      >
                        {updatingHappiness ? 'Saving...' : '✅ Save'}
                      </button>
                      <button
                        onClick={handleCancelHappinessEdit}
                        className="btn btn-xs btn-ghost"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-center justify-center space-x-2 mb-1">
                      <span className={`text-2xl ${getHappinessColor(entry.happiness_score)}`}>
                        {getHappinessEmoji(entry.happiness_score)}
                      </span>
                      <span className="font-bold text-lg">
                        {entry.happiness_score}/10
                      </span>
                      <button
                        onClick={handleEditHappiness}
                        className="btn btn-xs btn-ghost ml-2"
                        title="Edit happiness score"
                      >
                        ✏️
                      </button>
                    </div>
                    <p className="text-xs text-base-content/60">
                      Happiness {happinessUpdateSuccess && <span className="text-success">✅ Updated!</span>}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* AI Summary */}
            {entry.summary && (
              <div className="bg-base-200 rounded-lg p-4 mb-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium">🤖 AI Summary</h3>
                  <button
                    onClick={handleRegenerateSummary}
                    disabled={regenerating}
                    className={`btn btn-xs ${regenerateSuccess ? 'btn-success' : 'btn-ghost'} ${regenerating ? 'loading' : ''}`}
                    title="Regenerate AI summary with current AI model"
                  >
                    {regenerateSuccess ? '✅ Updated!' : regenerating ? 'Regenerating...' : '🔄 Regenerate'}
                  </button>
                </div>
                <p className="text-base-content/80">
                  {entry.summary}
                </p>
              </div>
            )}

            {/* Emotions */}
            {entry.emotions && entry.emotions.length > 0 && (
              <div className="mb-4">
                <h3 className="font-medium mb-2">😊 Emotions</h3>
                <div className="flex flex-wrap gap-2">
                  {entry.emotions.map((emotion, index) => (
                    <div
                      key={index}
                      className="badge badge-outline badge-lg"
                    >
                      {emotion.emotion?.name || emotion.emotion_name}
                      {emotion.intensity && (
                        <span className="ml-1 text-xs opacity-60">
                          {emotion.intensity}/5
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Questions and Responses */}
        <div className="space-y-4">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body p-4">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setResponsesVisible(!responsesVisible)}
                  className="flex items-center gap-2 text-lg font-semibold hover:text-primary transition-colors"
                >
                  <span className={`transform transition-transform ${responsesVisible ? 'rotate-90' : ''}`}>
                    ▶️
                  </span>
                  💬 Your Responses
                  <span className="text-sm font-normal text-base-content/60">
                    ({entry.responses?.length || 0} responses)
                  </span>
                </button>
                {isEntryEditable() && (
                  <div className="badge badge-info">Editable for {3 - Math.ceil((new Date() - new Date(entry.entry_date)) / (1000 * 60 * 60 * 24))} more days</div>
                )}
              </div>
              
              {!responsesVisible && (
                <p className="text-sm text-base-content/60 mt-2">
                  🔒 Click to view your detailed responses (collapsed for privacy)
                </p>
              )}
            </div>
          </div>
          
          {responsesVisible && (
            <>
              {entry.responses && entry.responses.length > 0 ? (
                entry.responses.map((response, index) => (
              <div key={response.id || index} className="card bg-base-100 border border-base-300">
                <div className="card-body p-6">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-content font-bold text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-primary">
                          {response.question?.question_text || `Question ${index + 1}`}
                        </h3>
                        {isEntryEditable() && !editingResponses[response.id] && (
                          <button
                            onClick={() => handleEditResponse(response.id, response.response_text)}
                            className="btn btn-xs btn-ghost"
                            title="Edit response"
                          >
                            ✏️ Edit
                          </button>
                        )}
                      </div>
                      
                      {editingResponses[response.id] ? (
                        <div className="space-y-3">
                          <textarea
                            className="textarea textarea-bordered w-full h-32 resize-none"
                            value={editedResponses[response.id] || ''}
                            onChange={(e) => handleResponseTextChange(response.id, e.target.value)}
                            placeholder="Edit your response..."
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleSaveResponse(response.id)}
                              disabled={updatingResponse}
                              className={`btn btn-xs btn-success ${updatingResponse ? 'loading' : ''}`}
                            >
                              {updatingResponse ? 'Saving...' : '✅ Save'}
                            </button>
                            <button
                              onClick={() => handleCancelResponseEdit(response.id)}
                              className="btn btn-xs btn-ghost"
                            >
                              Cancel
                            </button>
                          </div>
                          {responseUpdateSuccess === response.id && (
                            <div className="text-success text-sm">✅ Response updated!</div>
                          )}
                        </div>
                      ) : (
                        <div>
                          <p className="text-base-content/80 leading-relaxed">
                            {response.response_text}
                          </p>
                          {responseUpdateSuccess === response.id && (
                            <div className="text-success text-sm mt-2">✅ Response updated!</div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="card bg-base-100 border border-base-300">
              <div className="card-body p-6 text-center">
                <div className="text-4xl mb-2">🔒</div>
                <h3 className="font-medium mb-2">Detailed responses not available</h3>
                <p className="text-sm text-base-content/60">
                  Individual responses are encrypted for privacy. You can see the AI summary above.
                </p>
              </div>
            </div>
          )}
            </>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => navigate('/diary/history')}
            className="btn btn-ghost"
          >
            ← Back to History
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-outline"
          >
            🏠 Dashboard
          </button>
        </div>

        {/* Entry Stats */}
        <div className="card bg-base-100 border border-base-300">
          <div className="card-body p-4">
            <h3 className="font-medium mb-2">📊 Entry Statistics</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-base-content/60">Questions answered:</span>
                <span className="font-medium ml-2">{entry.response_count || 0}</span>
              </div>
              <div>
                <span className="text-base-content/60">Emotions detected:</span>
                <span className="font-medium ml-2">{entry.emotions?.length || 0}</span>
              </div>
              <div>
                <span className="text-base-content/60">Entry type:</span>
                <span className="font-medium ml-2 capitalize">{entry.entry_type || 'diary'}</span>
              </div>
              <div>
                <span className="text-base-content/60">Status:</span>
                <span className="font-medium ml-2">
                  {entry.is_completed ? '✅ Complete' : '⏳ In Progress'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiaryEntryDetail;
