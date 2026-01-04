from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField

class Agent(models.Model):
    name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, default="gemma3-32k:latest")
    system_prompt = models.TextField(blank=True)
    max_context_tokens = models.IntegerField(default=32768)  # Token limit for context window
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Conversation(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name='conversations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Summary fields
    summary = models.TextField(blank=True, null=True)
    summary_generated_at = models.DateTimeField(blank=True, null=True)
    summary_needs_regeneration = models.BooleanField(default=False, help_text="Flag indicating new messages since last summary")
    summary_message_count = models.IntegerField(default=0, help_text="Number of messages included in current summary")
    
    # Memory fields
    short_term_memory = models.JSONField(default=dict, blank=True)
    
    # Embeddings
    embedding = VectorField(dimensions=768, null=True, blank=True, help_text="Embedding of the conversation summary")

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"User {username} conversation with {self.agent.name}. Conversation ID: {self.id}"
    
    def mark_for_summarization(self):
        # Mark conversation as needing summary regeneration
        self.summary_needs_regeneration = True
        self.save(update_fields=['summary_needs_regeneration', 'updated_at'])
    
    def update_summary(self, new_summary: str, embedding=None):
        # Update summary and reset regeneration flag
        self.summary = new_summary
        self.summary_generated_at = models.functions.Now()
        self.summary_needs_regeneration = False
        self.summary_message_count = self.messages.count()
        if embedding is not None:
            self.embedding = embedding
        self.save()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    # Request Part (User)
    user_prompt = models.TextField(help_text="The user's input message")
    # Response Part (AI)
    ai_response = models.TextField(help_text="The AI's final text response")
    ai_reasoning = models.TextField(blank=True, null=True, help_text="Internal thought process (ThinkingPart)")
    # Debugging - Full LLM interaction history
    debug_data = models.JSONField(
        null=True, 
        blank=True, 
        help_text="Complete pydantic-ai result with all messages, tool calls, thinking, and usage stats"
    )
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)

    embedding = VectorField(dimensions=768, null=True, blank=True)  # For pgvector semantic search

    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        username = self.conversation.user.username if self.conversation.user else "Anonymous"
        message_number = self.conversation.messages.filter(timestamp__lte=self.timestamp).count()
        return f"Message {message_number} in conversation {self.conversation.id} for {username} with {self.conversation.agent.name}"


class UserAgentPreference(models.Model):
    """
    User-specific preferences for AI agents.
    Allows customization of agent name, communication style, and other traits.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_preferences')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='user_preferences')
    
    # Common personalization fields
    agent_name = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Custom name for this agent (e.g., 'Steve', 'Kevin')"
    )
    communication_style = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Communication style preference (e.g., 'supportive', 'drill sergeant', 'casual')"
    )
    response_length = models.CharField(
        max_length=50,
        blank=True,
        help_text="Preferred response length (e.g., 'concise', 'detailed', 'moderate')"
    )
    formality_level = models.CharField(
        max_length=50,
        blank=True,
        help_text="Formality preference (e.g., 'casual', 'professional', 'formal')"
    )
    language = models.CharField(
        max_length=10,
        blank=True,
        default='en',
        help_text="Preferred language code (e.g., 'en', 'es', 'fr')"
    )
    
    # Flexible field for any additional preferences
    additional_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional customization preferences as key-value pairs"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user', 'agent']]
    
    def __str__(self):
        agent_display = self.agent_name or self.agent.name
        return f"{self.user.username}'s {agent_display}"
    
    def get_personalization_text(self) -> str:
        """
        Generate text snippet to inject into system prompt.
        Returns empty string if no preferences set.
        """
        parts = []
        
        if self.agent_name:
            parts.append(f"Your name is {self.agent_name}.")
        
        if self.communication_style:
            parts.append(f"Use a {self.communication_style} communication style.")
        
        if self.response_length:
            parts.append(f"Keep responses {self.response_length}.")
        
        if self.formality_level:
            parts.append(f"Maintain a {self.formality_level} tone.")
        
        if self.language and self.language != 'en':
            parts.append(f"Respond in {self.language} language.")
        
        # Add any additional preferences
        for key, value in self.additional_preferences.items():
            if value:
                parts.append(f"{key}: {value}")
        
        return " ".join(parts) if parts else ""