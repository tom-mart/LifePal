from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid


class Emotion(models.Model):
    """Simple emotion reference model (not encrypted - it's just a label)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, help_text="E.g., 'Happy', 'Anxious', 'Calm'")
    emoji = models.CharField(max_length=10, blank=True, help_text="Emoji representation")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Emotion')
        verbose_name_plural = _('Emotions')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.emoji} {self.name}" if self.emoji else self.name


class DailyLog(models.Model):
    """Represents a complete day's wellbeing data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField(help_text="The date this log represents")
    
    # LLM-generated summary at end of day
    summary = models.TextField(blank=True, null=True, help_text="AI-generated summary of the day")
    summary_generated_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    is_completed = models.BooleanField(default=False, help_text="Whether the day is complete and summarized")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Daily Log')
        verbose_name_plural = _('Daily Logs')
        ordering = ['-date']
        unique_together = ['user', 'date']  # One log per user per day
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    @classmethod
    def get_or_create_for_date(cls, user, date):
        """Get or create a DailyLog for a specific user and date.
        
        Args:
            user: User instance
            date: date object or datetime object
            
        Returns:
            tuple: (DailyLog instance, created boolean)
        """
        from datetime import datetime
        
        # If datetime is passed, extract date
        if isinstance(date, datetime):
            date = date.date()
        
        return cls.objects.get_or_create(
            user=user,
            date=date
        )
    
    @classmethod
    def get_or_create_today(cls, user):
        """Get or create today's DailyLog for a user.
        
        Args:
            user: User instance
            
        Returns:
            tuple: (DailyLog instance, created boolean)
        """
        from datetime import date
        return cls.get_or_create_for_date(user, date.today())


class DailyLogEmotion(models.Model):
    """Links emotions to daily logs with intensity"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='emotions')
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE)
    intensity = models.IntegerField(
        default=5,
        help_text="Intensity from 1-10"
    )
    
    class Meta:
        verbose_name = _('Daily Log Emotion')
        verbose_name_plural = _('Daily Log Emotions')
        unique_together = ['daily_log', 'emotion']  # Each emotion once per day
    
    def __str__(self):
        return f"{self.emotion.name} ({self.intensity}/10)"


class CheckIn(models.Model):
    """Scheduled and ad-hoc wellbeing check-ins throughout the day.
    
    This model serves as a metadata wrapper around conversations that happen
    in the context of wellbeing check-ins. It tracks:
    - The type and scheduling of the check-in
    - The conversation where it happened
    - LLM-extracted insights and summary
    - Actions taken during the conversation (e.g., reminders created)
    """
    CHECK_IN_TYPES = (
        ('morning', 'Morning Catch-up'),
        ('midday', 'Midday Check-in'),
        ('evening', 'Evening Reflection'),
        ('adhoc', 'Ad-hoc Check-in'),  # User-initiated or dynamic
    )
    
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),  # Notification sent, not started
        ('in_progress', 'In Progress'),  # User opened chat, conversation ongoing
        ('completed', 'Completed'),  # Conversation ended, insights extracted
        ('skipped', 'Skipped'),  # User dismissed notification
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='checkins')
    check_in_type = models.CharField(max_length=20, choices=CHECK_IN_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Scheduling information
    scheduled_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this check-in was scheduled for"
    )
    trigger_context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Context that triggered this check-in (e.g., stressful event mentioned in morning)"
    )
    
    # Link to the conversation where this check-in happened
    conversation = models.ForeignKey(
        'llm_chat.Conversation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkins'
    )
    
    # LLM-extracted insights (stored for quick access without parsing full conversation)
    insights = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured insights extracted by LLM (emotions, concerns, highlights, etc.)"
    )
    
    # Brief summary for display
    summary = models.TextField(
        blank=True,
        help_text="Brief LLM-generated summary of the check-in"
    )
    
    # Actions taken during the conversation
    actions_taken = models.JSONField(
        default=list,
        blank=True,
        help_text="List of actions LLM performed (e.g., [{action: 'create_reminder', time: '17:30', type: 'midday'}])"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True, help_text="When user opened the chat")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When conversation ended")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Check-in')
        verbose_name_plural = _('Check-ins')
        ordering = ['-created_at']
        # Removed unique_together to allow multiple adhoc check-ins per day
        indexes = [
            models.Index(fields=['daily_log', 'check_in_type']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_time']),
        ]
    
    def __str__(self):
        return f"{self.get_check_in_type_display()} - {self.daily_log.date} ({self.status})"
    
    @classmethod
    def create_scheduled(cls, user, check_in_type, scheduled_time, trigger_context=None):
        """Create a scheduled check-in.
        
        Args:
            user: User instance
            check_in_type: One of 'morning', 'midday', 'evening'
            scheduled_time: datetime when this check-in should trigger
            trigger_context: Optional dict with context (e.g., {'reason': 'stressful_event', 'event': '...'})
            
        Returns:
            CheckIn instance
        """
        from datetime import datetime
        
        # Get or create DailyLog for the scheduled date
        daily_log, _ = DailyLog.get_or_create_for_date(user, scheduled_time.date())
        
        return cls.objects.create(
            daily_log=daily_log,
            check_in_type=check_in_type,
            status='scheduled',
            scheduled_time=scheduled_time,
            trigger_context=trigger_context or {}
        )
    
    @classmethod
    def create_adhoc(cls, user, trigger_context=None):
        """Create an ad-hoc check-in (user or system initiated).
        
        Args:
            user: User instance
            trigger_context: Optional dict with context
            
        Returns:
            CheckIn instance
        """
        daily_log, _ = DailyLog.get_or_create_today(user)
        
        return cls.objects.create(
            daily_log=daily_log,
            check_in_type='adhoc',
            status='scheduled',
            trigger_context=trigger_context or {}
        )
    
    def start_conversation(self, conversation):
        """Mark check-in as started and link conversation.
        
        Args:
            conversation: Conversation instance
        """
        from django.utils import timezone
        
        self.conversation = conversation
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save(update_fields=['conversation', 'status', 'started_at', 'updated_at'])
    
    def complete(self, insights=None, summary=None, actions_taken=None):
        """Mark check-in as completed with extracted insights.
        
        Args:
            insights: Dict of structured insights
            summary: Brief text summary
            actions_taken: List of actions performed
        """
        from django.utils import timezone
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        if insights is not None:
            self.insights = insights
        if summary is not None:
            self.summary = summary
        if actions_taken is not None:
            self.actions_taken = actions_taken
        
        self.save(update_fields=['status', 'completed_at', 'insights', 'summary', 'actions_taken', 'updated_at'])
    
    def skip(self):
        """Mark check-in as skipped."""
        self.status = 'skipped'
        self.save(update_fields=['status', 'updated_at'])
    
    def add_action(self, action_type, **action_data):
        """Add an action taken during this check-in.
        
        Args:
            action_type: Type of action (e.g., 'create_reminder', 'create_task')
            **action_data: Additional data about the action
        """
        from django.utils import timezone
        
        action = {
            'action': action_type,
            'timestamp': timezone.now().isoformat(),
            **action_data
        }
        self.actions_taken.append(action)
        self.save(update_fields=['actions_taken', 'updated_at'])


class Moment(models.Model):
    """User-created journal moments throughout the day"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='moments')
    
    # Core moment data
    what_happened = models.TextField(blank=True, null=True, help_text="Description of what happened")
    when_it_happened = models.TextField(blank=True, null=True, help_text="When the moment occurred")
    how_it_felt = models.TextField(blank=True, null=True, help_text="How it made the user feel")
    
    # Optional image attachment
    image = models.ImageField(upload_to='moments/%Y/%m/%d/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Moment')
        verbose_name_plural = _('Moments')
        ordering = ['created_at']
    
    def __str__(self):
        preview = self.what_happened[:50] if self.what_happened else "Moment"
        return f"{preview}... - {self.moment_time}"
    
    @classmethod
    def create_for_user(cls, user, what_happened, moment_time=None, **kwargs):
        """Create a moment, ensuring DailyLog exists.
        
        Args:
            user: User instance
            what_happened: Description of what happened
            moment_time: When the moment occurred (defaults to now)
            **kwargs: Additional fields (how_it_felt, image)
            
        Returns:
            Moment instance
        """
        from datetime import datetime
        
        if moment_time is None:
            moment_time = datetime.now()
        
        # Get or create DailyLog for the moment's date
        daily_log, _ = DailyLog.get_or_create_for_date(user, moment_time)
        
        return cls.objects.create(
            daily_log=daily_log,
            what_happened=what_happened,
            moment_time=moment_time,
            **kwargs
        ) 
