import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../../shared/services/api.js';
import InvitationCodeManager from '../../components/InvitationCodeManager.jsx';

const RelationshipsPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [relationships, setRelationships] = useState([]);
  const [receivedRequests, setReceivedRequests] = useState([]);
  const [stats, setStats] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRequest, setNewRequest] = useState({
    to_user_email: '',
    relationship_type: 'friend',
    message: ''
  });

  useEffect(() => {
    loadRelationshipData();
  }, []);

  const loadRelationshipData = async () => {
    try {
      setLoading(true);
      
      // Load relationships
      const relResponse = await apiService.relationships.getRelationships();
      if (relResponse.data.results) {
        setRelationships(relResponse.data.results);
      }

      // Load received requests
      const reqResponse = await apiService.relationships.getReceivedRequests();
      if (reqResponse.data.results) {
        setReceivedRequests(reqResponse.data.results);
      }

      // Load stats
      const statsResponse = await apiService.relationships.getStats();
      setStats(statsResponse.data);

    } catch (err) {
      console.error('Error loading relationships:', err);
      setError('Failed to load relationship data');
    } finally {
      setLoading(false);
    }
  };

  const sendRequest = async () => {
    try {
      const response = await apiService.relationships.sendRequest(newRequest);
      if (response.data.success) {
        setShowAddForm(false);
        setNewRequest({ to_user_email: '', relationship_type: 'friend', message: '' });
        // Show success message
        alert('Relationship request sent successfully!');
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      console.error('Error sending request:', err);
      setError('Failed to send relationship request');
    }
  };

  const respondToRequest = async (requestId, action) => {
    try {
      const response = await apiService.relationships.respondToRequest(requestId, { action });
      if (response.data.success) {
        // Reload data
        loadRelationshipData();
        alert(`Request ${action}ed successfully!`);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      console.error('Error responding to request:', err);
      setError('Failed to respond to request');
    }
  };

  const analyzeRelationship = async (relationshipId) => {
    try {
      const response = await apiService.relationships.analyzeRelationship(
        relationshipId, 
        { analysis_days: 30 }
      );
      if (response.data.success) {
        alert(`Analysis complete! Generated ${response.data.data.insights_created} new insights.`);
        // Reload to show updated data
        loadRelationshipData();
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      console.error('Error analyzing relationship:', err);
      setError('Failed to analyze relationship');
    }
  };

  const getHealthColor = (score) => {
    if (score >= 8) return 'text-success';
    if (score >= 6) return 'text-warning';
    return 'text-error';
  };

  const getHealthEmoji = (score) => {
    if (score >= 8) return '💚';
    if (score >= 6) return '💛';
    return '❤️‍🩹';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-200 flex items-center justify-center">
        <div className="text-center">
          <span className="loading loading-spinner loading-lg"></span>
          <p className="mt-4">Loading relationships...</p>
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
            <h1 className="text-2xl font-bold">🤝 Relationships</h1>
            <p className="text-base-content/60">Connect with family and friends</p>
          </div>
          <button
            onClick={() => navigate('/diary')}
            className="btn btn-ghost"
          >
            ← Back
          </button>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="stat bg-base-100 rounded-lg">
              <div className="stat-title">Total Connections</div>
              <div className="stat-value text-primary">{stats.total_relationships}</div>
            </div>
            <div className="stat bg-base-100 rounded-lg">
              <div className="stat-title">Active</div>
              <div className="stat-value text-success">{stats.active_relationships}</div>
            </div>
            <div className="stat bg-base-100 rounded-lg">
              <div className="stat-title">Pending Requests</div>
              <div className="stat-value text-warning">{stats.pending_requests_received}</div>
            </div>
            <div className="stat bg-base-100 rounded-lg">
              <div className="stat-title">Avg Health</div>
              <div className="stat-value text-secondary">{stats.average_health_score}</div>
            </div>
          </div>
        )}

        {/* Invitation Code Manager */}
        <InvitationCodeManager onCodeUsed={loadRelationshipData} />

        {/* Legacy Email-based Connection (Collapsible) */}
        <div className="card bg-base-100">
          <div className="card-body">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="card-title">📧 Email-based Connection</h2>
                <p className="text-sm text-base-content/60">Legacy method - use invitation codes above instead</p>
              </div>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="btn btn-outline btn-sm"
              >
                {showAddForm ? 'Cancel' : 'Use Email'}
              </button>
            </div>

            {showAddForm && (
              <div className="space-y-4">
                <div className="alert alert-warning">
                  <span>⚠️ Email-based invitations require knowing the exact email address. Consider using invitation codes instead!</span>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Email Address</span>
                  </label>
                  <input
                    type="email"
                    placeholder="friend@example.com"
                    className="input input-bordered"
                    value={newRequest.to_user_email}
                    onChange={(e) => setNewRequest({...newRequest, to_user_email: e.target.value})}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Relationship Type</span>
                  </label>
                  <select
                    className="select select-bordered"
                    value={newRequest.relationship_type}
                    onChange={(e) => setNewRequest({...newRequest, relationship_type: e.target.value})}
                  >
                    <option value="friend">Friend</option>
                    <option value="family">Family Member</option>
                    <option value="spouse">Spouse/Partner</option>
                    <option value="parent">Parent</option>
                    <option value="child">Child</option>
                    <option value="sibling">Sibling</option>
                    <option value="colleague">Colleague</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Message (Optional)</span>
                  </label>
                  <textarea
                    placeholder="Hi! I'd like to connect with you on LifePal..."
                    className="textarea textarea-bordered"
                    value={newRequest.message}
                    onChange={(e) => setNewRequest({...newRequest, message: e.target.value})}
                  />
                </div>

                <button
                  onClick={sendRequest}
                  className="btn btn-primary"
                  disabled={!newRequest.to_user_email}
                >
                  Send Email Request
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Pending Requests */}
        {receivedRequests.length > 0 && (
          <div className="card bg-base-100">
            <div className="card-body">
              <h2 className="card-title">📬 Pending Requests</h2>
              
              <div className="space-y-3">
                {receivedRequests.map((request) => (
                  <div key={request.id} className="border border-base-300 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="font-medium">
                            {request.from_user.first_name} {request.from_user.last_name}
                          </h3>
                          <span className="badge badge-outline badge-xs">
                            {request.request_method === 'code' ? '🔗 Code' : '📧 Email'}
                          </span>
                        </div>
                        <p className="text-sm text-base-content/60">{request.from_user.email}</p>
                        <p className="text-sm">Wants to connect as: <span className="font-medium">{request.relationship_type}</span></p>
                        {request.message && (
                          <p className="text-sm text-base-content/80 mt-2">"{request.message}"</p>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => respondToRequest(request.id, 'accept')}
                          className="btn btn-success btn-sm"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => respondToRequest(request.id, 'decline')}
                          className="btn btn-error btn-sm"
                        >
                          Decline
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Active Relationships */}
        <div className="card bg-base-100">
          <div className="card-body">
            <h2 className="card-title">👥 Your Connections</h2>
            
            {relationships.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🤝</div>
                <h3 className="font-medium mb-2">No connections yet</h3>
                <p className="text-sm text-base-content/60 mb-4">
                  Start building meaningful connections with family and friends
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {relationships.map((relationship) => {
                  const otherUser = relationship.user1.id === relationship.user2.id ? 
                    relationship.user2 : relationship.user1;
                  
                  return (
                    <div key={relationship.id} className="border border-base-300 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="font-medium">
                              {otherUser.first_name} {otherUser.last_name}
                            </h3>
                            <span className="badge badge-outline badge-sm">
                              {relationship.relationship_type}
                            </span>
                          </div>
                          <p className="text-sm text-base-content/60">{otherUser.email}</p>
                          
                          <div className="flex items-center space-x-2 mt-2">
                            <span className="text-sm">Health Score:</span>
                            <span className={`font-medium ${getHealthColor(relationship.health_score)}`}>
                              {getHealthEmoji(relationship.health_score)} {relationship.health_score}/10
                            </span>
                          </div>
                          
                          {relationship.last_analysis_date && (
                            <p className="text-xs text-base-content/50 mt-1">
                              Last analyzed: {new Date(relationship.last_analysis_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                        
                        <div className="flex flex-col gap-2">
                          <button
                            onClick={() => analyzeRelationship(relationship.id)}
                            className="btn btn-outline btn-sm"
                          >
                            🔍 Analyze
                          </button>
                          <button
                            className="btn btn-ghost btn-sm"
                            disabled
                          >
                            📊 Insights
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Feature Notice */}
        <div className="card bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/20">
          <div className="card-body text-center">
            <div className="text-2xl mb-2">🎉</div>
            <h3 className="font-medium mb-2">New: Invitation Code System!</h3>
            <p className="text-sm text-base-content/80 mb-3">
              Connect with anyone easily using shareable 8-character codes. No email required!
              Share codes via text, voice, or in-person for privacy-friendly connections.
            </p>
            <div className="text-xs text-base-content/60">
              Plus: AI relationship analysis and privacy-preserving insights using aggregated patterns.
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

export default RelationshipsPage;
