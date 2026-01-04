import json
import traceback
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


@router.post("/stream")
def chat_stream(request, payload: ChatRequest):
    """Stream chat responses with SSE"""
    
    conversation = get_or_create_conversation(
        user=request.user,
        conversation_id=payload.conversation_id,
        agent_id=payload.agent_id
    )
    
    # Get Operator agent for error responses
    operator_agent = Agent.objects.filter(name="Operator").first()
    
    embedding_service = EmbeddingService()
    
    def stream_response():
        stream = None
        agent = None
        full_content = ""
        
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
            stream = agent.process_message_stream(
                message=payload.message,
                conversation=conversation,
                user=request.user
            )
            
            for chunk in stream.stream_text(delta=True):
                full_content += chunk
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            
            # Update memory (skip for mock streams that don't use LLM)
            if not getattr(stream, 'skip_memory_update', False):
                agent.update_memory(conversation, stream)
            
            # Extract reasoning
            reasoning = None
            all_messages = stream.all_messages()
            if all_messages:  # Only extract reasoning if there are messages
                for part in all_messages[-1].parts:
                    if isinstance(part, ThinkingPart):
                        reasoning = part.content
                        break
            
            # Generate embedding and save
            exchange_text = f"User: {payload.message}\nAssistant: {full_content}"
            exchange_embedding = embedding_service.generate_embedding(
                text=exchange_text,
                model="nomic-embed-text:v1.5"
            )
            
            # Capture full debug data
            try:
                debug_data = {'messages': json.loads(stream.all_messages_json())}
            except Exception:
                debug_data = None
            
            save_message(
                conversation=conversation,
                user_prompt=payload.message,
                ai_response=full_content,
                reasoning=reasoning,
                timestamp=stream.timestamp(),
                embedding=exchange_embedding,
                debug_data=debug_data
            )
            
            # End event
            yield f"data: {json.dumps({'type': 'end', 'conversation_id': conversation.id, 'agent_id': agent_model.id, 'agent_name': agent_model.name})}\n\n"
            
        except Exception as exc:
            # Check if it's a connection error to Ollama
            error_str = str(exc).lower()
            if any(keyword in error_str for keyword in ['connection', 'connect', 'timeout', 'unreachable', 'refused']):
                friendly_msg = "I can't connect with my brain at the moment. Please try again later."
            else:
                friendly_msg = "I encountered an unexpected error. Please try again."
            
            traceback.print_exc()
            
            # Send error as a normal chat message from Operator
            yield f"data: {json.dumps({'type': 'content', 'content': friendly_msg})}\n\n"
            yield f"data: {json.dumps({'type': 'end', 'conversation_id': conversation.id, 'agent_id': operator_agent.id, 'agent_name': operator_agent.name})}\n\n"
    
    return StreamingHttpResponse(stream_response(), content_type="text/event-stream")


@router.post("/chat", response=ChatResponse)
def chat(request, payload: ChatRequest):
    """Non-streaming chat endpoint"""
    
    conversation = None
    agent_model = None
    
    # Get Operator agent for error responses
    operator_agent = Agent.objects.filter(name="Operator").first()
    
    try:
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
        
        # Capture full debug data
        debug_data = {'messages': json.loads(result.all_messages_json())}
        
        save_message(
            conversation=conversation,
            user_prompt=payload.message,
            ai_response=response_text,
            reasoning=reasoning,
            timestamp=result.timestamp(),
            embedding=exchange_embedding,
            debug_data=debug_data
        )
        
        return ChatResponse(
            conversation_id=conversation.id,
            agent_id=agent_model.id,
            agent_name=agent_model.name,
            message=response_text,
            reasoning=reasoning
        )
    
    except Exception as exc:
        # Check if it's a connection error to Ollama
        error_str = str(exc).lower()
        if any(keyword in error_str for keyword in ['connection', 'connect', 'timeout', 'unreachable', 'refused']):
            friendly_msg = "I can't connect with my brain at the moment. Please try again later."
        else:
            friendly_msg = "I encountered an unexpected error. Please try again."
        
        traceback.print_exc()
        
        # Return error as a normal chat response from Operator (200 OK)
        return ChatResponse(
            conversation_id=conversation.id if conversation else None,
            agent_id=operator_agent.id,
            agent_name=operator_agent.name,
            message=friendly_msg,
            reasoning=None
        )

