'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import SettingsLayout from '@/components/SettingsLayout';

interface LLMContextProfile {
  id: string;
  user_id: number;
  date_of_birth: string | null;  // ISO date string
  age: number | null;  // Computed from date_of_birth
  gender: string | null;
  ethnic_background: string | null;
  occupation: string | null;
  relationship_status: string | null;
  living_situation: string | null;
  has_children: boolean | null;
  children_info: string | null;
  health_conditions: string | null;
  mental_health_history: string | null;
  current_challenges: string | null;
  stress_factors: string | null;
  coping_mechanisms: string | null;
  communication_style: string | null;
  learning_style: string | null;
  response_preferences: string | null;
  personal_goals: string | null;
  professional_goals: string | null;
  core_values: string | null;
  interests: string | null;
  typical_schedule: string | null;
  sleep_pattern: string | null;
  support_network: string | null;
  professional_support: string | null;
  lifepal_usage_goals: string | null;
  topics_of_interest: string | null;
  topics_to_avoid: string | null;
}

export default function ContextPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [context, setContext] = useState<LLMContextProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('personal');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadContext();
    }
  }, [user, authLoading, router]);

  const loadContext = async () => {
    try {
      const data = await apiClient.get<LLMContextProfile>('/api/users/llm_context_profile');
      setContext(data);
    } catch (err: any) {
      setError('Failed to load context profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!context) return;
    
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      await apiClient.patch('/api/users/llm_context_profile', context);
      setSuccess('Context saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save context');
    } finally {
      setSaving(false);
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

  if (!context) {
    return (
      <SettingsLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-error mb-4">Failed to load context profile</p>
            <button onClick={loadContext} className="btn btn-primary">
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
        <h1 className="text-3xl font-bold mb-3">AI Context Profile</h1>
        <p className="text-base-content/70 mb-6">
          Help LifePal understand you better. All data is encrypted and used only to personalize your experience.
        </p>

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

        {/* Section Selector - Dropdown on Mobile, Tabs on Desktop */}
        <div className="mb-6">
          {/* Mobile Dropdown */}
          <select
            className="select select-bordered w-full lg:hidden"
            value={activeTab}
            onChange={(e) => setActiveTab(e.target.value)}
          >
            <option value="personal">Personal Info</option>
            <option value="wellbeing">Wellbeing</option>
            <option value="goals">Goals & Values</option>
            <option value="routine">Daily Routine</option>
            <option value="support">Support System</option>
            <option value="preferences">Preferences</option>
          </select>

          {/* Desktop Tabs */}
          <div className="hidden lg:flex tabs tabs-boxed">
            <button
              className={`tab ${activeTab === 'personal' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('personal')}
            >
              Personal Info
            </button>
            <button
              className={`tab ${activeTab === 'wellbeing' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('wellbeing')}
            >
              Wellbeing
            </button>
            <button
              className={`tab ${activeTab === 'goals' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('goals')}
            >
              Goals & Values
            </button>
            <button
              className={`tab ${activeTab === 'routine' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('routine')}
            >
              Daily Routine
            </button>
            <button
              className={`tab ${activeTab === 'support' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('support')}
            >
              Support System
            </button>
            <button
              className={`tab ${activeTab === 'preferences' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('preferences')}
            >
              Preferences
            </button>
          </div>
        </div>

        {/* Context Form */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body space-y-6">
            
            {/* Personal Information Tab */}
            {activeTab === 'personal' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Personal Information</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">Date of Birth</span>
                    </label>
                    <input
                      type="date"
                      className="input input-bordered w-full"
                      value={context.date_of_birth || ''}
                      onChange={(e) => setContext({ ...context, date_of_birth: e.target.value })}
                    />
                    {context.age !== null && (
                      <label className="label">
                        <span className="label-text-alt text-base-content/60">
                          Age: {context.age} years
                        </span>
                      </label>
                    )}
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">Gender</span>
                    </label>
                    <input
                      type="text"
                      placeholder="Your gender"
                      className="input input-bordered w-full"
                      value={context.gender || ''}
                      onChange={(e) => setContext({ ...context, gender: e.target.value })}
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">Ethnic Background</span>
                    </label>
                    <input
                      type="text"
                      placeholder="Optional"
                      className="input input-bordered w-full"
                      value={context.ethnic_background || ''}
                      onChange={(e) => setContext({ ...context, ethnic_background: e.target.value })}
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">Occupation</span>
                    </label>
                    <input
                      type="text"
                      placeholder="Your occupation"
                      className="input input-bordered w-full"
                      value={context.occupation || ''}
                      onChange={(e) => setContext({ ...context, occupation: e.target.value })}
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">Relationship Status</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., Single, Married, In a relationship"
                      className="input input-bordered w-full"
                      value={context.relationship_status || ''}
                      onChange={(e) => setContext({ ...context, relationship_status: e.target.value })}
                    />
                  </div>

                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">Living Situation</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., Lives alone, With family"
                      className="input input-bordered w-full"
                      value={context.living_situation || ''}
                      onChange={(e) => setContext({ ...context, living_situation: e.target.value })}
                    />
                  </div>
                </div>

                <div className="form-control">
                  <label className="label cursor-pointer justify-start gap-4">
                    <input
                      type="checkbox"
                      className="checkbox checkbox-primary"
                      checked={context.has_children || false}
                      onChange={(e) => setContext({ ...context, has_children: e.target.checked })}
                    />
                    <span className="label-text font-semibold">I have children</span>
                  </label>
                </div>

                {context.has_children && (
                  <div className="form-control">
                    <label className="label">
                      <span className="label-text font-semibold">Children Information</span>
                    </label>
                    <textarea
                      placeholder="Brief info about your children (ages, etc.)"
                      className="textarea textarea-bordered h-24 w-full"
                      value={context.children_info || ''}
                      onChange={(e) => setContext({ ...context, children_info: e.target.value })}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Wellbeing Tab */}
            {activeTab === 'wellbeing' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Wellbeing Context</h2>
                <p className="text-base-content/70 text-sm">
                  This information helps LifePal provide more personalized support. All data is encrypted.
                </p>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Health Conditions</span>
                  </label>
                  <textarea
                    placeholder="Any health conditions you wish to share (optional)"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.health_conditions || ''}
                    onChange={(e) => setContext({ ...context, health_conditions: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Mental Health History</span>
                  </label>
                  <textarea
                    placeholder="Optional - helps LifePal provide better support"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.mental_health_history || ''}
                    onChange={(e) => setContext({ ...context, mental_health_history: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Current Challenges</span>
                  </label>
                  <textarea
                    placeholder="What challenges are you currently facing?"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.current_challenges || ''}
                    onChange={(e) => setContext({ ...context, current_challenges: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Stress Factors</span>
                  </label>
                  <textarea
                    placeholder="What causes you stress?"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.stress_factors || ''}
                    onChange={(e) => setContext({ ...context, stress_factors: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Coping Mechanisms</span>
                  </label>
                  <textarea
                    placeholder="What helps you cope with stress?"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.coping_mechanisms || ''}
                    onChange={(e) => setContext({ ...context, coping_mechanisms: e.target.value })}
                  />
                </div>
              </div>
            )}

            {/* Goals & Values Tab */}
            {activeTab === 'goals' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Goals & Values</h2>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Personal Goals</span>
                  </label>
                  <textarea
                    placeholder="What are your personal goals?"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.personal_goals || ''}
                    onChange={(e) => setContext({ ...context, personal_goals: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Professional Goals</span>
                  </label>
                  <textarea
                    placeholder="What are your career/professional goals?"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.professional_goals || ''}
                    onChange={(e) => setContext({ ...context, professional_goals: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Core Values</span>
                  </label>
                  <textarea
                    placeholder="What values are most important to you?"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.core_values || ''}
                    onChange={(e) => setContext({ ...context, core_values: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Interests & Hobbies</span>
                  </label>
                  <textarea
                    placeholder="What are your interests and hobbies?"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.interests || ''}
                    onChange={(e) => setContext({ ...context, interests: e.target.value })}
                  />
                </div>
              </div>
            )}

            {/* Daily Routine Tab */}
            {activeTab === 'routine' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Daily Routine</h2>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Typical Schedule</span>
                  </label>
                  <textarea
                    placeholder="Describe your typical daily schedule"
                    className="textarea textarea-bordered h-32 w-full"
                    value={context.typical_schedule || ''}
                    onChange={(e) => setContext({ ...context, typical_schedule: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Sleep Pattern</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., 11 PM - 7 AM, irregular, etc."
                    className="input input-bordered w-full"
                    value={context.sleep_pattern || ''}
                    onChange={(e) => setContext({ ...context, sleep_pattern: e.target.value })}
                  />
                </div>
              </div>
            )}

            {/* Support System Tab */}
            {activeTab === 'support' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Support System</h2>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Support Network</span>
                  </label>
                  <textarea
                    placeholder="Describe your support network (family, friends, etc.)"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.support_network || ''}
                    onChange={(e) => setContext({ ...context, support_network: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Professional Support</span>
                  </label>
                  <textarea
                    placeholder="Any professional support you receive (therapist, coach, etc.)"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.professional_support || ''}
                    onChange={(e) => setContext({ ...context, professional_support: e.target.value })}
                  />
                </div>
              </div>
            )}

            {/* Preferences Tab */}
            {activeTab === 'preferences' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Communication Preferences</h2>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Communication Style</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={context.communication_style || ''}
                    onChange={(e) => setContext({ ...context, communication_style: e.target.value })}
                  >
                    <option value="">Select...</option>
                    <option value="Direct">Direct</option>
                    <option value="Supportive">Supportive</option>
                    <option value="Analytical">Analytical</option>
                    <option value="Casual">Casual</option>
                    <option value="Formal">Formal</option>
                  </select>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Learning Style</span>
                  </label>
                  <select
                    className="select select-bordered w-full"
                    value={context.learning_style || ''}
                    onChange={(e) => setContext({ ...context, learning_style: e.target.value })}
                  >
                    <option value="">Select...</option>
                    <option value="Visual">Visual</option>
                    <option value="Auditory">Auditory</option>
                    <option value="Reading/Writing">Reading/Writing</option>
                    <option value="Kinesthetic">Kinesthetic</option>
                  </select>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Response Preferences</span>
                  </label>
                  <textarea
                    placeholder="How do you prefer responses? (length, tone, format, etc.)"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.response_preferences || ''}
                    onChange={(e) => setContext({ ...context, response_preferences: e.target.value })}
                  />
                </div>

                <div className="divider"></div>

                <h3 className="text-xl font-bold">LifePal Usage</h3>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">What do you hope to achieve with LifePal?</span>
                  </label>
                  <textarea
                    placeholder="Your goals for using LifePal"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.lifepal_usage_goals || ''}
                    onChange={(e) => setContext({ ...context, lifepal_usage_goals: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Topics of Interest</span>
                  </label>
                  <textarea
                    placeholder="Topics you'd like to discuss with LifePal"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.topics_of_interest || ''}
                    onChange={(e) => setContext({ ...context, topics_of_interest: e.target.value })}
                  />
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text font-semibold">Topics to Avoid</span>
                  </label>
                  <textarea
                    placeholder="Topics you'd prefer not to discuss"
                    className="textarea textarea-bordered h-24 w-full"
                    value={context.topics_to_avoid || ''}
                    onChange={(e) => setContext({ ...context, topics_to_avoid: e.target.value })}
                  />
                </div>
              </div>
            )}

            {/* Save Button */}
            <div className="card-actions justify-end mt-6">
              <button
                onClick={handleSave}
                className={`btn btn-primary ${saving ? 'loading' : ''}`}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Context'}
              </button>
            </div>
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="alert alert-info mt-6">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <h3 className="font-bold">Your Privacy Matters</h3>
            <div className="text-xs">All sensitive information is encrypted and stored securely. This data is only used to personalize your LifePal experience.</div>
          </div>
        </div>
      </div>
    </SettingsLayout>
  );
}
