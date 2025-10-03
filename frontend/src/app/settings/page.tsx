'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import SettingsLayout from '@/components/SettingsLayout';
import PushNotificationManager from '@/components/PushNotificationManager';

interface UserSettings {
  id: string;
  timezone: string;
  theme: string;
  email_notifications: boolean;
  push_notifications: boolean;
  allow_relationship_requests: boolean;
  data_sharing_consent: boolean;
  last_active: string | null;
  login_count: number;
}

export default function SettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [vapidPublicKey, setVapidPublicKey] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadSettings();
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    // Get environment variables
    setVapidPublicKey(process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || '');
  }, []);

  const loadSettings = async () => {
    try {
      const data = await apiClient.get<UserSettings>('/api/users/settings');
      setSettings(data);
    } catch (err: any) {
      setError('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      await apiClient.patch('/api/users/settings', {
        timezone: settings.timezone,
        theme: settings.theme,
        email_notifications: settings.email_notifications,
        push_notifications: settings.push_notifications,
        allow_relationship_requests: settings.allow_relationship_requests,
        data_sharing_consent: settings.data_sharing_consent,
      });
      setSuccess('Settings saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
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

  if (!settings) {
    return (
      <SettingsLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-error mb-4">Failed to load settings</p>
            <button onClick={loadSettings} className="btn btn-primary">
              Retry
            </button>
          </div>
        </div>
      </SettingsLayout>
    );
  }

  return (
    <SettingsLayout>
      <div className="max-w-3xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">Settings</h1>

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
            {/* Appearance */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Appearance</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Theme</span>
                </label>
                <select
                  className="select select-bordered w-full"
                  value={settings.theme}
                  onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System Default</option>
                </select>
              </div>
            </div>

            <div className="divider"></div>

            {/* Regional */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Regional</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Timezone</span>
                </label>
                <select
                  className="select select-bordered w-full"
                  value={settings.timezone}
                  onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                >
                  <option value="Europe/London">Europe/London (GMT)</option>
                  <option value="America/New_York">America/New York (EST)</option>
                  <option value="America/Los_Angeles">America/Los Angeles (PST)</option>
                  <option value="America/Chicago">America/Chicago (CST)</option>
                  <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                  <option value="Australia/Sydney">Australia/Sydney (AEST)</option>
                </select>
              </div>
            </div>

            <div className="divider"></div>

            {/* Notifications */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Notifications</h2>
              
              <div className="form-control mb-6">
                <label className="label cursor-pointer">
                  <span className="label-text font-semibold">Email Notifications</span>
                  <input
                    type="checkbox"
                    className="toggle toggle-primary"
                    checked={settings.email_notifications}
                    onChange={(e) => setSettings({ ...settings, email_notifications: e.target.checked })}
                  />
                </label>
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    Receive important updates via email
                  </span>
                </label>
              </div>

              {/* Push Notifications Section */}
              <div className="mt-4">
                <h3 className="text-lg font-semibold mb-3">Push Notifications</h3>
                {!vapidPublicKey ? (
                  <div className="alert alert-warning">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="stroke-current shrink-0 h-6 w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                    <span>VAPID public key is not configured. Push notifications will not work.</span>
                  </div>
                ) : (
                  <PushNotificationManager vapidPublicKey={vapidPublicKey} />
                )}
              </div>
            </div>

            <div className="divider"></div>

            {/* Privacy */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Privacy</h2>
              
              <div className="form-control">
                <label className="label cursor-pointer">
                  <span className="label-text font-semibold">Allow Relationship Requests</span>
                  <input
                    type="checkbox"
                    className="toggle toggle-primary"
                    checked={settings.allow_relationship_requests}
                    onChange={(e) => setSettings({ ...settings, allow_relationship_requests: e.target.checked })}
                  />
                </label>
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    Allow other users to send you relationship requests
                  </span>
                </label>
              </div>

              <div className="form-control">
                <label className="label cursor-pointer">
                  <span className="label-text font-semibold">Data Sharing Consent</span>
                  <input
                    type="checkbox"
                    className="toggle toggle-primary"
                    checked={settings.data_sharing_consent}
                    onChange={(e) => setSettings({ ...settings, data_sharing_consent: e.target.checked })}
                  />
                </label>
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    Share anonymized data to improve LifePal
                  </span>
                </label>
              </div>
            </div>

            <div className="divider"></div>

            {/* Account Info */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Account Information</h2>
              <div className="stats stats-vertical lg:stats-horizontal shadow w-full">
                <div className="stat">
                  <div className="stat-title">Login Count</div>
                  <div className="stat-value text-primary">{settings.login_count}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Last Active</div>
                  <div className="stat-value text-sm">
                    {settings.last_active 
                      ? new Date(settings.last_active).toLocaleDateString()
                      : 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="card-actions justify-end mt-6">
              <button
                onClick={handleSave}
                className={`btn btn-primary ${saving ? 'loading' : ''}`}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </SettingsLayout>
  );
}
