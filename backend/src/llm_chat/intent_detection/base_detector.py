"""
Base Detector Class

Provides core functionality for intent detection that all specific detectors inherit from.
"""

import re
import logging
from typing import Tuple, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result of intent detection"""
    intent_type: str
    confidence: float
    parameters: Dict[str, Any]
    
    def __post_init__(self):
        """Validate confidence is between 0 and 1"""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


class BaseDetector:
    """
    Base class for intent detectors.
    
    Each app should create its own detector by inheriting from this class
    and implementing the required methods.
    """
    
    # Override in subclasses
    # Can be either a dict or list of tuples for ordered patterns
    INTENT_PATTERNS = {}
    DETECTOR_NAME: str = "base"
    
    def detect(self, content: str, context: Dict[str, Any] = None) -> List[IntentResult]:
        """
        Detect intents from message content.
        
        Args:
            content: Message content to analyze
            context: Optional conversation context
            
        Returns:
            List of IntentResult objects, ordered by confidence (highest first)
        """
        results = []
        
        # Rule-based detection - handle both dict and list formats
        patterns_iter = self.INTENT_PATTERNS.items() if isinstance(self.INTENT_PATTERNS, dict) else self.INTENT_PATTERNS
        
        for intent_type, pattern in patterns_iter:
            matches = re.findall(pattern, content.lower(), re.IGNORECASE)
            if matches:
                confidence = self._calculate_confidence(content, matches)
                parameters = self._extract_parameters(content, intent_type, matches)
                
                results.append(IntentResult(
                    intent_type=intent_type,
                    confidence=confidence,
                    parameters=parameters
                ))
        
        # Sort by confidence (highest first)
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        return results
    
    def _calculate_confidence(self, content: str, matches: List) -> float:
        """
        Calculate confidence score based on matches.
        
        Args:
            content: Original message content
            matches: Regex matches found
            
        Returns:
            Confidence score between 0.5 and 0.95
        """
        if not matches:
            return 0.0
        
        # Calculate based on match length relative to content
        match_length = sum(len(m) if isinstance(m, str) else len(m[0]) for m in matches)
        confidence = min(0.5 + (match_length / len(content)) * 0.5, 0.95)
        
        return confidence
    
    def _extract_parameters(self, content: str, intent_type: str, matches: List) -> Dict[str, Any]:
        """
        Extract parameters from content based on intent type.
        Override in subclasses for app-specific parameter extraction.
        
        Args:
            content: Message content
            intent_type: Detected intent type
            matches: Regex matches
            
        Returns:
            Dictionary of extracted parameters
        """
        return {'content': content, 'matches': matches}
    
    def check_context(self, content: str, context: Dict[str, Any]) -> IntentResult:
        """
        Check conversation context for intent continuation.
        Override in subclasses for app-specific context checking.
        
        Args:
            content: Current message content
            context: Conversation context (recent messages, previous intents, etc.)
            
        Returns:
            IntentResult or None if no context match
        """
        return None
    
    def get_supported_intents(self) -> List[str]:
        """Get list of intent types this detector supports"""
        if isinstance(self.INTENT_PATTERNS, dict):
            return list(self.INTENT_PATTERNS.keys())
        elif isinstance(self.INTENT_PATTERNS, list):
            # List of tuples: [(intent_type, pattern), ...]
            return [intent_type for intent_type, _ in self.INTENT_PATTERNS]
        return []
