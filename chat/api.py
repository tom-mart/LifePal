import json
import os
from ninja import Router
from django.http import StreamingHttpResponse
from pydantic_ai import ThinkingPart

from agents.models import Agent
from agents import registry
from agents.services.embedding_service import EmbeddingService
from .schemas import ChatRequest, ChatResponse, AgentSchema
from .helpers import get_or_create_conversation, route_to_specialist, save_message


router = Router(tags=["chat"])

@router.get("/agents", response=list[AgentSchema])
def list_agents(request):
    """List all available agents"""
    return Agent.objects.all()


@router.post("/chat/stream")
def chat_stream(request, payload: ChatRequest):
    """Stream chat responses with SSE"""
    
    conversation = get_or_create_conversation(
        user=request.user,
        conversation_id=payload.conversation_id,
        agent_id=payload.agent_id
    )
    
    embedding_service = EmbeddingService()
    
    def stream_response():
        try:
            # Route to specialist if needed
            agent_model, agent_name = route_to_specialist(
                message=payload.message,
                conversation=conversation,
                user=request.user
            )
            
            # Get agent instance
            agent = registry.get_instance(agent_name, agent_model)
            
            # Start event
            yield f"data: {json.dumps({'type': 'start', 'conversation_id': conversation.id, 'agent_id': agent_model.id, 'agent_name': agent_model.name})}\n\n"
            
            # Stream response
            full_content = ""
            stream = agent.process_message_stream(
                message=payload.message,
                conversation=conversation,
                user=request.user
            )
            
            for chunk in stream.stream_text(delta=True):
                full_content += chunk
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            
            # Update memory
            agent.update_memory(conversation, stream)
            
            # Extract reasoning
            reasoning = None
            for part in stream.all_messages()[-1].parts:
                if isinstance(part, ThinkingPart):
                    reasoning = part.content
                    break
            
            # Generate embedding and save
            exchange_text = f"User: {payload.message}\nAssistant: {full_content}"
            exchange_embedding = embedding_service.generate_embedding(
                text=exchange_text,
                model="nomic-embed-text:v1.5"
            )
            
            save_message(
                conversation=conversation,
                user_prompt=payload.message,
                ai_response=full_content,
                reasoning=reasoning,
                timestamp=stream.timestamp(),
                embedding=exchange_embedding
            )
            
            # End event
            yield f"data: {json.dumps({'type': 'end', 'conversation_id': conversation.id, 'agent_id': agent_model.id, 'agent_name': agent_model.name})}\n\n"
            
        except Exception as exc:
            error_msg = f"Error: {str(exc)}"
            print(f"ERROR in chat_stream: {exc}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
    
    return StreamingHttpResponse(stream_response(), content_type="text/event-stream")


@router.post("/chat", response=ChatResponse)
def chat(request, payload: ChatRequest):
    """Non-streaming chat endpoint"""
    
    conversation = get_or_create_conversation(
        user=request.user,
        conversation_id=payload.conversation_id,
        agent_id=payload.agent_id
    )
    
    # Route to specialist if needed
    agent_model, agent_name = route_to_specialist(
        message=payload.message,
        conversation=conversation,
        user=request.user
    )
    
    # Get agent and process message
    agent = registry.get_instance(agent_name, agent_model)
    response_text, reasoning, result = agent.process_message(
        message=payload.message,
        conversation=conversation,
        user=request.user
    )
    
    # Generate embedding and save
    embedding_service = EmbeddingService()
    exchange_text = f"User: {payload.message}\nAssistant: {response_text}"
    exchange_embedding = embedding_service.generate_embedding(
        text=exchange_text,
        model="nomic-embed-text:v1.5"
    )
    
    save_message(
        conversation=conversation,
        user_prompt=payload.message,
        ai_response=response_text,
        reasoning=reasoning,
        timestamp=result.timestamp(),
        embedding=exchange_embedding
    )
    
    return ChatResponse(
        conversation_id=conversation.id,
        agent_id=agent_model.id,
        agent_name=agent_model.name,
        message=response_text,
        reasoning=reasoning
    )

