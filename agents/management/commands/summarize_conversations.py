import os
from django.core.management.base import BaseCommand
from django.db.models import Q
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from agents.models import Conversation
from agents.services.embedding_service import EmbeddingService


class Command(BaseCommand):
    help = 'Summarize all conversations that need it'

    def handle(self, *args, **options):
        # Create summarization agent
        ollama_model = OpenAIChatModel(
            model_name="gemma3-128k",
            provider=OllamaProvider(base_url=os.environ.get("OLLAMA_BASE_URL")),
        )
        
        summarization_agent = Agent(
            ollama_model,
            system_prompt="""You are a professional conversation summarizer. Create clear, concise summaries of conversations.
        
        Guidelines:
        - Identify and highlight key topics discussed
        - Capture important facts, decisions, or information shared
        - Note any questions asked or problems solved
        - Preserve context and relationships between topics
        - Keep summaries focused and structured
        - Aim for 150-200 words
        - Use bullet points for clarity when appropriate
        - Write in third person perspective

        Example format:
        The conversation covered [main topics]. The user discussed [key points]. Important information shared includes [facts/decisions]. [Any notable context or outcomes]."""
        )
        
        embedding_service = EmbeddingService()
        
        # Find conversations that need summarization
        conversations = Conversation.objects.filter(
            Q(summary__isnull=True) | Q(summary_needs_regeneration=True)
        ).distinct()
        
        total = conversations.count()
        self.stdout.write(f'\n📊 Found {total} conversation(s) to summarize\n')
        
        if total == 0:
            self.stdout.write(self.style.WARNING('✓ All conversations are up to date'))
            return
        
        summarized = 0
        
        for conversation in conversations:
            messages = conversation.messages.all()
            
            # Skip if no messages
            if messages.count() == 0:
                continue
            
            self.stdout.write(f'\n📝 Conversation {conversation.id} ({messages.count()} messages)')
            
            try:
                # Build conversation text
                conversation_text = "\n\n".join([
                    f"User: {msg.user_prompt}\nAI: {msg.ai_response}"
                    for msg in messages
                ])
                
                # Generate summary
                prompt = f"Summarize this conversation:\n\n{conversation_text}"
                response = summarization_agent.run_sync(prompt)
                summary = response.output
                
                # Generate embedding
                embedding = embedding_service.generate_embedding(
                    text=summary,
                    model="nomic-embed-text:v1.5"
                )
                
                # Update conversation
                conversation.update_summary(summary, embedding)
                
                self.stdout.write(self.style.SUCCESS(f'✅ Summarized'))
                self.stdout.write(f'   {summary[:100]}...')
                summarized += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
        
        self.stdout.write(f'\n✨ Done! Summarized {summarized} conversations\n')