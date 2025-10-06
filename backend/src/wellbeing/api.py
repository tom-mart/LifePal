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
    """Start a check-in conversation"""
    user = request.auth
    checkin = get_object_or_404(
        CheckIn,
        id=checkin_id,
        daily_log__user=user,
        status='scheduled'
    )
    
    # Create conversation
    conversation = Conversation.objects.create(
        user=user,
        title=f"{checkin.get_check_in_type_display()} - {checkin.daily_log.date}",
        conversation_type='checkin'
    )
    
    # Start the check-in
    checkin.start_conversation(conversation)
    
    # Build context and add system message
    from .context_builder import CheckInContextBuilder
    context_builder = CheckInContextBuilder(user, checkin)
    system_prompt = context_builder.build_system_prompt()
    
    Message.objects.create(
        conversation=conversation,
        role='system',
        content=system_prompt
    )
    
    # Add initial LLM message
    initial_message = context_builder.get_initial_message()
    assistant_message = Message.objects.create(
        conversation=conversation,
        role='assistant',
        content=initial_message
    )
    
    return {
        'success': True,
        'conversation_id': str(conversation.id),
        'checkin_id': str(checkin.id),
        'initial_message': {
            'id': str(assistant_message.id),
            'content': assistant_message.content,
            'created_at': assistant_message.created_at
        }
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
