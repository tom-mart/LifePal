import React, { useState, useEffect } from 'react';
import { apiService } from '../shared/services/api.js';

const InvitationCodeManager = ({ onCodeUsed }) => {
  const [activeTab, setActiveTab] = useState('use'); // 'use' or 'create' or 'manage'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Use code state
  const [codeToUse, setCodeToUse] = useState('');

  // Create code state
  const [newCode, setNewCode] = useState({
    relationship_type: 'friend',
    message: '',
    expires_in_days: 7,
    max_uses: 1
  });

  // Manage codes state
  const [myCodes, setMyCodes] = useState([]);

  useEffect(() => {
    if (activeTab === 'manage') {
      loadMyCodes();
    }
  }, [activeTab]);

  const loadMyCodes = async () => {
    try {
      setLoading(true);
      const response = await apiService.relationships.getInvitationCodes();
      if (response.data.results) {
        setMyCodes(response.data.results);
      }
    } catch (err) {
      console.error('Error loading invitation codes:', err);
      setError('Failed to load your invitation codes');
    } finally {
      setLoading(false);
    }
  };

  const useInvitationCode = async () => {
    if (!codeToUse.trim()) {
      setError('Please enter an invitation code');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.relationships.useInvitationCode({
        invitation_code: codeToUse.trim().toUpperCase()
      });

      if (response.data.success) {
        setSuccess(response.data.message);
        setCodeToUse('');
        if (onCodeUsed) onCodeUsed();
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      console.error('Error using invitation code:', err);
      setError('Failed to use invitation code');
    } finally {
      setLoading(false);
    }
  };

  const createInvitationCode = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.relationships.createInvitationCode(newCode);
      
      if (response.data.code) {
        setSuccess(`Invitation code created: ${response.data.code}`);
        setNewCode({
          relationship_type: 'friend',
          message: '',
          expires_in_days: 7,
          max_uses: 1
        });
        // Refresh codes if on manage tab
        if (activeTab === 'manage') {
          loadMyCodes();
        }
      } else {
        setError('Failed to create invitation code');
      }
    } catch (err) {
      console.error('Error creating invitation code:', err);
      setError('Failed to create invitation code');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (code) => {
    navigator.clipboard.writeText(code).then(() => {
      setSuccess(`Code ${code} copied to clipboard!`);
    }).catch(() => {
      setError('Failed to copy code to clipboard');
    });
  };

  const formatExpiryDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const isCodeExpired = (expiryDate) => {
    return new Date(expiryDate) < new Date();
  };

  return (
    <div className="card bg-base-100">
      <div className="card-body">
        <h2 className="card-title">🔗 Invitation Codes</h2>
        
        {/* Tabs */}
        <div className="tabs tabs-boxed mb-4">
          <button 
            className={`tab ${activeTab === 'use' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('use')}
          >
            Use Code
          </button>
          <button 
            className={`tab ${activeTab === 'create' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('create')}
          >
            Create Code
          </button>
          <button 
            className={`tab ${activeTab === 'manage' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('manage')}
          >
            My Codes
          </button>
        </div>

        {/* Use Code Tab */}
        {activeTab === 'use' && (
          <div className="space-y-4">
            <div className="alert alert-info">
              <span>📱 Got an invitation code? Enter it here to connect with someone!</span>
            </div>
            
            <div className="form-control">
              <label className="label">
                <span className="label-text">Invitation Code</span>
              </label>
              <div className="join">
                <input
                  type="text"
                  placeholder="ABC3XY7Z"
                  className="input input-bordered join-item flex-1"
                  value={codeToUse}
                  onChange={(e) => setCodeToUse(e.target.value.toUpperCase())}
                  maxLength={8}
                />
                <button
                  onClick={useInvitationCode}
                  className="btn btn-primary join-item"
                  disabled={loading || !codeToUse.trim()}
                >
                  {loading ? <span className="loading loading-spinner loading-sm"></span> : 'Use Code'}
                </button>
              </div>
              <div className="label">
                <span className="label-text-alt">Enter the 8-character code someone shared with you</span>
              </div>
            </div>
          </div>
        )}

        {/* Create Code Tab */}
        {activeTab === 'create' && (
          <div className="space-y-4">
            <div className="alert alert-info">
              <span>🎯 Create a code to share with someone you want to connect with!</span>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text">Relationship Type</span>
              </label>
              <select
                className="select select-bordered"
                value={newCode.relationship_type}
                onChange={(e) => setNewCode({...newCode, relationship_type: e.target.value})}
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
                value={newCode.message}
                onChange={(e) => setNewCode({...newCode, message: e.target.value})}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Expires in (days)</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="30"
                  className="input input-bordered"
                  value={newCode.expires_in_days}
                  onChange={(e) => setNewCode({...newCode, expires_in_days: parseInt(e.target.value) || 7})}
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Max Uses</span>
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  className="input input-bordered"
                  value={newCode.max_uses}
                  onChange={(e) => setNewCode({...newCode, max_uses: parseInt(e.target.value) || 1})}
                />
              </div>
            </div>

            <button
              onClick={createInvitationCode}
              className="btn btn-primary w-full"
              disabled={loading}
            >
              {loading ? <span className="loading loading-spinner loading-sm"></span> : 'Create Invitation Code'}
            </button>
          </div>
        )}

        {/* Manage Codes Tab */}
        {activeTab === 'manage' && (
          <div className="space-y-4">
            <div className="alert alert-info">
              <span>📋 Manage your created invitation codes</span>
            </div>

            {loading && (
              <div className="flex justify-center">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            )}

            {myCodes.length === 0 && !loading ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📝</div>
                <h3 className="font-medium mb-2">No invitation codes yet</h3>
                <p className="text-sm text-base-content/60">
                  Create your first invitation code to share with others
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {myCodes.map((code) => (
                  <div key={code.id} className="border border-base-300 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="font-mono text-lg font-bold text-primary">
                            {code.code}
                          </span>
                          <span className="badge badge-outline badge-sm">
                            {code.relationship_type}
                          </span>
                          {isCodeExpired(code.expires_at) && (
                            <span className="badge badge-error badge-sm">Expired</span>
                          )}
                          {!code.is_active && (
                            <span className="badge badge-neutral badge-sm">Used Up</span>
                          )}
                        </div>
                        
                        <div className="text-sm text-base-content/60 space-y-1">
                          <p>Uses: {code.current_uses}/{code.max_uses}</p>
                          <p>Expires: {formatExpiryDate(code.expires_at)}</p>
                          {code.message && (
                            <p>Message: "{code.message}"</p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <button
                          onClick={() => copyToClipboard(code.code)}
                          className="btn btn-ghost btn-sm"
                          disabled={isCodeExpired(code.expires_at) || !code.is_active}
                        >
                          📋 Copy
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Success/Error Messages */}
        {success && (
          <div className="alert alert-success">
            <span>{success}</span>
            <button 
              onClick={() => setSuccess(null)}
              className="btn btn-ghost btn-sm"
            >
              ✕
            </button>
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            <span>{error}</span>
            <button 
              onClick={() => setError(null)}
              className="btn btn-ghost btn-sm"
            >
              ✕
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default InvitationCodeManager;
