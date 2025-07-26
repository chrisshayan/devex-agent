"""
DevEx Ambient Agent - Main Application Entry Point
Following LangChain Academy ambient agent patterns with Knowledge Graph integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .core.ambient_orchestrator import AmbientOrchestrator
from .api.models import EventRequest, MorningBriefResponse
from .knowledge_graph.core.service import KnowledgeGraphService
from .knowledge_graph.core.models import (
    GoldenSourceConfig, KnowledgeQuery, SearchResults,
    IngestionResult, EvaluationResult, IngestionJob, CodeEvaluationRequest
)
from .config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DevEx Ambient Agent with Knowledge Graph",
    description="Ambient AI agent for enhanced developer experience with knowledge-driven insights",
    version="1.0.0"
)

# Configure CORS for IDE plugin communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
ambient_orchestrator: AmbientOrchestrator = None
knowledge_graph: KnowledgeGraphService = None

@app.on_event("startup")
async def startup_event():
    """Initialize ambient agent and knowledge graph on startup"""
    global ambient_orchestrator, knowledge_graph
    
    logger.info("🚀 Starting DevEx Ambient Agent with Knowledge Graph...")
    
    # Initialize Knowledge Graph Service
    knowledge_graph = KnowledgeGraphService()
    await knowledge_graph.initialize()
    
    # Initialize Ambient Orchestrator with Knowledge Graph service
    ambient_orchestrator = AmbientOrchestrator(knowledge_graph_service=knowledge_graph)
    await ambient_orchestrator.initialize()
    
    logger.info("✅ DevEx Ambient Agent with Knowledge Graph initialized and monitoring")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if ambient_orchestrator:
        await ambient_orchestrator.cleanup()
    if knowledge_graph:
        await knowledge_graph.cleanup()
    logger.info("👋 DevEx Ambient Agent shutdown complete")

# === Core Agent Endpoints ===

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "DevEx Ambient Agent with Knowledge Graph is running", 
        "status": "active",
        "features": ["ambient_monitoring", "knowledge_graph", "code_evaluation"]
    }

@app.post("/events/ingest")
async def ingest_event(event: EventRequest):
    """Receive events from IDE plugin or other sources"""
    try:
        logger.info(f"📥 Received event: {event.type} from {event.source}")
        
        # Process event through ambient orchestrator (which now has KG integration)
        result = await ambient_orchestrator.process_event(event.dict())
        
        return {
            "status": "success",
            "message": "Event processed successfully",
            "event_id": result.get("event_id"),
            "action_taken": result.get("action_taken", "queued_for_processing"),
            "kg_context_added": "kg_context" in result
        }
    except Exception as e:
        logger.error(f"❌ Error processing event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing event: {str(e)}")

@app.get("/brief/morning/{developer_id}")
async def get_morning_brief(developer_id: str) -> MorningBriefResponse:
    """Generate or retrieve morning brief for developer (now with KG insights)"""
    try:
        logger.info(f"📋 Generating morning brief for {developer_id}")
        
        brief_data = await ambient_orchestrator.generate_morning_brief(developer_id)
        
        return MorningBriefResponse(**brief_data)
    except Exception as e:
        logger.error(f"❌ Error generating morning brief: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating morning brief: {str(e)}"
        )

@app.get("/status/{developer_id}")
async def get_agent_status(developer_id: str):
    """Get current agent status for developer"""
    try:
        status = await ambient_orchestrator.get_agent_status(developer_id)
        
        # Add knowledge graph status
        if knowledge_graph.is_initialized:
            kg_sources = await knowledge_graph.list_golden_sources()
            status["knowledge_graph"] = {
                "initialized": True,
                "sources_count": len(kg_sources),
                "enabled_sources": len([s for s in kg_sources if s.enabled])
            }
        else:
            status["knowledge_graph"] = {"initialized": False}
        
        return status
    except Exception as e:
        logger.error(f"❌ Error getting agent status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

# === Knowledge Graph Endpoints ===

@app.post("/api/v1/knowledge-graph/sources")
async def register_golden_source(source_config: GoldenSourceConfig, background_tasks: BackgroundTasks):
    """Register a new golden source for ingestion"""
    try:
        logger.info(f"📚 Registering golden source: {source_config.type.value}")
        
        source_id = await knowledge_graph.register_golden_source(source_config)
        
        return {
            "status": "success",
            "source_id": source_id,
            "message": f"Golden source '{source_config.config.name}' registered successfully",
            "auto_sync": source_config.auto_sync
        }
    except Exception as e:
        logger.error(f"❌ Error registering golden source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering golden source: {str(e)}")

@app.get("/api/v1/knowledge-graph/sources")
async def list_golden_sources() -> List[GoldenSourceConfig]:
    """List all registered golden sources"""
    try:
        return await knowledge_graph.list_golden_sources()
    except Exception as e:
        logger.error(f"❌ Error listing golden sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing golden sources: {str(e)}")

@app.get("/api/v1/knowledge-graph/sources/{source_id}")
async def get_golden_source(source_id: str) -> GoldenSourceConfig:
    """Get a specific golden source configuration"""
    try:
        source = await knowledge_graph.get_golden_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Golden source not found: {source_id}")
        return source
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting golden source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting golden source: {str(e)}")

@app.put("/api/v1/knowledge-graph/sources/{source_id}")
async def update_golden_source(source_id: str, updates: Dict[str, Any]):
    """Update an existing golden source configuration"""
    try:
        success = await knowledge_graph.update_golden_source(source_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail=f"Golden source not found: {source_id}")
        
        return {
            "status": "success",
            "source_id": source_id,
            "message": "Golden source updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating golden source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating golden source: {str(e)}")

@app.delete("/api/v1/knowledge-graph/sources/{source_id}")
async def remove_golden_source(source_id: str):
    """Remove a golden source and all its data"""
    try:
        success = await knowledge_graph.remove_golden_source(source_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Golden source not found: {source_id}")
        
        return {
            "status": "success",
            "source_id": source_id,
            "message": "Golden source removed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error removing golden source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error removing golden source: {str(e)}")

@app.post("/api/v1/knowledge-graph/sources/{source_id}/ingest")
async def trigger_ingestion(source_id: str, background_tasks: BackgroundTasks, force: bool = False):
    """Trigger ingestion for a specific golden source"""
    try:
        logger.info(f"🚀 Triggering ingestion for source: {source_id}")
        
        # Run ingestion in background
        async def run_ingestion():
            try:
                await knowledge_graph.ingest_source(source_id, force=force)
                logger.info(f"✅ Background ingestion completed for source: {source_id}")
            except Exception as e:
                logger.error(f"❌ Background ingestion failed for source {source_id}: {e}")
        
        background_tasks.add_task(run_ingestion)
        
        return {
            "status": "success",
            "source_id": source_id,
            "message": "Ingestion started in background",
            "force": force
        }
    except Exception as e:
        logger.error(f"❌ Error triggering ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering ingestion: {str(e)}")

@app.get("/api/v1/knowledge-graph/sources/{source_id}/health")
async def get_source_health(source_id: str):
    """Get health status of a golden source"""
    try:
        health = await knowledge_graph.get_source_health(source_id)
        return health
    except Exception as e:
        logger.error(f"❌ Error getting source health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting source health: {str(e)}")

@app.get("/api/v1/knowledge-graph/jobs/{job_id}")
async def get_ingestion_status(job_id: str) -> IngestionJob:
    """Get the status of an ingestion job"""
    try:
        job = await knowledge_graph.get_ingestion_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Ingestion job not found: {job_id}")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting ingestion status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting ingestion status: {str(e)}")

# === Search and Retrieval Endpoints ===

@app.post("/api/v1/knowledge-graph/search")
async def search_knowledge(query: KnowledgeQuery) -> SearchResults:
    """Search across all knowledge sources"""
    try:
        logger.info(f"🔍 Knowledge search: '{query.query}' for {query.developer_id}")
        
        results = await knowledge_graph.search_knowledge(query)
        return results
    except Exception as e:
        logger.error(f"❌ Error searching knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching knowledge: {str(e)}")

@app.get("/api/v1/knowledge-graph/context/{developer_id}")
async def get_contextual_knowledge(
    developer_id: str,
    current_file: Optional[str] = None,
    project_path: Optional[str] = None,
    language: Optional[str] = None
):
    """Get contextual knowledge for current development situation"""
    try:
        context = await knowledge_graph.get_relevant_context(
            developer_id=developer_id,
            current_file=current_file,
            project_path=project_path,
            language=language
        )
        return context
    except Exception as e:
        logger.error(f"❌ Error getting contextual knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting contextual knowledge: {str(e)}")

@app.post("/api/v1/knowledge-graph/evaluate")
async def evaluate_code(request: CodeEvaluationRequest) -> EvaluationResult:
    """Evaluate code against golden source patterns"""
    try:
        logger.info(f"⚖️ Evaluating code for {request.developer_id}: {request.file_path}")
        
        result = await knowledge_graph.evaluate_code_against_golden_sources(
            developer_id=request.developer_id,
            code_content=request.code_content,
            file_path=request.file_path,
            language=request.language,
            context=request.context
        )
        return result
    except Exception as e:
        logger.error(f"❌ Error evaluating code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error evaluating code: {str(e)}")

# === Relationship and Analytics Endpoints ===

@app.get("/api/v1/knowledge-graph/relationships/{entity_id}")
async def get_relationships(entity_id: str):
    """Get relationships for an entity"""
    try:
        relationships = await knowledge_graph.get_relationships(entity_id)
        return {"entity_id": entity_id, "relationships": relationships}
    except Exception as e:
        logger.error(f"❌ Error getting relationships: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting relationships: {str(e)}")

@app.post("/api/v1/knowledge-graph/feedback")
async def submit_feedback(
    developer_id: str,
    feedback_type: str,
    target_id: str,
    rating: Optional[int] = None,
    comment: Optional[str] = None
):
    """Submit feedback about knowledge graph results"""
    try:
        # Store feedback in relational database
        feedback_data = {
            "developer_id": developer_id,
            "feedback_type": feedback_type,
            "target_id": target_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, this would be stored in the relational store
        logger.info(f"📝 Received feedback from {developer_id}: {feedback_type}")
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully"
        }
    except Exception as e:
        logger.error(f"❌ Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@app.get("/api/v1/knowledge-graph/analytics")
async def get_analytics(developer_id: Optional[str] = None):
    """Get usage analytics and statistics"""
    try:
        analytics = await knowledge_graph.get_usage_analytics(developer_id)
        return analytics
    except Exception as e:
        logger.error(f"❌ Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

# === Performance Monitoring Endpoints ===

@app.get("/api/v1/performance/stats")
async def get_performance_stats():
    """Get performance statistics for all operations"""
    try:
        from .knowledge_graph.utils.performance import get_performance_stats
        stats = get_performance_stats()
        return {
            "status": "success",
            "performance_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting performance stats: {str(e)}")

@app.get("/api/v1/performance/cache")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        from .knowledge_graph.utils.performance import get_cache_stats
        stats = get_cache_stats()
        return {
            "status": "success",
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

@app.post("/api/v1/performance/cache/clear")
async def clear_cache():
    """Clear all cached data"""
    try:
        from .knowledge_graph.utils.performance import clear_cache
        clear_cache()
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

# === Sync and Maintenance Endpoints ===

@app.post("/api/v1/knowledge-graph/sync-all")
async def sync_all_sources(background_tasks: BackgroundTasks):
    """Sync all auto-sync enabled sources"""
    try:
        background_tasks.add_task(knowledge_graph.sync_all_sources)
        
        return {
            "status": "success",
            "message": "Source synchronization started in background"
        }
    except Exception as e:
        logger.error(f"❌ Error starting sync: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting sync: {str(e)}")

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "devex_agent.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 