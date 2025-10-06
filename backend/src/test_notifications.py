#!/usr/bin/env python
"""
Quick test script for LifePal push notifications.

Usage:
    python test_notifications.py <username>
    python test_notifications.py <username> --scheduled-only
    python test_notifications.py <username> --immediate-only
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from notifications.models import ScheduledNotification, PushSubscription
from notifications.api import send_push_notification_to_user

User = get_user_model()


def check_user_subscriptions(user):
    """Check if user has active push subscriptions"""
    subs = PushSubscription.objects.filter(user=user, is_active=True)
    count = subs.count()
    
    if count == 0:
        print(f"⚠️  WARNING: User {user.username} has no active push subscriptions!")
        print("   Please subscribe to notifications in the frontend first.")
        return False
    else:
        print(f"✓ User has {count} active subscription(s)")
        return True


def test_immediate_notification(username):
    """Test sending immediate notification"""
    print("\n" + "="*60)
    print("TEST 1: IMMEDIATE NOTIFICATION")
    print("="*60)
    
    user = User.objects.get(username=username)
    
    if not check_user_subscriptions(user):
        return False
    
    print(f"\nSending immediate notification to {user.username}...")
    
    success = send_push_notification_to_user(
        user=user,
        title="🔔 Immediate Test Notification",
        body="This notification was sent immediately from the backend!",
        url="/",
        tag="immediate-test"
    )
    
    if success:
        print("✓ Notification sent successfully!")
        print("  Check your browser - it should appear now!")
        return True
    else:
        print("✗ Failed to send notification")
        print("  Check VAPID keys and backend logs")
        return False


def test_scheduled_notification(username, minutes_from_now=1):
    """Test creating scheduled notification with snooze"""
    print("\n" + "="*60)
    print("TEST 2: SCHEDULED NOTIFICATION WITH SNOOZE")
    print("="*60)
    
    user = User.objects.get(username=username)
    
    if not check_user_subscriptions(user):
        return None
    
    scheduled_time = timezone.now() + timedelta(minutes=minutes_from_now)
    
    print(f"\nCreating scheduled notification for {user.username}...")
    print(f"Scheduled time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"(in {minutes_from_now} minute(s))")
    
    notification = ScheduledNotification.objects.create(
        user=user,
        notification_type='test',
        title='⏰ Scheduled Test Notification',
        body=f'This was scheduled for {minutes_from_now} minute(s) from creation. Try the snooze button!',
        scheduled_time=scheduled_time,
        url='/chat',
        tag='scheduled-test',
        snooze_duration_minutes=1,  # 1 minute for testing
        max_snooze_count=3,
        metadata={'test': True}
    )
    
    print(f"\n✓ Scheduled notification created!")
    print(f"  ID: {notification.id}")
    print(f"  Status: {notification.status}")
    print(f"  Snooze duration: {notification.snooze_duration_minutes} minutes")
    print(f"  Max snoozes: {notification.max_snooze_count}")
    print(f"\n  The notification will appear in {minutes_from_now} minute(s).")
    print(f"  It will have a 'Snooze' button - try clicking it!")
    
    return notification


def test_evening_wrapup(username, minutes_from_now=2):
    """Test evening wrap-up notification (the actual use case)"""
    print("\n" + "="*60)
    print("TEST 3: EVENING WRAP-UP NOTIFICATION")
    print("="*60)
    
    user = User.objects.get(username=username)
    
    if not check_user_subscriptions(user):
        return None
    
    scheduled_time = timezone.now() + timedelta(minutes=minutes_from_now)
    
    print(f"\nCreating evening wrap-up notification for {user.username}...")
    print(f"Scheduled time: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"(in {minutes_from_now} minute(s))")
    
    notification = ScheduledNotification.objects.create(
        user=user,
        notification_type='evening_wrapup',
        title='Time for your evening wrap-up! 🌙',
        body='Do you want to catch up with LifePal?',
        scheduled_time=scheduled_time,
        url='/chat?session=evening_wrapup',
        tag='evening-wrapup',
        snooze_duration_minutes=30,
        max_snooze_count=3,
        metadata={
            'session_type': 'evening_wrapup',
            'auto_start': True
        }
    )
    
    print(f"\n✓ Evening wrap-up notification created!")
    print(f"  ID: {notification.id}")
    print(f"  Will open: /chat?session=evening_wrapup")
    print(f"  Snooze duration: 30 minutes")
    print(f"\n  When it appears:")
    print(f"    - Click the notification body → Opens chat with evening_wrapup session")
    print(f"    - Click 'Snooze 30min' button → Reschedules for 30 minutes later")
    
    return notification


def list_pending_notifications(username):
    """List all pending notifications for user"""
    print("\n" + "="*60)
    print("PENDING NOTIFICATIONS")
    print("="*60)
    
    user = User.objects.get(username=username)
    
    notifications = ScheduledNotification.objects.filter(
        user=user,
        status__in=['pending', 'snoozed']
    ).order_by('scheduled_time')
    
    if not notifications.exists():
        print("\nNo pending notifications.")
        return
    
    print(f"\nFound {notifications.count()} pending notification(s):\n")
    
    for notif in notifications:
        print(f"  • {notif.title}")
        print(f"    ID: {notif.id}")
        print(f"    Type: {notif.notification_type}")
        print(f"    Status: {notif.status}")
        print(f"    Scheduled: {notif.scheduled_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"    Snooze count: {notif.snooze_count}/{notif.max_snooze_count}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_notifications.py <username> [options]")
        print("\nOptions:")
        print("  --immediate-only    Only test immediate notification")
        print("  --scheduled-only    Only test scheduled notification")
        print("  --evening-only      Only test evening wrap-up")
        print("  --list              List pending notifications")
        sys.exit(1)
    
    username = sys.argv[1]
    
    # Check if user exists
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"✗ Error: User '{username}' not found")
        print("\nAvailable users:")
        for u in User.objects.all()[:10]:
            print(f"  - {u.username}")
        sys.exit(1)
    
    print("\n" + "🔔" * 30)
    print(f"  LIFEPAL PUSH NOTIFICATION TESTER")
    print("🔔" * 30)
    print(f"\nTesting for user: {user.username}")
    
    # Parse options
    immediate_only = '--immediate-only' in sys.argv
    scheduled_only = '--scheduled-only' in sys.argv
    evening_only = '--evening-only' in sys.argv
    list_only = '--list' in sys.argv
    
    if list_only:
        list_pending_notifications(username)
        return
    
    # Run tests
    if immediate_only:
        test_immediate_notification(username)
    elif scheduled_only:
        test_scheduled_notification(username, minutes_from_now=1)
    elif evening_only:
        test_evening_wrapup(username, minutes_from_now=2)
    else:
        # Run all tests
        test_immediate_notification(username)
        test_scheduled_notification(username, minutes_from_now=1)
        test_evening_wrapup(username, minutes_from_now=2)
    
    # Show pending notifications
    list_pending_notifications(username)
    
    print("\n" + "="*60)
    print("IMPORTANT REMINDERS")
    print("="*60)
    print("\n1. Make sure Celery worker and beat are running:")
    print("   celery -A core worker -B -l info")
    print("\n2. Check browser console for any errors")
    print("\n3. Scheduled notifications are processed every 60 seconds")
    print("\n4. Check Celery logs to see when notifications are sent")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
