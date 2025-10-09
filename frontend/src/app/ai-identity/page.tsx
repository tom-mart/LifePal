'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import SettingsLayout from '@/components/SettingsLayout';

interface AIIdentityProfile {
  id: string;
  user_id: number;
  preferred_model: string;
  ai_name: string;
  ai_role: string;
  ai_personality_traits: string;
  core_instructions: string;
  communication_style: string;
  response_length_preference: string;
  topics_to_emphasize: string;
  topics_to_avoid: string;
  custom_instructions: string;
  use_emojis: boolean;
  formality_level: string;
  question_frequency: string;
  remember_preferences: boolean;
  proactive_suggestions: boolean;
  created_at: string;
  updated_at: string;
}

interface ModelInfo {
  name: string;
  supports_tools: boolean;
  tool_quality: string;
}

interface ConnectionStatus {
  connected: boolean;
  checking: boolean;
  models: string[];
  models_info: ModelInfo[];
}

export default function AIIdentityPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<AIIdentityProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    connected: false,
    checking: true,
    models: [],
    models_info: []
  });
  const [showOnlyToolCapable, setShowOnlyToolCapable] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadProfile();
      checkConnection();
    }
  }, [user, authLoading, router]);

  const checkConnection = async () => {
    setConnectionStatus(prev => ({ ...prev, checking: true }));
    try {
      const data = await apiClient.get<{ models: string[]; models_info?: ModelInfo[] }>('/api/users/ai-identity/available-models');
      setConnectionStatus({
        connected: data.models.length > 0,
        checking: false,
        models: data.models,
        models_info: data.models_info || []
      });
    } catch (err) {
      setConnectionStatus({
        connected: false,
        checking: false,
        models: [],
        models_info: []
      });
    }
  };

  const loadProfile = async () => {
    try {
      const data = await apiClient.get<AIIdentityProfile>('/api/users/ai-identity');
      setProfile(data);
    } catch (err: any) {
      setError('Failed to load AI identity profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!profile) return;
    
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const updateData = {
        preferred_model: profile.preferred_model,
        ai_name: profile.ai_name,
        ai_role: profile.ai_role,
        ai_personality_traits: profile.ai_personality_traits,
        core_instructions: profile.core_instructions,
        communication_style: profile.communication_style,
        response_length_preference: profile.response_length_preference,
        topics_to_emphasize: profile.topics_to_emphasize,
        topics_to_avoid: profile.topics_to_avoid,
        custom_instructions: profile.custom_instructions,
        use_emojis: profile.use_emojis,
        formality_level: profile.formality_level,
        question_frequency: profile.question_frequency,
        remember_preferences: profile.remember_preferences,
        proactive_suggestions: profile.proactive_suggestions,
      };
      
      await apiClient.patch('/api/users/ai-identity', updateData);
      setSuccess('AI Identity saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save AI identity');
    } finally {
      setSaving(false);
    }
  };

  const handlePreview = async () => {
    try {
      const data = await apiClient.get<{ system_prompt: string }>('/api/users/ai-identity/preview-prompt');
      setSystemPrompt(data.system_prompt);
      setShowPreview(true);
    } catch (err: any) {
      setError('Failed to generate preview');
    }
  };

  if (authLoading || loading) {
    return (
      <SettingsLayout>
        <div className="flex items-center justify-center h-full">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      </SettingsLayout>
    );
  }

  if (!profile) {
    return (
      <SettingsLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-error mb-4">Failed to load AI identity profile</p>
            <button onClick={loadProfile} className="btn btn-primary">
              Retry
            </button>
          </div>
        </div>
      </SettingsLayout>
    );
  }

  return (
    <SettingsLayout>
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">AI Identity & Behavior</h1>
          
          {/* Connection Status Indicator */}
          <div className="flex items-center gap-2">
            <div className="tooltip" data-tip={connectionStatus.connected ? 'Connected to AI service' : 'AI service unavailable'}>
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-base-200">
                {connectionStatus.checking ? (
                  <span className="loading loading-spinner loading-xs"></span>
                ) : (
                  <div className={`w-3 h-3 rounded-full ${connectionStatus.connected ? 'bg-success animate-pulse' : 'bg-error'}`}></div>
                )}
                <span className="text-sm font-medium">
                  {connectionStatus.checking ? 'Checking...' : connectionStatus.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            <button onClick={checkConnection} className="btn btn-ghost btn-sm btn-circle">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="alert alert-error mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="alert alert-success mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{success}</span>
          </div>
        )}

        {/* Settings Form */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body space-y-6">
            
            {/* Model Selection */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Model Selection</h2>
              
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text font-semibold">Preferred AI Model</span>
                  <span className={`badge ${connectionStatus.connected ? 'badge-success' : 'badge-warning'}`}>
                    {connectionStatus.models.length} models available
                  </span>
                </label>
                <select
                  className="select select-bordered w-full"
                  value={profile.preferred_model}
                  onChange={(e) => setProfile({ ...profile, preferred_model: e.target.value })}
                  disabled={!connectionStatus.connected}
                >
                  {connectionStatus.models.length > 0 ? (
                    connectionStatus.models_info
                      .filter(m => !showOnlyToolCapable || m.supports_tools)
                      .map(modelInfo => (
                        <option key={modelInfo.name} value={modelInfo.name}>
                          {modelInfo.name}
                          {modelInfo.supports_tools && ` ✓ Tools`}
                          {modelInfo.tool_quality === 'excellent' && ' ⭐'}
                        </option>
                      ))
                  ) : (
                    <option value={profile.preferred_model}>{profile.preferred_model} (offline)</option>
                  )}
                </select>
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    Choose which AI model powers your assistant
                  </span>
                </label>
              </div>

              {connectionStatus.models_info.length > 0 && (
                <div className="form-control mb-4">
                  <label className="label cursor-pointer">
                    <span className="label-text">Show only models with tool support</span>
                    <input
                      type="checkbox"
                      className="toggle toggle-primary"
                      checked={showOnlyToolCapable}
                      onChange={(e) => setShowOnlyToolCapable(e.target.checked)}
                    />
                  </label>
                  <label className="label">
                    <span className="label-text-alt text-base-content/60">
                      Tool-capable models can use features like file management, reminders, and web searches
                    </span>
                  </label>
                </div>
              )}

              {profile.preferred_model && connectionStatus.models_info.length > 0 && (
                <div className="alert alert-info">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <div>
                    {(() => {
                      const currentModel = connectionStatus.models_info.find(m => m.name === profile.preferred_model);
                      if (!currentModel) return <span>Model information unavailable</span>;
                      if (currentModel.tool_quality === 'excellent') {
                        return <span><strong>Excellent choice!</strong> This model has excellent tool calling capabilities.</span>;
                      } else if (currentModel.supports_tools) {
                        return <span><strong>Good choice!</strong> This model supports tool calling.</span>;
                      } else {
                        return <span><strong>Limited tools:</strong> This model has weak tool support. Consider qwen2.5 for better functionality.</span>;
                      }
                    })()}
                  </div>
                </div>
              )}
            </div>

            <div className="divider"></div>

            {/* AI Identity */}
            <div>
              <h2 className="text-2xl font-bold mb-4">AI Identity</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">AI Name</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  value={profile.ai_name}
                  onChange={(e) => setProfile({ ...profile, ai_name: e.target.value })}
                  placeholder="e.g., LifePal, Frankie"
                />
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    What should your AI assistant call itself?
                  </span>
                </label>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">AI Role</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  value={profile.ai_role}
                  onChange={(e) => setProfile({ ...profile, ai_role: e.target.value })}
                  placeholder="e.g., supportive life assistant and wellbeing companion"
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Personality Traits</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  value={profile.ai_personality_traits}
                  onChange={(e) => setProfile({ ...profile, ai_personality_traits: e.target.value })}
                  placeholder="e.g., empathetic, supportive, warm, encouraging"
                />
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    Comma-separated personality traits
                  </span>
                </label>
              </div>
            </div>

            <div className="divider"></div>

            {/* Core Instructions */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Core Instructions</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Core Behavioral Instructions</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-32"
                  value={profile.core_instructions}
                  onChange={(e) => setProfile({ ...profile, core_instructions: e.target.value })}
                  placeholder="Define how your AI should behave and what it should focus on..."
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Communication Style</span>
                </label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  value={profile.communication_style}
                  onChange={(e) => setProfile({ ...profile, communication_style: e.target.value })}
                  placeholder="e.g., conversational, warm, and empathetic"
                />
              </div>
            </div>

            <div className="divider"></div>

            {/* Response Preferences */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Response Preferences</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Response Length</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={profile.response_length_preference}
                    onChange={(e) => setProfile({ ...profile, response_length_preference: e.target.value })}
                  >
                    <option value="concise">Concise (1-2 sentences)</option>
                    <option value="moderate">Moderate (2-4 sentences)</option>
                    <option value="detailed">Detailed (4+ sentences)</option>
                  </select>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Formality Level</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={profile.formality_level}
                    onChange={(e) => setProfile({ ...profile, formality_level: e.target.value })}
                  >
                    <option value="casual">Casual (friendly, informal)</option>
                    <option value="balanced">Balanced (professional yet warm)</option>
                    <option value="formal">Formal (professional, structured)</option>
                  </select>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Question Frequency</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={profile.question_frequency}
                    onChange={(e) => setProfile({ ...profile, question_frequency: e.target.value })}
                  >
                    <option value="low">Low (mostly listen)</option>
                    <option value="moderate">Moderate (balanced)</option>
                    <option value="high">High (ask many questions)</option>
                  </select>
                </div>

                <div className="form-control">
                  <label className="label cursor-pointer">
                    <span className="label-text font-semibold">Use Emojis</span>
                    <input
                      type="checkbox"
                      className="toggle toggle-primary"
                      checked={profile.use_emojis}
                      onChange={(e) => setProfile({ ...profile, use_emojis: e.target.checked })}
                    />
                  </label>
                </div>
              </div>
            </div>

            <div className="divider"></div>

            {/* Topics */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Topic Preferences</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Topics to Emphasize</span>
                </label>
                <textarea
                  className="textarea textarea-bordered"
                  value={profile.topics_to_emphasize}
                  onChange={(e) => setProfile({ ...profile, topics_to_emphasize: e.target.value })}
                  placeholder="e.g., gratitude, mindfulness, relationships, personal growth"
                />
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Topics to Avoid</span>
                </label>
                <textarea
                  className="textarea textarea-bordered"
                  value={profile.topics_to_avoid}
                  onChange={(e) => setProfile({ ...profile, topics_to_avoid: e.target.value })}
                  placeholder="Topics the AI should handle carefully or avoid"
                />
              </div>
            </div>

            <div className="divider"></div>

            {/* Behavior Settings */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Behavior Settings</h2>
              
              <div className="form-control">
                <label className="label cursor-pointer">
                  <span className="label-text font-semibold">Remember Preferences</span>
                  <input
                    type="checkbox"
                    className="toggle toggle-primary"
                    checked={profile.remember_preferences}
                    onChange={(e) => setProfile({ ...profile, remember_preferences: e.target.checked })}
                  />
                </label>
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    Reference past conversations and preferences
                  </span>
                </label>
              </div>

              <div className="form-control">
                <label className="label cursor-pointer">
                  <span className="label-text font-semibold">Proactive Suggestions</span>
                  <input
                    type="checkbox"
                    className="toggle toggle-primary"
                    checked={profile.proactive_suggestions}
                    onChange={(e) => setProfile({ ...profile, proactive_suggestions: e.target.checked })}
                  />
                </label>
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    Allow AI to make proactive suggestions
                  </span>
                </label>
              </div>
            </div>

            <div className="divider"></div>

            {/* Custom Instructions */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Custom Instructions</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Additional Custom Instructions</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-32"
                  value={profile.custom_instructions}
                  onChange={(e) => setProfile({ ...profile, custom_instructions: e.target.value })}
                  placeholder="Any additional instructions or preferences for your AI..."
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="card-actions justify-between mt-6">
              <button
                onClick={handlePreview}
                className="btn btn-outline"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                Preview System Prompt
              </button>
              <button
                onClick={handleSave}
                className={`btn btn-primary ${saving ? 'loading' : ''}`}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save AI Identity'}
              </button>
            </div>
          </div>
        </div>

        {/* Preview Modal */}
        {showPreview && (
          <div className="modal modal-open">
            <div className="modal-box max-w-3xl">
              <h3 className="font-bold text-lg mb-4">Generated System Prompt Preview</h3>
              <div className="bg-base-200 p-4 rounded-lg max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm">{systemPrompt}</pre>
              </div>
              <div className="modal-action">
                <button onClick={() => setShowPreview(false)} className="btn">Close</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </SettingsLayout>
  );
}
