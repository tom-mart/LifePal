from django.db import models
import uuid
from datetime import date

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='userprofile')
    preferred_name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

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
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='usersettings')

    timezone = models.CharField(max_length=50, default='Europe/London')
    
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
    
    # Check-in schedule settings
    checkin_schedule = models.JSONField(
        default=dict,
        blank=True,
        help_text="Check-in schedule configuration with weekday/weekend times"
    )
    
    # Usage statistics
    last_active = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

    def __str__(self):
        # Try to get preferred_name from UserProfile, then fall back to email
        try:
            if hasattr(self.user, 'userprofile') and self.user.userprofile.preferred_name:
                return f"Settings for {self.user.userprofile.preferred_name}"
            return f"Settings for {self.user.email or 'Unknown User'}"
        except Exception:
            return f"Settings for {getattr(self.user, 'email', 'Unknown User')}"
    
    def get_checkin_schedule(self):
        """Get check-in schedule with defaults if not set."""
        default_schedule = {
            "morning": {
                "weekday": {
                    "time": "06:00",
                    "enabled": True
                },
                "weekend": {
                    "time": "09:00",
                    "enabled": True
                }
            },
            "evening": {
                "weekday": {
                    "time": "21:00",
                    "enabled": True
                },
                "weekend": {
                    "time": "21:00",
                    "enabled": True
                }
            }
        }
        
        if not self.checkin_schedule:
            return default_schedule
        
        # Merge with defaults to ensure all keys exist
        schedule = default_schedule.copy()
        schedule.update(self.checkin_schedule)
        return schedule
    
    def set_checkin_schedule(self, schedule):
        """Set check-in schedule."""
        self.checkin_schedule = schedule
        self.save(update_fields=['checkin_schedule', 'updated_at'])

class LLMContextProfile(models.Model):
    """User context information for LLM personalization.
    
    Note: Sensitive data should be protected at the infrastructure level
    (database encryption, access controls, HTTPS, etc.) rather than
    field-level encryption which doesn't prevent admin access.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='llm_context')

    # Demographics
    date_of_birth = models.DateField(blank=True, null=True, help_text="User's date of birth")
    gender = models.CharField(max_length=50, blank=True, null=True)
    ethnic_background = models.CharField(max_length=255, blank=True, null=True)
    
    # Life Context
    occupation = models.CharField(max_length=100, blank=True, null=True)
    relationship_status = models.CharField(max_length=100, blank=True, null=True)
    living_situation = models.CharField(max_length=100, blank=True, null=True,
                                      help_text="E.g., 'Lives alone', 'With family', 'Shared housing'")
    location = models.CharField(max_length=255, blank=True, null=True,
                                  help_text="User's location (city, country)")
    has_children = models.BooleanField(null=True, blank=True)
    children_info = models.TextField(blank=True, null=True,
                                   help_text="Brief info about children if applicable")
    
    # Wellbeing Context - Sensitive fields
    health_conditions = models.TextField(blank=True, null=True,
                                      help_text="Any health conditions the user wishes to disclose")
    mental_health_history = models.TextField(blank=True, null=True)
    current_challenges = models.TextField(blank=True, null=True,
                                       help_text="Current life challenges the user is facing")
    stress_factors = models.TextField(blank=True, null=True)
    coping_mechanisms = models.TextField(blank=True, null=True,
                                      help_text="What helps the user cope with stress")
    
    # Preferences
    communication_style = models.CharField(max_length=50, blank=True, null=True,
                                        help_text="E.g., 'Direct', 'Supportive', 'Analytical'")
    learning_style = models.CharField(max_length=50, blank=True, null=True)
    response_preferences = models.TextField(blank=True, null=True,
                                         help_text="How the user prefers responses (length, tone, etc.)")
    
    # Goals and Values
    personal_goals = models.TextField(blank=True, null=True)
    professional_goals = models.TextField(blank=True, null=True)
    core_values = models.TextField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    
    # Daily Routine
    typical_schedule = models.TextField(blank=True, null=True,
                                     help_text="Overview of user's typical daily schedule")
    sleep_pattern = models.CharField(max_length=100, blank=True, null=True)
    
    # Support System
    support_network = models.TextField(blank=True, null=True,
                                    help_text="Description of user's support network")
    professional_support = models.TextField(blank=True, null=True,
                                         help_text="Any professional support the user receives")
    
    # Preferences for LifePal
    lifepal_usage_goals = models.TextField(blank=True, null=True,
                                        help_text="What the user hopes to achieve using LifePal")
    topics_of_interest = models.TextField(blank=True, null=True)
    topics_to_avoid = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'LLM Context Profile'
        verbose_name_plural = 'LLM Context Profiles'
        indexes = [
            models.Index(fields=['user']),
        ]

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


class AIIdentityProfile(models.Model):
    """
    User's customizable AI identity and behavior preferences.
    Allows users to control system prompts and LLM settings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='ai_identity')
    
    # Model Selection
    preferred_model = models.CharField(
        max_length=100,
        default='llama3.2:latest',
        help_text="Ollama model to use (e.g., llama3.2:latest, mistral:latest)"
    )
    
    # AI Identity/Personality
    ai_name = models.CharField(
        max_length=100,
        default='LifePal',
        help_text="What the AI calls itself"
    )
    
    ai_role = models.CharField(
        max_length=200,
        default='supportive life assistant and wellbeing companion',
        help_text="The AI's primary role/purpose"
    )
    
    ai_personality_traits = models.TextField(
        default='empathetic, non-judgmental, supportive, encouraging, warm',
        help_text="Comma-separated personality traits"
    )
    
    # System Prompt Components
    core_instructions = models.TextField(
        default=(
            "You are a supportive AI companion focused on mental wellbeing and personal growth. "
            "Listen actively, ask thoughtful questions, and provide encouragement. "
            "Never judge, always validate feelings, and help users reflect on their experiences."
        ),
        help_text="Core behavioral instructions for the AI"
    )
    
    communication_style = models.TextField(
        default='conversational, warm, and empathetic',
        help_text="How the AI should communicate"
    )
    
    response_length_preference = models.CharField(
        max_length=20,
        choices=[
            ('concise', 'Concise (1-2 sentences)'),
            ('moderate', 'Moderate (2-4 sentences)'),
            ('detailed', 'Detailed (4+ sentences)'),
        ],
        default='moderate',
        help_text="Preferred response length"
    )
    
    # Conversation Guidelines
    topics_to_emphasize = models.TextField(
        blank=True,
        help_text="Topics the AI should focus on (e.g., 'gratitude, mindfulness, relationships')"
    )
    
    topics_to_avoid = models.TextField(
        blank=True,
        help_text="Topics the AI should avoid or handle carefully"
    )
    
    # Special Instructions
    custom_instructions = models.TextField(
        blank=True,
        help_text="Additional custom instructions or preferences"
    )
    
    # Behavior Preferences
    use_emojis = models.BooleanField(
        default=True,
        help_text="Whether AI should use emojis in responses"
    )
    
    formality_level = models.CharField(
        max_length=20,
        choices=[
            ('casual', 'Casual (friendly, informal)'),
            ('balanced', 'Balanced (professional yet warm)'),
            ('formal', 'Formal (professional, structured)'),
        ],
        default='balanced'
    )
    
    question_frequency = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low (mostly listen)'),
            ('moderate', 'Moderate (balanced)'),
            ('high', 'High (ask many questions)'),
        ],
        default='moderate',
        help_text="How often the AI asks follow-up questions"
    )
    
    # Context Awareness
    remember_preferences = models.BooleanField(
        default=True,
        help_text="Whether to reference past conversations and preferences"
    )
    
    proactive_suggestions = models.BooleanField(
        default=True,
        help_text="Whether AI can make proactive suggestions"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'AI Identity Profile'
        verbose_name_plural = 'AI Identity Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s AI Identity ({self.ai_name})"
    
    def generate_system_prompt(self):
        """
        Generate the complete system prompt based on user preferences.
        This will be used when making LLM API calls.
        """
        # Response length guidance
        length_guidance = {
            'concise': 'Keep responses brief and to the point (1-2 sentences).',
            'moderate': 'Provide thoughtful responses (2-4 sentences).',
            'detailed': 'Give comprehensive, detailed responses when appropriate.'
        }
        
        # Question frequency guidance
        question_guidance = {
            'low': 'Listen more than you ask. Only ask essential questions.',
            'moderate': 'Balance listening with thoughtful follow-up questions.',
            'high': 'Ask many clarifying and exploratory questions to deepen understanding.'
        }
        
        # Formality guidance
        formality_guidance = {
            'casual': 'Use casual, friendly language. Be informal and approachable.',
            'balanced': 'Be professional yet warm. Strike a balance between formal and casual.',
            'formal': 'Maintain professional, structured communication.'
        }
        
        prompt_parts = [
            f"You are {self.ai_name}, a {self.ai_role}.",
            f"Your personality traits: {self.ai_personality_traits}.",
            "",
            "Core Instructions:",
            self.core_instructions,
            "",
            f"Communication Style: {self.communication_style}",
            formality_guidance[self.formality_level],
            length_guidance[self.response_length_preference],
            question_guidance[self.question_frequency],
        ]
        
        if not self.use_emojis:
            prompt_parts.append("Do not use emojis in your responses.")
        
        if self.topics_to_emphasize:
            prompt_parts.append(f"\nFocus on these topics: {self.topics_to_emphasize}")
        
        if self.topics_to_avoid:
            prompt_parts.append(f"\nHandle these topics carefully or avoid: {self.topics_to_avoid}")
        
        if self.remember_preferences:
            prompt_parts.append("\nReference past conversations and user preferences when relevant.")
        
        if self.proactive_suggestions:
            prompt_parts.append("\nFeel free to make proactive suggestions for wellbeing and growth.")
        
        if self.custom_instructions:
            prompt_parts.append(f"\nAdditional Instructions:\n{self.custom_instructions}")
        
        return "\n".join(prompt_parts)
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create AI identity profile for a user with defaults."""
        profile, created = cls.objects.get_or_create(user=user)
        return profile