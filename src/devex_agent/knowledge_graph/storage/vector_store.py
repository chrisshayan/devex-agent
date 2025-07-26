"""
Vector Store Manager - Handles vector embeddings for semantic search
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available - Knowledge Graph vector search will be limited")

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Manages vector embeddings and semantic search using ChromaDB
    
    Provides functionality for storing, retrieving, and searching
    code and documentation embeddings for knowledge graph operations.
    """
    
    def __init__(self, persist_directory: str = "./data/vector_store"):
        self.persist_directory = persist_directory
        self.client = None
        self.collections = {}
        self.embedding_model = None
        self.is_initialized = False
        
        # Collection names for different content types
        self.collection_names = {
            "code_chunks": "kg_code_chunks",
            "documentation": "kg_documentation", 
            "patterns": "kg_patterns",
            "conversations": "kg_conversations",
            "context": "kg_context"
        }
    
    async def initialize(self):
        """Initialize the vector store"""
        try:
            if not CHROMADB_AVAILABLE:
                logger.warning("⚠️ ChromaDB not available - using mock vector store")
                self.is_initialized = True
                return
            
            logger.info("🔄 Initializing Vector Store...")
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize collections
            await self._initialize_collections()
            
            self.is_initialized = True
            logger.info("✅ Vector Store initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vector Store: {e}")
            raise
    
    async def _initialize_collections(self):
        """Initialize ChromaDB collections"""
        for collection_type, collection_name in self.collection_names.items():
            try:
                # Try to get existing collection
                collection = self.client.get_collection(name=collection_name)
                logger.info(f"📂 Found existing collection: {collection_name}")
            except:
                # Create new collection if it doesn't exist
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": f"Knowledge Graph {collection_type}"}
                )
                logger.info(f"📁 Created new collection: {collection_name}")
            
            self.collections[collection_type] = collection
    
    async def cleanup(self):
        """Cleanup vector store resources"""
        logger.info("🧹 Cleaning up Vector Store...")
        
        # Close ChromaDB client if available
        if self.client:
            try:
                # ChromaDB doesn't have an explicit close method
                self.client = None
            except:
                pass
        
        self.collections.clear()
        self.is_initialized = False
        logger.info("✅ Vector Store cleanup complete")
    
    async def add_documents(
        self,
        documents: List[Dict[str, Any]],
        collection_type: str = "documentation"
    ) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of documents with content and metadata
            collection_type: Type of collection to store in
            
        Returns:
            List of document IDs
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Store not initialized")
        
        if not CHROMADB_AVAILABLE:
            # Return mock IDs
            return [f"mock_{uuid.uuid4().hex[:8]}" for _ in documents]
        
        collection = self.collections.get(collection_type)
        if not collection:
            raise ValueError(f"Unknown collection type: {collection_type}")
        
        # Prepare data for ChromaDB
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            doc_id = doc.get("id", f"{collection_type}_{uuid.uuid4().hex[:8]}")
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Add system metadata
            metadata.update({
                "collection_type": collection_type,
                "added_at": datetime.now().isoformat(),
                "source_id": doc.get("source_id", "unknown")
            })
            
            ids.append(doc_id)
            texts.append(content)
            metadatas.append(metadata)
        
        # Generate embeddings
        embeddings = self._generate_embeddings(texts)
        
        # Add to ChromaDB
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        logger.info(f"📝 Added {len(documents)} documents to {collection_type}")
        return ids
    
    async def search_similar(
        self,
        query: str,
        collection_type: str = "documentation",
        limit: int = 10,
        where_filter: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity
        
        Args:
            query: Search query text
            collection_type: Collection to search in
            limit: Maximum number of results
            where_filter: Metadata filter
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of search results with similarities
        """
        if not self.is_initialized:
            raise RuntimeError("Vector Store not initialized")
        
        if not CHROMADB_AVAILABLE:
            # Return mock results
            return [
                {
                    "id": f"mock_result_{i}",
                    "content": f"Mock search result {i} for query: {query}",
                    "similarity_score": 0.8 - (i * 0.1),
                    "metadata": {"source": "mock", "type": collection_type}
                }
                for i in range(min(3, limit))
            ]
        
        collection = self.collections.get(collection_type)
        if not collection:
            raise ValueError(f"Unknown collection type: {collection_type}")
        
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]
        
        # Search ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_filter
        )
        
        # Process results
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # Calculate similarity score (ChromaDB returns distances)
                distance = results["distances"][0][i] if results["distances"] else 0.0
                similarity_score = max(0.0, 1.0 - distance)  # Convert distance to similarity
                
                if similarity_score >= similarity_threshold:
                    search_results.append({
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "similarity_score": similarity_score,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                    })
        
        logger.info(f"🔍 Found {len(search_results)} similar documents for query: '{query}'")
        return search_results
    
    async def get_document(self, document_id: str, collection_type: str = "documentation") -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        if not self.is_initialized:
            raise RuntimeError("Vector Store not initialized")
        
        if not CHROMADB_AVAILABLE:
            return {
                "id": document_id,
                "content": f"Mock document content for {document_id}",
                "metadata": {"source": "mock"}
            }
        
        collection = self.collections.get(collection_type)
        if not collection:
            return None
        
        try:
            results = collection.get(ids=[document_id])
            if results["ids"] and results["ids"][0]:
                return {
                    "id": document_id,
                    "content": results["documents"][0] if results["documents"] else "",
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
        except Exception as e:
            logger.warning(f"Failed to get document {document_id}: {e}")
        
        return None
    
    async def remove_source_data(self, source_id: str):
        """Remove all data from a specific source"""
        if not self.is_initialized:
            return
        
        if not CHROMADB_AVAILABLE:
            logger.info(f"🗑️ Mock removal of source data: {source_id}")
            return
        
        removed_count = 0
        for collection_type, collection in self.collections.items():
            try:
                # Get all documents from this source
                results = collection.get(where={"source_id": source_id})
                if results["ids"]:
                    # Delete documents
                    collection.delete(ids=results["ids"])
                    removed_count += len(results["ids"])
            except Exception as e:
                logger.warning(f"Failed to remove source data from {collection_type}: {e}")
        
        logger.info(f"🗑️ Removed {removed_count} documents from source: {source_id}")
    
    async def get_source_item_count(self, source_id: str) -> int:
        """Get the number of items from a specific source"""
        if not self.is_initialized:
            return 0
        
        if not CHROMADB_AVAILABLE:
            return 42  # Mock count
        
        total_count = 0
        for collection in self.collections.values():
            try:
                results = collection.get(where={"source_id": source_id})
                if results["ids"]:
                    total_count += len(results["ids"])
            except Exception as e:
                logger.warning(f"Failed to count items for source {source_id}: {e}")
        
        return total_count
    
    async def search_cross_collection(
        self,
        query: str,
        collection_types: List[str] = None,
        limit_per_collection: int = 5,
        similarity_threshold: float = 0.7
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple collections
        
        Args:
            query: Search query
            collection_types: Collections to search (all if None)
            limit_per_collection: Max results per collection
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            Dict mapping collection types to search results
        """
        if not collection_types:
            collection_types = list(self.collection_names.keys())
        
        results = {}
        for collection_type in collection_types:
            if collection_type in self.collections:
                collection_results = await self.search_similar(
                    query=query,
                    collection_type=collection_type,
                    limit=limit_per_collection,
                    similarity_threshold=similarity_threshold
                )
                if collection_results:
                    results[collection_type] = collection_results
        
        return results
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not self.embedding_model:
            # Return mock embeddings
            return [[0.1] * 384 for _ in texts]  # MiniLM has 384 dimensions
        
        try:
            embeddings = self.embedding_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.warning(f"Failed to generate embeddings: {e}")
            return [[0.1] * 384 for _ in texts]  # Fallback to mock embeddings
    
    async def get_collection_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all collections"""
        stats = {}
        
        if not CHROMADB_AVAILABLE:
            return {
                collection_type: {
                    "count": 100 + i * 50,
                    "status": "mock"
                }
                for i, collection_type in enumerate(self.collection_names.keys())
            }
        
        for collection_type, collection in self.collections.items():
            try:
                # Get collection count
                result = collection.get()
                count = len(result["ids"]) if result["ids"] else 0
                
                stats[collection_type] = {
                    "count": count,
                    "status": "active"
                }
            except Exception as e:
                stats[collection_type] = {
                    "count": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        return stats 