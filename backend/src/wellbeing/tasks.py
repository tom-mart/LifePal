"""
Celery tasks for wellbeing check-ins.
"""
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, time, timedelta
import logging
import pytz

from .models import CheckIn, DailyLog
from .scheduler import CheckInScheduler
from notifications.models import ScheduledNotification

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def schedule_daily_checkins_for_all_users():
    """
    Schedule check-ins for all active users based on their preferences.
    This should run daily at midnight (00:00) in each user's timezone.
    """
    users = User.objects.filter(is_active=True).select_related('usersettings')
    
    scheduled_count = 0
    error_count = 0
    
    for user in users:
        try:
            # Get user settings
            if not hasattr(user, 'usersettings'):
                logger.warning(f"User {user.username} has no settings, skipping")
                continue
            
            settings = user.usersettings
            schedule = settings.get_checkin_schedule()
            user_tz = pytz.timezone(settings.timezone)
            
            # Get current date in user's timezone
            now_user_tz = timezone.now().astimezone(user_tz)
            today = now_user_tz.date()
            
            # Determine if today is weekend
            is_weekend = today.weekday() >= 5  # 5=Saturday, 6=Sunday
            day_type = 'weekend' if is_weekend else 'weekday'
            
            # Get or create daily log
            daily_log, _ = DailyLog.get_or_create_for_date(user, today)
            
            # Schedule morning check-in
            morning_config = schedule.get('morning', {}).get(day_type, {})
            if morning_config.get('enabled', True):
                if not daily_log.checkins.filter(check_in_type='morning').exists():
                    morning_time_str = morning_config.get('time', '06:00')
                    morning_hour, morning_minute = map(int, morning_time_str.split(':'))
                    
                    # Create datetime in user's timezone
                    morning_dt = user_tz.localize(
                        datetime.combine(today, time(morning_hour, morning_minute))
                    )
                    
                    # Convert to UTC for storage
                    morning_dt_utc = morning_dt.astimezone(pytz.UTC)
                    
                    checkin = CheckIn.create_scheduled(
                        user=user,
                        check_in_type='morning',
                        scheduled_time=morning_dt_utc
                    )
                    scheduled_count += 1
                    logger.info(f"Scheduled morning check-in for {user.username} at {morning_dt_utc}")
            
            # Schedule evening check-in
            evening_config = schedule.get('evening', {}).get(day_type, {})
            if evening_config.get('enabled', True):
                if not daily_log.checkins.filter(check_in_type='evening').exists():
                    evening_time_str = evening_config.get('time', '21:00')
                    evening_hour, evening_minute = map(int, evening_time_str.split(':'))
                    
                    # Create datetime in user's timezone
                    evening_dt = user_tz.localize(
                        datetime.combine(today, time(evening_hour, evening_minute))
                    )
                    
                    # Convert to UTC for storage
                    evening_dt_utc = evening_dt.astimezone(pytz.UTC)
                    
                    checkin = CheckIn.create_scheduled(
                        user=user,
                        check_in_type='evening',
                        scheduled_time=evening_dt_utc
                    )
                    scheduled_count += 1
                    logger.info(f"Scheduled evening check-in for {user.username} at {evening_dt_utc}")
                    
        except Exception as e:
            error_count += 1
            logger.error(f"Error scheduling check-ins for user {user.username}: {str(e)}", exc_info=True)
    
    logger.info(f"Daily check-in scheduling complete: {scheduled_count} scheduled, {error_count} errors")
    return {"scheduled": scheduled_count, "errors": error_count}


@shared_task
def send_pending_checkin_notifications():
    """
    Send notifications for pending check-ins that are due.
    This should run every minute.
    """
    now = timezone.now()
    notification_window = now + timedelta(minutes=5)
    
    # Get pending check-ins that are due
    pending_checkins = CheckIn.objects.filter(
        status='scheduled',
        scheduled_time__lte=notification_window
    ).select_related('daily_log__user')
    
    sent_count = 0
    error_count = 0
    
    for checkin in pending_checkins:
        try:
            user = checkin.daily_log.user
            
            # Check if user has checkin notifications enabled
            if hasattr(user, 'usersettings') and not user.usersettings.checkin_notifications:
                logger.debug(f"User {user.username} has checkin notifications disabled, skipping notification for check-in {checkin.id}")
                continue
            
            # Check if user has active push subscriptions
            has_active_subscription = user.push_subscriptions.filter(is_active=True).exists()
            if not has_active_subscription:
                logger.debug(f"User {user.username} has no active push subscriptions, skipping notification for check-in {checkin.id}")
                continue
            
            # Check if notification already exists for this check-in
            existing_notification = ScheduledNotification.objects.filter(
                metadata__checkin_id=str(checkin.id)
            ).first()
            
            if existing_notification:
                logger.debug(f"Notification already exists for check-in {checkin.id}, skipping")
                continue
            
            # Determine notification content based on check-in type
            notification_config = {
                'morning': {
                    'title': 'Good morning! Time for your morning catch-up ☀️',
                    'body': 'Let\'s start the day with a quick check-in',
                    'icon': '/icons/morning.png',
                },
                'midday': {
                    'title': 'Midday check-in 🌤️',
                    'body': checkin.trigger_context.get('reason', 'How are you doing?'),
                    'icon': '/icons/midday.png',
                },
                'evening': {
                    'title': 'Evening reflection time 🌙',
                    'body': 'Let\'s reflect on your day together',
                    'icon': '/icons/evening.png',
                },
                'adhoc': {
                    'title': 'Check-in reminder',
                    'body': 'Time for a wellbeing check-in',
                    'icon': '/icons/checkin.png',
                }
            }
            
            config = notification_config.get(checkin.check_in_type, notification_config['adhoc'])
            
            # Create scheduled notification
            notification = ScheduledNotification.objects.create(
                user=user,
                notification_type='daily_checkin',
                title=config['title'],
                body=config['body'],
                icon=config.get('icon', '/icons/checkin.png'),
                url=f'/chat?checkin_id={checkin.id}',
                tag=f'checkin-{checkin.id}',
                scheduled_time=checkin.scheduled_time,
                snooze_duration_minutes=30,
                max_snooze_count=3,
                metadata={
                    'checkin_id': str(checkin.id),
                    'checkin_type': checkin.check_in_type,
                    'trigger_context': checkin.trigger_context
                }
            )
            
            sent_count += 1
            logger.info(f"Created notification for check-in {checkin.id} ({checkin.check_in_type}) for user {user.username}")
            
        except Exception as e:
            error_count += 1
            logger.error(f"Error creating notification for check-in {checkin.id}: {str(e)}", exc_info=True)
    
    logger.info(f"Check-in notifications: {sent_count} created, {error_count} errors")
    return {"sent": sent_count, "errors": error_count}


@shared_task
def generate_daily_summary(user_id, date_str=None):
    """
    Generate end-of-day summary from completed check-ins.
    
    Args:
        user_id: User ID
        date_str: Date string in YYYY-MM-DD format (defaults to today)
    """
    try:
        user = User.objects.get(id=user_id)
        
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date_obj = timezone.now().date()
        
        daily_log, _ = DailyLog.get_or_create_for_date(user, date_obj)
        
        # Get all completed check-ins for the day
        completed_checkins = daily_log.checkins.filter(status='completed')
        
        if not completed_checkins.exists():
            logger.info(f"No completed check-ins for {user.username} on {date_obj}")
            return None
        
        # Aggregate insights from all check-ins
        all_insights = []
        all_summaries = []
        
        for checkin in completed_checkins:
            if checkin.insights:
                all_insights.append({
                    'type': checkin.check_in_type,
                    'insights': checkin.insights
                })
            if checkin.summary:
                all_summaries.append(f"**{checkin.get_check_in_type_display()}**: {checkin.summary}")
        
        # Create a combined summary
        combined_summary = "\n\n".join(all_summaries)
        
        # Update daily log
        daily_log.summary = combined_summary
        daily_log.summary_generated_at = timezone.now()
        daily_log.is_completed = True
        daily_log.save()
        
        logger.info(f"Generated daily summary for {user.username} on {date_obj}")
        return str(daily_log.id)
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error generating daily summary: {str(e)}", exc_info=True)
        return None
