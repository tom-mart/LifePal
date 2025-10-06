# Check-in System Migration & Setup Guide

## Overview

This guide walks you through setting up the redesigned check-in system for LifePal.

## Step 1: Run Migrations

```bash
cd backend

# Create migrations for both apps
python manage.py makemigrations llm_chat wellbeing

# Review the migrations
python manage.py showmigrations llm_chat wellbeing

# Apply migrations
python manage.py migrate llm_chat
python manage.py migrate wellbeing
```

### Expected Migration Changes

**llm_chat app:**
- Add `conversation_type` field to Conversation model (default='general')
- Add database indexes for conversation_type queries

**wellbeing app:**
- Add new fields to CheckIn model:
  - `status` (CharField with choices)
  - `scheduled_time` (DateTimeField, nullable)
  - `trigger_context` (JSONField)
  - `insights` (JSONField)
  - `summary` (TextField)
  - `actions_taken` (JSONField)
  - `started_at` (DateTimeField, nullable)
  - `updated_at` (DateTimeField, auto_now)
- Remove old fields:
  - `physical_feeling`
  - `mental_feeling`
  - `notes`
- Remove `unique_together` constraint
- Add database indexes
- Add 'adhoc' to CHECK_IN_TYPES choices

## Step 2: Populate Initial Data

### Create Emotion Reference Data

```bash
python manage.py shell
```

```python
from wellbeing.models import Emotion

emotions = [
    {'name': 'Happy', 'emoji': '😊'},
    {'name': 'Sad', 'emoji': '😢'},
    {'name': 'Anxious', 'emoji': '😰'},
    {'name': 'Calm', 'emoji': '😌'},
    {'name': 'Excited', 'emoji': '🤩'},
    {'name': 'Angry', 'emoji': '😠'},
    {'name': 'Tired', 'emoji': '😴'},
    {'name': 'Energetic', 'emoji': '⚡'},
    {'name': 'Stressed', 'emoji': '😫'},
    {'name': 'Grateful', 'emoji': '🙏'},
    {'name': 'Confident', 'emoji': '💪'},
    {'name': 'Overwhelmed', 'emoji': '🤯'},
]

for emotion_data in emotions:
    Emotion.objects.get_or_create(
        name=emotion_data['name'],
        defaults={'emoji': emotion_data['emoji']}
    )

print(f"Created {Emotion.objects.count()} emotions")
```

## Step 3: Set Up Scheduling

Choose one of the following methods:

### Option A: Django Management Command (Simplest)

1. Create the management command directory:

```bash
mkdir -p src/wellbeing/management/commands
touch src/wellbeing/management/commands/__init__.py
```

2. Create `src/wellbeing/management/commands/schedule_checkins.py`:

```python
from django.core.management.base import BaseCommand
from wellbeing.scheduler import CheckInScheduler


class Command(BaseCommand):
    help = 'Schedule daily check-ins for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to schedule for (YYYY-MM-DD), defaults to today'
        )

    def handle(self, *args, **options):
        from datetime import datetime
        
        date = None
        if options['date']:
            date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        
        results = CheckInScheduler.schedule_for_all_users(date)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Scheduled check-ins for {results['total_users']} users. "
                f"Created {results['scheduled']} check-ins."
            )
        )
        
        if results['errors']:
            self.stdout.write(
                self.style.ERROR(
                    f"✗ Errors: {len(results['errors'])}"
                )
            )
            for error in results['errors']:
                self.stdout.write(f"  User {error['user_id']}: {error['error']}")
```

3. Add to crontab:

```bash
crontab -e
```

```
# Schedule daily check-ins at midnight
0 0 * * * cd /path/to/lifepal/backend && /path/to/venv/bin/python manage.py schedule_checkins
```

### Option B: Celery (For Production)

1. Install Celery:

```bash
pip install celery redis
```

2. Create `src/wellbeing/tasks.py`:

```python
from celery import shared_task
from .scheduler import CheckInScheduler


@shared_task
def schedule_daily_checkins():
    """Run daily at midnight to schedule check-ins"""
    results = CheckInScheduler.schedule_for_all_users()
    return results


@shared_task
def send_pending_notifications():
    """Run every minute to send notifications for pending check-ins"""
    from .notifications import send_checkin_notification
    
    pending = CheckInScheduler.get_pending_notifications()
    
    for checkin in pending:
        send_checkin_notification(checkin)
    
    return len(pending)
```

3. Configure Celery Beat in `settings.py`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'schedule-daily-checkins': {
        'task': 'wellbeing.tasks.schedule_daily_checkins',
        'schedule': crontab(hour=0, minute=0),  # Midnight
    },
    'send-pending-notifications': {
        'task': 'wellbeing.tasks.send_pending_notifications',
        'schedule': 60.0,  # Every minute
    },
}
```

## Step 4: Test the System

### Test Check-in Creation

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from wellbeing.scheduler import CheckInScheduler
from django.utils import timezone

# Get a test user
user = User.objects.first()

# Schedule check-ins
checkins = CheckInScheduler.schedule_daily_checkins(user)

print(f"Created {len(checkins)} check-ins:")
for checkin in checkins:
    print(f"  - {checkin.get_check_in_type_display()} at {checkin.scheduled_time}")

# Verify
from wellbeing.models import DailyLog
daily_log, _ = DailyLog.get_or_create_today(user)
print(f"\nToday's check-ins: {daily_log.checkins.count()}")
```

### Test API Endpoints

```bash
# Get auth token first
curl -X POST http://localhost:8000/api/token/pair \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'

# Get today's check-ins
curl http://localhost:8000/api/wellbeing/checkins/today \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get daily log
curl http://localhost:8000/api/wellbeing/daily-log/today \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Step 5: Update Frontend (Optional)

If you want to add a wellbeing dashboard to the frontend:

1. Create a new page: `frontend/src/app/wellbeing/page.tsx`
2. Fetch check-ins using the API
3. Display check-in status and summaries
4. Add buttons to start/skip check-ins

Example API calls from frontend:

```typescript
// Get today's check-ins
const response = await apiClient.get('/api/wellbeing/checkins/today');

// Start a check-in
const startResponse = await apiClient.post(`/api/wellbeing/checkins/${checkinId}/start`);
// This returns conversation_id and initial_message
// Redirect to chat with this conversation

// Skip a check-in
await apiClient.post(`/api/wellbeing/checkins/${checkinId}/skip`);
```

## Step 6: Configure Notifications

The check-in system needs to send notifications when check-ins are scheduled.

### Using Your Existing Notification System

You already have a notifications app. Integrate it:

```python
# In wellbeing/notifications.py

from notifications.models import Notification  # Your existing model

def send_checkin_notification(checkin):
    """Send notification for a scheduled check-in"""
    
    messages = {
        'morning': {
            'title': 'Good morning! Time for a catch-up',
            'body': 'Let\'s check in on how you\'re feeling today'
        },
        'midday': {
            'title': 'Midday check-in',
            'body': 'How are things going?'
        },
        'evening': {
            'title': 'Evening reflection',
            'body': 'Let\'s reflect on your day'
        }
    }
    
    msg = messages.get(checkin.check_in_type, {
        'title': 'Check-in time',
        'body': 'Time for a wellbeing check-in'
    })
    
    # Create notification
    Notification.objects.create(
        user=checkin.daily_log.user,
        title=msg['title'],
        message=msg['body'],
        notification_type='checkin',
        data={
            'checkin_id': str(checkin.id),
            'action': 'start_checkin'
        }
    )
```

## Step 7: Verify Everything Works

### Checklist

- [ ] Migrations applied successfully
- [ ] Emotions created
- [ ] Check-ins can be scheduled
- [ ] API endpoints return data
- [ ] Conversations are created with correct type
- [ ] General chat history excludes check-ins
- [ ] Notifications are sent (if configured)

### Test Full Flow

1. Schedule a check-in for a user
2. Trigger notification (manually or via scheduler)
3. User clicks notification → starts check-in
4. Check-in creates conversation with type='checkin'
5. User has conversation with LLM
6. LLM extracts insights and completes check-in
7. Verify check-in is marked as completed
8. Verify conversation doesn't appear in general chat history

## Troubleshooting

### Migration Issues

**Error: Field 'conversation_type' doesn't have a default**

Solution: The migration should set default='general'. If it doesn't, edit the migration file:

```python
migrations.AddField(
    model_name='conversation',
    name='conversation_type',
    field=models.CharField(default='general', max_length=20, ...),
)
```

### JSONField Issues

**Error: JSONField requires PostgreSQL**

If using SQLite for development, install:

```bash
pip install django-jsonfield-backport
```

Then in models.py:
```python
from django.db.models import JSONField  # This works on all databases
```

### Scheduling Issues

**Check-ins not being created**

1. Verify scheduler is running: `python manage.py schedule_checkins`
2. Check for errors in logs
3. Verify users exist and are active

## Next Steps

1. **Build Frontend UI** - Create wellbeing dashboard
2. **Implement Tool Calling** - Allow LLM to create reminders/tasks during check-ins
3. **Add Analytics** - Track wellbeing trends over time
4. **Customize Scheduling** - Let users set their preferred check-in times
5. **Add Insights Dashboard** - Visualize emotions and patterns

## Resources

- [Check-in Usage Guide](./checkin_usage_guide.md) - Detailed usage examples
- [Models Documentation](../src/wellbeing/models.py) - Model definitions
- [API Documentation](../src/wellbeing/api.py) - API endpoints
