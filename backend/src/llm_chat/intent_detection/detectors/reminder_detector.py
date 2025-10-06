"""
Reminder Intent Detector

Detects when users want to set, list, cancel, or edit reminders.
"""
import re
from typing import Dict, Any, List
from ..base_detector import BaseDetector, IntentResult
from notifications.utils import extract_reminder_details


class ReminderDetector(BaseDetector):
    """
    Detector for reminder-related intents.
    
    Detects patterns like:
    - Create: "Set a reminder to call mom tomorrow at 3pm"
    - List: "Show my reminders", "What reminders do I have?"
    - Cancel: "Cancel my reminder about groceries", "Delete all reminders"
    - Edit: "Change my reminder to 4pm", "Move my meeting reminder to tomorrow"
    """
    
    DETECTOR_NAME = "reminder"
    
    # Use a list of tuples to enforce order. Most specific patterns first.
    INTENT_PATTERNS = [
        ('list_reminders', r'^(show|list|display|what|view|see|do i have any)\s+(me\s+)?(my|all)?\s*reminders?'),
        ('cancel_reminder', r'^(cancel|delete|remove|clear)\s+(my|all|the)?\s*reminder'),
        ('edit_reminder', r'^(change|edit|update|modify|move|reschedule)\s+(my|the)?\s*reminder'),
        ('create_reminder', r'(set|create|make|add)?\s*(a|an)?\s*reminder|remind\s+me\s+(to|in|at|that)'),
    ]
    
    def _extract_parameters(self, content: str, intent_type: str, matches: List) -> Dict[str, Any]:
        """Extract parameters based on intent type"""
        content_lower = content.lower()
        
        if intent_type == 'create_reminder':
            task, scheduled_time = extract_reminder_details(content)
            
            return {
                'task': task,
                'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                'original_text': content
            }
        
        elif intent_type == 'list_reminders':
            # Check if user wants only upcoming or all
            filter_type = 'upcoming'  # default
            if any(word in content_lower for word in ['all', 'every']):
                filter_type = 'all'
            
            return {
                'filter_type': filter_type,
                'original_text': content
            }
        
        elif intent_type == 'cancel_reminder':
            # Extract what reminder to cancel
            cancel_all = any(word in content_lower for word in ['all', 'every', 'everything'])
            
            # Try to extract specific reminder description
            about_match = re.search(r'(?:about|for|to)\s+(.+?)(?:\s+reminder)?$', content_lower)
            description = about_match.group(1).strip() if about_match else None
            
            return {
                'cancel_all': cancel_all,
                'description': description,
                'original_text': content
            }
        
        elif intent_type == 'edit_reminder':
            # Extract what to change and new time
            about_match = re.search(r'(?:about|for|to)\s+(.+?)(?:\s+to|\s+at|\s+for|$)', content_lower)
            description = about_match.group(1).strip() if about_match else None
            
            # Try to extract new time
            new_time = extract_reminder_details(content)[1]
            
            return {
                'description': description,
                'new_time': new_time.isoformat() if new_time else None,
                'original_text': content
            }
        
        return super()._extract_parameters(content, intent_type, matches)
    
    def _calculate_confidence(self, content: str, matches: List) -> float:
        """
        Calculate confidence for reminder detection.
        Higher confidence if we can extract both task and time.
        """
        base_confidence = super()._calculate_confidence(content, matches)
        
        # For create_reminder, boost confidence if we can extract details
        # For create_reminder, boost confidence significantly if we can extract details
        if 'remind' in content.lower() or 'reminder' in content.lower():
            task, scheduled_time = extract_reminder_details(content)
            
            # If we have both a task and a time, we are very confident.
            if task and scheduled_time:
                return 0.95 # High confidence
            
            # If we have one or the other, it's still a strong signal.
            elif task or scheduled_time:
                return 0.85 # Medium-high confidence
        
        return base_confidence
