'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import SettingsLayout from '@/components/SettingsLayout';

interface UserProfile {
  id: string;
  preferred_name: string | null;
  bio: string | null;
}

export default function ProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadProfile();
    }
  }, [user, authLoading, router]);

  const loadProfile = async () => {
    try {
      const data = await apiClient.get<UserProfile>('/api/users/profile');
      setProfile(data);
    } catch (err: any) {
      setError('Failed to load profile');
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
      await apiClient.patch('/api/users/profile', {
        preferred_name: profile.preferred_name,
        bio: profile.bio,
      });
      setSuccess('Profile saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save profile');
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

  if (!profile) {
    return (
      <SettingsLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-error mb-4">Failed to load profile</p>
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
      <div className="max-w-3xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">Profile</h1>

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

        {/* Profile Form */}
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-4">Basic Information</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Preferred Name</span>
                </label>
                <input
                  type="text"
                  placeholder="How would you like to be called?"
                  className="input input-bordered w-full"
                  value={profile.preferred_name || ''}
                  onChange={(e) => setProfile({ ...profile, preferred_name: e.target.value })}
                />
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    This is how LifePal will address you
                  </span>
                </label>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text font-semibold">Bio</span>
                </label>
                <textarea
                  placeholder="Tell us a bit about yourself..."
                  className="textarea textarea-bordered h-32 w-full"
                  value={profile.bio || ''}
                  onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                />
                <label className="label">
                  <span className="label-text-alt text-base-content/60">
                    A brief description about yourself
                  </span>
                </label>
              </div>
            </div>

            {/* Save Button */}
            <div className="card-actions justify-end mt-6">
              <button
                onClick={handleSave}
                className={`btn btn-primary ${saving ? 'loading' : ''}`}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Profile'}
              </button>
            </div>
          </div>
        </div>

        {/* Additional Info Card */}
        <div className="card bg-base-100 shadow-xl mt-6">
          <div className="card-body">
            <h2 className="text-2xl font-bold mb-4">Need More Personalization?</h2>
            <p className="text-base-content/70 mb-4">
              To help LifePal provide better assistance, you can add more detailed information about yourself in the AI Context section.
            </p>
            <Link href="/context" className="btn btn-outline btn-primary">
              Go to AI Context →
            </Link>
          </div>
        </div>
      </div>
    </SettingsLayout>
  );
}
