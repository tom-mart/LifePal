"""
Scheduler for creating daily check-ins.

This module provides utilities for scheduling check-ins.
You can integrate this with:
- Django-Q or Celery for background tasks
- Cron jobs
- Django management commands
"""

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time, timedelta
from typing import List

from .models import CheckIn, DailyLog


class CheckInScheduler:
    """Handles scheduling of check-ins"""
    
    # Default check-in times
    DEFAULT_MORNING_TIME = time(8, 0)  # 8:00 AM
    DEFAULT_EVENING_TIME = time(20, 0)  # 8:00 PM
    
    @classmethod
    def schedule_daily_checkins(cls, user: User, date=None) -> List[CheckIn]:
        """
        Schedule morning and evening check-ins for a user.
        
        Args:
            user: User instance
            date: Date to schedule for (defaults to today)
            
        Returns:
            List of created CheckIn instances
        """
        if date is None:
            date = timezone.now().date()
        
        # Get or create daily log
        daily_log, _ = DailyLog.get_or_create_for_date(user, date)
        
        created_checkins = []
        
        # Check if morning check-in already exists
        if not daily_log.checkins.filter(check_in_type='morning').exists():
            morning_time = datetime.combine(date, cls.DEFAULT_MORNING_TIME)
            morning_time = timezone.make_aware(morning_time)
            
            morning_checkin = CheckIn.create_scheduled(
                user=user,
                check_in_type='morning',
                scheduled_time=morning_time
            )
            created_checkins.append(morning_checkin)
        
        # Check if evening check-in already exists
        if not daily_log.checkins.filter(check_in_type='evening').exists():
            evening_time = datetime.combine(date, cls.DEFAULT_EVENING_TIME)
            evening_time = timezone.make_aware(evening_time)
            
            evening_checkin = CheckIn.create_scheduled(
                user=user,
                check_in_type='evening',
                scheduled_time=evening_time
            )
            created_checkins.append(evening_checkin)
        
        return created_checkins
    
    @classmethod
    def schedule_for_all_users(cls, date=None):
        """
        Schedule check-ins for all active users.
        
        This should be run daily (e.g., via cron at midnight).
        """
        if date is None:
            date = timezone.now().date()
        
        users = User.objects.filter(is_active=True)
        
        results = {
            'total_users': users.count(),
            'scheduled': 0,
            'errors': []
        }
        
        for user in users:
            try:
                checkins = cls.schedule_daily_checkins(user, date)
                results['scheduled'] += len(checkins)
            except Exception as e:
                results['errors'].append({
                    'user_id': user.id,
                    'error': str(e)
                })
        
        return results
    
    @classmethod
    def get_pending_notifications(cls) -> List[CheckIn]:
        """
        Get check-ins that should trigger notifications now.
        
        Returns check-ins that are:
        - Status: scheduled
        - Scheduled time is in the past or within the next 5 minutes
        
        This should be called frequently (e.g., every minute) by a background task.
        """
        now = timezone.now()
        notification_window = now + timedelta(minutes=5)
        
        pending = CheckIn.objects.filter(
            status='scheduled',
            scheduled_time__lte=notification_window
        ).select_related('daily_log__user')
        
        return list(pending)
    
    @classmethod
    def create_dynamic_midday_checkin(
        cls,
        user: User,
        scheduled_time: datetime,
        trigger_context: dict
    ) -> CheckIn:
        """
        Create a dynamic midday check-in (called by LLM during morning check-in).
        
        Args:
            user: User instance
            scheduled_time: When to trigger the check-in
            trigger_context: Context about why this was created
            
        Returns:
            CheckIn instance
        """
        return CheckIn.create_scheduled(
            user=user,
            check_in_type='midday',
            scheduled_time=scheduled_time,
            trigger_context=trigger_context
        )


# Django management command example
"""
Create a file: wellbeing/management/commands/schedule_checkins.py

from django.core.management.base import BaseCommand
from wellbeing.scheduler import CheckInScheduler


class Command(BaseCommand):
    help = 'Schedule daily check-ins for all users'

    def handle(self, *args, **options):
        results = CheckInScheduler.schedule_for_all_users()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Scheduled check-ins for {results['total_users']} users. "
                f"Created {results['scheduled']} check-ins."
            )
        )
        
        if results['errors']:
            self.stdout.write(
                self.style.ERROR(
                    f"Errors: {len(results['errors'])}"
                )
            )
"""

# Celery task example
"""
Create a file: wellbeing/tasks.py

from celery import shared_task
from .scheduler import CheckInScheduler
from .notifications import send_checkin_notification


@shared_task
def schedule_daily_checkins():
    '''Run daily at midnight to schedule check-ins'''
    results = CheckInScheduler.schedule_for_all_users()
    return results


@shared_task
def send_pending_notifications():
    '''Run every minute to send notifications for pending check-ins'''
    pending = CheckInScheduler.get_pending_notifications()
    
    for checkin in pending:
        send_checkin_notification(checkin)
    
    return len(pending)
"""

# Cron job example
"""
Add to your crontab:

# Schedule daily check-ins at midnight
0 0 * * * cd /path/to/project && python manage.py schedule_checkins

# Send notifications every minute
* * * * * cd /path/to/project && python manage.py send_checkin_notifications
"""
