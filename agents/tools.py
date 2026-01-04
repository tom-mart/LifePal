"""
Common tools available to all agents.
"""

from pydantic_ai import RunContext
from agents.services.deps import AgentDeps
from agents.services.embedding_service import EmbeddingService
from agents.models import Message, Conversation


def search_past_conversations(ctx: RunContext[AgentDeps], query: str, limit: int = 3) -> str:
    """
    Search through past conversation summaries for relevant information.
    Use this when you need context about previous discussions with the user.
    
    Args:
        query: What to search for (e.g., "weight loss goals", "previous workout plans")
        limit: Maximum number of conversations to retrieve (default 3)
    
    Returns:
        Formatted summaries of relevant past conversations
    """
    user = ctx.deps.user
    
    # Generate embedding for the query
    embedding_service = EmbeddingService()
    query_embedding = embedding_service.generate_embedding(
        text=query,
        model="nomic-embed-text:v1.5"
    )
    
    # Get agent from context
    agent = ctx.deps.agent
    
    # Search for similar conversations (summaries) - user and agent specific
    similar_conversations = embedding_service.search_similar_conversations(
        query_embedding=query_embedding,
        user=user,
        agent=agent,
        limit=limit
    )
    
    if not similar_conversations:
        return "No relevant past conversations found."
    
    # Format results
    results = []
    for conv in similar_conversations:
        if conv.summary:
            date = conv.updated_at.strftime('%Y-%m-%d')
            results.append(f"[{date}] Previous conversation:\n{conv.summary}")
    
    if not results:
        return "Found conversations but they don't have summaries yet."
    
    return "\n\n---\n\n".join(results)


def search_past_messages(ctx: RunContext[AgentDeps], query: str, limit: int = 5) -> str:
    """
    Search through individual past messages for specific information.
    Use this when you need exact details from previous interactions.
    
    Args:
        query: What to search for (e.g., "last weight measurement", "exercise preferences")
        limit: Maximum number of messages to retrieve (default 5)
    
    Returns:
        Formatted relevant messages from conversation history
    """
    user = ctx.deps.user
    
    # Generate embedding for the query
    embedding_service = EmbeddingService()
    query_embedding = embedding_service.generate_embedding(
        text=query,
        model="nomic-embed-text:v1.5"
    )
    
    # Search for similar messages
    similar_messages = embedding_service.search_similar_messages(
        query_embedding=query_embedding,
        user=user,
        limit=limit
    )
    
    if not similar_messages:
        return "No relevant past messages found."
    
    # Format results
    results = []
    for msg in similar_messages:
        date = msg.timestamp.strftime('%Y-%m-%d %H:%M')
        results.append(f"[{date}]\nUser: {msg.user_prompt}\nAssistant: {msg.ai_response}")
    
    return "\n\n---\n\n".join(results)


def update_agent_preferences(
    ctx: RunContext[AgentDeps],
    agent_name: str = None,
    communication_style: str = None,
    response_length: str = None,
    formality_level: str = None,
    language: str = None,
    **additional_preferences
) -> str:
    """
    Update user's preferences for this AI agent based on their requests.
    Use this when the user wants to customize how you interact with them.
    
    Args:
        agent_name: Custom name the user wants to call this agent (e.g., "Steve", "Kevin", "Coach")
        communication_style: How the user wants you to communicate (e.g., "supportive", "drill sergeant", "casual", "professional", "motivational")
        response_length: How detailed responses should be (e.g., "concise", "detailed", "moderate", "brief")
        formality_level: Level of formality (e.g., "casual", "professional", "formal")
        language: Language code for responses (e.g., "en", "es", "fr", "de")
        **additional_preferences: Any other customization preferences as key-value pairs
    
    Returns:
        Confirmation message about updated preferences
    
    Examples:
        - User says "I want to call you Steve" → update_agent_preferences(agent_name="Steve")
        - User says "Be more supportive" → update_agent_preferences(communication_style="supportive")
        - User says "Keep your answers short" → update_agent_preferences(response_length="concise")
        - User says "Be more professional" → update_agent_preferences(formality_level="professional")
        - User says "Respond in Spanish" → update_agent_preferences(language="es")
    """
    from agents.models import UserAgentPreference
    
    user = ctx.deps.user
    agent = ctx.deps.agent
    
    # Get or create preference
    preference, created = UserAgentPreference.objects.get_or_create(
        user=user,
        agent=agent
    )
    
    # Track what was updated
    updates = []
    
    # Update agent name
    if agent_name is not None:
        preference.agent_name = agent_name
        updates.append(f"name set to '{agent_name}'")
    
    # Update communication style
    if communication_style is not None:
        preference.communication_style = communication_style
        updates.append(f"communication style set to '{communication_style}'")
    
    # Update response length
    if response_length is not None:
        preference.response_length = response_length
        updates.append(f"response length set to '{response_length}'")
    
    # Update formality level
    if formality_level is not None:
        preference.formality_level = formality_level
        updates.append(f"formality level set to '{formality_level}'")
    
    # Update language
    if language is not None:
        preference.language = language
        updates.append(f"language set to '{language}'")
    
    # Update additional preferences
    if additional_preferences:
        if not preference.additional_preferences:
            preference.additional_preferences = {}
        
        for key, value in additional_preferences.items():
            preference.additional_preferences[key] = value
            updates.append(f"{key} set to '{value}'")
    
    preference.save()
    
    if updates:
        return f"✓ Preferences updated: {', '.join(updates)}. These preferences will apply to our future conversations."
    else:
        return "No preferences were changed."


def get_agent_preferences(ctx: RunContext[AgentDeps]) -> str:
    """
    Get current user preferences for this AI agent.
    Use this to check what preferences the user has set.
    
    Returns:
        Current preference settings
    """
    from agents.models import UserAgentPreference
    
    user = ctx.deps.user
    agent = ctx.deps.agent
    
    try:
        preference = UserAgentPreference.objects.get(user=user, agent=agent)
        
        prefs = []
        if preference.agent_name:
            prefs.append(f"Name: {preference.agent_name}")
        if preference.communication_style:
            prefs.append(f"Communication style: {preference.communication_style}")
        if preference.response_length:
            prefs.append(f"Response length: {preference.response_length}")
        if preference.formality_level:
            prefs.append(f"Formality level: {preference.formality_level}")
        if preference.language and preference.language != 'en':
            prefs.append(f"Language: {preference.language}")
        if preference.additional_preferences:
            for key, value in preference.additional_preferences.items():
                prefs.append(f"{key}: {value}")
        
        if prefs:
            return "Current preferences:\n" + "\n".join(f"• {p}" for p in prefs)
        else:
            return "No custom preferences set yet. Using default settings."
    
    except UserAgentPreference.DoesNotExist:
        return "No custom preferences set yet. Using default settings."


# Export common tools list
COMMON_TOOLS = [
    search_past_conversations,
    search_past_messages,
    update_agent_preferences,
    get_agent_preferences,
]
