import requests
import os
from pgvector.django import CosineDistance

class EmbeddingService:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    
    def generate_embedding(self, text: str, model: str = "nomic-embed-text:v1.5") -> list[float]:
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except requests.exceptions.RequestException as e:
            print(f"Error generating embedding: {e}")
            raise

    def search_similar_messages(self, query_embedding: list[float], user=None, agent=None, limit: int = 5):
        from ..models import Message
        
        queryset = Message.objects.filter(embedding__isnull=False)
        
        # filter by user
        if user:
            queryset = queryset.filter(conversation__user=user)
        
        # filter by agent
        if agent:
            queryset = queryset.filter(conversation__agent=agent)
        
        # Use pgvector's CosineDistance annotation
        similar_messages = queryset.annotate(
            distance=CosineDistance('embedding', query_embedding)
        ).order_by('distance')[:limit]
        
        return similar_messages
    
    def search_similar_conversations(self, query_embedding: list[float], user=None, agent=None, limit: int = 1):
        from ..models import Conversation
        
        queryset = Conversation.objects.filter(embedding__isnull=False)
        
        if user:
            queryset = queryset.filter(user=user)
            
        if agent:
            queryset = queryset.filter(agent=agent)
            
        similar_conversations = queryset.annotate(
            distance=CosineDistance('embedding', query_embedding)
        ).order_by('distance')[:limit]
        
        return similar_conversations