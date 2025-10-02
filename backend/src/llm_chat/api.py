from ninja import Router
from ninja_jwt.authentication import JWTAuth
from typing import List, Dict, Any, Optional
from django.shortcuts import get_object_or_404
from django.db import transaction
from ninja.files import UploadedFile
from django.conf import settings
from pathlib import Path
from django.http import StreamingHttpResponse
import json

from .models import Conversation, Message, Intent
from .schemas import (
    ChatRequestSchema, 
    ChatResponseSchema, 
    ConversationSchema, 
    ConversationDetailSchema,
    ConversationListSchema
)
from llm_service.ollama_client import OllamaClient
from llm_service.prompt_manager import PromptManager

# Intent processing imports
try:
    from .intent_processor import IntentProcessor
    INTENT_PROCESSING_ENABLED = True
except ImportError:
    INTENT_PROCESSING_ENABLED = False
    IntentProcessor = None

router = Router(tags=['Chat'], auth=JWTAuth())

# Lazy initialization of services to avoid module-level initialization issues
_ollama_client = None
_intent_processor = None

def get_ollama_client():
    """Lazy initialization of Ollama client"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client

def get_intent_processor():
    """Lazy initialization of intent processor"""
    global _intent_processor
    if _intent_processor is None and INTENT_PROCESSING_ENABLED:
        _intent_processor = IntentProcessor()
    return _intent_processor


@router.post('/send', response=ChatResponseSchema)
@transaction.atomic
def send_message(request, data: ChatRequestSchema = None, file: UploadedFile = None):
    """Send a message to the chatbot and get a response"""
    user = request.auth
    
    # Handle both JSON and form data
    if data is None:
        # Form data - parse JSON from 'data' field
        import json
        try:
            data_str = request.POST.get('data', '{}')
            data_dict = json.loads(data_str)
            user_message = data_dict.get('message', '')
            conv_id = data_dict.get('conversation_id')
        except (json.JSONDecodeError, AttributeError):
            user_message = request.POST.get('message', '')
            conv_id = request.POST.get('conversation_id')
    else:
        # JSON data
        user_message = data.message
        conv_id = data.conversation_id
    
    # Get or create conversation
    if conv_id:
        conversation = get_object_or_404(
            Conversation, 
            id=conv_id, 
            user=user
        )
    else:
        # Create a new conversation
        title = user_message[:50] if user_message else "New conversation"
        conversation = Conversation.objects.create(
            user=user,
            title=title
        )
        
        # Add system message with user context ONLY for new conversations
        prompt_manager = PromptManager(user=user)
        Message.objects.create(
            conversation=conversation,
            role='system',
            content=prompt_manager.get_system_prompt(include_user_context=True)
        )
    
    # Save user message
    user_message_obj = Message.objects.create(
        conversation=conversation,
        role='user',
        content=user_message
    )
    
    # Handle file upload if present
    if file:
        # Create media directory if it doesn't exist
        media_dir = Path(settings.MEDIA_ROOT) / 'chat_uploads' / str(conversation.id)
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        file_name = file.name
        file_path = media_dir / file_name
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Add file information to the message context
        file_type = file.content_type
        user_message_obj.content += f"\n[File uploaded: {file_name}, Type: {file_type}]"
        user_message_obj.save()
    
    # Get conversation history for context
    messages = []
    
    # Add ALL conversation history (including system message from conversation start)
    previous_messages = conversation.get_messages().exclude(id=user_message_obj.id)
    for msg in previous_messages:
        messages.append({
            'role': msg.role,
            'content': msg.content
        })
    
    # Add current message
    messages.append({
        'role': 'user',
        'content': user_message_obj.content
    })
    
    # Process intent (detect and handle) if enabled
    intent_data = None
    processor = get_intent_processor()
    if processor:
        intent_data = processor.process_message(user_message_obj)
        if intent_data:
            pass  # Intent processed successfully
    
    # If we have a specific response from the intent handler, use that
    if intent_data and 'message' in intent_data:
        response_content = intent_data['message']
    else:
        # Otherwise get response from Ollama
        try:
            response_content = get_ollama_client().chat(messages, user=user)
        except Exception as e:
            response_content = f"I'm sorry, I'm having trouble connecting to my brain. Please try again later."
    
    # Save assistant response
    assistant_message = Message.objects.create(
        conversation=conversation,
        role='assistant',
        content=response_content
    )
    
    # Update conversation timestamp
    conversation.save()
    
    # Prepare intent response - match IntentSchema format
    intent_response = None
    if intent_data:
        intent_response = {
            'intent_type': intent_data.get('response_type', 'unknown'),
            'confidence': 0.8,  # Default confidence
            'parameters': intent_data
        }
    
    return {
        'message': {
            'id': assistant_message.id,
            'role': assistant_message.role,
            'content': assistant_message.content,
            'created_at': assistant_message.created_at
        },
        'conversation_id': conversation.id,
        'intent': intent_response
    }


@router.get('/conversations', response=ConversationListSchema)
def list_conversations(request):
    """List all conversations for the current user"""
    user = request.auth
    conversations = Conversation.objects.filter(user=user).order_by('-updated_at')
    
    return {
        'conversations': [
            {
                'id': conv.id,
                'title': conv.title or 'Untitled',
                'created_at': conv.created_at,
                'updated_at': conv.updated_at
            }
            for conv in conversations
        ]
    }


@router.get('/conversations/{conversation_id}', response=ConversationDetailSchema)
def get_conversation(request, conversation_id: str):
    """Get a specific conversation with all messages"""
    user = request.auth
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        user=user
    )
    
    messages = conversation.get_messages()
    
    return {
        'id': conversation.id,
        'title': conversation.title or 'Untitled',
        'created_at': conversation.created_at,
        'updated_at': conversation.updated_at,
        'messages': [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at
            }
            for msg in messages
        ]
    }


@router.delete('/conversations/{conversation_id}')
def delete_conversation(request, conversation_id: str):
    """Delete a conversation"""
    user = request.auth
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        user=user
    )
    
    conversation.delete()
    
    return {'success': True}


@router.post('/send/stream')
def send_message_stream(request, data: ChatRequestSchema):
    """Send a message to the chatbot and get a streaming response"""
    user = request.auth
    
    # Extract message and conversation ID from schema
    user_message = data.message
    conv_id = data.conversation_id
    
    # Get or create conversation
    if conv_id:
        conversation = get_object_or_404(
            Conversation, 
            id=conv_id, 
            user=user
        )
    else:
        title = user_message[:50] if user_message else "New conversation"
        conversation = Conversation.objects.create(
            user=user,
            title=title
        )
        
        # Add system message with user context ONLY for new conversations
        prompt_manager = PromptManager(user=user)
        Message.objects.create(
            conversation=conversation,
            role='system',
            content=prompt_manager.get_system_prompt(include_user_context=True)
        )
    
    # Save user message
    user_message_obj = Message.objects.create(
        conversation=conversation,
        role='user',
        content=user_message
    )
    
    # Get conversation history for context
    messages = []
    
    # Add ALL conversation history (including system message from conversation start)
    previous_messages = conversation.get_messages().exclude(id=user_message_obj.id)
    for msg in previous_messages:
        messages.append({
            'role': msg.role,
            'content': msg.content
        })
    
    messages.append({
        'role': 'user',
        'content': user_message_obj.content
    })
    
    # Process intent (detect and handle) if enabled
    intent_data = None
    processor = get_intent_processor()
    if processor:
        intent_data = processor.process_message(user_message_obj)
        if intent_data:
            pass  # Intent processed successfully
    
    # If we have a specific response from the intent handler, use that
    if intent_data and 'message' in intent_data:
        # Create a simple streaming response for intent-based messages
        def simple_stream():
            yield json.dumps({'type': 'start', 'conversation_id': str(conversation.id)}) + '\n'
            yield json.dumps({'type': 'content', 'content': intent_data['message']}) + '\n'
            
            # Save the message to the database
            assistant_message = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=intent_data['message']
            )
            
            # Prepare intent response
            intent_response = None
            if intent_data:
                intent_response = {
                    'response_type': intent_data.get('response_type'),
                    'data': intent_data
                }
            
            # Send the final message with metadata
            yield json.dumps({
                'type': 'end',
                'message': {
                    'id': str(assistant_message.id),
                    'role': assistant_message.role,
                    'content': assistant_message.content,
                    'created_at': assistant_message.created_at.isoformat()
                },
                'intent': intent_response
            }) + '\n'
            
            # Update conversation timestamp
            conversation.save()
            
        return StreamingHttpResponse(simple_stream(), content_type='application/x-ndjson')
    else:
        # Otherwise get streaming response from Ollama
        def stream_response():
            # Send initial message with conversation ID
            yield json.dumps({'type': 'start', 'conversation_id': str(conversation.id)}) + '\n'
            
            full_content = ""
            try:
                # Stream the response from Ollama
                for content_chunk in get_ollama_client().chat_stream(messages, user=user):
                    full_content += content_chunk
                    yield json.dumps({'type': 'content', 'content': content_chunk}) + '\n'
            except Exception as e:
                error_msg = f"I'm sorry, I'm having trouble connecting to my brain. Please try again later. Error: {str(e)}"
                yield json.dumps({'type': 'content', 'content': error_msg}) + '\n'
                full_content = error_msg
            
            # Save the complete message to the database
            assistant_message = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=full_content
            )
            
            # Prepare intent response
            intent_response = None
            if intent_data:
                intent_response = {
                    'response_type': intent_data.get('response_type'),
                    'data': intent_data
                }
            
            # Send the final message with metadata
            yield json.dumps({
                'type': 'end',
                'message': {
                    'id': str(assistant_message.id),
                    'role': assistant_message.role,
                    'content': full_content,
                    'created_at': assistant_message.created_at.isoformat()
                },
                'intent': intent_response
            }) + '\n'
            
            # Update conversation timestamp
            conversation.save()
        
        return StreamingHttpResponse(stream_response(), content_type='application/x-ndjson')
