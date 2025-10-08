"""
Check-in Tool

Handles wellbeing check-in initiation and management.
"""

from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


def start_checkin(
    user: User,
    checkin_type: str = 'adhoc',
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Start a wellbeing check-in conversation with the user.
    
    Use this tool when:
    - User explicitly asks for a check-in
    - User wants to talk about their day, feelings, or wellbeing
    - You identify the user might benefit from structured reflection
    - User mentions morning routine, evening reflection, or daily review
    
    This tool will:
    - Create a check-in record
    - Gather relevant context (tasks, previous check-ins)
    - Provide you with information to personalize the conversation
    
    Args:
        user: User context (automatically provided)
        checkin_type: Type of check-in. Options:
            - 'morning': Daily morning check-in
            - 'midday': Midday check-up
            - 'evening': Evening reflection
            - 'adhoc': Any-time check-in
        reason: Optional reason for the check-in (useful for midday/adhoc)
        
    Returns:
        dict: Check-in context including tasks, previous check-ins, and suggestions
        
    Examples:
        - start_checkin(checkin_type='morning') → Morning check-in with today's tasks
        - start_checkin(checkin_type='evening') → Evening reflection
        - start_checkin(checkin_type='adhoc', reason='feeling stressed') → Ad-hoc check-in
    """
    try:
        from wellbeing.models import CheckIn, DailyLog
        from tasks.models import Task
        
        # Create check-in record
        daily_log, _ = DailyLog.get_or_create_today(user)
        checkin = CheckIn.objects.create(
            daily_log=daily_log,
            check_in_type=checkin_type,
            status='in_progress',
            trigger_context={'reason': reason, 'source': 'tool_call'} if reason else {'source': 'tool_call'}
        )
        
        # Gather context
        today = date.today()
        
        # Get today's tasks
        tasks_today = Task.objects.filter(
            user=user,
            due_date=today,
            status='pending'
        ).values('id', 'title', 'priority', 'due_time')
        
        # Get previous check-ins today
        previous_checkins_today = CheckIn.objects.filter(
            daily_log=daily_log,
            status='completed'
        ).exclude(id=checkin.id).values('check_in_type', 'summary', 'insights')
        
        # Get user timezone
        user_timezone = 'UTC'
        if hasattr(user, 'usersettings'):
            user_timezone = user.usersettings.timezone
        
        # Build context response
        context = {
            'success': True,
            'checkin_id': str(checkin.id),
            'checkin_type': checkin_type,
            'context': {
                'tasks_today': list(tasks_today),
                'tasks_count': len(tasks_today),
                'previous_checkins': list(previous_checkins_today),
                'previous_checkins_count': len(previous_checkins_today),
                'user_timezone': user_timezone,
                'current_time': datetime.now().strftime('%H:%M'),
                'reason': reason
            },
            'suggestions': _get_checkin_suggestions(checkin_type),
            'message': f'{checkin_type.capitalize()} check-in started successfully'
        }
        
        logger.info(f"Started {checkin_type} check-in for user {user.username}")
        return context
    
    except Exception as e:
        logger.error(f"Error starting check-in: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to start check-in'
        }


def _get_checkin_suggestions(checkin_type: str) -> list:
    """Get conversation suggestions based on check-in type"""
    suggestions = {
        'morning': [
            'Ask about sleep quality',
            'Discuss today\'s tasks and priorities',
            'Check energy levels and mood',
            'Identify potential challenges for the day',
            'Set intentions for the day'
        ],
        'evening': [
            'Review what went well today',
            'Discuss challenges faced',
            'Capture emotions and feelings',
            'Celebrate accomplishments',
            'Plan for tomorrow',
            'Assess sleep readiness'
        ],
        'midday': [
            'Check current stress levels',
            'Assess progress on tasks',
            'Identify if support is needed',
            'Quick mood check',
            'Energy level assessment'
        ],
        'adhoc': [
            'Listen to what\'s on their mind',
            'Provide support and understanding',
            'Help process emotions',
            'Offer practical suggestions',
            'Validate their feelings'
        ]
    }
    
    return suggestions.get(checkin_type, suggestions['adhoc'])


# Tool metadata for registry
start_checkin.tool_metadata = {
    'name': 'start_checkin',
    'description': start_checkin.__doc__,
    'category': 'wellbeing',
    'parameters': {
        'type': 'object',
        'properties': {
            'checkin_type': {
                'type': 'string',
                'enum': ['morning', 'midday', 'evening', 'adhoc'],
                'description': 'Type of check-in to start',
                'default': 'adhoc'
            },
            'reason': {
                'type': 'string',
                'description': 'Optional reason for the check-in (especially for midday/adhoc)'
            }
        },
        'required': []
    }
}
