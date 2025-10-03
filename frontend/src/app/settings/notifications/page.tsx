'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import SettingsLayout from '@/components/SettingsLayout';
import PushNotificationManager from '@/components/PushNotificationManager';

export default function NotificationsSettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [vapidPublicKey, setVapidPublicKey] = useState('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    // Get environment variables
    setVapidPublicKey(process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || '');
  }, []);

  if (authLoading) {
    return (
      <SettingsLayout>
        <div className="flex items-center justify-center h-full">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      </SettingsLayout>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <SettingsLayout>
      <div className="max-w-3xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-2">Push Notifications</h1>
        <p className="text-base-content/60 mb-6">
          Manage your push notification preferences and test notifications.
        </p>

        {!vapidPublicKey && (
          <div className="alert alert-warning mb-6">
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
        )}

        <PushNotificationManager vapidPublicKey={vapidPublicKey} />

        <div className="mt-8 card bg-base-200">
          <div className="card-body">
            <h3 className="card-title">About Push Notifications</h3>
            <div className="space-y-2 text-sm">
              <p>
                <strong>What are push notifications?</strong><br />
                Push notifications allow LifePal to send you timely updates even when you're not actively using the app.
              </p>
              <p>
                <strong>What will I be notified about?</strong><br />
                You'll receive notifications for important events like task reminders, chat messages, and system updates.
              </p>
              <p>
                <strong>Can I control what I receive?</strong><br />
                Yes! You can enable or disable push notifications at any time from this page.
              </p>
              <p>
                <strong>Privacy:</strong><br />
                Your notification preferences are stored securely and you can revoke permission at any time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </SettingsLayout>
  );
}
