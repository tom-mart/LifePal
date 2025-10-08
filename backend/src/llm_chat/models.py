from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid


class Conversation(models.Model):
    """Model for storing chat conversations"""
    CONVERSATION_TYPES = (
        ('general', 'General Chat'),
        ('checkin', 'Check-in'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True)
    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPES,
        default='general',
        help_text="Type of conversation - check-ins are excluded from general chat history"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        indexes = [
            models.Index(fields=['user', 'conversation_type']),
            models.Index(fields=['conversation_type', '-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.user.email}"
    
    def get_messages(self):
        return self.messages.all().order_by('created_at')
    
    @classmethod
    def get_general_chats(cls, user):
        """Get only general chat conversations, excluding check-ins."""
        return cls.objects.filter(user=user, conversation_type='general', is_active=True)
    
    @classmethod
    def get_checkin_conversations(cls, user):
        """Get only check-in conversations."""
        return cls.objects.filter(user=user, conversation_type='checkin', is_active=True)


class Message(models.Model):
    """Model for storing individual chat messages"""
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
        ('trigger', 'Trigger'),  # Hidden message that triggers conversation but not displayed
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class Intent(models.Model):
    """Model for storing detected intents from user messages"""
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='intent')
    intent_type = models.CharField(max_length=50)
    confidence = models.FloatField(default=0.0)
    parameters = models.JSONField(default=dict, blank=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Intent')
        verbose_name_plural = _('Intents')
    
    def __str__(self):
        return f"{self.intent_type} ({self.confidence})"
