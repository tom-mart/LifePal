# Check-in System Quick Reference

## API Endpoints

### Get Today's Check-ins
```
GET /api/wellbeing/checkins/today
```

### Get Specific Check-in
```
GET /api/wellbeing/checkins/{checkin_id}
```

### Start Check-in
```
POST /api/wellbeing/checkins/{checkin_id}/start
```
Returns: `conversation_id`, `initial_message`

### Complete Check-in
```
POST /api/wellbeing/checkins/{checkin_id}/complete
Body: {
  "insights": {...},
  "summary": "...",
  "actions_taken": [...]
}
```

### Skip Check-in
```
POST /api/wellbeing/checkins/{checkin_id}/skip
```

### Create Ad-hoc Check-in
```
POST /api/wellbeing/checkins/adhoc
```

### Get Today's Daily Log
```
GET /api/wellbeing/daily-log/today
```

### Get Daily Log by Date
```
GET /api/wellbeing/daily-log/{YYYY-MM-DD}
```

## Model Quick Reference

### CheckIn States
- `scheduled` - Notification sent, not started
- `in_progress` - User opened chat
- `completed` - Conversation ended
- `skipped` - User dismissed

### CheckIn Types
- `morning` - Morning Catch-up
- `midday` - Midday Check-in
- `evening` - Evening Reflection
- `adhoc` - Ad-hoc Check-in

### Conversation Types
- `general` - Regular chat (shown in history)
- `checkin` - Check-in conversation (hidden from history)

## Common Code Snippets

### Schedule Check-ins for User
```python
from wellbeing.scheduler import CheckInScheduler

checkins = CheckInScheduler.schedule_daily_checkins(user)
```

### Create Dynamic Midday Check-in
```python
from datetime import datetime, time
from django.utils import timezone

scheduled_time = datetime.combine(date.today(), time(17, 30))
scheduled_time = timezone.make_aware(scheduled_time)

checkin = CheckInScheduler.create_dynamic_midday_checkin(
    user=user,
    scheduled_time=scheduled_time,
    trigger_context={
        'reason': 'stressful_event',
        'event': 'Presentation at 6pm',
        'created_by': 'llm'
    }
)
```

### Get Completed Check-ins for Context
```python
from wellbeing.models import DailyLog

daily_log, _ = DailyLog.get_or_create_today(user)
completed = daily_log.checkins.filter(status='completed')

for checkin in completed:
    print(f"{checkin.check_in_type}: {checkin.summary}")
```

### Start Check-in Conversation
```python
from llm_chat.models import Conversation, Message
from wellbeing.context_builder import CheckInContextBuilder

# Create conversation
conversation = Conversation.objects.create(
    user=user,
    title=f"Morning Catch-up - {date.today()}",
    conversation_type='checkin'
)

# Start check-in
checkin.start_conversation(conversation)

# Build context
builder = CheckInContextBuilder(user, checkin)
system_prompt = builder.build_system_prompt()
initial_message = builder.get_initial_message()

# Add messages
Message.objects.create(
    conversation=conversation,
    role='system',
    content=system_prompt
)

Message.objects.create(
    conversation=conversation,
    role='assistant',
    content=initial_message
)
```

### Complete Check-in with Insights
```python
insights = {
    'mood': 'anxious',
    'physical_state': 'tired',
    'concerns': ['presentation', 'deadline'],
    'upcoming_challenges': [
        {'event': 'presentation', 'time': '18:00', 'stress_level': 'high'}
    ]
}

checkin.complete(
    insights=insights,
    summary="User feeling anxious about presentation. Created midday reminder.",
    actions_taken=checkin.actions_taken
)
```

### Track Action During Check-in
```python
checkin.add_action(
    'create_reminder',
    reminder_type='midday',
    scheduled_time='17:30',
    reason='Follow-up before presentation'
)
```

### Get Only General Chats (Exclude Check-ins)
```python
from llm_chat.models import Conversation

general_chats = Conversation.get_general_chats(user)
checkin_conversations = Conversation.get_checkin_conversations(user)
```

### Update Daily Log at Evening
```python
from wellbeing.models import Emotion, DailyLogEmotion

# Extract emotions from evening check-in
emotions_data = evening_checkin.insights.get('emotions', [])

for emotion_data in emotions_data:
    emotion = Emotion.objects.get(name=emotion_data['emotion'])
    DailyLogEmotion.objects.update_or_create(
        daily_log=daily_log,
        emotion=emotion,
        defaults={'intensity': emotion_data['intensity']}
    )

# Generate summary
daily_log.summary = generate_day_summary(daily_log)
daily_log.is_completed = True
daily_log.save()
```

## Tool Calling Examples

### LLM Creates Reminder
```python
# During conversation, LLM decides to create reminder
tool_call = {
    'tool': 'create_reminder',
    'parameters': {
        'time': '17:30',
        'reason': 'Check in before stressful event'
    }
}

# Execute
midday_checkin = CheckInScheduler.create_dynamic_midday_checkin(
    user=user,
    scheduled_time=parse_time(tool_call['parameters']['time']),
    trigger_context={
        'reason': tool_call['parameters']['reason'],
        'source_checkin': str(checkin.id)
    }
)

# Track action
checkin.add_action('create_reminder', **tool_call['parameters'])
```

### LLM Creates Task
```python
from todo.models import Task

tool_call = {
    'tool': 'create_task',
    'parameters': {
        'title': 'Prepare presentation slides',
        'due_date': '2025-10-07',
        'priority': 'high'
    }
}

task = Task.objects.create(
    user=user,
    title=tool_call['parameters']['title'],
    due_date=tool_call['parameters']['due_date'],
    priority=tool_call['parameters']['priority']
)

checkin.add_action('create_task', task_id=str(task.id), **tool_call['parameters'])
```

### LLM Saves Moment
```python
from wellbeing.models import Moment

tool_call = {
    'tool': 'save_moment',
    'parameters': {
        'what_happened': 'Had a great conversation with a friend',
        'how_it_felt': 'Felt supported and understood'
    }
}

moment = Moment.create_for_user(
    user=user,
    what_happened=tool_call['parameters']['what_happened'],
    how_it_felt=tool_call['parameters']['how_it_felt']
)

checkin.add_action('save_moment', moment_id=str(moment.id))
```

## Frontend Integration

### Fetch Check-ins
```typescript
const response = await apiClient.get('/api/wellbeing/checkins/today');
const checkins = response.checkins;
```

### Start Check-in from Notification
```typescript
// User clicks notification
const checkinId = notification.data.checkin_id;

// Start check-in
const response = await apiClient.post(
  `/api/wellbeing/checkins/${checkinId}/start`
);

// Redirect to chat with the conversation
router.push(`/chat?conversation_id=${response.conversation_id}`);
```

### Display Check-in Status
```typescript
const statusColors = {
  scheduled: 'badge-info',
  in_progress: 'badge-warning',
  completed: 'badge-success',
  skipped: 'badge-ghost'
};

<div className={`badge ${statusColors[checkin.status]}`}>
  {checkin.status}
</div>
```

## Testing Commands

```bash
# Schedule check-ins manually
python manage.py schedule_checkins

# Test in shell
python manage.py shell
>>> from wellbeing.scheduler import CheckInScheduler
>>> from django.contrib.auth.models import User
>>> user = User.objects.first()
>>> CheckInScheduler.schedule_daily_checkins(user)

# Check pending notifications
>>> pending = CheckInScheduler.get_pending_notifications()
>>> print(f"Pending: {len(pending)}")
```
