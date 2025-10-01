"""
Detector Registry

Manages registration and discovery of intent detectors.
"""

import logging
from typing import List, Dict, Any, Optional
from .base_detector import BaseDetector, IntentResult

logger = logging.getLogger(__name__)


class DetectorRegistry:
    """Registry for managing intent detectors"""
    
    def __init__(self):
        self._detectors: List[BaseDetector] = []
        self._intent_map: Dict[str, BaseDetector] = {}
    
    def register(self, detector: BaseDetector):
        """
        Register a detector.
        
        Args:
            detector: Detector instance to register
        """
        if detector not in self._detectors:
            self._detectors.append(detector)
            
            # Map intent types to detectors
            for intent_type in detector.get_supported_intents():
                self._intent_map[intent_type] = detector
            
            logger.info(f"Registered detector: {detector.DETECTOR_NAME} with intents: {detector.get_supported_intents()}")
    
    def detect_intent(self, content: str, context: Dict[str, Any] = None) -> Optional[IntentResult]:
        """
        Detect intent from content using all registered detectors.
        
        Args:
            content: Message content to analyze
            context: Optional conversation context
            
        Returns:
            Best matching IntentResult or None
        """
        all_results = []
        
        # First check context with all detectors
        if context:
            for detector in self._detectors:
                context_result = detector.check_context(content, context)
                if context_result and context_result.confidence > 0.8:
                    # High confidence context match, return immediately
                    logger.debug(f"High confidence context match: {context_result.intent_type}")
                    return context_result
                elif context_result:
                    all_results.append(context_result)
        
        # Run pattern-based detection on all detectors
        for detector in self._detectors:
            results = detector.detect(content, context)
            all_results.extend(results)
        
        # Return best result (highest confidence)
        if all_results:
            all_results.sort(key=lambda x: x.confidence, reverse=True)
            best_result = all_results[0]
            logger.debug(f"Best intent match: {best_result.intent_type} (confidence: {best_result.confidence})")
            return best_result
        
        # No intent detected, return chat intent
        logger.debug("No specific intent detected, defaulting to chat")
        return IntentResult(
            intent_type='chat',
            confidence=0.5,
            parameters={'content': content}
        )
    
    def get_detector_for_intent(self, intent_type: str) -> Optional[BaseDetector]:
        """Get the detector that handles a specific intent type"""
        return self._intent_map.get(intent_type)
    
    def get_all_supported_intents(self) -> List[str]:
        """Get list of all supported intent types across all detectors"""
        return list(self._intent_map.keys())
    
    def auto_discover(self):
        """
        Auto-discover and register all available detectors.
        
        This method imports all detector modules and registers them automatically.
        """
        try:
            from .detectors import TaskDetector
            self.register(TaskDetector())
            logger.info("Auto-discovery complete")
        except ImportError as e:
            logger.warning(f"Could not import some detectors during auto-discovery: {e}")


# Global registry instance
_registry = None


def get_detector_registry() -> DetectorRegistry:
    """Get the global detector registry instance"""
    global _registry
    if _registry is None:
        _registry = DetectorRegistry()
        _registry.auto_discover()
    return _registry
