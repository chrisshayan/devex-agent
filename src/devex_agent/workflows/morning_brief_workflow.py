"""
Morning Brief Workflow - LangGraph implementation
Following LangChain Academy ambient agent patterns
"""

from typing import Dict, Any, List, TypedDict, Annotated
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MorningBriefState(TypedDict):
    """State for morning brief generation workflow"""
    developer_id: str
    events: List[Dict[str, Any]]
    context: Dict[str, Any]
    analysis_results: List[Dict[str, Any]]
    last_brief_generated: str
    current_analysis: Dict[str, Any]
    generated_brief: Dict[str, Any]

class MorningBriefWorkflow:
    """
    Morning Brief Workflow implementation
    
    This is a simplified implementation that will be enhanced with
    LangGraph integration for more sophisticated ambient agent patterns.
    """
    
    def __init__(self):
        self.name = "morning_brief_workflow"
    
    async def analyze_events(self, state: MorningBriefState) -> Dict[str, Any]:
        """Analyze recent events for patterns and insights"""
        events = state["events"]
        context = state["context"]
        
        logger.info(f"🔍 Analyzing {len(events)} events for morning brief")
        
        # Basic event analysis
        analysis = {
            "event_summary": self._summarize_events(events),
            "productivity_metrics": self._calculate_productivity_metrics(events),
            "patterns_detected": self._detect_patterns(events),
            "context_insights": self._analyze_context(context)
        }
        
        return analysis
    
    def _summarize_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize events by type and significance"""
        summary = {
            "total_events": len(events),
            "event_types": {},
            "timespan": None
        }
        
        for event in events:
            event_type = event.get("type", "unknown")
            summary["event_types"][event_type] = summary["event_types"].get(event_type, 0) + 1
        
        # Calculate timespan
        if events:
            timestamps = []
            for event in events:
                try:
                    timestamp = datetime.fromisoformat(event.get("timestamp", ""))
                    timestamps.append(timestamp)
                except (ValueError, TypeError):
                    continue
            
            if timestamps:
                timestamps.sort()
                timespan_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
                summary["timespan"] = f"{timespan_hours:.1f} hours"
        
        return summary
    
    def _calculate_productivity_metrics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate productivity metrics from events"""
        file_changes = [e for e in events if e.get("type") == "file_changed"]
        git_commits = [e for e in events if e.get("type") == "git_commit"]
        build_events = [e for e in events if e.get("type") == "build_event"]
        
        # Calculate lines of code metrics
        total_lines_added = sum(
            e.get("metadata", {}).get("lines_added", 0) for e in file_changes
        )
        total_lines_deleted = sum(
            e.get("metadata", {}).get("lines_deleted", 0) for e in file_changes
        )
        
        # Calculate build success rate
        successful_builds = [
            e for e in build_events 
            if e.get("metadata", {}).get("build_status") == "success"
        ]
        build_success_rate = (
            len(successful_builds) / len(build_events) 
            if build_events else 1.0
        )
        
        return {
            "files_modified": len(file_changes),
            "commits_made": len(git_commits),
            "lines_added": total_lines_added,
            "lines_deleted": total_lines_deleted,
            "builds_attempted": len(build_events),
            "build_success_rate": build_success_rate,
            "productivity_score": self._calculate_productivity_score(
                file_changes, git_commits, build_events
            )
        }
    
    def _calculate_productivity_score(
        self, 
        file_changes: List[Dict[str, Any]], 
        git_commits: List[Dict[str, Any]], 
        build_events: List[Dict[str, Any]]
    ) -> float:
        """Calculate a simple productivity score (0-10)"""
        score = 0.0
        
        # Points for file changes (up to 3 points)
        score += min(3.0, len(file_changes) * 0.3)
        
        # Points for commits (up to 4 points)
        score += min(4.0, len(git_commits) * 0.8)
        
        # Points for successful builds (up to 3 points)
        successful_builds = [
            e for e in build_events 
            if e.get("metadata", {}).get("build_status") == "success"
        ]
        score += min(3.0, len(successful_builds) * 0.5)
        
        return min(10.0, score)
    
    def _detect_patterns(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect patterns in development activity"""
        patterns = []
        
        # Detect frequent file changes without commits
        file_changes = [e for e in events if e.get("type") == "file_changed"]
        git_commits = [e for e in events if e.get("type") == "git_commit"]
        
        if len(file_changes) > 5 and len(git_commits) == 0:
            patterns.append({
                "type": "uncommitted_changes",
                "description": "Many file changes without commits detected",
                "significance": "medium",
                "suggestion": "Consider committing changes more frequently"
            })
        
        # Detect build failures
        build_events = [e for e in events if e.get("type") == "build_event"]
        failed_builds = [
            e for e in build_events 
            if e.get("metadata", {}).get("build_status") == "failed"
        ]
        
        if failed_builds:
            patterns.append({
                "type": "build_failures",
                "description": f"{len(failed_builds)} build failures detected",
                "significance": "high",
                "suggestion": "Review and fix build issues"
            })
        
        # Detect error events
        error_events = [e for e in events if e.get("type") == "error_event"]
        if error_events:
            patterns.append({
                "type": "error_occurrences",
                "description": f"{len(error_events)} errors encountered",
                "significance": "high",
                "suggestion": "Address error conditions for stability"
            })
        
        # Detect high activity periods
        if len(events) > 20:
            patterns.append({
                "type": "high_activity",
                "description": "High development activity detected",
                "significance": "positive",
                "suggestion": "Great momentum! Consider regular breaks"
            })
        
        return patterns
    
    def _analyze_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze developer context for insights"""
        insights = {}
        
        # Analyze active projects
        active_projects = context.get("active_projects", [])
        if len(active_projects) > 1:
            insights["multi_project"] = {
                "count": len(active_projects),
                "suggestion": "Multiple projects detected - consider time boxing"
            }
        
        # Analyze language usage
        languages_used = context.get("languages_used", [])
        if len(languages_used) > 3:
            insights["language_diversity"] = {
                "languages": languages_used,
                "suggestion": "Working across multiple languages - great versatility!"
            }
        
        # Analyze event distribution
        event_counts = context.get("event_counts", {})
        if event_counts:
            most_common_event = max(event_counts.items(), key=lambda x: x[1])
            insights["primary_activity"] = {
                "type": most_common_event[0],
                "count": most_common_event[1],
                "message": f"Primary activity: {most_common_event[0]}"
            }
        
        return insights
    
    async def generate_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable suggestions based on analysis"""
        suggestions = []
        
        patterns = analysis.get("patterns_detected", [])
        productivity_metrics = analysis.get("productivity_metrics", {})
        context_insights = analysis.get("context_insights", {})
        
        # Suggestions based on patterns
        for pattern in patterns:
            if pattern["type"] == "uncommitted_changes":
                suggestions.append({
                    "type": "version_control",
                    "title": "Commit your changes",
                    "description": pattern["suggestion"],
                    "priority": "medium"
                })
            elif pattern["type"] == "build_failures":
                suggestions.append({
                    "type": "build_issues",
                    "title": "Fix build failures",
                    "description": pattern["suggestion"],
                    "priority": "high"
                })
            elif pattern["type"] == "error_occurrences":
                suggestions.append({
                    "type": "error_resolution",
                    "title": "Address errors",
                    "description": pattern["suggestion"],
                    "priority": "high"
                })
        
        # Suggestions based on productivity
        productivity_score = productivity_metrics.get("productivity_score", 0)
        if productivity_score < 3:
            suggestions.append({
                "type": "productivity",
                "title": "Increase development activity",
                "description": "Consider setting small, achievable coding goals",
                "priority": "low"
            })
        elif productivity_score > 8:
            suggestions.append({
                "type": "wellness",
                "title": "Great productivity! Remember to take breaks",
                "description": "High activity detected - ensure work-life balance",
                "priority": "low"
            })
        
        # Suggestions based on context
        if "multi_project" in context_insights:
            suggestions.append({
                "type": "focus",
                "title": "Consider project focus",
                "description": context_insights["multi_project"]["suggestion"],
                "priority": "medium"
            })
        
        return suggestions
    
    async def generate_brief(self, state: MorningBriefState) -> Dict[str, Any]:
        """Generate the final morning brief"""
        developer_id = state["developer_id"]
        events = state["events"]
        analysis = state.get("current_analysis", {})
        
        logger.info(f"📋 Generating morning brief for {developer_id}")
        
        # Extract analysis components
        event_summary = analysis.get("event_summary", {})
        productivity_metrics = analysis.get("productivity_metrics", {})
        patterns = analysis.get("patterns_detected", [])
        context_insights = analysis.get("context_insights", {})
        
        # Generate suggestions
        suggestions = await self.generate_suggestions(analysis)
        
        # Generate critical items
        critical_items = []
        for pattern in patterns:
            if pattern.get("significance") == "high":
                critical_items.append({
                    "type": pattern["type"],
                    "title": pattern["description"],
                    "description": pattern["suggestion"],
                    "priority": "high"
                })
        
        # Generate summary text
        summary = self._generate_summary_text(
            event_summary, productivity_metrics, patterns
        )
        
        # Build final brief
        brief = {
            "developer_id": developer_id,
            "generated_at": datetime.now().isoformat(),
            "status": "success",
            "greeting": "Good morning! Here's your development activity summary.",
            "summary": summary,
            "activity_overview": {
                **event_summary,
                **productivity_metrics
            },
            "critical_items": critical_items,
            "suggestions": suggestions,
            "insights": {
                "patterns_detected": len(patterns),
                "context_insights": context_insights,
                "productivity_score": productivity_metrics.get("productivity_score", 0),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
        
        return brief
    
    def _generate_summary_text(
        self, 
        event_summary: Dict[str, Any], 
        productivity_metrics: Dict[str, Any], 
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable summary text"""
        total_events = event_summary.get("total_events", 0)
        files_modified = productivity_metrics.get("files_modified", 0)
        commits_made = productivity_metrics.get("commits_made", 0)
        
        if total_events == 0:
            return "Good morning! No recent development activity detected. Ready to start fresh!"
        
        summary_parts = []
        
        if files_modified > 0:
            summary_parts.append(f"modified {files_modified} file{'s' if files_modified != 1 else ''}")
        
        if commits_made > 0:
            summary_parts.append(f"made {commits_made} commit{'s' if commits_made != 1 else ''}")
        
        # Add pattern-based insights
        high_significance_patterns = [p for p in patterns if p.get("significance") == "high"]
        if high_significance_patterns:
            summary_parts.append(f"encountered {len(high_significance_patterns)} issue{'s' if len(high_significance_patterns) != 1 else ''} requiring attention")
        
        if summary_parts:
            base_summary = f"Good morning! Recently you {', '.join(summary_parts)}."
        else:
            base_summary = "Good morning! Some development activity detected."
        
        # Add timespan if available
        timespan = event_summary.get("timespan")
        if timespan:
            base_summary += f" Activity span: {timespan}."
        
        return base_summary


async def create_morning_brief_workflow() -> MorningBriefWorkflow:
    """
    Create and return a morning brief workflow instance
    
    This function will be enhanced to return a full LangGraph workflow
    when LangGraph integration is implemented.
    """
    logger.info("🔄 Creating morning brief workflow")
    workflow = MorningBriefWorkflow()
    return workflow 