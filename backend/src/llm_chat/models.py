from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import uuid
from encrypted_model_fields.fields import EncryptedTextField, EncryptedCharField


class Conversation(models.Model):
    """Model for storing chat conversations with encrypted title"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = EncryptedCharField(max_length=255, blank=True)  # Encrypt conversation titles
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
    
    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.user.email}"
    
    def get_messages(self):
        return self.messages.all().order_by('created_at')


class Message(models.Model):
    """Model for storing individual chat messages with encrypted content"""
    ROLE_CHOICES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = EncryptedTextField()  # Encrypt message content
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
