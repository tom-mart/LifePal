"""
Task Intent Handler

Handles all task/todo-related intents by interacting with the todo app.
"""

import logging
from typing import Dict, Any, Optional
from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from ..base_handler import BaseHandler, HandlerResponse
from todo.models import Task

logger = logging.getLogger(__name__)


class TaskHandler(BaseHandler):
    """Handler for task/todo-related intents"""
    
    HANDLER_NAME = "task"
    SUPPORTED_INTENTS = [
        'task_create',
        'task_list',
        'task_complete',
        'task_update',
        'task_delete',
    ]
    
    @transaction.atomic
    def handle(self, intent_type: str, parameters: Dict[str, Any], user, message) -> Optional[HandlerResponse]:
        """Handle task-related intents"""
        
        if intent_type == 'task_create':
            return self._handle_task_create(parameters, user)
        elif intent_type == 'task_list':
            return self._handle_task_list(parameters, user)
        elif intent_type == 'task_complete':
            return self._handle_task_complete(parameters, user)
        elif intent_type == 'task_update':
            return self._handle_task_update(parameters, user)
        elif intent_type == 'task_delete':
            return self._handle_task_delete(parameters, user)
        
        return None
    
    def _handle_task_create(self, parameters: Dict[str, Any], user) -> HandlerResponse:
        """Handle task creation"""
        try:
            title = parameters.get('title', parameters.get('content', ''))
            priority = parameters.get('priority', 2)
            due_date_keyword = parameters.get('due_date_keyword')
            
            # Validate title
            if not title or len(title.strip()) < 3:
                return HandlerResponse(
                    response_type='task_create_clarification',
                    message="I'd be happy to create a task for you! What would you like to call it?"
                )
            
            # Calculate due date
            due_date = None
            if due_date_keyword:
                due_date = self._parse_due_date_keyword(due_date_keyword)
            
            # Create task
            task = Task.objects.create(
                user=user,
                title=title,
                priority=priority,
                due_date=due_date,
                status=Task.Status.TODO
            )
            
            # Format response
            priority_text = {1: 'low', 2: 'medium', 3: 'high', 4: 'urgent'}.get(priority, 'medium')
            due_text = f" due {due_date.strftime('%B %d')}" if due_date else ""
            
            message = (
                f"✅ I've created a new task for you:\n\n"
                f"**{task.title}**\n"
                f"Priority: {priority_text.capitalize()}{due_text}\n\n"
                f"You can view and manage your tasks anytime!"
            )
            
            return HandlerResponse(
                response_type='task_created',
                message=message,
                data={
                    'task_id': task.id,
                    'task_title': task.title,
                    'task_priority': priority,
                    'task_due_date': due_date.isoformat() if due_date else None,
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return HandlerResponse(
                response_type='error',
                message="I couldn't create that task right now. Please try again later."
            )
    
    def _handle_task_list(self, parameters: Dict[str, Any], user) -> HandlerResponse:
        """Handle task listing"""
        try:
            filter_type = parameters.get('filter', 'all')
            
            # Build query
            tasks = Task.objects.filter(user=user)
            
            if filter_type == 'today':
                today = timezone.now().date()
                tasks = tasks.filter(
                    due_date__date=today,
                    status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
                )
            elif filter_type == 'pending':
                tasks = tasks.filter(status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS])
            elif filter_type == 'completed':
                tasks = tasks.filter(status=Task.Status.COMPLETED)
            elif filter_type == 'high_priority':
                tasks = tasks.filter(
                    priority__gte=3,
                    status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
                )
            else:
                # Default: show pending tasks
                tasks = tasks.filter(status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS])
            
            # Order by priority and due date
            tasks = tasks.order_by('-priority', 'due_date')[:10]
            
            if not tasks.exists():
                filter_text = {
                    'today': "for today",
                    'pending': "pending",
                    'completed': "completed",
                    'high_priority': "high priority"
                }.get(filter_type, "")
                
                return HandlerResponse(
                    response_type='task_list_empty',
                    message=f"You don't have any {filter_text} tasks right now. Great job staying on top of things! 🎉"
                )
            
            # Format task list
            task_list = []
            for task in tasks:
                priority_emoji = {1: '🔵', 2: '🟡', 3: '🔴', 4: '🚨'}.get(task.priority, '⚪')
                due_text = f" (due {task.due_date.strftime('%b %d')})" if task.due_date else ""
                task_list.append(f"{priority_emoji} **{task.title}**{due_text}")
            
            filter_text = {
                'today': "for today",
                'pending': "pending",
                'completed': "completed",
                'high_priority': "high priority"
            }.get(filter_type, "")
            
            message = f"Here are your {filter_text} tasks:\n\n" + "\n".join(task_list)
            
            return HandlerResponse(
                response_type='task_list',
                message=message,
                data={
                    'task_count': len(task_list),
                    'tasks': [
                        {'id': t.id, 'title': t.title, 'priority': t.priority}
                        for t in tasks
                    ]
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return HandlerResponse(
                response_type='error',
                message="I couldn't retrieve your tasks right now. Please try again later."
            )
    
    def _handle_task_complete(self, parameters: Dict[str, Any], user) -> HandlerResponse:
        """Handle task completion"""
        try:
            content = parameters.get('content', '').lower()
            task_reference = parameters.get('task_reference', '')
            
            # Find matching task
            pending_tasks = Task.objects.filter(
                user=user,
                status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
            ).order_by('-priority', 'due_date')
            
            matched_task = None
            search_text = task_reference or content
            
            for task in pending_tasks:
                if task.title.lower() in search_text or search_text in task.title.lower():
                    matched_task = task
                    break
            
            if matched_task:
                matched_task.status = Task.Status.COMPLETED
                matched_task.completed_at = timezone.now()
                matched_task.save()
                
                return HandlerResponse(
                    response_type='task_completed',
                    message=f"🎉 Great job! I've marked **{matched_task.title}** as complete!",
                    data={
                        'task_id': matched_task.id,
                        'task_title': matched_task.title
                    }
                )
            else:
                # Couldn't identify specific task
                if pending_tasks.count() == 0:
                    return HandlerResponse(
                        response_type='no_tasks',
                        message="You don't have any pending tasks to complete. You're all caught up! 🌟"
                    )
                
                task_list = "\n".join([f"• {t.title}" for t in pending_tasks[:5]])
                return HandlerResponse(
                    response_type='task_complete_clarification',
                    message=f"Which task would you like to mark as complete?\n\n{task_list}"
                )
            
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return HandlerResponse(
                response_type='error',
                message="I couldn't complete that task right now. Please try again later."
            )
    
    def _handle_task_update(self, parameters: Dict[str, Any], user) -> HandlerResponse:
        """Handle task update"""
        return HandlerResponse(
            response_type='task_update_info',
            message="To update a task, you can tell me which task you'd like to change and what you'd like to update (title, priority, or due date)."
        )
    
    def _handle_task_delete(self, parameters: Dict[str, Any], user) -> HandlerResponse:
        """Handle task deletion"""
        return HandlerResponse(
            response_type='task_delete_info',
            message="To delete a task, please tell me which task you'd like to remove."
        )
    
    def _parse_due_date_keyword(self, keyword: str) -> Optional[timezone.datetime]:
        """Parse due date keyword into datetime"""
        now = timezone.now()
        
        if keyword == 'today':
            return now.replace(hour=23, minute=59, second=59)
        elif keyword == 'tomorrow':
            return (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
        elif keyword == 'this_week':
            days_until_sunday = (6 - now.weekday()) % 7
            return (now + timedelta(days=days_until_sunday)).replace(hour=23, minute=59, second=59)
        elif keyword == 'next_week':
            days_until_next_sunday = ((6 - now.weekday()) % 7) + 7
            return (now + timedelta(days=days_until_next_sunday)).replace(hour=23, minute=59, second=59)
        
        return None
