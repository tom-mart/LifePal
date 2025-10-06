"""
Context builder for check-in conversations.

This module builds the system prompt and initial messages for check-in conversations
based on the check-in type, user data, and previous check-ins.
"""

from django.contrib.auth.models import User
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .models import CheckIn, DailyLog


class CheckInContextBuilder:
    """Builds context for check-in conversations"""
    
    def __init__(self, user: User, checkin: CheckIn):
        self.user = user
        self.checkin = checkin
        self.daily_log = checkin.daily_log
        
    def build_system_prompt(self) -> str:
        """Build the complete system prompt for this check-in"""
        
        # Base identity
        identity = self._get_ai_identity()
        
        # Check-in specific instructions
        checkin_instructions = self._get_checkin_instructions()
        
        # User context
        user_context = self._get_user_context()
        
        # Previous check-ins context
        previous_context = self._get_previous_checkins_context()
        
        # Tool instructions
        tool_instructions = self._get_tool_instructions()
        
        prompt = f"""
{identity}

{checkin_instructions}

{user_context}

{previous_context}

{tool_instructions}

Remember:
- Be warm, empathetic, and supportive
- Ask follow-up questions to understand deeply
- Keep the conversation focused on the check-in purpose
- Extract structured insights at the end
- Suggest actions when appropriate (reminders, tasks, etc.)
"""
        
        return prompt.strip()
    
    def _get_ai_identity(self) -> str:
        """Get AI identity from user's AI Identity Profile"""
        if hasattr(self.user, 'ai_identity'):
            identity = self.user.ai_identity
            return f"""You are {identity.name}, {identity.role}.

Personality: {identity.personality}
Communication Style: {identity.communication_style}"""
        
        return """You are LifePal, a supportive AI life assistant focused on wellbeing.

You are empathetic, non-judgmental, and focused on helping users understand and improve their wellbeing."""
    
    def _get_checkin_instructions(self) -> str:
        """Get instructions specific to the check-in type"""
        
        instructions = {
            'morning': """
## Morning Catch-Up

This is a morning check-in to help the user start their day mindfully.

Your goals:
1. Learn how the user is feeling physically and mentally
2. Understand what's on their mind for today
3. Identify any upcoming challenges or stressful events
4. Offer support and encouragement
5. If there are significant stressful events, consider creating a midday check-in reminder

Questions to explore:
- How did they sleep?
- How are they feeling physically and mentally?
- What's on their schedule today?
- Any concerns or things they're looking forward to?
- Do they need any support or reminders?

At the end, extract:
- mood (string)
- physical_state (string)
- concerns (list)
- upcoming_challenges (list with event, time, stress_level)
- positive_notes (list)
""",
            'midday': """
## Midday Check-In

This is a midday check-in, likely triggered by something mentioned in the morning.

Your goals:
1. Follow up on the context that triggered this check-in
2. See how the user is feeling now
3. Offer support before any upcoming stressful events
4. Help them prepare or decompress

Questions to explore:
- How are they feeling right now?
- How is the day going so far?
- Are they ready for upcoming events?
- Do they need a break or any support?

At the end, extract:
- current_mood (string)
- stress_level (1-10)
- needs_support (boolean)
- notes (string)
""",
            'evening': """
## Evening Reflection

This is an evening reflection to help the user process their day.

Your goals:
1. Help them reflect on the day
2. Identify positive moments and challenges
3. Process any difficult experiences
4. Plan for tomorrow
5. Assign emotions to the day for tracking

Questions to explore:
- How did the day go overall?
- What went well?
- What was challenging?
- How are they feeling now?
- What's on their mind for tomorrow?
- What emotions best describe today?

At the end, extract:
- overall_mood (string)
- day_rating (1-10)
- highlights (list)
- challenges (list)
- emotions (list with emotion name and intensity 1-10)
- tomorrow_concerns (list)
""",
            'adhoc': """
## Ad-hoc Check-In

This is a user-initiated check-in. Be flexible and follow their lead.

Your goals:
1. Understand why they wanted to check in
2. Provide support and active listening
3. Help them process whatever is on their mind
4. Offer practical suggestions if appropriate

Be responsive to their needs and adjust your approach accordingly.
"""
        }
        
        return instructions.get(self.checkin.check_in_type, instructions['adhoc'])
    
    def _get_user_context(self) -> str:
        """Get relevant user context (tasks, diary entries, etc.)"""
        context_parts = []
        
        # Get today's tasks
        tasks = self._get_todays_tasks()
        if tasks:
            context_parts.append(f"## User's Tasks for Today\n{tasks}")
        
        # Get this week's tasks
        week_tasks = self._get_week_tasks()
        if week_tasks:
            context_parts.append(f"## User's Tasks This Week\n{week_tasks}")
        
        # Get recent diary entries (if you have a diary model)
        # diary = self._get_recent_diary_entries()
        # if diary:
        #     context_parts.append(f"## Recent Diary Entries\n{diary}")
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    def _get_todays_tasks(self) -> str:
        """Get user's tasks for today"""
        try:
            from todo.models import Task
            from django.utils import timezone
            
            today = timezone.now().date()
            tasks = Task.objects.filter(
                user=self.user,
                due_date=today,
                is_completed=False
            ).order_by('priority', 'due_date')
            
            if not tasks:
                return ""
            
            task_list = []
            for task in tasks:
                priority = task.get_priority_display() if hasattr(task, 'get_priority_display') else task.priority
                task_list.append(f"- [{priority}] {task.title}")
            
            return "\n".join(task_list)
        except Exception:
            return ""
    
    def _get_week_tasks(self) -> str:
        """Get user's tasks for this week"""
        try:
            from todo.models import Task
            from django.utils import timezone
            
            today = timezone.now().date()
            week_end = today + timedelta(days=7)
            
            tasks = Task.objects.filter(
                user=self.user,
                due_date__gt=today,
                due_date__lte=week_end,
                is_completed=False
            ).order_by('due_date', 'priority')
            
            if not tasks:
                return ""
            
            task_list = []
            for task in tasks:
                priority = task.get_priority_display() if hasattr(task, 'get_priority_display') else task.priority
                due = task.due_date.strftime('%A, %b %d')
                task_list.append(f"- [{priority}] {task.title} (Due: {due})")
            
            return "\n".join(task_list)
        except Exception:
            return ""
    
    def _get_previous_checkins_context(self) -> str:
        """Get context from previous check-ins today"""
        
        # Get completed check-ins from today, before this one
        previous_checkins = self.daily_log.checkins.filter(
            status='completed',
            completed_at__lt=self.checkin.created_at
        ).order_by('completed_at')
        
        if not previous_checkins:
            return ""
        
        context_parts = ["## Earlier Check-ins Today"]
        
        for checkin in previous_checkins:
            context_parts.append(f"\n### {checkin.get_check_in_type_display()}")
            if checkin.summary:
                context_parts.append(checkin.summary)
            if checkin.insights:
                context_parts.append(f"Key insights: {checkin.insights}")
        
        # Add trigger context if this check-in was created dynamically
        if self.checkin.trigger_context:
            context_parts.append(f"\n## Why This Check-in Was Created")
            context_parts.append(str(self.checkin.trigger_context))
        
        return "\n".join(context_parts)
    
    def _get_tool_instructions(self) -> str:
        """Get instructions for available tools"""
        
        return """
## Available Actions

You can perform the following actions during the conversation:

1. **Create Reminder**: If the user mentions a stressful event or something they need to prepare for, you can create a midday check-in reminder.
   - Use this when you identify a need for follow-up support
   - Suggest a time that makes sense (e.g., 30 minutes before a stressful event)

2. **Create Task**: If the user mentions something they need to do, you can create a task for them.
   - Only do this if they explicitly want to remember something
   - Ask for details like due date and priority

3. **Save Moment**: If the user shares a significant positive or negative moment, you can save it to their journal.
   - Use this for meaningful experiences they want to remember

When you want to perform an action, clearly state what you're doing to the user.
"""
    
    def get_initial_message(self) -> str:
        """Get the initial message to start the conversation"""
        
        messages = {
            'morning': "Good morning! How are you feeling today?",
            'midday': "Hi! Just checking in. How are things going?",
            'evening': "Good evening! How did your day go?",
            'adhoc': "Hi! I'm here to chat. What's on your mind?"
        }
        
        # Customize based on trigger context
        if self.checkin.trigger_context:
            reason = self.checkin.trigger_context.get('reason')
            if reason == 'stressful_event':
                event = self.checkin.trigger_context.get('event', 'your upcoming event')
                return f"Hi! Just checking in before {event}. How are you feeling?"
        
        return messages.get(self.checkin.check_in_type, messages['adhoc'])
