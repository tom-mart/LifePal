from django.db import models
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField, EncryptedDateField
import uuid
from datetime import date

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    preferred_name = EncryptedCharField(max_length=255, blank=True, null=True)
    bio = EncryptedTextField(blank=True, null=True)

    def __str__(self):
        # Try to get preferred_name from UserProfile, then fall back to email
        try:
            if hasattr(self.user, 'userprofile') and self.user.userprofile.preferred_name:
                return f"User Profile for {self.user.userprofile.preferred_name}"
            return f"User Profile for {self.user.email or 'Unknown User'}"
        except Exception:
            return f"User Profile for {getattr(self.user, 'email', 'Unknown User')}"

class UserSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)

    timezone = models.CharField(max_length=30, default='Europe/London')
    
    # UI preferences
    theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System Default')
    ])
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Privacy settings
    allow_relationship_requests = models.BooleanField(default=True)
    data_sharing_consent = models.BooleanField(default=False)
    
    # Usage statistics
    last_active = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        # Try to get preferred_name from UserProfile, then fall back to email
        try:
            if hasattr(self.user, 'userprofile') and self.user.userprofile.preferred_name:
                return f"Settings for {self.user.userprofile.preferred_name}"
            return f"Settings for {self.user.email or 'Unknown User'}"
        except Exception:
            return f"Settings for {getattr(self.user, 'email', 'Unknown User')}"

class LLMContextProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)

    date_of_birth = EncryptedDateField(blank=True, null=True, help_text="User's date of birth")
    gender = EncryptedCharField(max_length=50, blank=True, null=True)
    ethnic_background = EncryptedCharField(max_length=255, blank=True, null=True)
    
    occupation = EncryptedCharField(max_length=100, blank=True, null=True)
    relationship_status = EncryptedCharField(max_length=100, blank=True, null=True)
    living_situation = EncryptedCharField(max_length=100, blank=True, null=True,
                                      help_text="E.g., 'Lives alone', 'With family', 'Shared housing'")
    location = EncryptedCharField(max_length=255, blank=True, null=True,
                                  help_text="User's location (city, country)")
    has_children = models.BooleanField(null=True, blank=True)  # Not encrypted as it's a boolean
    children_info = EncryptedTextField(blank=True, null=True,
                                   help_text="Brief info about children if applicable")
    
    # Wellbeing Context - Highly sensitive fields (encrypted)
    health_conditions = EncryptedTextField(blank=True, null=True,
                                      help_text="Any health conditions the user wishes to disclose")
    mental_health_history = EncryptedTextField(blank=True, null=True)
    current_challenges = EncryptedTextField(blank=True, null=True,
                                       help_text="Current life challenges the user is facing")
    stress_factors = EncryptedTextField(blank=True, null=True)
    coping_mechanisms = EncryptedTextField(blank=True, null=True,
                                      help_text="What helps the user cope with stress")
    
    # Preferences - Less sensitive fields
    communication_style = models.CharField(max_length=50, blank=True, null=True,
                                        help_text="E.g., 'Direct', 'Supportive', 'Analytical'")
    learning_style = models.CharField(max_length=50, blank=True, null=True)
    response_preferences = models.TextField(blank=True, null=True,
                                         help_text="How the user prefers responses (length, tone, etc.)")
    
    # Goals and Values - Sensitive fields (encrypted)
    personal_goals = EncryptedTextField(blank=True, null=True)
    professional_goals = EncryptedTextField(blank=True, null=True)
    core_values = EncryptedTextField(blank=True, null=True)
    interests = EncryptedTextField(blank=True, null=True)
    
    # Daily Routine - Sensitive fields (encrypted)
    typical_schedule = EncryptedTextField(blank=True, null=True,
                                     help_text="Overview of user's typical daily schedule")
    sleep_pattern = EncryptedCharField(max_length=100, blank=True, null=True)
    
    # Support System - Sensitive fields (encrypted)
    support_network = EncryptedTextField(blank=True, null=True,
                                    help_text="Description of user's support network")
    professional_support = EncryptedTextField(blank=True, null=True,
                                         help_text="Any professional support the user receives")
    
    # Preferences for LifePal - Sensitive fields (encrypted)
    lifepal_usage_goals = EncryptedTextField(blank=True, null=True,
                                        help_text="What the user hopes to achieve using LifePal")
    topics_of_interest = EncryptedTextField(blank=True, null=True)
    topics_to_avoid = EncryptedTextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def age(self):
        """Calculate age from date of birth."""
        if not self.date_of_birth:
            return None
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        # Adjust if birthday hasn't occurred yet this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age

    def __str__(self):
    # Try to get preferred_name from UserProfile, then fall back to email
        try:
            if hasattr(self.user, 'userprofile') and self.user.userprofile.preferred_name:
                return f"LLM Context Profile for {self.user.userprofile.preferred_name}"
            return f"LLM Context Profile for {self.user.email or 'Unknown User'}"
        except Exception:
            return f"LLM Context Profile for {getattr(self.user, 'email', 'Unknown User')}"