'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import SettingsLayout from '@/components/SettingsLayout';

interface CheckInSchedule {
  morning: {
    weekday: {
      time: string;
      enabled: boolean;
    };
    weekend: {
      time: string;
      enabled: boolean;
    };
  };
  evening: {
    weekday: {
      time: string;
      enabled: boolean;
    };
    weekend: {
      time: string;
      enabled: boolean;
    };
  };
}

interface UserSettings {
  id: string;
  timezone: string;
  checkin_schedule?: CheckInSchedule;
}

const DEFAULT_SCHEDULE: CheckInSchedule = {
  morning: {
    weekday: { time: '06:00', enabled: true },
    weekend: { time: '09:00', enabled: true }
  },
  evening: {
    weekday: { time: '21:00', enabled: true },
    weekend: { time: '21:00', enabled: true }
  }
};

export default function CheckInSettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [schedule, setSchedule] = useState<CheckInSchedule>(DEFAULT_SCHEDULE);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadSettings();
    }
  }, [user, authLoading, router]);

  const loadSettings = async () => {
    try {
      const data = await apiClient.get<UserSettings>('/api/users/settings');
      setSettings(data);
      
      // Load schedule or use defaults
      if (data.checkin_schedule && Object.keys(data.checkin_schedule).length > 0) {
        // Merge with defaults to ensure all fields exist
        const mergedSchedule = {
          morning: {
            weekday: {
              time: data.checkin_schedule.morning?.weekday?.time || DEFAULT_SCHEDULE.morning.weekday.time,
              enabled: data.checkin_schedule.morning?.weekday?.enabled ?? DEFAULT_SCHEDULE.morning.weekday.enabled
            },
            weekend: {
              time: data.checkin_schedule.morning?.weekend?.time || DEFAULT_SCHEDULE.morning.weekend.time,
              enabled: data.checkin_schedule.morning?.weekend?.enabled ?? DEFAULT_SCHEDULE.morning.weekend.enabled
            }
          },
          evening: {
            weekday: {
              time: data.checkin_schedule.evening?.weekday?.time || DEFAULT_SCHEDULE.evening.weekday.time,
              enabled: data.checkin_schedule.evening?.weekday?.enabled ?? DEFAULT_SCHEDULE.evening.weekday.enabled
            },
            weekend: {
              time: data.checkin_schedule.evening?.weekend?.time || DEFAULT_SCHEDULE.evening.weekend.time,
              enabled: data.checkin_schedule.evening?.weekend?.enabled ?? DEFAULT_SCHEDULE.evening.weekend.enabled
            }
          }
        };
        setSchedule(mergedSchedule);
      } else {
        // Use defaults if no schedule exists
        setSchedule(DEFAULT_SCHEDULE);
      }
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
        checkin_schedule: schedule
      });
      setSuccess('Check-in schedule saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save schedule');
    } finally {
      setSaving(false);
    }
  };

  const updateSchedule = (
    type: 'morning' | 'evening',
    dayType: 'weekday' | 'weekend',
    field: 'time' | 'enabled',
    value: string | boolean
  ) => {
    setSchedule(prev => ({
      ...prev,
      [type]: {
        ...prev[type],
        [dayType]: {
          ...prev[type][dayType],
          [field]: value
        }
      }
    }));
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

  if (!settings || !schedule) {
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
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Check-in Schedule</h1>
          <p className="text-base-content/70">
            Configure when you'd like to receive your daily check-in reminders
          </p>
        </div>

        {error && (
          <div className="alert alert-error mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="alert alert-success mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{success}</span>
          </div>
        )}

        <div className="space-y-6">
          {/* Morning Check-in */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-2xl mb-4">
                <span className="text-3xl mr-2">☀️</span>
                Morning Catch-Up
              </h2>
              <p className="text-base-content/70 mb-4">
                Start your day with a mindful check-in about how you're feeling and what's ahead
              </p>

              {/* Weekday */}
              <div className="form-control mb-4">
                <label className="label cursor-pointer justify-start gap-4">
                  <input
                    type="checkbox"
                    className="checkbox checkbox-primary"
                    checked={schedule.morning.weekday.enabled}
                    onChange={(e) => updateSchedule('morning', 'weekday', 'enabled', e.target.checked)}
                  />
                  <span className="label-text font-semibold">Weekdays (Mon-Fri)</span>
                </label>
                {schedule.morning.weekday.enabled && (
                  <div className="ml-12 mt-2">
                    <input
                      type="time"
                      className="input input-bordered w-full max-w-xs"
                      value={schedule.morning.weekday.time}
                      onChange={(e) => updateSchedule('morning', 'weekday', 'time', e.target.value)}
                    />
                  </div>
                )}
              </div>

              {/* Weekend */}
              <div className="form-control">
                <label className="label cursor-pointer justify-start gap-4">
                  <input
                    type="checkbox"
                    className="checkbox checkbox-primary"
                    checked={schedule.morning.weekend.enabled}
                    onChange={(e) => updateSchedule('morning', 'weekend', 'enabled', e.target.checked)}
                  />
                  <span className="label-text font-semibold">Weekends (Sat-Sun)</span>
                </label>
                {schedule.morning.weekend.enabled && (
                  <div className="ml-12 mt-2">
                    <input
                      type="time"
                      className="input input-bordered w-full max-w-xs"
                      value={schedule.morning.weekend.time}
                      onChange={(e) => updateSchedule('morning', 'weekend', 'time', e.target.value)}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Evening Reflection */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-2xl mb-4">
                <span className="text-3xl mr-2">🌙</span>
                Evening Reflection
              </h2>
              <p className="text-base-content/70 mb-4">
                End your day by reflecting on what happened and how you're feeling
              </p>

              {/* Weekday */}
              <div className="form-control mb-4">
                <label className="label cursor-pointer justify-start gap-4">
                  <input
                    type="checkbox"
                    className="checkbox checkbox-primary"
                    checked={schedule.evening.weekday.enabled}
                    onChange={(e) => updateSchedule('evening', 'weekday', 'enabled', e.target.checked)}
                  />
                  <span className="label-text font-semibold">Weekdays (Mon-Fri)</span>
                </label>
                {schedule.evening.weekday.enabled && (
                  <div className="ml-12 mt-2">
                    <input
                      type="time"
                      className="input input-bordered w-full max-w-xs"
                      value={schedule.evening.weekday.time}
                      onChange={(e) => updateSchedule('evening', 'weekday', 'time', e.target.value)}
                    />
                  </div>
                )}
              </div>

              {/* Weekend */}
              <div className="form-control">
                <label className="label cursor-pointer justify-start gap-4">
                  <input
                    type="checkbox"
                    className="checkbox checkbox-primary"
                    checked={schedule.evening.weekend.enabled}
                    onChange={(e) => updateSchedule('evening', 'weekend', 'enabled', e.target.checked)}
                  />
                  <span className="label-text font-semibold">Weekends (Sat-Sun)</span>
                </label>
                {schedule.evening.weekend.enabled && (
                  <div className="ml-12 mt-2">
                    <input
                      type="time"
                      className="input input-bordered w-full max-w-xs"
                      value={schedule.evening.weekend.time}
                      onChange={(e) => updateSchedule('evening', 'weekend', 'time', e.target.value)}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Info Card */}
          <div className="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
              <h3 className="font-bold">About Check-ins</h3>
              <div className="text-sm">
                <p>• Check-ins help you stay connected with your wellbeing throughout the day</p>
                <p>• Times are in your local timezone ({settings.timezone})</p>
                <p>• You can snooze notifications if you're busy</p>
                <p>• The AI may create additional midday check-ins based on your morning conversation</p>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end gap-4">
            <button
              onClick={() => setSchedule(settings.checkin_schedule || DEFAULT_SCHEDULE)}
              className="btn btn-ghost"
              disabled={saving}
            >
              Reset
            </button>
            <button
              onClick={handleSave}
              className={`btn btn-primary ${saving ? 'loading' : ''}`}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Schedule'}
            </button>
          </div>
        </div>
      </div>
    </SettingsLayout>
  );
}
