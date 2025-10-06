# CheckIn Model Usage Guide

## Overview

The redesigned `CheckIn` model serves as a **metadata wrapper** around conversations that happen during wellbeing check-ins. It tracks scheduling, state, LLM-extracted insights, and actions taken during conversations.

## Key Design Decisions

### 1. **Conversation Storage**
- **Full conversation** is stored in `Conversation` and `Message` models (already exists)
- **CheckIn model** stores metadata, insights, and summary for quick access
- This separation allows:
  - Fast queries for daily summaries without parsing full conversations
  - Full conversation history available when needed for context
  - LLM can reference past check-ins efficiently

### 2. **State Tracking**
The model tracks four states:
- `scheduled`: Notification sent, user hasn't opened chat yet
- `in_progress`: User opened chat, conversation ongoing
- `completed`: Conversation ended, insights extracted
- `skipped`: User dismissed notification

### 3. **Dynamic Reminders**
The `trigger_context` field stores why a check-in was created:
```json
{
  "reason": "stressful_event",
  "event": "Important presentation at 6pm",
  "mentioned_in": "morning_checkin_id",
  "created_by": "llm"
}
```

## Usage Patterns

### Morning Catch-Up Flow

```python
from wellbeing.models import CheckIn
from llm_chat.models import Conversation, Message
from django.utils import timezone
from datetime import datetime, time

# 1. Schedule morning check-in (done by scheduler/cron)
morning_time = datetime.combine(user.date.today(), time(8, 0))
checkin = CheckIn.create_scheduled(
    user=user,
    check_in_type='morning',
    scheduled_time=morning_time
)

# 2. User clicks notification - create conversation with context
conversation = Conversation.objects.create(
    user=user,
    title=f"Morning Catch-up - {timezone.now().date()}",
    conversation_type='checkin'  # Exclude from general chat history
)

# 3. Start the check-in
checkin.start_conversation(conversation)

# 4. Add system message with context (not shown to user)
system_prompt = build_morning_context(user)  # Your function to build context
Message.objects.create(
    conversation=conversation,
    role='system',
    content=system_prompt
)

# 5. Add initial LLM message (shown to user)
initial_message = "Good morning! How are you feeling today?"
Message.objects.create(
    conversation=conversation,
    role='assistant',
    content=initial_message
)

# 6. During conversation, LLM can call tools
# Example: User mentions stressful event at 6pm
if llm_decides_to_create_reminder:
    # Create midday check-in
    midday_checkin = CheckIn.create_scheduled(
        user=user,
        check_in_type='midday',
        scheduled_time=datetime.combine(user.date.today(), time(17, 30)),
        trigger_context={
            'reason': 'stressful_event',
            'event': 'Presentation at 6pm',
            'mentioned_in': str(checkin.id),
            'created_by': 'llm'
        }
    )
    
    # Track action in current check-in
    checkin.add_action(
        'create_reminder',
        reminder_type='midday',
        scheduled_time='17:30',
        reason='Follow-up before stressful event'
    )

# 7. When conversation ends, extract insights
insights = {
    'mood': 'anxious',
    'physical_state': 'tired',
    'concerns': ['presentation', 'workload'],
    'positive_notes': ['good sleep'],
    'upcoming_challenges': [
        {'event': 'presentation', 'time': '18:00', 'stress_level': 'high'}
    ]
}

summary = "User is feeling anxious about presentation at 6pm. Slept well but feeling tired. Created midday check-in reminder."

checkin.complete(
    insights=insights,
    summary=summary,
    actions_taken=checkin.actions_taken  # Already populated via add_action
)
```

### Midday Check-In Flow (Dynamic)

```python
# 1. Notification triggers at scheduled time
# Fetch the check-in with context
checkin = CheckIn.objects.get(id=checkin_id)

# 2. Build conversation with context from morning
morning_checkin = CheckIn.objects.filter(
    daily_log=checkin.daily_log,
    check_in_type='morning',
    status='completed'
).first()

conversation = Conversation.objects.create(
    user=user,
    title=f"Midday Check-in - {timezone.now().date()}",
    conversation_type='checkin'
)

checkin.start_conversation(conversation)

# 3. System prompt includes trigger context
system_prompt = f"""
You are conducting a midday check-in.

Context from morning:
- User was anxious about presentation at 6pm
- {morning_checkin.summary if morning_checkin else 'No morning check-in'}

Trigger reason: {checkin.trigger_context.get('reason')}
Event: {checkin.trigger_context.get('event')}

Ask how they're feeling now and if they need support before the event.
"""

Message.objects.create(
    conversation=conversation,
    role='system',
    content=system_prompt
)

# 4. LLM starts conversation
initial_message = "Hi! Just checking in before your presentation. How are you feeling?"
Message.objects.create(
    conversation=conversation,
    role='assistant',
    content=initial_message
)
```

### Evening Reflection Flow

```python
# 1. Schedule evening check-in
evening_time = datetime.combine(user.date.today(), time(20, 0))
checkin = CheckIn.create_scheduled(
    user=user,
    check_in_type='evening',
    scheduled_time=evening_time
)

# 2. When user opens, include full day context
conversation = Conversation.objects.create(
    user=user,
    title=f"Evening Reflection - {timezone.now().date()}",
    conversation_type='checkin'
)

checkin.start_conversation(conversation)

# 3. Build context from all check-ins today
daily_log = checkin.daily_log
morning = daily_log.checkins.filter(check_in_type='morning', status='completed').first()
midday = daily_log.checkins.filter(check_in_type='midday', status='completed').first()

system_prompt = f"""
You are conducting an evening reflection.

Today's check-ins:
Morning: {morning.summary if morning else 'Not completed'}
Midday: {midday.summary if midday else 'Not completed'}

Focus on:
- Reflecting on the day
- Highlighting positive moments
- Processing challenges
- Planning for tomorrow
- Assigning emotions to the day

At the end, you should extract structured data to save to DailyLog.
"""

# 4. At completion, update DailyLog
insights = {
    'overall_mood': 'relieved',
    'day_rating': 7,
    'highlights': ['presentation went well', 'productive afternoon'],
    'challenges': ['morning anxiety', 'time management'],
    'emotions': [
        {'emotion': 'anxious', 'intensity': 7, 'time': 'morning'},
        {'emotion': 'confident', 'intensity': 8, 'time': 'evening'}
    ]
}

checkin.complete(insights=insights, summary="...")

# Update DailyLog with emotions
from wellbeing.models import Emotion, DailyLogEmotion

for emotion_data in insights['emotions']:
    emotion = Emotion.objects.get(name=emotion_data['emotion'])
    DailyLogEmotion.objects.update_or_create(
        daily_log=daily_log,
        emotion=emotion,
        defaults={'intensity': emotion_data['intensity']}
    )

# Generate day summary
daily_log.summary = generate_day_summary(daily_log)  # Your function
daily_log.is_completed = True
daily_log.summary_generated_at = timezone.now()
daily_log.save()
```

## Tool Calling During Conversations

The LLM can call tools during any check-in conversation. Here's how to structure it:

### Available Tools for Check-ins

```python
CHECKIN_TOOLS = [
    {
        'name': 'create_reminder',
        'description': 'Create a reminder for a midday check-in',
        'parameters': {
            'time': 'HH:MM format',
            'reason': 'Why this reminder is needed',
            'context': 'Additional context'
        }
    },
    {
        'name': 'fetch_tasks',
        'description': 'Fetch user tasks for today or this week',
        'parameters': {
            'timeframe': 'today|week'
        }
    },
    {
        'name': 'create_task',
        'description': 'Create a task based on conversation',
        'parameters': {
            'title': 'Task title',
            'due_date': 'ISO format',
            'priority': 'low|medium|high'
        }
    },
    {
        'name': 'save_moment',
        'description': 'Save a significant moment from the conversation',
        'parameters': {
            'what_happened': 'Description',
            'how_it_felt': 'Emotional response'
        }
    }
]
```

### Tool Call Example

```python
# During conversation, LLM decides to call a tool
tool_call = {
    'tool': 'create_reminder',
    'parameters': {
        'time': '17:30',
        'reason': 'Check in before stressful presentation',
        'context': 'User mentioned anxiety about 6pm presentation'
    }
}

# Execute tool
if tool_call['tool'] == 'create_reminder':
    midday_checkin = CheckIn.create_scheduled(
        user=user,
        check_in_type='midday',
        scheduled_time=datetime.combine(date.today(), time(17, 30)),
        trigger_context={
            'reason': tool_call['parameters']['reason'],
            'context': tool_call['parameters']['context'],
            'created_by': 'llm',
            'source_checkin': str(checkin.id)
        }
    )
    
    # Record action
    checkin.add_action(
        'create_reminder',
        reminder_id=str(midday_checkin.id),
        **tool_call['parameters']
    )
    
    # LLM confirms to user
    Message.objects.create(
        conversation=conversation,
        role='assistant',
        content="I've set a reminder for 5:30 PM to check in with you before your presentation."
    )
```

## Querying Check-ins

### Get today's check-ins
```python
from wellbeing.models import DailyLog

daily_log, _ = DailyLog.get_or_create_today(user)
checkins = daily_log.checkins.all()
```

### Get general chat history (excluding check-ins)
```python
from llm_chat.models import Conversation

# Only general chats
general_chats = Conversation.get_general_chats(user)

# Only check-in conversations
checkin_conversations = Conversation.get_checkin_conversations(user)
```

### Get completed check-ins for context
```python
completed_checkins = daily_log.checkins.filter(
    status='completed'
).order_by('completed_at')

for checkin in completed_checkins:
    print(f"{checkin.check_in_type}: {checkin.summary}")
    print(f"Insights: {checkin.insights}")
    print(f"Actions: {checkin.actions_taken}")
```

### Get full conversation
```python
checkin = CheckIn.objects.get(id=checkin_id)
if checkin.conversation:
    messages = checkin.conversation.messages.all()
    for msg in messages:
        if msg.role != 'system':  # Don't show system prompts
            print(f"{msg.role}: {msg.content}")
```

## Best Practices

1. **Always store full conversation** - Don't rely only on insights
2. **Extract insights at completion** - Makes querying faster
3. **Track all tool calls** - Helps with debugging and analytics
4. **Use trigger_context** - Provides continuity between check-ins
5. **Update DailyLog at evening** - Consolidate all check-ins into day summary
6. **Allow multiple adhoc check-ins** - User can initiate anytime
7. **System prompts not shown** - Keep context hidden from user UI

## Migration Notes

You'll need to create a migration for these changes:

```bash
python manage.py makemigrations wellbeing
python manage.py migrate wellbeing
```

The migration will:
- Add new fields (status, scheduled_time, trigger_context, insights, summary, actions_taken, started_at, updated_at)
- Remove old fields (physical_feeling, mental_feeling, notes)
- Update indexes
- Remove unique_together constraint
