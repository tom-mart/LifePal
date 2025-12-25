"""
Helper utilities for chat API endpoints
"""
import os
from django.shortcuts import get_object_or_404
from agents.models import Agent, Conversation
from agents.services.llm_service import LLMService
from agents import registry


def get_or_create_conversation(user, conversation_id=None, agent_id=None):
    """
    Get existing conversation or create new one.
    Defaults to Operator agent if no agent_id provided.
    """
    if conversation_id:
        return get_object_or_404(Conversation, id=conversation_id)
    
    # New conversation
    if agent_id is None:
        agent_model = Agent.objects.filter(name="Operator").first()
        if not agent_model:
            agent_model = Agent.objects.first()
    else:
        agent_model = get_object_or_404(Agent, id=agent_id)
    
    return Conversation.objects.create(
        agent=agent_model,
        user=user,
        short_term_memory={}
    )


def route_to_specialist(message, conversation, user):
    """
    Route message through Operator to get specialist agent.
    Returns (agent_model, agent_name) tuple.
    
    If already using a specialist, returns that agent directly.
    """
    agent_model = conversation.agent
    
    # If not Operator, use current agent directly
    if agent_model.name != "Operator":
        agent_name = agent_model.name.lower().replace(' ', '_')
        return agent_model, agent_name
    
    # Use Operator to route
    operator_llm = LLMService(
        model_name=agent_model.model_name,
        base_url=os.environ.get("OLLAMA_BASE_URL"),
        system_prompt=agent_model.system_prompt,
        max_tokens=agent_model.max_context_tokens
    )
    
    routing_response = operator_llm.chat(
        message=message,
        message_history={"messages": [], "usage": {}},
        user=user
    )
    
    agent_name = routing_response.output.strip().lower()
    specialist = Agent.objects.filter(name__icontains=agent_name.replace('_', ' ')).first()
    
    if not specialist:
        specialist = Agent.objects.filter(name__icontains="general").first()
    
    if not specialist:
        specialist = agent_model
        agent_name = "general_agent"
    else:
        agent_name = specialist.name.lower().replace(' ', '_')
    
    # Update conversation agent
    conversation.agent = specialist
    conversation.save()
    
    return specialist, agent_name


def save_message(conversation, user_prompt, ai_response, reasoning, timestamp, embedding):
    """Save message with all metadata to database"""
    from agents.models import Message
    
    Message.objects.create(
        conversation=conversation,
        user_prompt=user_prompt,
        ai_response=ai_response,
        ai_reasoning=reasoning,
        timestamp=timestamp,
        embedding=embedding
    )
    
    conversation.mark_for_summarization()
