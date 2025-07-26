"""
Ingestion Engine - Handles content ingestion from various sources (Stub Implementation)
"""

import logging
from typing import Dict, Any, Optional

from ..core.models import GoldenSourceConfig

logger = logging.getLogger(__name__)

class IngestionEngine:
    """
    Manages content ingestion from various golden sources (Stub Implementation)
    
    This is a stub implementation that provides the interface without
    actual ingestion functionality. Can be extended later.
    """
    
    def __init__(self, vector_store=None, graph_store=None, relational_store=None):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.relational_store = relational_store
        self.is_initialized = False
        logger.info("🔄 IngestionEngine initialized (stub implementation)")
    
    async def initialize(self):
        """Initialize the ingestion engine"""
        try:
            logger.info("🔄 Initializing Ingestion Engine (stub)...")
            self.is_initialized = True
            logger.info("✅ Ingestion Engine initialized successfully (stub)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ingestion Engine: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup ingestion engine resources"""
        logger.info("🧹 Cleaning up Ingestion Engine (stub)...")
        self.is_initialized = False
        logger.info("✅ Ingestion Engine cleanup complete (stub)")
    
    async def ingest_source(self, source_config: GoldenSourceConfig, connector=None, job=None) -> Dict[str, Any]:
        """Ingest content from a golden source"""
        logger.info(f"📥 Ingesting content from source: {source_config.id}")
        
        from ..core.models import IngestionResult
        from datetime import datetime
        import time
        
        start_time = time.time()
        items_ingested = 0
        items_failed = 0
        
        try:
            if not connector:
                raise ValueError("No connector provided for ingestion")
            
            # Extract content from the source using the connector
            logger.info(f"🔄 Extracting content using {type(connector).__name__}")
            extraction_result = await connector.extract_content()
            
            if "error" in extraction_result:
                raise Exception(extraction_result["error"])
            
            content_items = extraction_result.get("content", [])
            metadata = extraction_result.get("metadata", {})
            
            logger.info(f"📊 Extracted {len(content_items)} items from {source_config.id}")
            
            # Process each content item
            for item in content_items:
                try:
                    await self._process_content_item(item, source_config.id)
                    items_ingested += 1
                except Exception as e:
                    logger.error(f"❌ Failed to process item {item.get('id', 'unknown')}: {e}")
                    items_failed += 1
            
            # Update last sync time
            duration = time.time() - start_time
            
            result = IngestionResult(
                job_id=job.id if job else f"ingest_{source_config.id}_{int(time.time())}",
                success=True,
                items_ingested=items_ingested,
                items_failed=items_failed,
                duration_seconds=duration,
                summary={
                    "total_extracted": len(content_items),
                    "source_metadata": metadata,
                    "processed_successfully": items_ingested,
                    "processing_errors": items_failed
                }
            )
            
            logger.info(f"✅ Ingestion completed for source: {source_config.id} - {items_ingested} items processed")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ Ingestion failed for source: {source_config.id}: {e}")
            
            result = IngestionResult(
                job_id=job.id if job else f"ingest_{source_config.id}_{int(time.time())}",
                success=False,
                items_ingested=items_ingested,
                items_failed=items_failed + 1,
                duration_seconds=duration,
                error_message=str(e),
                summary={
                    "error": str(e),
                    "items_processed_before_error": items_ingested
                }
            )
            
            return result
    
    async def _process_content_item(self, item: Dict[str, Any], source_id: str):
        """Process a single content item and store it in the knowledge graph"""
        try:
            # Add to vector store for semantic search
            if self.vector_store:
                # Determine collection type based on item type
                collection_type = self._get_collection_type(item.get("type", "unknown"))
                
                # Prepare document for vector store
                doc = {
                    "id": item.get("id", f"item_{hash(item.get('content', ''))}"),
                    "content": item.get("content", ""),
                    "source_id": source_id,
                    "metadata": {
                        **item.get("metadata", {}),
                        "title": item.get("title", ""),
                        "file_path": item.get("file_path", ""),
                        "url": item.get("url", ""),
                        "type": item.get("type", ""),
                        "ingested_at": datetime.now().isoformat()
                    }
                }
                
                await self.vector_store.add_documents([doc], collection_type=collection_type)
            
            # Create entity in graph store
            if self.graph_store:
                entity_id = item.get("id", f"entity_{hash(item.get('content', ''))}")
                entity_type = item.get("type", "content")
                
                properties = {
                    "title": item.get("title", ""),
                    "content_preview": item.get("content", "")[:200],  # First 200 chars
                    "file_path": item.get("file_path", ""),
                    "url": item.get("url", ""),
                    **item.get("metadata", {})
                }
                
                await self.graph_store.create_entity(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    properties=properties,
                    source_id=source_id
                )
            
            logger.debug(f"📝 Processed content item: {item.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process content item: {e}")
            raise
    
    def _get_collection_type(self, item_type: str) -> str:
        """Map item type to vector store collection type"""
        type_mapping = {
            "code_file": "code_chunks",
            "documentation": "documentation",
            "readme": "documentation",
            "repository_metadata": "documentation",
            "issue": "documentation",
            "pull_request": "documentation",
            "wiki": "documentation"
        }
        
        return type_mapping.get(item_type, "documentation") 