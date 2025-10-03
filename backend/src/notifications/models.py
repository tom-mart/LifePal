from django.db import models
import uuid


class PushSubscription(models.Model):
    """Store push notification subscriptions for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='push_subscriptions')
    
    # Push subscription details
    endpoint = models.TextField(unique=True)
    p256dh_key = models.TextField(help_text="P256DH public key")
    auth_key = models.TextField(help_text="Auth secret")
    
    # Metadata
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Push Subscription'
        verbose_name_plural = 'Push Subscriptions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"Push subscription for {self.user.username} ({self.endpoint[:50]}...)"
