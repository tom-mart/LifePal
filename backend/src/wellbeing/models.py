from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField
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
    summary = EncryptedTextField(blank=True, null=True, help_text="AI-generated summary of the day")
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
    """Scheduled check-ins throughout the day"""
    CHECK_IN_TYPES = (
        ('morning', 'Morning Catch-up'),
        ('midday', 'Lunch Check-in'),
        ('evening', 'Evening Reflection'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='checkins')
    check_in_type = models.CharField(max_length=20, choices=CHECK_IN_TYPES)
    
    # Link to the conversation where this check-in happened
    conversation = models.ForeignKey(
        'llm_chat.Conversation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkins'
    )
    
    # Quick summary fields (encrypted)
    physical_feeling = EncryptedTextField(blank=True, help_text="How user feels physically")
    mental_feeling = EncryptedTextField(blank=True, help_text="How user feels mentally")
    notes = EncryptedTextField(blank=True, help_text="Additional notes from the check-in")
    
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Check-in')
        verbose_name_plural = _('Check-ins')
        ordering = ['completed_at']
        unique_together = ['daily_log', 'check_in_type']  # One of each type per day
    
    def __str__(self):
        return f"{self.get_check_in_type_display()} - {self.daily_log.date}"
    
    @classmethod
    def create_for_user(cls, user, check_in_type, conversation=None, **kwargs):
        """Create a check-in, ensuring DailyLog exists.
        
        Args:
            user: User instance
            check_in_type: One of 'morning', 'midday', 'evening'
            conversation: Optional Conversation instance
            **kwargs: Additional fields (physical_feeling, mental_feeling, notes)
            
        Returns:
            CheckIn instance
        """
        daily_log, _ = DailyLog.get_or_create_today(user)
        
        return cls.objects.create(
            daily_log=daily_log,
            check_in_type=check_in_type,
            conversation=conversation,
            **kwargs
        )


class Moment(models.Model):
    """User-created journal moments throughout the day"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='moments')
    
    # Core moment data (all encrypted)
    what_happened = EncryptedTextField(blank=True, null=True, help_text="Description of what happened")
    when_it_happened = EncryptedTextField(blank=True, null=True, help_text="When the moment occurred")
    how_it_felt = EncryptedTextField(blank=True, null=True, help_text="How it made the user feel")
    
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
