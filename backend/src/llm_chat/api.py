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

router = Router(tags=['Chat'], auth=JWTAuth())

# Lazy initialization of services to avoid module-level initialization issues
_ollama_client = None

def get_ollama_client():
    """Lazy initialization of Ollama client"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


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
    
    # Get response from Ollama with tool support
    try:
        # Get user's preferred model from AI Identity Profile
        model = None
        if user and hasattr(user, 'ai_identity'):
            model = user.ai_identity.preferred_model
        
        response_content = get_ollama_client().chat(
            messages, 
            user=user, 
            model=model,
            use_tools=True  # Enable Tool_Retriever pattern
        )
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
    
    return {
        'message': {
            'id': str(assistant_message.id),
            'role': assistant_message.role,
            'content': assistant_message.content,
            'created_at': assistant_message.created_at
        },
        'conversation_id': str(conversation.id)
    }


@router.get('/conversations', response=ConversationListSchema)
def list_conversations(request):
    """List all general conversations for the current user (excludes check-ins)"""
    user = request.auth
    conversations = Conversation.objects.filter(
        user=user, 
        conversation_type='general'
    ).order_by('-updated_at')
    
    return {
        'conversations': [
            {
                'id': str(conv.id),
                'title': conv.title or 'Untitled',
                'conversation_type': conv.conversation_type,
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
    try:
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id, 
            user=user
        )
        
        messages = conversation.get_messages()
        
        return {
            'id': str(conversation.id),
            'title': conversation.title or 'Untitled',
            'conversation_type': conversation.conversation_type,
            'created_at': conversation.created_at,
            'updated_at': conversation.updated_at,
            'messages': [
                {
                    'id': str(msg.id),
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at
                }
                for msg in messages
            ]
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading conversation {conversation_id}: {str(e)}", exc_info=True)
        raise


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
    try:
        user = request.auth
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
    
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
    
    # Get streaming response from Ollama with tool support
    def stream_response():
        # Send initial message with conversation ID
        yield json.dumps({'type': 'start', 'conversation_id': str(conversation.id)}) + '\n'
        
        full_content = ""
        try:
            # Get user's preferred model from AI Identity Profile
            model = None
            if user and hasattr(user, 'ai_identity'):
                model = user.ai_identity.preferred_model
            
            # Stream the response from Ollama with Tool_Retriever support
            for event in get_ollama_client().chat_stream(
                messages, 
                user=user, 
                model=model,
                use_tools=True  # Enable Tool_Retriever pattern
            ):
                # Handle different event types
                if isinstance(event, str):
                    # Content chunk
                    full_content += event
                    yield json.dumps({'type': 'content', 'content': event}) + '\n'
                elif isinstance(event, dict):
                    # Tool event (tool_call, tool_result, tools_discovered)
                    yield json.dumps(event) + '\n'
        except Exception as e:
            error_msg = f"I'm sorry, I'm having trouble connecting to my brain. Please try again later. Error: {str(e)}"
            yield json.dumps({'type': 'content', 'content': error_msg}) + '\n'
            full_content = error_msg
        
        # Check for check-in completion if this is a check-in conversation
        checkin_complete = False
        checkin_insights = None
        cleaned_content = full_content
        
        if conversation.conversation_type == 'checkin':
            from wellbeing.completion_detector import CheckInCompletionDetector
            from wellbeing.models import CheckIn
            
            # Detect completion
            is_complete, cleaned_msg = CheckInCompletionDetector.detect_completion(full_content)
            cleaned_content = cleaned_msg
            
            if is_complete:
                checkin_complete = True
                
                # Try to get the check-in
                try:
                    checkin = CheckIn.objects.get(conversation=conversation, status='in_progress')
                    
                    # Extract insights
                    insights = CheckInCompletionDetector.extract_insights(
                        full_content,
                        checkin.check_in_type
                    )
                    
                    # Generate summary
                    conv_messages = [
                        {'role': msg.role, 'content': msg.content}
                        for msg in conversation.get_messages()
                    ]
                    summary = CheckInCompletionDetector.generate_summary(
                        conv_messages,
                        checkin.check_in_type
                    )
                    
                    # Complete the check-in
                    checkin.complete(
                        insights=insights or {},
                        summary=summary,
                        actions_taken=checkin.actions_taken  # Keep existing actions
                    )
                    
                    checkin_insights = insights
                    
                except CheckIn.DoesNotExist:
                    pass  # No check-in found, just continue
        
        # Save the complete message to the database (with cleaned content)
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=cleaned_content
        )
        
        # Send the final message with metadata
        end_data = {
            'type': 'end',
            'message': {
                'id': str(assistant_message.id),
                'role': assistant_message.role,
                'content': cleaned_content,
                'created_at': assistant_message.created_at.isoformat()
            }
        }
        
        # Add check-in completion info if applicable
        if checkin_complete:
            end_data['checkin_complete'] = True
            end_data['checkin_insights'] = checkin_insights
        
        yield json.dumps(end_data) + '\n'
        
        # Update conversation timestamp
        conversation.save()
    
    return StreamingHttpResponse(stream_response(), content_type='application/x-ndjson')
