"""
Ambient Orchestrator - Core of the DevEx Ambient Agent
Implements LangGraph workflows for autonomous event processing
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging
import json
import uuid

from ..workflows.morning_brief_workflow import create_morning_brief_workflow
from ..config.settings import get_settings

logger = logging.getLogger(__name__)

class AmbientState:
    """State maintained by ambient agent for each developer"""
    
    def __init__(self, developer_id: str):
        self.developer_id = developer_id
        self.events: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.analysis_results: List[Dict[str, Any]] = []
        self.last_brief_generated: Optional[str] = None
        self.is_monitoring = True
        self.created_at = datetime.now().isoformat()
    
    def add_event(self, event: Dict[str, Any]) -> str:
        """Add an event and return event ID"""
        event_id = str(uuid.uuid4())
        event_with_id = {
            **event,
            "event_id": event_id,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event_with_id)
        
        # Keep only recent events to prevent memory bloat
        max_events = get_settings().max_events_per_developer
        if len(self.events) > max_events:
            self.events = self.events[-max_events:]
        
        return event_id
    
    def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get events from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = []
        
        for event in self.events:
            try:
                event_time = datetime.fromisoformat(event.get("timestamp", ""))
                if event_time >= cutoff:
                    recent_events.append(event)
            except (ValueError, TypeError):
                # Include events without valid timestamps
                recent_events.append(event)
        
        return recent_events


class AmbientOrchestrator:
    """
    Main coordinator for the DevEx Ambient Agent
    Manages state, processes events, and orchestrates workflows
    """
    
    def __init__(self):
        self.developer_states: Dict[str, AmbientState] = {}
        self.morning_brief_workflow = None
        self.settings = get_settings()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the ambient orchestrator"""
        try:
            # Initialize the morning brief workflow
            self.morning_brief_workflow = await create_morning_brief_workflow()
            self.is_initialized = True
            logger.info("🤖 Ambient Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ambient Orchestrator: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up Ambient Orchestrator...")
        self.is_initialized = False
        self.developer_states.clear()
    
    def _get_or_create_developer_state(self, developer_id: str) -> AmbientState:
        """Get or create state for a developer"""
        if developer_id not in self.developer_states:
            self.developer_states[developer_id] = AmbientState(developer_id)
            logger.info(f"👤 Created new state for developer: {developer_id}")
        return self.developer_states[developer_id]
    
    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming event from IDE or other sources
        This is the main entry point for ambient event processing
        """
        if not self.is_initialized:
            raise RuntimeError("Ambient Orchestrator not initialized")
        
        developer_id = event_data.get("developer_id")
        if not developer_id:
            raise ValueError("Event must include developer_id")
        
        # Get developer state
        state = self._get_or_create_developer_state(developer_id)
        
        # Add event to developer's history
        event_id = state.add_event(event_data)
        
        # Determine processing strategy based on event type and metadata
        action_taken = await self._determine_event_action(event_data, state)
        
        # Update context based on event
        await self._update_developer_context(event_data, state)
        
        logger.info(f"📝 Processed event {event_id} for {developer_id}: {action_taken}")
        
        return {
            "event_id": event_id,
            "action_taken": action_taken,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _determine_event_action(self, event_data: Dict[str, Any], state: AmbientState) -> str:
        """Determine what action to take based on the event"""
        event_type = event_data.get("type", "")
        metadata = event_data.get("metadata", {})
        
        # Critical events require immediate attention
        if (event_type == "error_event" and metadata.get("severity") == "critical") or \
           (event_type == "build_event" and metadata.get("build_status") == "failed"):
            return "immediate_analysis"
        
        # High-impact events get priority processing
        if event_type in ["build_event", "git_commit"] or \
           (event_type == "file_changed" and metadata.get("lines_added", 0) > 50):
            return "priority_processing"
        
        # Most events are queued for batch processing
        return "queued_for_processing"
    
    async def _update_developer_context(self, event_data: Dict[str, Any], state: AmbientState):
        """Update developer context based on new event"""
        context = state.context
        
        # Track project activity
        project_path = event_data.get("project_path")
        if project_path:
            if "active_projects" not in context:
                context["active_projects"] = set()
            context["active_projects"].add(project_path)
        
        # Track languages being used
        metadata = event_data.get("metadata", {})
        language = metadata.get("language")
        if language:
            if "languages_used" not in context:
                context["languages_used"] = set()
            context["languages_used"].add(language)
        
        # Track activity patterns
        event_type = event_data.get("type")
        if "event_counts" not in context:
            context["event_counts"] = {}
        context["event_counts"][event_type] = context["event_counts"].get(event_type, 0) + 1
        
        # Convert sets to lists for JSON serialization
        if "active_projects" in context:
            context["active_projects"] = list(context["active_projects"])
        if "languages_used" in context:
            context["languages_used"] = list(context["languages_used"])
    
    async def generate_morning_brief(self, developer_id: str) -> Dict[str, Any]:
        """Generate morning brief for a developer"""
        if not self.is_initialized:
            raise RuntimeError("Ambient Orchestrator not initialized")
        
        state = self._get_or_create_developer_state(developer_id)
        
        # Get recent events for analysis
        recent_events = state.get_recent_events(hours=24)
        
        if not recent_events:
            return self._generate_empty_brief(developer_id)
        
        try:
            # Use the morning brief workflow to generate insights
            brief_data = await self._run_morning_brief_workflow(developer_id, recent_events, state)
            
            # Update last brief timestamp
            state.last_brief_generated = datetime.now().isoformat()
            
            return brief_data
            
        except Exception as e:
            logger.error(f"Error generating morning brief for {developer_id}: {e}")
            return self._generate_error_brief(developer_id, str(e))
    
    def _generate_empty_brief(self, developer_id: str) -> Dict[str, Any]:
        """Generate a brief when no recent activity is found"""
        return {
            "developer_id": developer_id,
            "generated_at": datetime.now().isoformat(),
            "status": "success",
            "greeting": "Good morning! No recent development activity detected.",
            "summary": "No recent coding activity found. Ready to start a productive day!",
            "activity_overview": {
                "events_analyzed": 0,
                "time_period": "last 24 hours"
            },
            "critical_items": [],
            "suggestions": [
                {
                    "type": "productivity",
                    "title": "Start your day with a clear goal",
                    "description": "Consider reviewing your project roadmap and setting daily objectives",
                    "priority": "low"
                }
            ],
            "insights": {
                "message": "No recent activity to analyze"
            }
        }
    
    def _generate_error_brief(self, developer_id: str, error_message: str) -> Dict[str, Any]:
        """Generate a brief when there's an error in processing"""
        return {
            "developer_id": developer_id,
            "generated_at": datetime.now().isoformat(),
            "status": "error",
            "summary": f"Unable to generate morning brief: {error_message}",
            "activity_overview": {},
            "critical_items": [
                {
                    "type": "system_error",
                    "title": "Morning brief generation failed",
                    "description": f"Error: {error_message}",
                    "priority": "medium"
                }
            ],
            "suggestions": [],
            "insights": {}
        }
    
    async def _run_morning_brief_workflow(self, developer_id: str, events: List[Dict[str, Any]], state: AmbientState) -> Dict[str, Any]:
        """Run the LangGraph morning brief workflow"""
        
        # Prepare workflow input
        workflow_input = {
            "developer_id": developer_id,
            "events": events,
            "context": state.context,
            "analysis_results": state.analysis_results,
            "last_brief_generated": state.last_brief_generated
        }
        
        # For now, provide a mock implementation until LangGraph is fully integrated
        return await self._mock_morning_brief_workflow(workflow_input)
    
    async def _mock_morning_brief_workflow(self, workflow_input: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation of morning brief workflow"""
        developer_id = workflow_input["developer_id"]
        events = workflow_input["events"]
        context = workflow_input.get("context", {})
        
        # Analyze events
        file_changes = [e for e in events if e.get("type") == "file_changed"]
        git_commits = [e for e in events if e.get("type") == "git_commit"]
        build_events = [e for e in events if e.get("type") == "build_event"]
        error_events = [e for e in events if e.get("type") == "error_event"]
        
        # Generate activity overview
        activity_overview = {
            "total_events": len(events),
            "files_changed": len(file_changes),
            "commits_made": len(git_commits),
            "builds_triggered": len(build_events),
            "errors_encountered": len(error_events),
            "active_projects": len(context.get("active_projects", [])),
            "languages_used": context.get("languages_used", [])
        }
        
        # Generate suggestions based on activity
        suggestions = []
        
        if error_events:
            suggestions.append({
                "type": "error_resolution",
                "title": f"Address {len(error_events)} error(s)",
                "description": "Review and resolve recent errors to improve code stability",
                "priority": "high"
            })
        
        if file_changes and not git_commits:
            suggestions.append({
                "type": "version_control",
                "title": "Consider committing your changes",
                "description": f"You've modified {len(file_changes)} files without committing",
                "priority": "medium"
            })
        
        if len(file_changes) > 10:
            suggestions.append({
                "type": "code_review",
                "title": "Consider breaking down large changes",
                "description": "Large change sets can be harder to review and debug",
                "priority": "medium"
            })
        
        # Generate critical items
        critical_items = []
        
        failed_builds = [e for e in build_events if e.get("metadata", {}).get("build_status") == "failed"]
        if failed_builds:
            critical_items.append({
                "type": "build_failure",
                "title": f"{len(failed_builds)} build failure(s) detected",
                "description": "Recent builds have failed and need attention",
                "priority": "high"
            })
        
        critical_errors = [e for e in error_events if e.get("metadata", {}).get("severity") == "critical"]
        if critical_errors:
            critical_items.append({
                "type": "critical_error",
                "title": f"{len(critical_errors)} critical error(s)",
                "description": "Critical errors detected that need immediate attention",
                "priority": "critical"
            })
        
        # Generate summary
        summary_parts = []
        if file_changes:
            summary_parts.append(f"modified {len(file_changes)} files")
        if git_commits:
            summary_parts.append(f"made {len(git_commits)} commits")
        if build_events:
            summary_parts.append(f"triggered {len(build_events)} builds")
        
        if summary_parts:
            summary = f"Good morning! Yesterday you {', '.join(summary_parts)}."
        else:
            summary = "Good morning! Ready to start a productive coding session."
        
        return {
            "developer_id": developer_id,
            "generated_at": datetime.now().isoformat(),
            "status": "success",
            "greeting": "Good morning! Here's your development activity summary.",
            "summary": summary,
            "activity_overview": activity_overview,
            "critical_items": critical_items,
            "suggestions": suggestions,
            "insights": {
                "productivity_score": min(10, len(file_changes) + len(git_commits) * 2),
                "focus_areas": context.get("languages_used", []),
                "recent_activity_trend": "active" if len(events) > 5 else "light"
            }
        }
    
    async def get_agent_status(self, developer_id: str) -> Dict[str, Any]:
        """Get current status of the agent for a developer"""
        if not self.is_initialized:
            return {
                "status": "not_initialized",
                "message": "Agent not initialized",
                "events_count": 0,
                "is_monitoring": False
            }
        
        state = self.developer_states.get(developer_id)
        if not state:
            return {
                "status": "no_activity",
                "message": "No activity recorded for this developer",
                "events_count": 0,
                "is_monitoring": True
            }
        
        return {
            "status": "active",
            "message": "Agent monitoring and processing events",
            "events_count": len(state.events),
            "last_brief": state.last_brief_generated,
            "is_monitoring": state.is_monitoring,
            "active_projects": len(state.context.get("active_projects", [])),
            "languages_used": state.context.get("languages_used", [])
        } 