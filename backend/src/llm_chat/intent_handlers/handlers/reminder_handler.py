"""
Reminder Intent Handler

Handles reminder creation, listing, cancellation, and editing.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from ..base_handler import BaseHandler, HandlerResponse
from notifications.models import ScheduledNotification
from notifications.utils import format_reminder_time

logger = logging.getLogger(__name__)


class ReminderHandler(BaseHandler):
    """
    Handler for reminder-related intents.
    
    Handles:
    - Creating reminders
    - Listing reminders
    - Canceling reminders
    - Editing reminders
    """
    
    HANDLER_NAME = "reminder"
    SUPPORTED_INTENTS = ['create_reminder', 'list_reminders', 'cancel_reminder', 'edit_reminder']
    
    @transaction.atomic
    def handle(self, intent_type: str, parameters: Dict[str, Any], user, message) -> Optional[HandlerResponse]:
        """
        Handle reminder intents.
        
        Args:
            intent_type: Type of intent (create/list/cancel/edit)
            parameters: Extracted parameters
            user: User who requested the action
            message: Original message object
            
        Returns:
            HandlerResponse with confirmation or error message
        """
        if intent_type == 'create_reminder':
            return self._handle_create(parameters, user, message)
        elif intent_type == 'list_reminders':
            return self._handle_list(parameters, user)
        elif intent_type == 'cancel_reminder':
            return self._handle_cancel(parameters, user)
        elif intent_type == 'edit_reminder':
            return self._handle_edit(parameters, user)
        
        return None
    
    def _handle_create(self, parameters: Dict[str, Any], user, message) -> Optional[HandlerResponse]:
        """Handle reminder creation"""
        
        task = parameters.get('task')
        scheduled_time_str = parameters.get('scheduled_time')
        
        # Validate we have the required information
        if not task:
            return HandlerResponse(
                response_type='error',
                message="I couldn't understand what you want to be reminded about. Could you please rephrase?",
                data={'error': 'missing_task'}
            )
        
        if not scheduled_time_str:
            return HandlerResponse(
                response_type='error',
                message="I couldn't understand when you want to be reminded. Could you specify a time or date?",
                data={'error': 'missing_time'}
            )
        
        try:
            # Parse the datetime
            parsed_time = datetime.fromisoformat(scheduled_time_str)

            # Make it timezone-aware if it's naive
            if timezone.is_naive(parsed_time):
                # Assume the parsed time is in the user's current timezone
                scheduled_time = timezone.make_aware(parsed_time, timezone.get_current_timezone())
            else:
                scheduled_time = parsed_time
            
            # Ensure it's in the future
            if scheduled_time <= timezone.now():
                return HandlerResponse(
                    response_type='error',
                    message="That time is in the past. Please specify a future time for the reminder.",
                    data={'error': 'past_time'}
                )
            
            # Create the scheduled notification
            notification = ScheduledNotification.objects.create(
                user=user,
                notification_type='reminder',
                title=f'Reminder: {task[:50]}',
                body=task,
                scheduled_time=scheduled_time,
                url='/chat',
                tag=f'reminder-{timezone.now().timestamp()}',
                snooze_duration_minutes=30,
                max_snooze_count=3,
                metadata={
                    'task': task,
                    'created_from_message': str(message.id),
                    'original_text': parameters.get('original_text', '')
                }
            )

            # Format the time for display
            formatted_time = format_reminder_time(scheduled_time)
            
            logger.info(f"Created reminder for {user.username}: '{task}' at {scheduled_time}")
            
            return HandlerResponse(
                response_type='reminder_created',
                message=f"✓ I'll remind you to {task} {formatted_time}",
                data={
                    'reminder_id': str(notification.id),
                    'task': task,
                    'scheduled_time': scheduled_time.isoformat(),
                    'formatted_time': formatted_time
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating reminder: {str(e)}", exc_info=True)
            return HandlerResponse(
                response_type='error',
                message="Sorry, I encountered an error while creating your reminder. Please try again.",
                data={'error': str(e)}
            )
    
    def _handle_list(self, parameters: Dict[str, Any], user) -> Optional[HandlerResponse]:
        """Handle listing reminders"""
        try:
            filter_type = parameters.get('filter_type', 'upcoming')
            
            # Query reminders
            query = ScheduledNotification.objects.filter(
                user=user,
                notification_type='reminder'
            )
            
            if filter_type == 'upcoming':
                query = query.filter(status__in=['pending', 'snoozed'])
            
            reminders = query.order_by('scheduled_time')[:20]  # Limit to 20
            
            if not reminders.exists():
                return HandlerResponse(
                    response_type='reminders_list',
                    message="You don't have any reminders set.",
                    data={'reminders': [], 'count': 0}
                )
            
            # Format reminders for display
            reminder_list = []
            message_parts = [f"You have {reminders.count()} reminder(s):\n"]
            
            for i, reminder in enumerate(reminders, 1):
                formatted_time = format_reminder_time(reminder.scheduled_time)
                status_emoji = "⏰" if reminder.status == 'pending' else "💤" if reminder.status == 'snoozed' else "✓"
                
                message_parts.append(f"{i}. {status_emoji} {reminder.body} - {formatted_time}")
                
                reminder_list.append({
                    'id': str(reminder.id),
                    'task': reminder.body,
                    'scheduled_time': reminder.scheduled_time.isoformat(),
                    'formatted_time': formatted_time,
                    'status': reminder.status,
                    'snooze_count': reminder.snooze_count
                })
            
            logger.info(f"Listed {reminders.count()} reminders for {user.username}")
            
            return HandlerResponse(
                response_type='reminders_list',
                message='\n'.join(message_parts),
                data={
                    'reminders': reminder_list,
                    'count': reminders.count()
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing reminders: {str(e)}", exc_info=True)
            return HandlerResponse(
                response_type='error',
                message="Sorry, I encountered an error while fetching your reminders.",
                data={'error': str(e)}
            )
    
    def _handle_cancel(self, parameters: Dict[str, Any], user) -> Optional[HandlerResponse]:
        """Handle canceling reminders"""
        try:
            cancel_all = parameters.get('cancel_all', False)
            description = parameters.get('description')
            
            if cancel_all:
                # Cancel all pending reminders
                cancelled = ScheduledNotification.objects.filter(
                    user=user,
                    notification_type='reminder',
                    status__in=['pending', 'snoozed']
                ).update(status='cancelled')
                
                logger.info(f"Cancelled {cancelled} reminders for {user.username}")
                
                return HandlerResponse(
                    response_type='reminders_cancelled',
                    message=f"✓ Cancelled {cancelled} reminder(s).",
                    data={'cancelled_count': cancelled}
                )
            
            elif description:
                # Find and cancel specific reminder
                reminders = ScheduledNotification.objects.filter(
                    user=user,
                    notification_type='reminder',
                    status__in=['pending', 'snoozed'],
                    body__icontains=description
                )
                
                if not reminders.exists():
                    return HandlerResponse(
                        response_type='error',
                        message=f"I couldn't find a reminder about '{description}'.",
                        data={'error': 'not_found'}
                    )
                
                # If multiple matches, cancel the first one
                reminder = reminders.first()
                reminder.cancel()
                
                formatted_time = format_reminder_time(reminder.scheduled_time)
                
                logger.info(f"Cancelled reminder {reminder.id} for {user.username}")
                
                return HandlerResponse(
                    response_type='reminders_cancelled',
                    message=f"✓ Cancelled reminder: {reminder.body} ({formatted_time})",
                    data={
                        'cancelled_count': 1,
                        'reminder_id': str(reminder.id)
                    }
                )
            
            else:
                return HandlerResponse(
                    response_type='error',
                    message="Please specify which reminder to cancel, or say 'cancel all reminders'.",
                    data={'error': 'missing_description'}
                )
                
        except Exception as e:
            logger.error(f"Error cancelling reminder: {str(e)}", exc_info=True)
            return HandlerResponse(
                response_type='error',
                message="Sorry, I encountered an error while cancelling the reminder.",
                data={'error': str(e)}
            )
    
    def _handle_edit(self, parameters: Dict[str, Any], user) -> Optional[HandlerResponse]:
        """Handle editing reminders"""
        try:
            description = parameters.get('description')
            new_time_str = parameters.get('new_time')
            
            if not description:
                return HandlerResponse(
                    response_type='error',
                    message="Please specify which reminder you want to change.",
                    data={'error': 'missing_description'}
                )
            
            if not new_time_str:
                return HandlerResponse(
                    response_type='error',
                    message="Please specify the new time for the reminder.",
                    data={'error': 'missing_time'}
                )
            
            # Find the reminder
            reminders = ScheduledNotification.objects.filter(
                user=user,
                notification_type='reminder',
                status__in=['pending', 'snoozed'],
                body__icontains=description
            )
            
            if not reminders.exists():
                return HandlerResponse(
                    response_type='error',
                    message=f"I couldn't find a reminder about '{description}'.",
                    data={'error': 'not_found'}
                )
            
            # Update the first matching reminder
            reminder = reminders.first()
            new_time = datetime.fromisoformat(new_time_str)
            
            # Ensure it's in the future
            if new_time <= timezone.now():
                return HandlerResponse(
                    response_type='error',
                    message="That time is in the past. Please specify a future time.",
                    data={'error': 'past_time'}
                )
            
            old_time = format_reminder_time(reminder.scheduled_time)
            reminder.scheduled_time = new_time
            reminder.status = 'pending'  # Reset status
            reminder.snooze_count = 0  # Reset snooze count
            reminder.save()
            
            new_time_formatted = format_reminder_time(new_time)
            
            logger.info(f"Updated reminder {reminder.id} for {user.username}: {old_time} -> {new_time_formatted}")
            
            return HandlerResponse(
                response_type='reminder_updated',
                message=f"✓ Updated reminder: {reminder.body}\nChanged from {old_time} to {new_time_formatted}",
                data={
                    'reminder_id': str(reminder.id),
                    'task': reminder.body,
                    'old_time': old_time,
                    'new_time': new_time_formatted,
                    'scheduled_time': new_time.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error editing reminder: {str(e)}", exc_info=True)
            return HandlerResponse(
                response_type='error',
                message="Sorry, I encountered an error while updating the reminder.",
                data={'error': str(e)}
            )
