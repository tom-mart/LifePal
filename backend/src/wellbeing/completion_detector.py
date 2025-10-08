"""
Check-in completion detection and insights extraction.

This module detects when an LLM wants to complete a check-in and extracts
structured insights from the conversation.
"""

import re
import json
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class CheckInCompletionDetector:
    """Detects check-in completion signals and extracts insights"""
    
    # Markers that indicate the LLM wants to complete the check-in
    COMPLETION_MARKERS = [
        r'\[CHECKIN_COMPLETE\]',
        r'\[END_CHECKIN\]',
        r'\[COMPLETE\]',
        r'<checkin_complete>',
        r'<end_checkin>',
    ]
    
    # Markers for insights extraction
    INSIGHTS_MARKERS = [
        r'\[INSIGHTS\](.*?)\[/INSIGHTS\]',
        r'<insights>(.*?)</insights>',
        r'```insights\n(.*?)\n```',
        r'```json\n(.*?)\n```',
    ]
    
    @classmethod
    def detect_completion(cls, message_content: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if the message contains a completion signal.
        
        Args:
            message_content: The LLM's message content
            
        Returns:
            Tuple of (is_complete, cleaned_message)
            - is_complete: True if completion signal detected
            - cleaned_message: Message with completion markers removed
        """
        is_complete = False
        cleaned_message = message_content
        
        # Check for completion markers
        for marker in cls.COMPLETION_MARKERS:
            if re.search(marker, message_content, re.IGNORECASE | re.DOTALL):
                is_complete = True
                # Remove the marker from the message
                cleaned_message = re.sub(marker, '', cleaned_message, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace
        cleaned_message = cleaned_message.strip()
        
        return is_complete, cleaned_message
    
    @classmethod
    def extract_insights(cls, message_content: str, checkin_type: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured insights from the message.
        
        Args:
            message_content: The LLM's message content
            checkin_type: Type of check-in (morning, midday, evening, adhoc)
            
        Returns:
            Dictionary of extracted insights or None
        """
        insights = None
        
        # Try to find insights in marked sections
        for marker in cls.INSIGHTS_MARKERS:
            match = re.search(marker, message_content, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    insights_text = match.group(1).strip()
                    insights = json.loads(insights_text)
                    logger.info(f"Extracted insights from marked section: {insights}")
                    return insights
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse insights JSON: {insights_text}")
                    continue
        
        # If no marked insights found, try to extract from conversation patterns
        insights = cls._extract_insights_from_patterns(message_content, checkin_type)
        
        return insights
    
    @classmethod
    def _extract_insights_from_patterns(cls, content: str, checkin_type: str) -> Dict[str, Any]:
        """
        Extract insights using pattern matching when no structured data is provided.
        This is a fallback method.
        """
        insights = {}
        
        # Common patterns
        mood_patterns = [
            r"(?:feeling|mood|feel)(?:\s+is)?(?:\s+like)?:?\s*([a-z]+)",
            r"(?:you're|you are|they're)\s+feeling\s+([a-z]+)",
        ]
        
        for pattern in mood_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                insights['mood'] = match.group(1).lower()
                break
        
        # Energy level patterns
        energy_patterns = [
            r"energy(?:\s+level)?:?\s*(\d+)",
            r"(\d+)/10\s+energy",
        ]
        
        for pattern in energy_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                insights['energy_level'] = int(match.group(1))
                break
        
        # Stress level patterns
        stress_patterns = [
            r"stress(?:\s+level)?:?\s*(\d+)",
            r"(\d+)/10\s+stress",
        ]
        
        for pattern in stress_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                insights['stress_level'] = int(match.group(1))
                break
        
        return insights if insights else {}
    
    @classmethod
    def generate_summary(cls, conversation_messages: list, checkin_type: str) -> str:
        """
        Generate a brief summary of the check-in conversation.
        
        Args:
            conversation_messages: List of message dicts with 'role' and 'content'
            checkin_type: Type of check-in
            
        Returns:
            Brief summary string
        """
        # Filter to user and assistant messages only
        relevant_messages = [
            msg for msg in conversation_messages
            if msg.get('role') in ['user', 'assistant']
        ]
        
        if not relevant_messages:
            return "No conversation recorded."
        
        # Simple summary: first user message + key points
        user_messages = [msg['content'] for msg in relevant_messages if msg['role'] == 'user']
        
        if user_messages:
            first_message = user_messages[0][:100]
            return f"Check-in started with: {first_message}..."
        
        return f"{checkin_type.title()} check-in completed."
    
    @classmethod
    def build_completion_instruction(cls, checkin_type: str) -> str:
        """
        Build instructions for the LLM on how to complete a check-in.
        This should be added to the system prompt.
        
        Args:
            checkin_type: Type of check-in
            
        Returns:
            Instruction string
        """
        base_instruction = """
## Completing the Check-in

When you feel the conversation has reached a natural conclusion and you've gathered sufficient information:

1. Provide a brief summary or closing statement
2. Include the completion marker: [CHECKIN_COMPLETE]
3. Include structured insights in JSON format between [INSIGHTS] and [/INSIGHTS] tags

Example:
"Thank you for sharing. It sounds like you're feeling anxious about the presentation but excited about the weekend plans. Take care, and I'll check in with you later.

[INSIGHTS]
{
  "mood": "anxious",
  "energy_level": 6,
  "concerns": ["presentation at 6pm", "deadline tomorrow"],
  "highlights": ["weekend plans"],
  "physical_state": "tired",
  "sleep_quality": "poor"
}
[/INSIGHTS]

[CHECKIN_COMPLETE]"
"""
        
        # Add type-specific fields
        type_specific = {
            'morning': """
Expected insights fields:
- mood (string): Overall mood
- physical_state (string): How they're feeling physically
- sleep_quality (string): How they slept
- energy_level (number 1-10): Energy level
- concerns (array): List of concerns or worries
- upcoming_challenges (array): Challenges they mentioned
- positive_notes (array): Positive things mentioned
""",
            'midday': """
Expected insights fields:
- current_mood (string): Current mood
- stress_level (number 1-10): Current stress level
- needs_support (boolean): Whether they need additional support
- notes (string): Any important notes
""",
            'evening': """
Expected insights fields:
- overall_mood (string): Overall mood for the day
- day_rating (number 1-10): How they'd rate the day
- highlights (array): Positive moments from the day
- challenges (array): Challenges faced
- emotions (array): List of {emotion: string, intensity: number 1-10}
- tomorrow_concerns (array): Concerns about tomorrow
- sleep_readiness (string): How ready they are for sleep
""",
            'adhoc': """
Expected insights fields:
- mood (string): Current mood
- reason_for_checkin (string): Why they initiated the check-in
- key_topics (array): Main topics discussed
- action_items (array): Any actions to take
"""
        }
        
        return base_instruction + type_specific.get(checkin_type, type_specific['adhoc'])
