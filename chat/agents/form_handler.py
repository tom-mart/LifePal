"""
Generic form handler for collecting structured data through conversational flows.
Handles state management, validation, and completion callbacks.
"""
import os
from typing import Dict, Any, Optional, Tuple, List, Callable
from agents.services.llm_service import LLMService


class FormState:
    """Manages form flow state"""
    
    def __init__(self, state_dict: Optional[Dict[str, Any]] = None, questions: List[Dict] = None):
        """Initialize from saved state or start fresh"""
        if state_dict:
            self.answers = state_dict.get('answers', {})
            self.current_step = state_dict.get('current_step', 0)
        else:
            self.answers = {}
            self.current_step = 0
        
        self.questions = questions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for storage"""
        return {
            'answers': self.answers,
            'current_step': self.current_step
        }
    
    def get_current_question(self) -> Optional[str]:
        """Get the current question to ask"""
        if self.current_step >= len(self.questions):
            return None
        
        # Skip questions based on previous answers if needed
        question = self.questions[self.current_step]
        
        # Check if this question should be skipped
        if 'skip_if' in question:
            skip_condition = question['skip_if']
            if skip_condition(self.answers):
                # Save a default answer and move to next
                if 'default_value' in question:
                    self.answers[question['key']] = question['default_value']
                self.current_step += 1
                return self.get_current_question()
        
        return question['question']
    
    def validate_and_save_answer(self, answer: str) -> Tuple[bool, str]:
        """
        Validate answer and save if valid.
        Returns (is_valid, message)
        """
        if self.current_step >= len(self.questions):
            return False, "Form is already complete"
        
        question = self.questions[self.current_step]
        answer = answer.strip()
        
        # Check valid values if specified
        if 'valid_values' in question:
            answer_lower = answer.lower()
            matched = None
            
            # Enhanced fuzzy matching with common variations
            answer_normalized = answer_lower.replace('_', ' ').replace('-', ' ')
            
            for valid in question['valid_values']:
                valid_normalized = valid.replace('_', ' ').replace('-', ' ')
                
                # Exact match
                if valid == answer_lower or valid_normalized == answer_normalized:
                    matched = valid
                    break
                
                # Substring match (either direction)
                if valid in answer_lower or answer_lower in valid:
                    matched = valid
                    break
                
                # Normalized substring match
                if valid_normalized in answer_normalized or answer_normalized in valid_normalized:
                    matched = valid
                    break
            
            if not matched:
                return False, f"I didn't understand '{answer}'. {question.get('error_msg', '')}"
            
            self.answers[question['key']] = matched
            self.current_step += 1
            return True, "Answer saved"
        
        # Use validator if specified
        if 'validator' in question:
            if not question['validator'](answer):
                return False, f"That doesn't seem right. {question.get('error_msg', '')}"
            
            # Parse the answer if parser specified
            if 'parser' in question:
                try:
                    parsed = question['parser'](answer)
                    self.answers[question['key']] = parsed
                except Exception as e:
                    return False, f"I couldn't understand that format. {question.get('error_msg', '')}"
            else:
                self.answers[question['key']] = answer
            
            self.current_step += 1
            return True, "Answer saved"
        
        # Default: save as-is
        self.answers[question['key']] = answer
        self.current_step += 1
        return True, "Answer saved"
    
    def is_complete(self) -> bool:
        """Check if all questions have been answered"""
        return self.current_step >= len(self.questions)
    
    def get_data(self) -> Dict[str, Any]:
        """Get the complete form data"""
        return self.answers.copy()


class FormHandler:
    """
    Handles conversational form flows.
    Uses LLM to extract answers from natural language.
    """
    
    def __init__(self, conversation, user, form_config: Dict[str, Any]):
        self.conversation = conversation
        self.user = user
        self.config = form_config
        self.state = self._load_state()
    
    def _load_state(self) -> FormState:
        """Load form state from conversation memory"""
        state_data = self.conversation.short_term_memory.get('form_state')
        questions = self.config.get('questions', [])
        return FormState(state_data, questions)
    
    def _save_state(self):
        """Save form state to conversation memory"""
        self.conversation.short_term_memory['form_state'] = self.state.to_dict()
        self.conversation.short_term_memory['form_active'] = True
        self.conversation.save(update_fields=['short_term_memory'])
    
    def _clear_state(self):
        """Clear form state from conversation memory"""
        if 'form_state' in self.conversation.short_term_memory:
            del self.conversation.short_term_memory['form_state']
        if 'form_active' in self.conversation.short_term_memory:
            del self.conversation.short_term_memory['form_active']
        if 'form_config' in self.conversation.short_term_memory:
            del self.conversation.short_term_memory['form_config']
        self.conversation.save(update_fields=['short_term_memory'])
    
    @staticmethod
    def is_active(conversation) -> bool:
        """Check if form mode is active for this conversation"""
        return conversation.short_term_memory.get('form_active', False)
    
    def start_form(self) -> str:
        """Start the form flow - returns welcome message with first question"""
        self.state = FormState(questions=self.config.get('questions', []))
        self._save_state()
        
        first_question = self.state.get_current_question()
        welcome_msg = self.config.get('welcome_message', 'Let me help you fill out this form.')
        total_questions = len(self.config.get('questions', []))
        
        return f"""{welcome_msg}

I'll ask you {total_questions} questions.

**Question 1:** {first_question}"""
    
    def process_answer(self, user_message: str) -> str:
        """
        Process user's answer to current form question.
        Uses LLM to extract and validate the answer from natural language.
        
        Returns the next question or completion message.
        """
        current_question = self.state.questions[self.state.current_step]
        
        # Use LLM to extract and validate the answer
        extracted_answer = self._extract_answer_with_llm(
            user_message=user_message,
            question_info=current_question
        )
        
        if extracted_answer is None:
            return f"I'm not sure I understood that. {current_question['question']}"
        
        # Validate and save the answer
        is_valid, message = self.state.validate_and_save_answer(extracted_answer)
        
        if not is_valid:
            return f"❌ {message}\n\nPlease try again."
        
        # Save progress
        self._save_state()
        
        # Check if form is complete
        if self.state.is_complete():
            return self._handle_completion()
        
        # Get next question
        next_question = self.state.get_current_question()
        question_num = self.state.current_step + 1
        
        return f"✅ Got it!\n\n**Question {question_num}:** {next_question}"
    
    def _extract_answer_with_llm(
        self, 
        user_message: str, 
        question_info: dict
    ) -> Optional[str]:
        """
        Use LLM to extract the answer from user's natural language message.
        Returns the extracted answer or None if couldn't understand.
        """
        # Build validation prompt based on question type
        if 'valid_values' in question_info:
            valid_options = ', '.join(question_info['valid_values'])
            validation_prompt = f"""You are extracting structured data from user responses.

Question: {question_info['question']}

VALID OPTIONS (you MUST choose one of these EXACT words):
{valid_options}

User said: "{user_message}"

INSTRUCTIONS:
1. Read the user's response carefully
2. Determine which valid option best matches their intent
3. Respond with ONLY the exact option word from the valid list above
4. Common variations to handle:
   - "lightly active" → "light"
   - "moderately active" → "moderate"  
   - "very active" → "very_active"
   - User descriptions should map to the closest option
5. If you cannot determine which option they mean, respond with: UNCLEAR

YOUR RESPONSE (one word from valid options only):"""
        
        else:
            # Free text extraction
            validation_prompt = f"""You are extracting structured data from user responses.

Question: {question_info['question']}

User said: "{user_message}"

INSTRUCTIONS:
1. Extract the user's answer from their natural language response
2. Normalize common formats:
   - Word numbers to digits: "four" → "4", "six" → "6", "zero" → "0"
   - Days of week: Extract as comma-separated list if multiple mentioned
   - Remove filler words and extract just the core answer
3. If they say none/no/nothing, respond with: none
4. If their response is unclear or off-topic, respond with: UNCLEAR

YOUR RESPONSE (extracted answer only):"""
        
        # Call LLM for extraction
        llm = LLMService(
            model_name="qwen3",
            base_url=os.environ.get("OLLAMA_BASE_URL"),
            system_prompt="You are a precise data extraction assistant. Follow instructions exactly.",
            max_tokens=8192
        )
        
        result = llm.chat(
            message=validation_prompt,
            message_history={"messages": [], "usage": {}},
            user=self.user
        )
        
        extracted = result.output.strip()
        
        if extracted == "UNCLEAR":
            return None
        
        return extracted
    
    def _handle_completion(self) -> str:
        """Handle form completion - call callback and cleanup"""
        try:
            completion_msg = None
            
            # Get completion callback
            callback_path = self.config.get('completion_callback')
            
            if callback_path:
                # Import and call the callback
                module_path, function_name = callback_path.rsplit('.', 1)
                module = __import__(module_path, fromlist=[function_name])
                callback = getattr(module, function_name)
                
                # Call with form data and user
                success, message = callback(self.state.get_data(), self.user, self.conversation)
                
                if not success:
                    return f"❌ {message}"
                
                # Use message from callback
                completion_msg = message
            
            # Clear form state
            self._clear_state()
            
            # Use callback message or config message or default
            if not completion_msg:
                completion_msg = self.config.get(
                    'completion_message',
                    '✅ Form completed successfully!'
                )
            
            return completion_msg
            
        except Exception as e:
            print(f"[FORM] Error in completion: {e}")
            import traceback
            traceback.print_exc()
            return "❌ There was an error processing your form. Please try again."
    
    def is_complete(self) -> bool:
        """Check if form is complete"""
        return self.state.is_complete()
    
    def get_data(self) -> Dict[str, Any]:
        """Get the collected form data"""
        return self.state.get_data()
