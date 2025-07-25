"""
API Models for DevEx Ambient Agent
Communication models between IntelliJ plugin and agent core
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class EventRequest(BaseModel):
    """Event data sent from IDE plugin to agent core"""
    type: str = Field(..., description="Type of event (file_changed, git_commit, build_event, etc.)")
    source: str = Field(..., description="Source of the event (intellij, git, build_system)")
    developer_id: str = Field(..., description="Unique identifier for the developer")
    project_path: Optional[str] = Field(None, description="Path to the project")
    file_path: Optional[str] = Field(None, description="Path to the affected file")
    description: Optional[str] = Field(None, description="Human-readable description of the event")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "file_changed",
                "source": "intellij",
                "developer_id": "alice@company.com",
                "project_path": "/home/alice/projects/my-app",
                "file_path": "src/main/java/com/example/UserService.java",
                "description": "Modified UserService.java - added new method",
                "metadata": {
                    "lines_changed": 25,
                    "change_type": "addition"
                }
            }
        }

class MorningBriefResponse(BaseModel):
    """Morning brief response model"""
    developer_id: str
    generated_at: str
    status: str = Field(..., description="Status of brief generation (success, error, partial)")
    greeting: Optional[str] = Field(None, description="Personalized greeting message")
    summary: str = Field(..., description="Brief summary of recent activity")
    
    activity_overview: Dict[str, Any] = Field(
        default_factory=dict,
        description="Overview of recent development activity"
    )
    
    critical_items: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="High priority items requiring immediate attention"
    )
    
    suggestions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Actionable suggestions for the developer"
    )
    
    insights: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional insights and observations"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "developer_id": "alice@company.com",
                "generated_at": "2024-01-15T08:00:00Z",
                "status": "success",
                "greeting": "Good morning! You've been productive recently.",
                "summary": "Good morning! Here's your development activity summary.",
                "activity_overview": {
                    "files_modified": 8,
                    "commits_made": 3,
                    "build_events": 2,
                    "hours_since_last_activity": 12.5
                },
                "critical_items": [
                    {
                        "type": "quality_concern",
                        "title": "Potential N+1 Query Detected",
                        "description": "Review database query in UserService.findAll()",
                        "action_required": True
                    }
                ],
                "suggestions": [
                    {
                        "type": "testing",
                        "priority": "high",
                        "title": "Add Test Coverage",
                        "description": "Consider adding tests for the new authentication method",
                        "action": "review_test_coverage"
                    }
                ],
                "insights": {
                    "quality_concerns": ["Database query optimization needed"],
                    "productivity_insights": ["Consistent commit patterns observed"],
                    "positive_patterns": ["Good separation of concerns in recent changes"]
                }
            }
        }

class AgentStatusResponse(BaseModel):
    """Agent status response model"""
    status: str = Field(..., description="Current agent status (active, inactive, error)")
    message: Optional[str] = Field(None, description="Status message")
    events_count: int = Field(0, description="Number of recent events")
    last_brief: Optional[str] = Field(None, description="Timestamp of last generated brief")
    pending_notifications: int = Field(0, description="Number of pending notifications")
    context_items: int = Field(0, description="Number of context items stored")
    is_monitoring: bool = Field(True, description="Whether ambient monitoring is active")

class TaskItem(BaseModel):
    """Task item for agent inbox"""
    id: str = Field(..., description="Unique task identifier")
    type: str = Field(..., description="Task type (suggestion, notification, review)")
    priority: str = Field(..., description="Task priority (low, medium, high, critical)")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    action: Optional[str] = Field(None, description="Recommended action")
    created_at: str = Field(..., description="Task creation timestamp")
    status: str = Field("pending", description="Task status (pending, in_progress, completed, dismissed)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")

class AgentInboxResponse(BaseModel):
    """Agent inbox response with tasks and notifications"""
    developer_id: str
    tasks: List[TaskItem] = Field(default_factory=list, description="List of tasks for the developer")
    notifications: List[Dict[str, Any]] = Field(default_factory=list, description="System notifications")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Inbox summary information")

class HealthCheckResponse(BaseModel):
    """Health check response"""
    message: str = "DevEx Ambient Agent is running"
    status: str = "active"
    version: str = "0.1.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Request models for plugin actions
class TaskUpdateRequest(BaseModel):
    """Request to update task status"""
    task_id: str
    status: str = Field(..., description="New task status")
    feedback: Optional[str] = Field(None, description="Optional feedback from developer")

class FeedbackRequest(BaseModel):
    """Feedback from developer about suggestions or brief quality"""
    type: str = Field(..., description="Feedback type (suggestion_rating, brief_quality, etc.)")
    target_id: str = Field(..., description="ID of the item being rated")
    rating: Optional[int] = Field(None, description="Rating (1-5 scale)")
    comment: Optional[str] = Field(None, description="Optional comment")
    developer_id: str = Field(..., description="Developer providing feedback") 