import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../core/auth/AuthContext.jsx';
import { apiService } from '../../../shared/services/api.js';

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, logout, updateUser } = useAuth();
  
  // Form state
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    timezone: 'UTC',
    allow_relationship_requests: true,
    data_sharing_consent: false,
  });
  
  // UI state
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState('');

  // Timezone options
  const timezoneOptions = [
    { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
    { value: 'America/New_York', label: 'Eastern Time (US & Canada)' },
    { value: 'America/Chicago', label: 'Central Time (US & Canada)' },
    { value: 'America/Denver', label: 'Mountain Time (US & Canada)' },
    { value: 'America/Los_Angeles', label: 'Pacific Time (US & Canada)' },
    { value: 'Europe/London', label: 'London (GMT/BST)' },
    { value: 'Europe/Paris', label: 'Paris (CET/CEST)' },
    { value: 'Europe/Berlin', label: 'Berlin (CET/CEST)' },
    { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
    { value: 'Asia/Shanghai', label: 'Shanghai (CST)' },
    { value: 'Australia/Sydney', label: 'Sydney (AEST/AEDT)' },
  ];

  // Initialize form data when user loads
  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        date_of_birth: user.date_of_birth || '',
        timezone: user.timezone || 'UTC',
        allow_relationship_requests: user.allow_relationship_requests ?? true,
        data_sharing_consent: user.data_sharing_consent ?? false,
      });
    }
  }, [user]);

  const handleInputChange = (field, value) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
    setSaveError('');
    setSaveSuccess(false);
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      setSaveError('');
      
      // Prepare data for API
      const updateData = { ...profileData };
      
      // Convert empty date to null
      if (!updateData.date_of_birth) {
        updateData.date_of_birth = null;
      }

      const response = await apiService.auth.updateProfile(updateData);
      
      // Update the user context
      if (updateUser) {
        updateUser(response.data);
      }
      
      setSaveSuccess(true);
      setIsEditing(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSaveSuccess(false), 3000);
      
    } catch (error) {
      console.error('Failed to update profile:', error);
      setSaveError(error.response?.data?.error || 'Failed to update profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    // Reset form to original user data
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        date_of_birth: user.date_of_birth || '',
        timezone: user.timezone || 'UTC',
        allow_relationship_requests: user.allow_relationship_requests ?? true,
        data_sharing_consent: user.data_sharing_consent ?? false,
      });
    }
    setIsEditing(false);
    setSaveError('');
    setSaveSuccess(false);
  };

  if (!user) {
    return (
      <div className="p-4">
        <div className="bg-base-100 rounded-xl p-6 border border-base-300">
          <p className="text-center text-base-content/60">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Breadcrumb */}
        <div className="breadcrumbs text-sm">
          <ul>
            <li><a onClick={() => navigate('/dashboard')} className="cursor-pointer">Dashboard</a></li>
            <li>Profile</li>
          </ul>
        </div>
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-base-content mb-2">My Profile</h1>
          <p className="text-base-content/60">Manage your personal information and privacy settings</p>
        </div>

        {/* Success/Error Messages */}
        {saveSuccess && (
          <div className="alert alert-success">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <span>Profile updated successfully!</span>
          </div>
        )}

        {saveError && (
          <div className="alert alert-error">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>{saveError}</span>
          </div>
        )}

        {/* Profile Information Card */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary-content">
                    {profileData.first_name?.charAt(0) || user.email?.charAt(0) || 'U'}
                  </span>
                </div>
                <div>
                  <h2 className="text-2xl font-bold">
                    {profileData.first_name && profileData.last_name 
                      ? `${profileData.first_name} ${profileData.last_name}`
                      : profileData.first_name || 'LifePal User'
                    }
                  </h2>
                  <p className="text-base-content/60">@{user.username}</p>
                  <p className="text-sm text-base-content/50">{user.email}</p>
                </div>
              </div>
              
              {!isEditing && (
                <button 
                  onClick={() => setIsEditing(true)}
                  className="btn btn-primary btn-outline"
                >
                  ✏️ Edit Profile
                </button>
              )}
            </div>

            {/* Profile Form */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b border-base-300 pb-2">Basic Information</h3>
                
                <div>
                  <label className="label">
                    <span className="label-text font-medium">First Name</span>
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      className="input input-bordered w-full"
                      value={profileData.first_name}
                      onChange={(e) => handleInputChange('first_name', e.target.value)}
                      placeholder="Enter your first name"
                    />
                  ) : (
                    <p className="text-base-content py-2">{profileData.first_name || 'Not set'}</p>
                  )}
                </div>

                <div>
                  <label className="label">
                    <span className="label-text font-medium">Last Name</span>
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      className="input input-bordered w-full"
                      value={profileData.last_name}
                      onChange={(e) => handleInputChange('last_name', e.target.value)}
                      placeholder="Enter your last name"
                    />
                  ) : (
                    <p className="text-base-content py-2">{profileData.last_name || 'Not set'}</p>
                  )}
                </div>

                <div>
                  <label className="label">
                    <span className="label-text font-medium">Date of Birth</span>
                  </label>
                  {isEditing ? (
                    <input
                      type="date"
                      className="input input-bordered w-full"
                      value={profileData.date_of_birth}
                      onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                    />
                  ) : (
                    <p className="text-base-content py-2">
                      {profileData.date_of_birth 
                        ? new Date(profileData.date_of_birth).toLocaleDateString('en-GB', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })
                        : 'Not set'
                      }
                    </p>
                  )}
                </div>

                <div>
                  <label className="label">
                    <span className="label-text font-medium">Timezone</span>
                  </label>
                  {isEditing ? (
                    <select
                      className="select select-bordered w-full"
                      value={profileData.timezone}
                      onChange={(e) => handleInputChange('timezone', e.target.value)}
                    >
                      {timezoneOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <p className="text-base-content py-2">
                      {timezoneOptions.find(tz => tz.value === profileData.timezone)?.label || profileData.timezone}
                    </p>
                  )}
                </div>
              </div>

              {/* Privacy & Relationship Settings */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold border-b border-base-300 pb-2">Privacy & Relationships</h3>
                
                <div className="form-control">
                  <label className="label cursor-pointer justify-start gap-3">
                    {isEditing ? (
                      <input 
                        type="checkbox" 
                        className="checkbox checkbox-primary" 
                        checked={profileData.allow_relationship_requests}
                        onChange={(e) => handleInputChange('allow_relationship_requests', e.target.checked)}
                      />
                    ) : (
                      <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                        profileData.allow_relationship_requests 
                          ? 'bg-primary border-primary text-primary-content' 
                          : 'border-base-300'
                      }`}>
                        {profileData.allow_relationship_requests && (
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    )}
                    <div>
                      <span className="label-text font-medium">Allow Relationship Requests</span>
                      <p className="text-sm text-base-content/60">Let others send you relationship connection requests</p>
                    </div>
                  </label>
                </div>

                <div className="form-control">
                  <label className="label cursor-pointer justify-start gap-3">
                    {isEditing ? (
                      <input 
                        type="checkbox" 
                        className="checkbox checkbox-primary" 
                        checked={profileData.data_sharing_consent}
                        onChange={(e) => handleInputChange('data_sharing_consent', e.target.checked)}
                      />
                    ) : (
                      <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                        profileData.data_sharing_consent 
                          ? 'bg-primary border-primary text-primary-content' 
                          : 'border-base-300'
                      }`}>
                        {profileData.data_sharing_consent && (
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    )}
                    <div>
                      <span className="label-text font-medium">Data Sharing for Relationships</span>
                      <p className="text-sm text-base-content/60">Allow sharing anonymized patterns for relationship insights</p>
                    </div>
                  </label>
                </div>

                {/* Account Info */}
                <div className="mt-6 p-4 bg-base-200 rounded-lg">
                  <h4 className="font-medium mb-2">Account Information</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-base-content/70">Member Since:</span>
                      <span>{new Date(user.created_at).toLocaleDateString('en-GB')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-base-content/70">Last Diary Entry:</span>
                      <span>
                        {user.last_diary_entry 
                          ? new Date(user.last_diary_entry).toLocaleDateString('en-GB')
                          : 'No entries yet'
                        }
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            {isEditing ? (
              <div className="card-actions justify-end mt-6 gap-3">
                <button 
                  onClick={handleCancelEdit}
                  className="btn btn-ghost"
                  disabled={isSaving}
                >
                  Cancel
                </button>
                <button 
                  onClick={handleSaveProfile}
                  className={`btn btn-primary ${isSaving ? 'loading' : ''}`}
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            ) : (
              <div className="card-actions justify-end mt-6 gap-3">
                <button 
                  onClick={() => navigate('/dashboard/settings')}
                  className="btn btn-secondary"
                >
                  ⚙️ Settings
                </button>
                <button 
                  onClick={logout}
                  className="btn btn-error btn-outline"
                >
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Privacy Information */}
        <div className="card bg-info/10 border border-info/20">
          <div className="card-body">
            <h3 className="card-title text-info-content">🔒 Your Privacy Matters</h3>
            <p className="text-info-content/80">
              Your diary entries are encrypted and stored securely. Only you can access your personal reflections. 
              When you enable data sharing for relationships, only anonymized patterns are shared - never your actual diary content.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
