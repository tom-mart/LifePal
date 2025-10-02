import logging
from typing import Optional
from django.contrib.auth.models import User
from users.models import AIIdentityProfile

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages system prompts for LLM interactions with user context."""
    
    # Default fallback prompt if no AIIdentityProfile exists
    DEFAULT_SYSTEM_PROMPT = """You are LifePal, a supportive life assistant and wellbeing companion.

Your core personality:
- Empathetic and understanding, never judgmental
- Encouraging and supportive while being realistic
- Knowledgeable about mental health, wellness, and personal development
- Respectful of boundaries and privacy
- Able to recognize when professional help might be needed

Your capabilities include:
- Helping with diary entries and emotional processing
- Managing todo lists and personal organization
- Providing wellness insights and gentle guidance
- Offering coping strategies and mindfulness techniques
- Supporting goal setting and habit formation

Always respond with warmth and understanding. Use markdown formatting for better readability."""

    def __init__(self, user: Optional[User] = None):
        """Initialize PromptManager with optional user context.
        
        Args:
            user: Django User instance. If provided, will load UserProfile, LLMContextProfile, and AIIdentityProfile.
        """
        self.user = user
        self.user_profile = None
        self.context_profile = None
        self.ai_identity = None
        
        if user:
            # Load UserProfile if exists
            if hasattr(user, 'userprofile'):
                self.user_profile = user.userprofile
            
            # Load LLMContextProfile if exists
            if hasattr(user, 'llmcontextprofile'):
                self.context_profile = user.llmcontextprofile
            
            # Load or create AIIdentityProfile
            self.ai_identity = AIIdentityProfile.get_or_create_for_user(user)
    
    def get_system_prompt(self, include_user_context: bool = True, include_dynamic_context: bool = True) -> str:
        """Generate system prompt with optional user context.
        
        Args:
            include_user_context: Whether to include user profile information in the prompt.
            include_dynamic_context: Whether to include dynamic context (date, time, etc.)
            
        Returns:
            Complete system prompt string.
        """
        # Use AI Identity Profile to generate base prompt, or fall back to default
        if self.ai_identity:
            prompt = self.ai_identity.generate_system_prompt()
        else:
            prompt = self.DEFAULT_SYSTEM_PROMPT
        
        # Add dynamic context (date, time, etc.)
        if include_dynamic_context:
            dynamic_context = self._build_dynamic_context()
            if dynamic_context:
                prompt += "\n\n=== CURRENT CONTEXT ===\n"
                prompt += dynamic_context
        
        # Add user profile context
        if include_user_context and (self.user_profile or self.context_profile):
            user_context = self._build_user_context()
            if user_context:
                prompt += "\n\n=== USER CONTEXT ===\n"
                prompt += user_context
        
        return prompt
    
    def _build_dynamic_context(self) -> str:
        """Build dynamic context (date, time, location, etc.).
        
        Returns:
            Formatted dynamic context string.
        """
        from django.utils import timezone as django_timezone
        from datetime import timezone as dt_timezone
        import zoneinfo
        
        context_parts = []
        
        # Get user's timezone if available
        tz = dt_timezone.utc
        if self.user and hasattr(self.user, 'usersettings'):
            try:
                tz = zoneinfo.ZoneInfo(self.user.usersettings.timezone)
            except:
                pass
        
        now = django_timezone.now().astimezone(tz)
        
        # Date and time information
        context_parts.append(f"Today's Date: {now.strftime('%A, %B %d, %Y')}")
        context_parts.append(f"Current Time: {now.strftime('%I:%M %p')}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _get_weather_info(self) -> Optional[str]:
        """Get weather information for user's location (optional feature).
        
        Returns:
            Weather description string or None
        """
        # Placeholder for weather API integration
        # You can integrate with OpenWeatherMap, WeatherAPI, etc.
        # Example:
        # if self.context_profile and self.context_profile.location:
        #     try:
        #         # Call weather API with location
        #         return "Sunny, 22°C"
        #     except:
        #         pass
        return None
    
    def _build_user_context(self) -> str:
        """Build user context string from UserProfile and LLMContextProfile.
        
        Returns:
            Formatted user context string, or empty string if no context available.
        """
        context_parts = []
        
        # Add UserProfile information
        if self.user_profile:
            user_info = self._format_user_profile()
            if user_info:
                context_parts.append(user_info)
        
        # Add LLMContextProfile information
        if self.context_profile:
            llm_context = self._format_llm_context_profile()
            if llm_context:
                context_parts.append(llm_context)
        
        return "\n\n".join(context_parts)
    
    def _format_user_profile(self) -> str:
        """Format UserProfile information.
        
        Returns:
            Formatted string with user profile data.
        """
        if not self.user_profile:
            return ""
        
        parts = []
        
        if self.user_profile.preferred_name:
            parts.append(f"Preferred Name: {self.user_profile.preferred_name}")
        
        if self.user_profile.bio:
            parts.append(f"Bio: {self.user_profile.bio}")
        
        if parts:
            return "User Profile:\n- " + "\n- ".join(parts)
        
        return ""
    
    def _format_llm_context_profile(self) -> str:
        """Format LLMContextProfile information into organized sections.
        
        Returns:
            Formatted string with LLM context profile data.
        """
        if not self.context_profile:
            return ""
        
        sections = []
        
        # Personal Information
        personal_info = self._build_section([
            ("Age", self.context_profile.age),
            ("Gender", self.context_profile.gender),
            ("Ethnic Background", self.context_profile.ethnic_background),
            ("Location", self.context_profile.location),
            ("Occupation", self.context_profile.occupation),
            ("Relationship Status", self.context_profile.relationship_status),
            ("Living Situation", self.context_profile.living_situation),
        ])
        if self.context_profile.has_children and self.context_profile.children_info:
            personal_info.append(f"Children: {self.context_profile.children_info}")
        
        if personal_info:
            sections.append("Personal Information:\n- " + "\n- ".join(personal_info))
        
        # Goals and Values
        goals = self._build_section([
            ("Personal Goals", self.context_profile.personal_goals),
            ("Professional Goals", self.context_profile.professional_goals),
            ("Core Values", self.context_profile.core_values),
            ("Interests", self.context_profile.interests),
        ])
        if goals:
            sections.append("Goals & Values:\n- " + "\n- ".join(goals))
        
        # Wellbeing Context
        wellbeing = self._build_section([
            ("Health Conditions", self.context_profile.health_conditions),
            ("Mental Health History", self.context_profile.mental_health_history),
            ("Current Challenges", self.context_profile.current_challenges),
            ("Stress Factors", self.context_profile.stress_factors),
            ("Coping Mechanisms", self.context_profile.coping_mechanisms),
        ])
        if wellbeing:
            sections.append("Wellbeing Context:\n- " + "\n- ".join(wellbeing))
        
        # Support System
        support = self._build_section([
            ("Support Network", self.context_profile.support_network),
            ("Professional Support", self.context_profile.professional_support),
        ])
        if support:
            sections.append("Support System:\n- " + "\n- ".join(support))
        
        # Daily Routine
        routine = self._build_section([
            ("Typical Schedule", self.context_profile.typical_schedule),
            ("Sleep Pattern", self.context_profile.sleep_pattern),
        ])
        if routine:
            sections.append("Daily Routine:\n- " + "\n- ".join(routine))
        
        # Communication Preferences
        communication = self._build_section([
            ("Communication Style", self.context_profile.communication_style),
            ("Learning Style", self.context_profile.learning_style),
            ("Response Preferences", self.context_profile.response_preferences),
        ])
        if communication:
            sections.append("Communication Preferences:\n- " + "\n- ".join(communication))
        
        # LifePal Usage
        lifepal = self._build_section([
            ("LifePal Goals", self.context_profile.lifepal_usage_goals),
            ("Topics of Interest", self.context_profile.topics_of_interest),
            ("Topics to Avoid", self.context_profile.topics_to_avoid),
        ])
        if lifepal:
            sections.append("LifePal Preferences:\n- " + "\n- ".join(lifepal))
        
        return "\n\n".join(sections)
    
    def _build_section(self, fields: list) -> list:
        """Build a section from a list of (label, value) tuples.
        
        Args:
            fields: List of tuples containing (label, value) pairs.
            
        Returns:
            List of formatted strings for non-empty fields.
        """
        result = []
        for label, value in fields:
            if value:
                result.append(f"{label}: {value}")
        return result
    
    def format_chat_messages(self, messages: list, include_user_context: bool = True) -> list:
        """Format messages for the LLM with the system prompt.
        
        Ensures the first message is always a system message with the appropriate prompt.
        If a system message already exists, it is preserved.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            include_user_context: Whether to include user context in system prompt.
            
        Returns:
            List of messages with system prompt prepended if needed.
        """
        if not messages or messages[0].get('role') != 'system':
            system_message = {
                'role': 'system',
                'content': self.get_system_prompt(include_user_context=include_user_context)
            }
            return [system_message] + messages
        return messages