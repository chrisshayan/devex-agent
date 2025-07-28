"""
DevEx Ambient Agent - Main Application Entry Point
Following LangChain Academy ambient agent patterns with Knowledge Graph integration
"""

# Standard library imports
import logging
import uvicorn
from datetime import datetime
from typing import Dict, Any, List, Optional

# Third-party imports
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Local application imports
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
    description=(
        "Ambient AI agent for enhanced developer experience "
        "with knowledge-driven insights"
    ),
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
    ambient_orchestrator = AmbientOrchestrator(
        knowledge_graph_service=knowledge_graph
    )
    await ambient_orchestrator.initialize()
    
    logger.info(
        "✅ DevEx Ambient Agent with Knowledge Graph initialized and monitoring"
    )

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
        raise HTTPException(
            status_code=500, detail=f"Error processing event: {str(e)}"
        )

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


# ===== Phase 2: Career Coaching API Endpoints =====

@app.post("/api/v1/coaching/session/{developer_id}")
async def generate_coaching_session(
    developer_id: str,
    request: Dict[str, Any]
):
    """Generate a personalized coaching session using Expert Career Coach LLM"""
    try:
        # Extract request parameters
        current_skill_profile = request.get("current_skill_profile")
        recent_pattern_analysis = request.get("recent_pattern_analysis")
        current_code_context = request.get("current_code_context")
        learning_goals = request.get("learning_goals", [])
        time_availability = request.get("time_availability", "medium")
        career_stage = request.get("career_stage", "mid")
        specific_question = request.get("specific_question")
        
        logger.info(f"🎯 Generating coaching session for developer: {developer_id}")
        
        # Convert string values to enums
        from devex_agent.knowledge_graph.ml.models import CareerStage, CoachingTrigger
        
        career_stage_enum = CareerStage(career_stage) if career_stage else CareerStage.MID
        trigger_type = CoachingTrigger.ON_DEMAND
        
        coaching_session = await knowledge_graph.generate_coaching_session(
            developer_id=developer_id,
            current_skill_profile=current_skill_profile,
            recent_pattern_analysis=recent_pattern_analysis,
            current_code_context=current_code_context,
            learning_goals=learning_goals,
            time_availability=time_availability,
            career_stage=career_stage_enum,
            trigger_type=trigger_type,
            specific_question=specific_question
        )
        
        if coaching_session is None:
            return {
                "status": "unavailable",
                "message": "Career coaching not available - ML engines not initialized",
                "coaching_session": None
            }
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "coaching_session": coaching_session.dict() if hasattr(coaching_session, 'dict') else coaching_session,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating coaching session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating coaching session: {str(e)}")


@app.post("/api/v1/learning/plan/{developer_id}")
async def generate_learning_plan(
    developer_id: str,
    request: Dict[str, Any]
):
    """Generate a personalized learning plan using Learning Path Engine"""
    try:
        # Extract request parameters
        current_skills = request.get("current_skills", {})
        target_skills = request.get("target_skills", {})
        career_stage = request.get("career_stage", "mid")
        time_availability = request.get("time_availability", "medium")
        learning_style = request.get("learning_style", "mixed")
        learning_goals = request.get("learning_goals", [])
        timeline_weeks = request.get("timeline_weeks")
        
        if not target_skills:
            raise HTTPException(status_code=400, detail="Target skills are required")
        
        logger.info(f"📋 Generating learning plan for developer: {developer_id}")
        
        # Convert string values to enums
        from devex_agent.knowledge_graph.ml.models import (
            CareerStage, TimeAvailability, LearningStyle, SkillAssessment, SkillCategory
        )
        
        career_stage_enum = CareerStage(career_stage) if career_stage else CareerStage.MID
        time_availability_enum = TimeAvailability(time_availability.upper()) if time_availability else TimeAvailability.MEDIUM
        learning_style_enum = LearningStyle(learning_style.upper()) if learning_style else LearningStyle.MIXED
        
        # Convert current skills to SkillAssessment objects if needed
        skill_assessments = {}
        for skill_name, skill_data in current_skills.items():
            if isinstance(skill_data, dict):
                skill_assessments[skill_name] = SkillAssessment(
                    skill_name=skill_name,
                    category=SkillCategory(skill_data.get("category", "technical")),
                    level=skill_data.get("level", 0.5),
                    confidence=skill_data.get("confidence", 0.5),
                    evidence=skill_data.get("evidence", [])
                )
            else:
                # Assume it's a level value
                skill_assessments[skill_name] = SkillAssessment(
                    skill_name=skill_name,
                    category=SkillCategory.TECHNICAL,
                    level=float(skill_data),
                    confidence=0.7,
                    evidence=[]
                )
        
        learning_plan = await knowledge_graph.generate_learning_plan(
            developer_id=developer_id,
            current_skills=skill_assessments,
            target_skills=target_skills,
            career_stage=career_stage_enum,
            time_availability=time_availability_enum,
            learning_style=learning_style_enum,
            learning_goals=learning_goals,
            timeline_weeks=timeline_weeks
        )
        
        if learning_plan is None:
            return {
                "status": "unavailable",
                "message": "Learning plan generation not available - ML engines not initialized",
                "learning_plan": None
            }
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "learning_plan": learning_plan.dict() if hasattr(learning_plan, 'dict') else learning_plan,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating learning plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating learning plan: {str(e)}")


@app.post("/api/v1/progress/snapshot/{developer_id}")
async def record_progress_snapshot(
    developer_id: str,
    request: Dict[str, Any]
):
    """Record a progress snapshot for learning progress tracking"""
    try:
        # Extract request parameters
        current_skills = request.get("current_skills", {})
        learning_plan = request.get("learning_plan")
        completed_milestones = request.get("completed_milestones", [])
        notes = request.get("notes")
        
        if not current_skills:
            raise HTTPException(status_code=400, detail="Current skills are required")
        
        logger.info(f"📈 Recording progress snapshot for developer: {developer_id}")
        
        # Convert current skills to SkillAssessment objects
        from devex_agent.knowledge_graph.ml.models import SkillAssessment, SkillCategory
        
        skill_assessments = {}
        for skill_name, skill_data in current_skills.items():
            if isinstance(skill_data, dict):
                skill_assessments[skill_name] = SkillAssessment(
                    skill_name=skill_name,
                    category=SkillCategory(skill_data.get("category", "technical")),
                    level=skill_data.get("level", 0.5),
                    confidence=skill_data.get("confidence", 0.5),
                    evidence=skill_data.get("evidence", [])
                )
            else:
                skill_assessments[skill_name] = SkillAssessment(
                    skill_name=skill_name,
                    category=SkillCategory.TECHNICAL,
                    level=float(skill_data),
                    confidence=0.7,
                    evidence=[]
                )
        
        snapshot = await knowledge_graph.track_progress_snapshot(
            developer_id=developer_id,
            current_skills=skill_assessments,
            learning_plan=learning_plan,
            completed_milestones=completed_milestones,
            notes=notes
        )
        
        if snapshot is None:
            return {
                "status": "unavailable",
                "message": "Progress tracking not available - ML engines not initialized",
                "snapshot": None
            }
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "snapshot": snapshot.dict() if hasattr(snapshot, 'dict') else snapshot,
            "recorded_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error recording progress snapshot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error recording progress snapshot: {str(e)}")


@app.get("/api/v1/progress/analysis/{developer_id}")
async def analyze_learning_progress(
    developer_id: str,
    time_period_days: int = 90
):
    """Analyze learning progress trends for a developer"""
    try:
        logger.info(f"📊 Analyzing learning progress for developer: {developer_id}")
        
        progress_analysis = await knowledge_graph.analyze_learning_progress(
            developer_id=developer_id,
            time_period_days=time_period_days
        )
        
        if progress_analysis is None:
            return {
                "status": "unavailable",
                "message": "Progress analysis not available - ML engines not initialized",
                "analysis": None
            }
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "time_period_days": time_period_days,
            "analysis": progress_analysis,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing learning progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing learning progress: {str(e)}")


@app.post("/api/v1/progress/timeline/{developer_id}")
async def predict_learning_timeline(
    developer_id: str,
    request: Dict[str, Any]
):
    """Predict learning timeline for target skills based on current velocity"""
    try:
        # Extract request parameters
        target_skills = request.get("target_skills", {})
        confidence_level = request.get("confidence_level", 0.8)
        
        if not target_skills:
            raise HTTPException(status_code=400, detail="Target skills are required")
        
        logger.info(f"🔮 Predicting learning timeline for developer: {developer_id}")
        
        timeline_prediction = await knowledge_graph.predict_learning_timeline(
            developer_id=developer_id,
            target_skills=target_skills,
            confidence_level=confidence_level
        )
        
        if timeline_prediction is None:
            return {
                "status": "unavailable",
                "message": "Timeline prediction not available - ML engines not initialized",
                "prediction": None
            }
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "prediction": timeline_prediction,
            "predicted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error predicting learning timeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error predicting learning timeline: {str(e)}")


@app.get("/api/v1/coaching/history/{developer_id}")
async def get_coaching_history(
    developer_id: str,
    limit: int = 10
):
    """Get coaching session history for a developer"""
    try:
        logger.info(f"📚 Retrieving coaching history for developer: {developer_id}")
        
        coaching_history = await knowledge_graph.get_coaching_history(
            developer_id=developer_id,
            limit=limit
        )
        
        if coaching_history is None:
            return {
                "status": "unavailable",
                "message": "Coaching history not available - ML engines not initialized",
                "history": []
            }
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "history": [session.dict() if hasattr(session, 'dict') else session for session in coaching_history],
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving coaching history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving coaching history: {str(e)}")


@app.get("/api/v1/progress/alerts/{developer_id}")
async def get_progress_alerts(
    developer_id: str,
    include_resolved: bool = False
):
    """Get progress alerts for a developer"""
    try:
        logger.info(f"🚨 Retrieving progress alerts for developer: {developer_id}")
        
        alerts = await knowledge_graph.get_progress_alerts(
            developer_id=developer_id,
            include_resolved=include_resolved
        )
        
        if alerts is None:
            return {
                "status": "unavailable",
                "message": "Progress alerts not available - ML engines not initialized",
                "alerts": []
            }
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "alerts": [alert.dict() if hasattr(alert, 'dict') else alert for alert in alerts],
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving progress alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving progress alerts: {str(e)}")


# ===== ML & Developer Intelligence Endpoints =====

@app.post("/api/v1/ml/developer/{developer_id}/analyze")
async def analyze_developer_code(
    developer_id: str,
    request: Dict[str, Any]
):
    """Analyze developer's code patterns using CodeBERT"""
    try:
        code_snippets = request.get("code_snippets", [])
        file_paths = request.get("file_paths", [])
        
        if not code_snippets:
            raise HTTPException(status_code=400, detail="No code snippets provided")
        
        logger.info(f"🔍 Analyzing code for developer: {developer_id}")
        
        analysis = await knowledge_graph.analyze_developer_code(
            developer_id=developer_id,
            code_snippets=code_snippets,
            file_paths=file_paths
        )
        
        if analysis is None:
            return {
                "status": "unavailable",
                "message": "ML capabilities not available",
                "analysis": None
            }
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "analysis": analysis.dict() if hasattr(analysis, 'dict') else analysis,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing developer code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")


@app.post("/api/v1/ml/developer/{developer_id}/skills")
async def assess_developer_skills(
    developer_id: str,
    request: Dict[str, Any]
):
    """Assess developer skills using CodeBERT analysis"""
    try:
        code_snippets = request.get("code_snippets", [])
        
        if not code_snippets:
            raise HTTPException(status_code=400, detail="No code snippets provided")
        
        logger.info(f"📏 Assessing skills for developer: {developer_id}")
        
        skills = await knowledge_graph.assess_developer_skills(
            developer_id=developer_id,
            code_snippets=code_snippets
        )
        
        if skills is None:
            return {
                "status": "unavailable",
                "message": "ML capabilities not available",
                "skills": {}
            }
        
        # Convert skill assessments to dict format
        skills_dict = {}
        for skill_name, assessment in skills.items():
            skills_dict[skill_name] = assessment.dict() if hasattr(assessment, 'dict') else assessment
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "skills": skills_dict,
            "assessed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error assessing developer skills: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error assessing skills: {str(e)}")


@app.post("/api/v1/ml/code/similar")
async def find_similar_code(request: Dict[str, Any]):
    """Find similar code patterns using CodeBERT"""
    try:
        query_code = request.get("query_code", "")
        developer_id = request.get("developer_id")
        threshold = request.get("threshold", 0.7)
        
        if not query_code:
            raise HTTPException(status_code=400, detail="No query code provided")
        
        logger.info("🔍 Finding similar code patterns")
        
        similar_patterns = await knowledge_graph.find_similar_code_patterns(
            query_code=query_code,
            developer_id=developer_id,
            threshold=threshold
        )
        
        if similar_patterns is None:
            return {
                "status": "unavailable", 
                "message": "ML capabilities not available",
                "similar_patterns": []
            }
        
        return {
            "status": "success",
            "query_code": query_code[:100] + "..." if len(query_code) > 100 else query_code,
            "threshold": threshold,
            "similar_patterns": similar_patterns,
            "found_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error finding similar code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding similar code: {str(e)}")


@app.post("/api/v1/ml/code/embeddings")
async def generate_code_embeddings(request: Dict[str, Any]):
    """Generate CodeBERT embeddings for code snippets"""
    try:
        code_snippets = request.get("code_snippets", [])
        
        if not code_snippets:
            raise HTTPException(status_code=400, detail="No code snippets provided")
        
        logger.info(f"🔮 Generating embeddings for {len(code_snippets)} snippets")
        
        embeddings = await knowledge_graph.generate_code_embeddings(code_snippets)
        
        if embeddings is None:
            return {
                "status": "unavailable",
                "message": "ML capabilities not available", 
                "embeddings": []
            }
        
        return {
            "status": "success",
            "snippet_count": len(code_snippets),
            "embeddings": embeddings,
            "embedding_dimension": len(embeddings[0]) if embeddings else 0,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")

# === Advanced Analytics Endpoints ===

@app.get("/api/v1/analytics/developer/{developer_id}/dashboard")
async def get_developer_analytics_dashboard(
    developer_id: str,
    time_period_days: int = 180
):
    """Generate comprehensive analytics dashboard for a developer"""
    try:
        logger.info(f"📊 Generating analytics dashboard for {developer_id}")
        
        # Initialize analytics service if not already done
        from .knowledge_graph.ml.analytics_service import AnalyticsService
        from .knowledge_graph.ml.progress_tracker import ProgressTracker
        
        analytics_service = AnalyticsService()
        await analytics_service.initialize()
        
        # Generate dashboard
        dashboard = await analytics_service.generate_developer_dashboard(
            developer_id, time_period_days
        )
        
        await analytics_service.cleanup()
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "dashboard": dashboard.dict() if hasattr(dashboard, 'dict') else dashboard,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating analytics dashboard: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating analytics dashboard: {str(e)}"
        )

@app.get("/api/v1/analytics/developer/{developer_id}/skills/timeline")
async def get_skill_progression_timeline(
    developer_id: str,
    time_period_days: int = 180
):
    """Get detailed skill progression timeline for a developer"""
    try:
        logger.info(f"📈 Getting skill progression timeline for {developer_id}")
        
        # Initialize analytics service
        from .knowledge_graph.ml.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        await analytics_service.initialize()
        
        # Get skill progression data
        skill_progressions = await analytics_service.analyze_skill_progression_timeline(
            developer_id, time_period_days
        )
        
        await analytics_service.cleanup()
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "time_period_days": time_period_days,
            "skill_progressions": [
                progression.dict() if hasattr(progression, 'dict') else progression
                for progression in skill_progressions
            ],
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting skill timeline: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting skill timeline: {str(e)}"
        )

@app.get("/api/v1/analytics/developer/{developer_id}/code-quality/trends")
async def get_code_quality_trends(
    developer_id: str,
    time_period_days: int = 180
):
    """Get code quality trends and metrics for a developer"""
    try:
        logger.info(f"🔍 Getting code quality trends for {developer_id}")
        
        # Initialize analytics service
        from .knowledge_graph.ml.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        await analytics_service.initialize()
        
        # Get code quality metrics
        code_quality = await analytics_service.analyze_code_quality_metrics(
            developer_id, time_period_days
        )
        
        await analytics_service.cleanup()
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "time_period_days": time_period_days,
            "code_quality_metrics": code_quality.dict() if hasattr(code_quality, 'dict') else code_quality,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting code quality trends: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting code quality trends: {str(e)}"
        )

@app.get("/api/v1/analytics/developer/{developer_id}/learning/velocity")
async def get_learning_velocity_analytics(
    developer_id: str,
    time_period_days: int = 180
):
    """Get learning velocity and efficiency analytics for a developer"""
    try:
        logger.info(f"⚡ Getting learning velocity analytics for {developer_id}")
        
        # Initialize analytics service
        from .knowledge_graph.ml.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        await analytics_service.initialize()
        
        # Get learning velocity analytics
        velocity_analytics = await analytics_service.analyze_learning_velocity(
            developer_id, time_period_days
        )
        
        await analytics_service.cleanup()
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "time_period_days": time_period_days,
            "velocity_analytics": velocity_analytics.dict() if hasattr(velocity_analytics, 'dict') else velocity_analytics,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting learning velocity: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting learning velocity: {str(e)}"
        )

@app.get("/api/v1/analytics/developer/{developer_id}/coaching/impact")
async def get_coaching_impact_analysis(
    developer_id: str,
    time_period_days: int = 180
):
    """Get coaching impact and effectiveness analysis for a developer"""
    try:
        logger.info(f"🎯 Getting coaching impact analysis for {developer_id}")
        
        # Initialize analytics service
        from .knowledge_graph.ml.analytics_service import AnalyticsService
        
        analytics_service = AnalyticsService()
        await analytics_service.initialize()
        
        # Get coaching impact analysis
        coaching_impact = await analytics_service.analyze_coaching_impact(
            developer_id, time_period_days
        )
        
        await analytics_service.cleanup()
        
        return {
            "status": "success",
            "developer_id": developer_id,
            "time_period_days": time_period_days,
            "coaching_impact": coaching_impact.dict() if hasattr(coaching_impact, 'dict') else coaching_impact,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting coaching impact: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting coaching impact: {str(e)}"
        )

@app.get("/api/v1/analytics/team/benchmarks")
async def get_team_benchmarks(
    team_id: Optional[str] = None,
    skill_category: Optional[str] = None,
    time_period_days: int = 180
):
    """Get team-level benchmarking and comparative analytics"""
    try:
        logger.info(f"👥 Getting team benchmarks for team_id: {team_id}")
        
        # This would be implemented with real team data
        # For now, return simulated benchmark data
        
        return {
            "status": "success",
            "team_id": team_id,
            "skill_category": skill_category,
            "time_period_days": time_period_days,
            "benchmarks": {
                "team_average_skills": {
                    "python": 0.72,
                    "javascript": 0.68,
                    "testing": 0.65,
                    "architecture": 0.58
                },
                "skill_distribution": {
                    "beginner": 0.2,
                    "intermediate": 0.5,
                    "advanced": 0.3
                },
                "learning_velocity": {
                    "team_average": 0.45,
                    "top_performers": [
                        {"developer_id": "alex_chen", "velocity": 0.8},
                        {"developer_id": "sarah_kim", "velocity": 0.75}
                    ]
                },
                "coaching_effectiveness": {
                    "team_average_roi": 3.2,
                    "session_acceptance_rate": 0.78
                }
            },
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting team benchmarks: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting team benchmarks: {str(e)}"
        )

# === Demo Data Endpoints ===

@app.get("/api/v1/demo/alex-chen/journey")
async def get_alex_chen_demo_journey():
    """Generate and return Alex Chen's complete 18-month journey demo data"""
    try:
        logger.info("🎭 Generating Alex Chen demo journey data...")
        
        from .knowledge_graph.ml.demo_data_generator import AlexChenDemoGenerator
        
        # Generate the complete demo scenario
        demo_generator = AlexChenDemoGenerator()
        scenario = await demo_generator.generate_complete_demo_scenario()
        
        return {
            "status": "success",
            "demo_type": "alex_chen_18_month_journey", 
            "scenario": scenario.dict() if hasattr(scenario, 'dict') else scenario,
            "narrative_summary": {
                "title": "Alex Chen: From Junior to Senior Developer",
                "timeframe": "18 months",
                "key_achievements": [
                    "Career progression 1.8x faster than average",
                    "Code quality improvement: 60%",
                    "Test coverage: 20% → 85%",
                    "78% coaching suggestion acceptance rate"
                ],
                "phases": [
                    {"name": "Foundation Building", "months": "1-3", "focus": "basic_skills"},
                    {"name": "Accelerated Learning", "months": "4-9", "focus": "rapid_growth"},
                    {"name": "Leadership Emergence", "months": "10-15", "focus": "technical_leadership"},
                    {"name": "Senior Contributor", "months": "16-18", "focus": "organizational_impact"}
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating Alex Chen demo: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating demo data: {str(e)}"
        )

@app.get("/api/v1/demo/alex-chen/dashboard/{month}")
async def get_alex_chen_dashboard_for_month(
    month: int,
    analytics_type: str = "complete"
):
    """Get Alex Chen's analytics dashboard for a specific month"""
    try:
        if month < 1 or month > 18:
            raise HTTPException(status_code=400, detail="Month must be between 1 and 18")
        
        logger.info(f"📊 Generating Alex Chen dashboard for month {month}")
        
        from .knowledge_graph.ml.demo_data_generator import AlexChenDemoGenerator
        from .knowledge_graph.ml.analytics_service import AnalyticsService
        
        # Generate demo data up to the specified month
        demo_generator = AlexChenDemoGenerator()
        scenario = await demo_generator.generate_complete_demo_scenario()
        
        # Filter data up to the specified month
        relevant_snapshots = [
            snapshot for snapshot in scenario.monthly_snapshots 
            if (snapshot.timestamp - demo_generator.journey_start).days <= month * 30
        ]
        
        relevant_coaching = [
            session for session in scenario.coaching_sessions
            if (session.timestamp - demo_generator.journey_start).days <= month * 30
        ]
        
        # Calculate phase information
        phase_info = demo_generator._get_phase_for_month(month - 1)
        
        return {
            "status": "success",
            "developer_id": "alex_chen",
            "month": month,
            "phase": phase_info,
            "dashboard_data": {
                "current_skills": relevant_snapshots[-1].skill_levels if relevant_snapshots else {},
                "progress_summary": {
                    "total_snapshots": len(relevant_snapshots),
                    "coaching_sessions": len(relevant_coaching),
                    "milestones_completed": len(relevant_snapshots[-1].milestone_completions) if relevant_snapshots else 0,
                    "learning_plan_progress": relevant_snapshots[-1].learning_plan_progress if relevant_snapshots else 0.0
                },
                "phase_narrative": demo_generator.phases[phase_info]["narrative"],
                "recent_achievements": [
                    milestone for milestone in scenario.milestone_completions
                    if milestone["month"] <= month
                ][-3:],  # Last 3 achievements
                "velocity_metrics": relevant_snapshots[-1].velocity_metrics if relevant_snapshots else {},
                "engagement_metrics": relevant_snapshots[-1].engagement_metrics if relevant_snapshots else {}
            },
            "timeline_context": {
                "months_elapsed": month,
                "months_remaining": 18 - month,
                "completion_percentage": (month / 18) * 100,
                "next_phase": demo_generator._get_phase_for_month(month) if month < 18 else "completed"
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating monthly dashboard: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating monthly dashboard: {str(e)}"
        )

@app.get("/api/v1/demo/alex-chen/highlights")
async def get_alex_chen_demo_highlights():
    """Get key demo highlights and visualizations for Alex Chen's journey"""
    try:
        logger.info("🌟 Generating Alex Chen demo highlights...")
        
        return {
            "status": "success",
            "demo_highlights": {
                "career_progression": {
                    "title": "Career Acceleration",
                    "metric": "1.8x Faster Than Average",
                    "details": "Junior → Senior in 18 months vs typical 24-36 months",
                    "visualization": "timeline_comparison",
                    "impact_score": 95
                },
                "code_quality": {
                    "title": "Code Quality Transformation",
                    "metric": "60% Overall Improvement",
                    "details": {
                        "complexity": "Cyclomatic complexity: 15 → 6",
                        "test_coverage": "Test coverage: 20% → 85%",
                        "pattern_adoption": "Design patterns: 0 → 8 patterns"
                    },
                    "visualization": "before_after_metrics",
                    "impact_score": 88
                },
                "coaching_effectiveness": {
                    "title": "DevEx Coaching Impact",
                    "metric": "78% Suggestion Acceptance",
                    "details": "52 coaching sessions with measurable skill improvements",
                    "visualization": "trend_line_chart",
                    "impact_score": 92
                },
                "learning_velocity": {
                    "title": "Learning Acceleration",
                    "metric": "Peak 0.6 Skills/Month",
                    "details": {
                        "phase_1": "0.3 skills/month (foundation)",
                        "phase_2": "0.6 skills/month (peak learning)",
                        "phase_3": "0.4 skills/month (mastery focus)"
                    },
                    "visualization": "velocity_curve",
                    "impact_score": 85
                }
            },
            "narrative_moments": [
                {
                    "month": 3,
                    "title": "First Breakthrough",
                    "description": "DevEx coaching helps Alex overcome initial code review struggles",
                    "emotional_impact": "frustration_to_hope"
                },
                {
                    "month": 8,
                    "title": "Technical Confidence",
                    "description": "Successfully implements complex React feature with DevEx guidance",
                    "emotional_impact": "confidence_building"
                },
                {
                    "month": 14,
                    "title": "Leadership Emergence",
                    "description": "Takes ownership of architecture decisions and mentors junior developer",
                    "emotional_impact": "pride_and_responsibility"
                },
                {
                    "month": 18,
                    "title": "Senior Achievement",
                    "description": "Promotion to Senior Developer and recognition as technical leader",
                    "emotional_impact": "achievement_and_vision"
                }
            ],
            "roi_analysis": {
                "devex_investment": "Minimal setup + AI-powered guidance",
                "developer_acceleration": "18 months vs 30+ months typical",
                "productivity_gain": "Estimated 40% faster feature delivery",
                "retention_impact": "High - developer feels supported and growing"
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating demo highlights: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating demo highlights: {str(e)}"
        )


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "devex_agent.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 