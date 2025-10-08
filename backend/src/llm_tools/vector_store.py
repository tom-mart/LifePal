"""
ChromaDB Vector Store for Tool Semantic Search

Manages tool embeddings in ChromaDB for semantic search capabilities.
"""

import chromadb
from chromadb.config import Settings
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)


class ToolVectorStore:
    """
    Manages tool embeddings in ChromaDB for semantic search.
    
    ChromaDB is already running in Docker at chromadb:8000.
    This class provides the integration layer.
    """
    
    def __init__(self):
        # Determine if running in production (Docker) or development (local)
        use_docker = os.getenv('USE_DOCKER_CHROMADB', 'false').lower() == 'true'
        
        if use_docker:
            # Production: Connect to ChromaDB Docker container via HTTP
            chroma_host = os.getenv('CHROMADB_HOST', 'chromadb')
            chroma_port = int(os.getenv('CHROMADB_PORT', '8000'))
            
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port
            )
            logger.info(f"Using Docker ChromaDB at {chroma_host}:{chroma_port}")
        else:
            # Development: Use local persistent ChromaDB
            persist_directory = os.getenv('CHROMADB_PATH', 
                                         os.path.join(settings.BASE_DIR, 'chromadb_data'))
            
            self.client = chromadb.PersistentClient(
                path=persist_directory
            )
            logger.info(f"Using local ChromaDB at {persist_directory}")
        
        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name="tools",
                metadata={"description": "LLM tool definitions for semantic search"}
            )
            logger.info(f"Connected to ChromaDB collection: tools")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    def add_tool(self, tool):
        """
        Add or update a tool in the vector store.
        
        Args:
            tool: ToolDefinition instance
        """
        try:
            # Create rich document for embedding
            document = self._create_document(tool)
            
            # Add to ChromaDB
            self.collection.upsert(
                ids=[str(tool.id)],
                documents=[document],
                metadatas=[{
                    'name': tool.name,
                    'category': tool.category,
                    'execution_type': tool.execution_type,
                    'is_active': tool.is_active
                }]
            )
            
            logger.info(f"Added tool to vector store: {tool.name}")
            
        except Exception as e:
            logger.error(f"Failed to add tool {tool.name} to vector store: {e}")
            # Don't raise - vector store is optional enhancement
    
    def remove_tool(self, tool_id):
        """Remove a tool from the vector store"""
        try:
            self.collection.delete(ids=[str(tool_id)])
            logger.info(f"Removed tool {tool_id} from vector store")
        except Exception as e:
            logger.error(f"Failed to remove tool {tool_id} from vector store: {e}")
    
    def search_tools(self, query, n_results=5, category=None):
        """
        Semantic search for tools.
        
        Args:
            query: Natural language query
            n_results: Number of results to return
            category: Optional category filter
            
        Returns:
            List of tool IDs ranked by relevance
        """
        try:
            # Build where filter
            where = {'is_active': True}
            if category:
                where['category'] = category
            
            # Search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Extract tool IDs
            if results['ids'] and len(results['ids']) > 0:
                tool_ids = results['ids'][0]
                distances = results['distances'][0]
                
                # Log results for debugging
                logger.info(f"Semantic search: '{query}' → {len(tool_ids)} results")
                for tool_id, distance in zip(tool_ids, distances):
                    logger.debug(f"  {tool_id}: similarity={1-distance:.3f}")
                
                return tool_ids
            
            return []
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    def sync_all_tools(self):
        """Sync all active tools from database to vector store"""
        from .models import ToolDefinition
        
        try:
            tools = ToolDefinition.objects.filter(is_active=True)
            
            for tool in tools:
                self.add_tool(tool)
            
            logger.info(f"Synced {tools.count()} tools to vector store")
            return tools.count()
            
        except Exception as e:
            logger.error(f"Failed to sync tools: {e}")
            return 0
    
    def _create_document(self, tool):
        """
        Create a rich document for embedding.
        
        Combines name, description, examples, and category
        for better semantic understanding.
        """
        parts = [
            f"Tool: {tool.name}",
            f"Category: {tool.category}",
            f"Description: {tool.description}",
        ]
        
        if tool.usage_examples:
            examples = "\n".join(f"- {ex}" for ex in tool.usage_examples)
            parts.append(f"Examples:\n{examples}")
        
        return "\n\n".join(parts)
    
    def get_stats(self):
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                'total_tools': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'total_tools': 0, 'error': str(e)}


# Global instance
_vector_store = None


def get_vector_store():
    """Get the global vector store instance"""
    global _vector_store
    
    if _vector_store is None:
        try:
            _vector_store = ToolVectorStore()
        except Exception as e:
            logger.warning(f"ChromaDB not available: {e}. Semantic search disabled.")
            _vector_store = None
    
    return _vector_store
