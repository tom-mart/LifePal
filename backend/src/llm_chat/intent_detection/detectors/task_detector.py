"""
Task Intent Detector

Detects intents related to task/todo management.
"""

import re
import logging
from typing import Dict, Any, List
from ..base_detector import BaseDetector, IntentResult

logger = logging.getLogger(__name__)


class TaskDetector(BaseDetector):
    """Detector for task/todo-related intents"""
    
    DETECTOR_NAME = "task"
    
    INTENT_PATTERNS = {
        'task_create': r'(?i)(create|add|make|new).*?(task|todo|to-do|to do)',
        'task_list': r'(?i)(show|list|display|view|what|get|see|check).*?(task|todo|to-do|to do|list)',
        'task_complete': r'(?i)(complete|finish|done|mark.*done|mark.*complete).*?(task|todo)',
        'task_update': r'(?i)(update|change|modify|edit).*?(task|todo)',
        'task_delete': r'(?i)(delete|remove|cancel).*?(task|todo)',
    }
    
    def _extract_parameters(self, content: str, intent_type: str, matches: List) -> Dict[str, Any]:
        """Extract task-specific parameters"""
        parameters = {'content': content}
        
        if intent_type == 'task_create':
            parameters.update(self._extract_task_create_params(content))
        elif intent_type == 'task_list':
            parameters.update(self._extract_task_list_params(content))
        elif intent_type == 'task_complete':
            parameters.update(self._extract_task_complete_params(content))
        
        return parameters
    
    def _extract_task_create_params(self, content: str) -> Dict[str, Any]:
        """Extract parameters for task creation"""
        params = {}
        
        # Extract task title (remove common prefixes)
        title = re.sub(
            r'^(create|add|make|new)\s+(a\s+)?(task|todo|to-do|to do)[:,]?\s*',
            '',
            content,
            flags=re.IGNORECASE
        ).strip()
        params['title'] = title if title else content
        
        # Extract priority
        if re.search(r'\b(high|urgent|important)\b', content, re.IGNORECASE):
            params['priority'] = 3  # HIGH
        elif re.search(r'\blow\b', content, re.IGNORECASE):
            params['priority'] = 1  # LOW
        else:
            params['priority'] = 2  # MEDIUM
        
        # Extract due date keywords
        if re.search(r'\btoday\b', content, re.IGNORECASE):
            params['due_date_keyword'] = 'today'
        elif re.search(r'\btomorrow\b', content, re.IGNORECASE):
            params['due_date_keyword'] = 'tomorrow'
        elif re.search(r'\bthis week\b', content, re.IGNORECASE):
            params['due_date_keyword'] = 'this_week'
        elif re.search(r'\bnext week\b', content, re.IGNORECASE):
            params['due_date_keyword'] = 'next_week'
        
        return params
    
    def _extract_task_list_params(self, content: str) -> Dict[str, Any]:
        """Extract parameters for task listing"""
        params = {}
        
        # Extract filter keywords
        if re.search(r'\b(today|today\'s)\b', content, re.IGNORECASE):
            params['filter'] = 'today'
        elif re.search(r'\b(pending|incomplete|todo)\b', content, re.IGNORECASE):
            params['filter'] = 'pending'
        elif re.search(r'\b(completed|done|finished)\b', content, re.IGNORECASE):
            params['filter'] = 'completed'
        elif re.search(r'\b(urgent|high priority)\b', content, re.IGNORECASE):
            params['filter'] = 'high_priority'
        else:
            params['filter'] = 'all'
        
        return params
    
    def _extract_task_complete_params(self, content: str) -> Dict[str, Any]:
        """Extract parameters for task completion"""
        params = {}
        
        # Try to extract task identifier (title or number)
        # Remove the action phrase to get the task reference
        task_ref = re.sub(
            r'^(complete|finish|done|mark.*done|mark.*complete)\s+(task|todo|to-do|to do)?\s*[:,]?\s*',
            '',
            content,
            flags=re.IGNORECASE
        ).strip()
        
        if task_ref:
            params['task_reference'] = task_ref
        
        return params
    
    def check_context(self, content: str, context: Dict[str, Any]) -> IntentResult:
        """Check for task-related conversation context"""
        if not context:
            return None
        
        recent_messages = context.get('recent_messages', [])
        if len(recent_messages) < 2:
            return None
        
        # Look for task creation follow-ups
        for i, msg in enumerate(recent_messages[1:], 1):
            if msg.get('role') == 'assistant':
                content_lower = msg.get('content', '').lower()
                
                task_followup_patterns = [
                    'what would you like to call',
                    'what\'s the task',
                    'when is it due',
                    'what priority',
                    'any other details',
                    'task created',
                    'added.*task'
                ]
                
                if any(pattern in content_lower for pattern in task_followup_patterns):
                    # Check if there was a task intent in recent history
                    for j, prev_msg in enumerate(recent_messages[i+1:], i+1):
                        prev_intent = prev_msg.get('intent')
                        if prev_intent and prev_intent.get('intent_type', '').startswith('task_'):
                            logger.debug(f"Found task context from {j} messages ago")
                            return IntentResult(
                                intent_type='task_create',
                                confidence=0.9,
                                parameters={
                                    'content': content,
                                    'context': 'continuation',
                                    'original_intent_id': prev_intent.get('id')
                                }
                            )
        
        return None
