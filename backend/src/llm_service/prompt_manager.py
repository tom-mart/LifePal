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
    
    def get_system_prompt(
        self, 
        include_user_context: bool = True, 
        include_dynamic_context: bool = True,
        include_tool_instructions: bool = True
    ) -> str:
        """Generate system prompt with optional user context and tool instructions.
        
        Args:
            include_user_context: Whether to include user profile information in the prompt.
            include_dynamic_context: Whether to include dynamic context (date, time, etc.)
            include_tool_instructions: Whether to include Tool_Retriever instructions (ReAct pattern)
            
        Returns:
            Complete system prompt string.
        """
        # Use AI Identity Profile to generate base prompt, or fall back to default
        if self.ai_identity:
            prompt = self.ai_identity.generate_system_prompt()
        else:
            prompt = self.DEFAULT_SYSTEM_PROMPT
        
        # Add Tool_Retriever instructions (ReAct pattern)
        if include_tool_instructions:
            tool_instructions = self._build_tool_instructions()
            if tool_instructions:
                prompt += "\n\n=== YOUR CAPABILITIES ===\n"
                prompt += tool_instructions
        
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
    
    def _get_category_list(self) -> str:
        """Get formatted list of tool categories from database."""
        try:
            from llm_tools.models import ToolCategory
            categories = ToolCategory.objects.filter(is_active=True).order_by('name')
            
            if not categories.exists():
                return "No categories available yet."
            
            category_lines = []
            for cat in categories:
                category_lines.append(f"- **{cat.name}**: {cat.description}")
            
            return "\n".join(category_lines)
        except Exception as e:
            logger.error(f"Error loading categories: {e}")
            return "- **general**: General purpose tools"
    
    def _build_tool_instructions(self) -> str:
        """Build Tool_Retriever instructions (ReAct pattern).
        
        Returns:
            Formatted tool instructions string.
        """
        instructions = f"""You have access to tools that allow you to perform actions and fetch data.

## ⚠️ CRITICAL: Silent Tool Usage

**DO NOT announce or mention that you are calling tools, retrieving tools, or using functions.**

Tool calls happen in the background. The user should NOT see:
- ❌ "I've retrieved the tool..."
- ❌ "I'm calling the start_checkin function..."
- ❌ "Let me use the tool_retriever..."
- ❌ "I'll now use this tool to..."

Instead, use tools silently and respond naturally:
- ✅ "Good morning! How are you feeling today?"
- ✅ "I see you have 3 tasks scheduled. Let's talk about your day."
- ✅ "Let's start your evening reflection."

## Tool Accuracy Rule

When listing or describing available tools (only when explicitly asked):
- ONLY mention tools that were explicitly returned by the tool_retriever function
- NEVER suggest, mention, or imply the existence of tools that were not in the tool_retriever response
- If tool_retriever returns only 1 tool, mention only that 1 tool
- If tool_retriever returns 0 tools, say "I currently don't have any tools available"
- Do NOT hallucinate or assume tools exist based on categories or previous knowledge

## Core Instructions

You MUST call the **tool_retriever** function FIRST in these situations:

1. **When asked about your capabilities or available tools**
   - User asks: "What can you do?", "What tools do you have?", "What features are available?"
   - Action: Call tool_retriever() to discover all available tools, then summarize them

2. **When the user's request requires action or data:**
   - Fetching live data (tasks, reminders, check-ins, wellbeing data, etc.)
   - Performing an action (creating tasks, starting check-ins, saving moments, etc.)
   - Interacting with external systems (scheduling, notifications, data storage)
   - Action: Call tool_retriever with appropriate category or query

3. **General conversation:**
   - If the user asks a general knowledge question or wants to have a conversation
   - You can answer directly without using tools

## Tool Usage Pattern (ReAct - Reason + Act)

1. **Reason**: Analyze the user's request and determine if it requires tool usage
2. **Act**: If tools are needed, call tool_retriever to discover available tools
3. **Execute**: Use the appropriate tools with extracted parameters
4. **Respond**: Generate a natural response incorporating tool results

## Tool Categories (for tool_retriever queries)

These are categories you can use when calling tool_retriever, NOT actual tools:
{self._get_category_list()}

Note: The actual available tools are determined by calling tool_retriever().

## Examples

**Example 1: User Asks About Capabilities**
User: "What tools do you have access to?"
→ Reason: User wants to know available tools
→ Act: Call tool_retriever() to get all tools
→ Respond: List ONLY the tools returned by tool_retriever. Do NOT mention or suggest tools that were not in the response. If only one tool is available, only mention that one tool.

**Example 2: Check-in Request**
User: "I want to start my morning check-in"
→ Reason: User wants to start a check-in (action needed)
→ Act: Call tool_retriever(intent_category='wellbeing')
→ Execute: Use start_checkin tool
→ Respond: Greet user with personalized opening based on context

**Example 3: Task Creation**
User: "Remind me to call mom at 5pm"
→ Reason: User wants to create a task (action needed)
→ Act: Call tool_retriever(intent_category='tasks')
→ Execute: Use create_task tool
→ Respond: Confirm task creation

**Example 4: General Conversation**
User: "How are you today?"
→ Reason: General conversation (no action needed)
→ Respond: Answer directly without tools

Remember: Always maintain your personality and communication style while using tools."""

        return instructions
    
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