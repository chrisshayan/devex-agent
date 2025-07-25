"""
DevEx Ambient Agent - Main Application Entry Point
Following LangChain Academy ambient agent patterns
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Any
import logging

from .core.ambient_orchestrator import AmbientOrchestrator
from .api.models import EventRequest, MorningBriefResponse
from .config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DevEx Ambient Agent",
    description="Ambient AI agent for enhanced developer experience",
    version="0.1.0"
)

# Configure CORS for IDE plugin communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global ambient orchestrator instance
ambient_orchestrator: AmbientOrchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize ambient agent on startup"""
    global ambient_orchestrator
    ambient_orchestrator = AmbientOrchestrator()
    await ambient_orchestrator.initialize()
    logger.info("🚀 Starting DevEx Ambient Agent...")
    logger.info("✅ Ambient Agent initialized and monitoring")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if ambient_orchestrator:
        await ambient_orchestrator.cleanup()
    logger.info("👋 DevEx Ambient Agent shutdown complete")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "DevEx Ambient Agent is running", "status": "active"}

@app.post("/events/ingest")
async def ingest_event(event: EventRequest):
    """Receive events from IDE plugin or other sources"""
    try:
        logger.info(f"📥 Received event: {event.type} from {event.source}")
        
        # Process event through ambient orchestrator
        result = await ambient_orchestrator.process_event(event.dict())
        
        return {
            "status": "success",
            "message": "Event processed successfully",
            "event_id": result.get("event_id"),
            "action_taken": result.get("action_taken", "queued_for_processing")
        }
    except Exception as e:
        logger.error(f"❌ Error processing event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing event: {str(e)}")

@app.get("/brief/morning/{developer_id}")
async def get_morning_brief(developer_id: str) -> MorningBriefResponse:
    """Generate or retrieve morning brief for developer"""
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
        return status
    except Exception as e:
        logger.error(f"❌ Error getting agent status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "devex_agent.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 