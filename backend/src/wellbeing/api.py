from ninja import Router
from ninja_jwt.authentication import JWTAuth
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date

from .models import CheckIn, DailyLog
from .schemas import (
    CheckInSchema,
    CheckInCreateSchema,
    CheckInCompleteSchema,
    CheckInListSchema,
    DailyLogSchema
)
from llm_chat.models import Conversation, Message

router = Router(tags=['Wellbeing'], auth=JWTAuth())


@router.get('/checkins/today', response=CheckInListSchema)
def get_todays_checkins(request):
    """Get all check-ins for today"""
    user = request.auth
    daily_log, _ = DailyLog.get_or_create_today(user)
    
    checkins = daily_log.checkins.all().order_by('created_at')
    
    return {
        'checkins': [
            {
                'id': checkin.id,
                'check_in_type': checkin.check_in_type,
                'status': checkin.status,
                'scheduled_time': checkin.scheduled_time,
                'started_at': checkin.started_at,
                'completed_at': checkin.completed_at,
                'summary': checkin.summary,
                'conversation_id': checkin.conversation.id if checkin.conversation else None
            }
            for checkin in checkins
        ]
    }


@router.get('/checkins/{checkin_id}', response=CheckInSchema)
def get_checkin(request, checkin_id: str):
    """Get a specific check-in with details"""
    user = request.auth
    checkin = get_object_or_404(
        CheckIn,
        id=checkin_id,
        daily_log__user=user
    )
    
    return {
        'id': checkin.id,
        'check_in_type': checkin.check_in_type,
        'status': checkin.status,
        'scheduled_time': checkin.scheduled_time,
        'trigger_context': checkin.trigger_context,
        'insights': checkin.insights,
        'summary': checkin.summary,
        'actions_taken': checkin.actions_taken,
        'started_at': checkin.started_at,
        'completed_at': checkin.completed_at,
        'conversation_id': checkin.conversation.id if checkin.conversation else None
    }


@router.post('/checkins/{checkin_id}/start')
def start_checkin(request, checkin_id: str):
    """
    Start a check-in conversation using Tool_Retriever pattern.
    
    This endpoint creates a conversation and returns the conversation_id.
    The frontend will then send an auto-trigger message, and the LLM will:
    1. Call Tool_Retriever to discover check-in tools
    2. Call start_checkin tool to get context
    3. Generate a personalized opening message
    
    This fixes the bug where users saw an empty chat instead of LLM's opening.
    """
    user = request.auth
    checkin = get_object_or_404(
        CheckIn,
        id=checkin_id,
        daily_log__user=user
    )
    
    # If already started, return existing conversation
    if checkin.status == 'in_progress' and checkin.conversation:
        return {
            'success': True,
            'conversation_id': str(checkin.conversation.id),
            'checkin_id': str(checkin.id),
            'already_started': True
        }
    
    # Create conversation with ReAct system prompt
    conversation = Conversation.objects.create(
        user=user,
        title=f"{checkin.get_check_in_type_display()} - {checkin.daily_log.date}",
        conversation_type='checkin'
    )
    
    # Start the check-in (marks as in_progress)
    checkin.start_conversation(conversation)
    
    # Add system message with Tool_Retriever instructions
    # PromptManager will automatically include tool instructions
    from llm_service.prompt_manager import PromptManager
    prompt_manager = PromptManager(user=user)
    system_prompt = prompt_manager.get_system_prompt(
        include_user_context=True,
        include_dynamic_context=True,
        include_tool_instructions=True  # ReAct pattern with Tool_Retriever
    )
    
    # Add check-in specific instructions
    checkin_instructions = f"""

## CHECK-IN SPECIFIC INSTRUCTIONS

This is a {checkin.get_check_in_type_display()} check-in conversation.

**IMPORTANT TOOL USAGE:**
- The user's first message will trigger you to call tool_retriever and start_checkin
- Call start_checkin ONLY ONCE at the beginning to get context
- DO NOT call start_checkin again during the conversation
- After getting the context, engage naturally with the user about their day

**CHECK-IN COMPLETION:**

Signs that the check-in is complete:
- User says they're done, finished, or ready to end
- User says goodbye, bye, see you later, etc.
- User indicates they have nothing more to share
- User says "that's it for today/now/this morning"
- Natural conversation ending after covering the check-in topics

When you detect completion:
1. Provide a warm closing message
2. Include [CHECKIN_COMPLETE] at the end of your message
3. The system will automatically save insights

Example:
"Thank you for sharing with me today, Tom. I hope you have a restful evening. Take care! [CHECKIN_COMPLETE]"
"""
    
    Message.objects.create(
        conversation=conversation,
        role='system',
        content=system_prompt + checkin_instructions
    )
    
    # Return conversation details
    # Frontend will auto-send trigger message to initiate the check-in
    return {
        'success': True,
        'conversation_id': str(conversation.id),
        'checkin_id': str(checkin.id),
        'checkin_type': checkin.check_in_type
    }


@router.post('/checkins/{checkin_id}/complete')
def complete_checkin(request, checkin_id: str, data: CheckInCompleteSchema):
    """Complete a check-in with extracted insights"""
    user = request.auth
    checkin = get_object_or_404(
        CheckIn,
        id=checkin_id,
        daily_log__user=user,
        status='in_progress'
    )
    
    checkin.complete(
        insights=data.insights,
        summary=data.summary,
        actions_taken=data.actions_taken
    )
    
    return {
        'success': True,
        'checkin_id': str(checkin.id),
        'status': checkin.status
    }


@router.post('/checkins/{checkin_id}/skip')
def skip_checkin(request, checkin_id: str):
    """Mark a check-in as skipped"""
    user = request.auth
    checkin = get_object_or_404(
        CheckIn,
        id=checkin_id,
        daily_log__user=user,
        status='scheduled'
    )
    
    checkin.skip()
    
    return {
        'success': True,
        'checkin_id': str(checkin.id),
        'status': checkin.status
    }


@router.post('/checkins/adhoc')
def create_adhoc_checkin(request):
    """Create an ad-hoc check-in"""
    user = request.auth
    
    checkin = CheckIn.create_adhoc(
        user=user,
        trigger_context={'source': 'user_initiated'}
    )
    
    return {
        'success': True,
        'checkin_id': str(checkin.id),
        'check_in_type': checkin.check_in_type,
        'status': checkin.status
    }


@router.get('/daily-log/today', response=DailyLogSchema)
def get_todays_log(request):
    """Get today's daily log with all check-ins"""
    user = request.auth
    daily_log, _ = DailyLog.get_or_create_today(user)
    
    return {
        'id': daily_log.id,
        'date': daily_log.date,
        'summary': daily_log.summary,
        'is_completed': daily_log.is_completed,
        'checkins': [
            {
                'id': checkin.id,
                'check_in_type': checkin.check_in_type,
                'status': checkin.status,
                'summary': checkin.summary,
                'completed_at': checkin.completed_at
            }
            for checkin in daily_log.checkins.all()
        ]
    }


@router.get('/daily-log/{date}', response=DailyLogSchema)
def get_daily_log(request, date: str):
    """Get daily log for a specific date"""
    user = request.auth
    
    try:
        log_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return {'error': 'Invalid date format. Use YYYY-MM-DD'}
    
    daily_log = get_object_or_404(
        DailyLog,
        user=user,
        date=log_date
    )
    
    return {
        'id': daily_log.id,
        'date': daily_log.date,
        'summary': daily_log.summary,
        'is_completed': daily_log.is_completed,
        'checkins': [
            {
                'id': checkin.id,
                'check_in_type': checkin.check_in_type,
                'status': checkin.status,
                'summary': checkin.summary,
                'completed_at': checkin.completed_at
            }
            for checkin in daily_log.checkins.all()
        ]
    }
