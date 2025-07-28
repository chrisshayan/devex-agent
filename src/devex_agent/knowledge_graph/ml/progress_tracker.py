"""
Progress Tracking System - Monitors skill development and learning progress

Tracks and analyzes:
- Individual skill progression over time
- Learning milestone completion
- Learning plan adherence and adaptation
- Skill velocity and acceleration metrics
- Personalized progress insights and recommendations
"""

import logging
import asyncio
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass

from .models import (
    DeveloperSkillProfile, SkillAssessment, SkillTimeline, LearningPlan,
    LearningMilestone, CoachingSession, SkillEvolution, PatternAnalysis,
    CareerStage, SkillCategory, TrendDirection
)

# Import performance utilities
try:
    from ..utils.performance import cached, timed, run_parallel
    PERFORMANCE_UTILS_AVAILABLE = True
except ImportError:
    PERFORMANCE_UTILS_AVAILABLE = False
    def cached(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def timed(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


@dataclass
class ProgressSnapshot:
    """Point-in-time snapshot of developer progress"""
    snapshot_id: str
    developer_id: str
    timestamp: datetime
    skill_levels: Dict[str, float]  # skill_name -> level
    milestone_completions: List[str]  # completed milestone IDs
    learning_plan_progress: float  # 0.0 - 1.0
    velocity_metrics: Dict[str, float]
    engagement_metrics: Dict[str, Any]
    notes: Optional[str] = None


@dataclass
class LearningVelocity:
    """Learning velocity metrics for a developer"""
    developer_id: str
    time_period: str  # "weekly", "monthly", "quarterly"
    skills_improved: int
    average_skill_increase: float
    learning_consistency: float  # 0.0 - 1.0
    milestone_completion_rate: float
    engagement_score: float
    velocity_trend: TrendDirection


@dataclass
class ProgressAlert:
    """Alert for progress issues or achievements"""
    alert_id: str
    developer_id: str
    alert_type: str  # "milestone_overdue", "skill_plateau", "velocity_decline", "achievement"
    priority: str  # "low", "medium", "high", "critical"
    title: str
    description: str
    recommendations: List[str]
    created_at: datetime
    resolved: bool = False


class ProgressTracker:
    """
    Advanced progress tracking system for developer skill development
    
    Provides comprehensive tracking of:
    - Individual skill progression over time
    - Learning milestone achievement and delays
    - Learning velocity and acceleration analysis
    - Engagement and consistency metrics
    - Predictive progress insights and alerts
    """
    
    def __init__(self, 
                 snapshot_retention_days: int = 365,
                 velocity_calculation_window_days: int = 30):
        """
        Initialize Progress Tracker
        
        Args:
            snapshot_retention_days: How long to keep progress snapshots
            velocity_calculation_window_days: Window for velocity calculations
        """
        self.snapshot_retention_days = snapshot_retention_days
        self.velocity_window_days = velocity_calculation_window_days
        
        # Progress data storage (would be database in production)
        self.progress_snapshots: Dict[str, List[ProgressSnapshot]] = defaultdict(list)
        self.skill_timelines: Dict[str, List[SkillTimeline]] = defaultdict(list)
        self.milestone_tracking: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.learning_plans: Dict[str, LearningPlan] = {}
        self.progress_alerts: Dict[str, List[ProgressAlert]] = defaultdict(list)
        
        # Analytics caches
        self.velocity_cache: Dict[str, LearningVelocity] = {}
        self.trend_cache: Dict[str, Dict[str, Any]] = {}
        
        # Progress thresholds and rules
        self.progress_rules = self._initialize_progress_rules()
        
        self.is_initialized = False
        logger.info("📈 Progress Tracker initialized")
    
    async def initialize(self):
        """Initialize the Progress Tracker"""
        try:
            logger.info("🔄 Initializing Progress Tracker...")
            
            # Clean up old snapshots
            await self._cleanup_old_snapshots()
            
            self.is_initialized = True
            logger.info("✅ Progress Tracker initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Progress Tracker: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup Progress Tracker resources"""
        logger.info("🧹 Cleaning up Progress Tracker...")
        
        # Save important data before cleanup
        await self._save_progress_data()
        
        # Clear caches
        self.velocity_cache.clear()
        self.trend_cache.clear()
        
        self.is_initialized = False
        logger.info("✅ Progress Tracker cleanup complete")
    
    @timed(operation_name="progress_snapshot_recording")
    async def record_progress_snapshot(self, 
                                     developer_id: str,
                                     current_skills: Dict[str, SkillAssessment],
                                     learning_plan: Optional[LearningPlan] = None,
                                     completed_milestones: List[str] = None,
                                     notes: Optional[str] = None) -> ProgressSnapshot:
        """
        Record a progress snapshot for a developer
        
        Args:
            developer_id: Developer identifier
            current_skills: Current skill assessments
            learning_plan: Current learning plan
            completed_milestones: Recently completed milestone IDs
            notes: Optional progress notes
            
        Returns:
            ProgressSnapshot: The recorded snapshot
        """
        if not self.is_initialized:
            raise RuntimeError("Progress Tracker not initialized")
        
        logger.info(f"📸 Recording progress snapshot for {developer_id}")
        
        try:
            # Calculate skill levels
            skill_levels = {
                skill_name: assessment.level 
                for skill_name, assessment in current_skills.items()
            }
            
            # Calculate learning plan progress
            plan_progress = 0.0
            if learning_plan:
                plan_progress = learning_plan.progress_percentage / 100.0
            
            # Calculate velocity metrics
            velocity_metrics = await self._calculate_current_velocity(developer_id, current_skills)
            
            # Calculate engagement metrics
            engagement_metrics = await self._calculate_engagement_metrics(developer_id)
            
            # Create snapshot
            snapshot = ProgressSnapshot(
                snapshot_id=f"snapshot_{developer_id}_{int(datetime.now().timestamp())}",
                developer_id=developer_id,
                timestamp=datetime.now(),
                skill_levels=skill_levels,
                milestone_completions=completed_milestones or [],
                learning_plan_progress=plan_progress,
                velocity_metrics=velocity_metrics,
                engagement_metrics=engagement_metrics,
                notes=notes
            )
            
            # Store snapshot
            self.progress_snapshots[developer_id].append(snapshot)
            
            # Update skill timelines
            await self._update_skill_timelines(developer_id, current_skills)
            
            # Check for progress alerts
            await self._check_progress_alerts(developer_id, snapshot)
            
            # Update caches
            await self._update_velocity_cache(developer_id)
            
            logger.info(f"✅ Progress snapshot recorded for {developer_id}")
            return snapshot
            
        except Exception as e:
            logger.error(f"❌ Failed to record progress snapshot: {e}")
            raise
    
    async def track_milestone_completion(self, 
                                       developer_id: str,
                                       milestone_id: str,
                                       completion_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Track completion of a learning milestone
        
        Args:
            developer_id: Developer identifier
            milestone_id: Milestone identifier
            completion_notes: Optional completion notes
            
        Returns:
            Dict containing completion analysis
        """
        logger.info(f"🏁 Tracking milestone completion: {milestone_id} for {developer_id}")
        
        try:
            completion_time = datetime.now()
            
            # Record milestone completion
            if developer_id not in self.milestone_tracking:
                self.milestone_tracking[developer_id] = {}
            
            self.milestone_tracking[developer_id][milestone_id] = {
                "completed_at": completion_time,
                "notes": completion_notes,
                "completion_analysis": await self._analyze_milestone_completion(
                    developer_id, milestone_id, completion_time
                )
            }
            
            # Update learning plan progress if applicable
            await self._update_learning_plan_progress(developer_id, milestone_id)
            
            # Generate achievement alert
            await self._create_achievement_alert(developer_id, milestone_id)
            
            completion_data = self.milestone_tracking[developer_id][milestone_id]
            logger.info(f"✅ Milestone {milestone_id} completed by {developer_id}")
            
            return completion_data
            
        except Exception as e:
            logger.error(f"❌ Failed to track milestone completion: {e}")
            raise
    
    @cached(ttl=3600)  # Cache for 1 hour
    async def analyze_progress_trends(self, 
                                    developer_id: str,
                                    time_period_days: int = 90) -> Dict[str, Any]:
        """
        Analyze progress trends for a developer over a time period
        
        Args:
            developer_id: Developer identifier
            time_period_days: Analysis time period in days
            
        Returns:
            Dict containing trend analysis
        """
        logger.info(f"📊 Analyzing progress trends for {developer_id} over {time_period_days} days")
        
        try:
            # Get snapshots for the time period
            cutoff_date = datetime.now() - timedelta(days=time_period_days)
            snapshots = [
                s for s in self.progress_snapshots.get(developer_id, [])
                if s.timestamp >= cutoff_date
            ]
            
            if len(snapshots) < 2:
                return {"status": "insufficient_data", "snapshots_count": len(snapshots)}
            
            # Sort by timestamp
            snapshots.sort(key=lambda x: x.timestamp)
            
            # Analyze skill progression trends
            skill_trends = self._analyze_skill_trends(snapshots)
            
            # Analyze learning velocity trends
            velocity_trends = self._analyze_velocity_trends(snapshots)
            
            # Analyze milestone completion trends
            milestone_trends = self._analyze_milestone_trends(developer_id, time_period_days)
            
            # Calculate overall progress score
            overall_score = self._calculate_overall_progress_score(
                skill_trends, velocity_trends, milestone_trends
            )
            
            # Generate insights and recommendations
            insights = self._generate_progress_insights(
                skill_trends, velocity_trends, milestone_trends, overall_score
            )
            
            trend_analysis = {
                "developer_id": developer_id,
                "analysis_period": f"{time_period_days} days",
                "snapshots_analyzed": len(snapshots),
                "overall_progress_score": overall_score,
                "skill_trends": skill_trends,
                "velocity_trends": velocity_trends,
                "milestone_trends": milestone_trends,
                "insights": insights,
                "recommendations": self._generate_progress_recommendations(insights),
                "analyzed_at": datetime.now()
            }
            
            # Cache the results
            self.trend_cache[developer_id] = trend_analysis
            
            logger.info(f"✅ Progress trends analyzed for {developer_id}: score {overall_score:.2f}")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze progress trends: {e}")
            raise
    
    async def get_learning_velocity(self, 
                                  developer_id: str,
                                  recalculate: bool = False) -> Optional[LearningVelocity]:
        """
        Get current learning velocity for a developer
        
        Args:
            developer_id: Developer identifier
            recalculate: Force recalculation
            
        Returns:
            LearningVelocity or None if insufficient data
        """
        # Check cache first
        if not recalculate and developer_id in self.velocity_cache:
            cached_velocity = self.velocity_cache[developer_id]
            # Check if cache is still fresh (within velocity window)
            cache_age = datetime.now() - datetime.now()  # Placeholder for actual cache timestamp
            if cache_age.days < self.velocity_window_days:
                return cached_velocity
        
        logger.info(f"🚀 Calculating learning velocity for {developer_id}")
        
        try:
            # Get recent snapshots
            cutoff_date = datetime.now() - timedelta(days=self.velocity_window_days)
            snapshots = [
                s for s in self.progress_snapshots.get(developer_id, [])
                if s.timestamp >= cutoff_date
            ]
            
            if len(snapshots) < 2:
                logger.info(f"Insufficient data for velocity calculation: {len(snapshots)} snapshots")
                return None
            
            # Sort by timestamp
            snapshots.sort(key=lambda x: x.timestamp)
            first_snapshot = snapshots[0]
            last_snapshot = snapshots[-1]
            
            # Calculate skills improved
            skills_improved = 0
            total_skill_increase = 0.0
            skill_count = 0
            
            for skill_name in set(first_snapshot.skill_levels.keys()) | set(last_snapshot.skill_levels.keys()):
                first_level = first_snapshot.skill_levels.get(skill_name, 0.0)
                last_level = last_snapshot.skill_levels.get(skill_name, 0.0)
                
                if last_level > first_level:
                    skills_improved += 1
                    total_skill_increase += (last_level - first_level)
                    skill_count += 1
            
            average_skill_increase = total_skill_increase / skill_count if skill_count > 0 else 0.0
            
            # Calculate learning consistency
            consistency = self._calculate_learning_consistency(snapshots)
            
            # Calculate milestone completion rate
            milestone_rate = await self._calculate_milestone_completion_rate(developer_id)
            
            # Calculate engagement score
            engagement_score = self._calculate_average_engagement(snapshots)
            
            # Determine velocity trend
            velocity_trend = self._determine_velocity_trend(snapshots)
            
            velocity = LearningVelocity(
                developer_id=developer_id,
                time_period=f"{self.velocity_window_days} days",
                skills_improved=skills_improved,
                average_skill_increase=average_skill_increase,
                learning_consistency=consistency,
                milestone_completion_rate=milestone_rate,
                engagement_score=engagement_score,
                velocity_trend=velocity_trend
            )
            
            # Cache the result
            self.velocity_cache[developer_id] = velocity
            
            logger.info(f"✅ Learning velocity calculated for {developer_id}: {skills_improved} skills improved")
            return velocity
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate learning velocity: {e}")
            return None
    
    async def get_progress_alerts(self, 
                                developer_id: str,
                                include_resolved: bool = False) -> List[ProgressAlert]:
        """
        Get progress alerts for a developer
        
        Args:
            developer_id: Developer identifier
            include_resolved: Include resolved alerts
            
        Returns:
            List of ProgressAlert objects
        """
        alerts = self.progress_alerts.get(developer_id, [])
        
        if not include_resolved:
            alerts = [alert for alert in alerts if not alert.resolved]
        
        # Sort by priority and creation time
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        alerts.sort(
            key=lambda x: (priority_order.get(x.priority, 0), x.created_at),
            reverse=True
        )
        
        return alerts
    
    async def resolve_progress_alert(self, 
                                   alert_id: str,
                                   resolution_notes: Optional[str] = None) -> bool:
        """
        Resolve a progress alert
        
        Args:
            alert_id: Alert identifier
            resolution_notes: Optional resolution notes
            
        Returns:
            Boolean indicating success
        """
        try:
            # Find and resolve the alert
            for developer_id, alerts in self.progress_alerts.items():
                for alert in alerts:
                    if alert.alert_id == alert_id:
                        alert.resolved = True
                        alert.resolution_notes = resolution_notes
                        alert.resolved_at = datetime.now()
                        
                        logger.info(f"✅ Resolved progress alert: {alert_id}")
                        return True
            
            logger.warning(f"Alert not found: {alert_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to resolve alert: {e}")
            return False
    
    async def predict_learning_timeline(self, 
                                      developer_id: str,
                                      target_skills: Dict[str, float],
                                      confidence_level: float = 0.8) -> Dict[str, Any]:
        """
        Predict learning timeline based on current velocity and targets
        
        Args:
            developer_id: Developer identifier
            target_skills: Target skill levels
            confidence_level: Prediction confidence level
            
        Returns:
            Dict containing timeline predictions
        """
        logger.info(f"🔮 Predicting learning timeline for {developer_id}")
        
        try:
            # Get current skills and velocity
            current_snapshots = self.progress_snapshots.get(developer_id, [])
            if not current_snapshots:
                return {"status": "no_data", "message": "No progress data available"}
            
            latest_snapshot = max(current_snapshots, key=lambda x: x.timestamp)
            current_skills = latest_snapshot.skill_levels
            
            velocity = await self.get_learning_velocity(developer_id)
            if not velocity:
                return {"status": "insufficient_velocity_data"}
            
            # Calculate predictions for each target skill
            predictions = {}
            overall_timeline_weeks = 0
            
            for skill_name, target_level in target_skills.items():
                current_level = current_skills.get(skill_name, 0.0)
                
                if target_level <= current_level:
                    predictions[skill_name] = {
                        "current_level": current_level,
                        "target_level": target_level,
                        "weeks_to_target": 0,
                        "confidence": 1.0,
                        "status": "already_achieved"
                    }
                    continue
                
                # Calculate time to target based on velocity
                level_gap = target_level - current_level
                
                # Estimate based on average velocity (with confidence adjustment)
                if velocity.average_skill_increase > 0:
                    weeks_to_target = level_gap / (velocity.average_skill_increase / 4)  # Assuming weekly assessments
                    
                    # Adjust for consistency and engagement
                    consistency_factor = velocity.learning_consistency
                    engagement_factor = velocity.engagement_score
                    
                    adjustment_factor = (consistency_factor + engagement_factor) / 2
                    weeks_to_target = weeks_to_target / max(0.1, adjustment_factor)
                    
                    # Apply confidence level
                    if confidence_level < 1.0:
                        confidence_buffer = 1.0 + (1.0 - confidence_level)
                        weeks_to_target = weeks_to_target * confidence_buffer
                    
                    predictions[skill_name] = {
                        "current_level": current_level,
                        "target_level": target_level,
                        "weeks_to_target": int(weeks_to_target),
                        "confidence": min(1.0, velocity.learning_consistency * velocity.engagement_score),
                        "status": "prediction_available"
                    }
                    
                    overall_timeline_weeks = max(overall_timeline_weeks, int(weeks_to_target))
                else:
                    predictions[skill_name] = {
                        "current_level": current_level,
                        "target_level": target_level,
                        "weeks_to_target": None,
                        "confidence": 0.0,
                        "status": "insufficient_velocity_data"
                    }
            
            # Generate timeline insights
            insights = self._generate_timeline_insights(predictions, velocity)
            
            timeline_prediction = {
                "developer_id": developer_id,
                "overall_timeline_weeks": overall_timeline_weeks,
                "confidence_level": confidence_level,
                "skill_predictions": predictions,
                "velocity_basis": {
                    "skills_improved_recently": velocity.skills_improved,
                    "average_skill_increase": velocity.average_skill_increase,
                    "learning_consistency": velocity.learning_consistency,
                    "engagement_score": velocity.engagement_score
                },
                "insights": insights,
                "predicted_at": datetime.now()
            }
            
            logger.info(f"✅ Timeline predicted for {developer_id}: {overall_timeline_weeks} weeks overall")
            return timeline_prediction
            
        except Exception as e:
            logger.error(f"❌ Failed to predict learning timeline: {e}")
            raise
    
    # Private helper methods
    
    async def _calculate_current_velocity(self, 
                                        developer_id: str, 
                                        current_skills: Dict[str, SkillAssessment]) -> Dict[str, float]:
        """Calculate current velocity metrics"""
        
        # Get recent snapshots for velocity calculation
        recent_snapshots = [
            s for s in self.progress_snapshots.get(developer_id, [])
            if s.timestamp >= datetime.now() - timedelta(days=30)
        ]
        
        if len(recent_snapshots) < 2:
            return {"skills_per_week": 0.0, "average_improvement": 0.0, "velocity_score": 0.0}
        
        # Calculate basic velocity metrics
        time_span = (recent_snapshots[-1].timestamp - recent_snapshots[0].timestamp).days
        weeks = max(1, time_span / 7)
        
        # Count skill improvements
        skill_improvements = 0
        total_improvement = 0.0
        
        for skill_name, current_assessment in current_skills.items():
            for snapshot in recent_snapshots:
                if skill_name in snapshot.skill_levels:
                    old_level = snapshot.skill_levels[skill_name]
                    improvement = current_assessment.level - old_level
                    if improvement > 0.05:  # Minimum meaningful improvement
                        skill_improvements += 1
                        total_improvement += improvement
                    break
        
        velocity_metrics = {
            "skills_per_week": skill_improvements / weeks,
            "average_improvement": total_improvement / max(1, skill_improvements),
            "velocity_score": min(1.0, (skill_improvements / weeks) * 0.5)  # Normalized score
        }
        
        return velocity_metrics
    
    async def _calculate_engagement_metrics(self, developer_id: str) -> Dict[str, Any]:
        """Calculate engagement metrics"""
        
        # Basic engagement metrics (would be more sophisticated in production)
        recent_snapshots = [
            s for s in self.progress_snapshots.get(developer_id, [])
            if s.timestamp >= datetime.now() - timedelta(days=7)
        ]
        
        engagement_metrics = {
            "weekly_activity": len(recent_snapshots),
            "consistency_score": min(1.0, len(recent_snapshots) / 7),  # Expecting daily activity
            "engagement_trend": "stable"  # Would calculate actual trend
        }
        
        return engagement_metrics
    
    async def _update_skill_timelines(self, 
                                    developer_id: str, 
                                    current_skills: Dict[str, SkillAssessment]):
        """Update skill timelines with new assessments"""
        
        for skill_name, assessment in current_skills.items():
            # Create or update skill timeline
            existing_timelines = [
                tl for tl in self.skill_timelines[developer_id]
                if tl.skill_name == skill_name
            ]
            
            if existing_timelines:
                timeline = existing_timelines[0]
                # Add new assessment point
                timeline.timeline_points.append({
                    "timestamp": datetime.now().isoformat(),
                    "level": assessment.level,
                    "confidence": assessment.confidence,
                    "evidence": assessment.evidence
                })
                timeline.last_updated = datetime.now()
            else:
                # Create new timeline
                timeline = SkillTimeline(
                    developer_id=developer_id,
                    skill_name=skill_name,
                    skill_category=assessment.category,
                    timeline_points=[{
                        "timestamp": datetime.now().isoformat(),
                        "level": assessment.level,
                        "confidence": assessment.confidence,
                        "evidence": assessment.evidence
                    }],
                    trend=TrendDirection.STABLE,  # Would calculate actual trend
                    velocity=0.0,  # Would calculate actual velocity
                    first_assessed=datetime.now(),
                    last_updated=datetime.now()
                )
                self.skill_timelines[developer_id].append(timeline)
    
    async def _check_progress_alerts(self, developer_id: str, snapshot: ProgressSnapshot):
        """Check for progress alerts based on snapshot"""
        
        alerts = []
        
        # Check for skill plateaus
        skill_plateau_alerts = await self._check_skill_plateaus(developer_id, snapshot)
        alerts.extend(skill_plateau_alerts)
        
        # Check for velocity decline
        velocity_alert = await self._check_velocity_decline(developer_id, snapshot)
        if velocity_alert:
            alerts.append(velocity_alert)
        
        # Check for overdue milestones
        milestone_alerts = await self._check_overdue_milestones(developer_id)
        alerts.extend(milestone_alerts)
        
        # Add alerts to tracking
        self.progress_alerts[developer_id].extend(alerts)
    
    async def _check_skill_plateaus(self, 
                                  developer_id: str, 
                                  snapshot: ProgressSnapshot) -> List[ProgressAlert]:
        """Check for skill learning plateaus"""
        
        alerts = []
        plateau_threshold_days = 30
        
        # Get snapshots from plateau threshold period
        cutoff_date = datetime.now() - timedelta(days=plateau_threshold_days)
        recent_snapshots = [
            s for s in self.progress_snapshots.get(developer_id, [])
            if s.timestamp >= cutoff_date
        ]
        
        if len(recent_snapshots) < 3:
            return alerts
        
        # Check each skill for plateau
        for skill_name, current_level in snapshot.skill_levels.items():
            skill_levels = []
            for s in recent_snapshots:
                if skill_name in s.skill_levels:
                    skill_levels.append(s.skill_levels[skill_name])
            
            if len(skill_levels) >= 3:
                # Check if skill has plateaued (no significant change)
                level_range = max(skill_levels) - min(skill_levels)
                if level_range < 0.05:  # Less than 5% improvement
                    alert = ProgressAlert(
                        alert_id=f"plateau_{developer_id}_{skill_name}_{int(datetime.now().timestamp())}",
                        developer_id=developer_id,
                        alert_type="skill_plateau",
                        priority="medium",
                        title=f"Learning Plateau Detected: {skill_name}",
                        description=f"No significant improvement in {skill_name} over the last {plateau_threshold_days} days",
                        recommendations=[
                            f"Try different learning approaches for {skill_name}",
                            "Consider seeking mentorship or guidance",
                            "Take on more challenging projects involving this skill",
                            "Review and update learning resources"
                        ],
                        created_at=datetime.now()
                    )
                    alerts.append(alert)
        
        return alerts
    
    async def _check_velocity_decline(self, 
                                    developer_id: str, 
                                    snapshot: ProgressSnapshot) -> Optional[ProgressAlert]:
        """Check for learning velocity decline"""
        
        velocity = await self.get_learning_velocity(developer_id)
        if not velocity:
            return None
        
        # Check if velocity is declining
        if (velocity.velocity_trend == TrendDirection.DECLINING and 
            velocity.average_skill_increase < 0.1):
            
            return ProgressAlert(
                alert_id=f"velocity_{developer_id}_{int(datetime.now().timestamp())}",
                developer_id=developer_id,
                alert_type="velocity_decline",
                priority="high",
                title="Learning Velocity Decline",
                description="Your learning velocity has decreased significantly",
                recommendations=[
                    "Review your current learning plan and approach",
                    "Consider adjusting time allocation for learning",
                    "Seek feedback on your learning methods",
                    "Take breaks if experiencing learning fatigue"
                ],
                created_at=datetime.now()
            )
        
        return None
    
    async def _check_overdue_milestones(self, developer_id: str) -> List[ProgressAlert]:
        """Check for overdue learning milestones"""
        
        alerts = []
        current_plan = self.learning_plans.get(developer_id)
        
        if not current_plan:
            return alerts
        
        current_time = datetime.now()
        
        for milestone in current_plan.milestones:
            if (not milestone.completed and 
                milestone.deadline and 
                current_time > milestone.deadline):
                
                days_overdue = (current_time - milestone.deadline).days
                
                priority = "critical" if days_overdue > 14 else "high" if days_overdue > 7 else "medium"
                
                alert = ProgressAlert(
                    alert_id=f"overdue_{milestone.milestone_id}_{int(datetime.now().timestamp())}",
                    developer_id=developer_id,
                    alert_type="milestone_overdue",
                    priority=priority,
                    title=f"Overdue Milestone: {milestone.title}",
                    description=f"Milestone is {days_overdue} days overdue",
                    recommendations=[
                        "Review milestone requirements and progress",
                        "Adjust timeline expectations if needed",
                        "Focus on completing this milestone before moving forward",
                        "Consider breaking down the milestone into smaller tasks"
                    ],
                    created_at=datetime.now()
                )
                alerts.append(alert)
        
        return alerts
    
    async def _update_velocity_cache(self, developer_id: str):
        """Update velocity cache for a developer"""
        try:
            velocity = await self.get_learning_velocity(developer_id, recalculate=True)
            if velocity:
                self.velocity_cache[developer_id] = velocity
        except Exception as e:
            logger.debug(f"Failed to update velocity cache for {developer_id}: {e}")
    
    async def _analyze_milestone_completion(self, 
                                          developer_id: str, 
                                          milestone_id: str, 
                                          completion_time: datetime) -> Dict[str, Any]:
        """Analyze milestone completion performance"""
        
        # Get the milestone details
        current_plan = self.learning_plans.get(developer_id)
        if not current_plan:
            return {"status": "no_plan"}
        
        milestone = None
        for m in current_plan.milestones:
            if m.milestone_id == milestone_id:
                milestone = m
                break
        
        if not milestone:
            return {"status": "milestone_not_found"}
        
        analysis = {
            "milestone_id": milestone_id,
            "completed_at": completion_time,
            "scheduled_completion": milestone.deadline,
            "completion_status": "on_time"
        }
        
        if milestone.deadline:
            if completion_time <= milestone.deadline:
                days_early = (milestone.deadline - completion_time).days
                analysis["completion_status"] = "early" if days_early > 0 else "on_time"
                analysis["days_difference"] = days_early
            else:
                days_late = (completion_time - milestone.deadline).days
                analysis["completion_status"] = "late"
                analysis["days_difference"] = -days_late
        
        return analysis
    
    async def _update_learning_plan_progress(self, developer_id: str, milestone_id: str):
        """Update learning plan progress after milestone completion"""
        
        current_plan = self.learning_plans.get(developer_id)
        if not current_plan:
            return
        
        # Mark milestone as completed
        for milestone in current_plan.milestones:
            if milestone.milestone_id == milestone_id:
                milestone.completed = True
                milestone.completed_at = datetime.now()
                break
        
        # Recalculate overall progress
        total_milestones = len(current_plan.milestones)
        completed_milestones = sum(1 for m in current_plan.milestones if m.completed)
        
        if total_milestones > 0:
            current_plan.progress_percentage = (completed_milestones / total_milestones) * 100
    
    async def _create_achievement_alert(self, developer_id: str, milestone_id: str):
        """Create achievement alert for milestone completion"""
        
        alert = ProgressAlert(
            alert_id=f"achievement_{milestone_id}_{int(datetime.now().timestamp())}",
            developer_id=developer_id,
            alert_type="achievement",
            priority="low",
            title=f"Milestone Completed: {milestone_id}",
            description="Congratulations on completing this learning milestone!",
            recommendations=[
                "Continue with the next milestone in your learning plan",
                "Reflect on what you learned and how you can apply it",
                "Consider sharing your achievement with your team",
                "Update your skills profile with new capabilities"
            ],
            created_at=datetime.now()
        )
        
        self.progress_alerts[developer_id].append(alert)
    
    def _analyze_skill_trends(self, snapshots: List[ProgressSnapshot]) -> Dict[str, Any]:
        """Analyze skill progression trends from snapshots"""
        
        skill_trends = {}
        
        # Get all skills mentioned in snapshots
        all_skills = set()
        for snapshot in snapshots:
            all_skills.update(snapshot.skill_levels.keys())
        
        for skill_name in all_skills:
            skill_values = []
            timestamps = []
            
            for snapshot in snapshots:
                if skill_name in snapshot.skill_levels:
                    skill_values.append(snapshot.skill_levels[skill_name])
                    timestamps.append(snapshot.timestamp)
            
            if len(skill_values) >= 2:
                # Calculate trend
                first_value = skill_values[0]
                last_value = skill_values[-1]
                change = last_value - first_value
                
                # Calculate velocity (change per week)
                time_span = (timestamps[-1] - timestamps[0]).days / 7
                velocity = change / max(1, time_span)
                
                # Determine trend direction
                if abs(change) < 0.05:
                    trend = TrendDirection.STABLE
                elif change > 0:
                    trend = TrendDirection.IMPROVING
                else:
                    trend = TrendDirection.DECLINING
                
                skill_trends[skill_name] = {
                    "initial_level": first_value,
                    "current_level": last_value,
                    "total_change": change,
                    "weekly_velocity": velocity,
                    "trend": trend,
                    "data_points": len(skill_values)
                }
        
        return skill_trends
    
    def _analyze_velocity_trends(self, snapshots: List[ProgressSnapshot]) -> Dict[str, Any]:
        """Analyze velocity trends from snapshots"""
        
        velocities = []
        for snapshot in snapshots:
            if "velocity_score" in snapshot.velocity_metrics:
                velocities.append(snapshot.velocity_metrics["velocity_score"])
        
        if len(velocities) < 2:
            return {"status": "insufficient_data"}
        
        # Calculate velocity trend
        first_velocity = velocities[0]
        last_velocity = velocities[-1]
        velocity_change = last_velocity - first_velocity
        
        trend = TrendDirection.STABLE
        if abs(velocity_change) > 0.1:
            trend = TrendDirection.IMPROVING if velocity_change > 0 else TrendDirection.DECLINING
        
        return {
            "initial_velocity": first_velocity,
            "current_velocity": last_velocity,
            "velocity_change": velocity_change,
            "trend": trend,
            "average_velocity": sum(velocities) / len(velocities)
        }
    
    def _analyze_milestone_trends(self, developer_id: str, time_period_days: int) -> Dict[str, Any]:
        """Analyze milestone completion trends"""
        
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        
        milestone_data = self.milestone_tracking.get(developer_id, {})
        recent_completions = []
        
        for milestone_id, completion_data in milestone_data.items():
            completion_time = completion_data.get("completed_at")
            if completion_time and completion_time >= cutoff_date:
                recent_completions.append(completion_data)
        
        if not recent_completions:
            return {"status": "no_completions", "completions_count": 0}
        
        # Analyze completion performance
        on_time_count = 0
        early_count = 0
        late_count = 0
        
        for completion in recent_completions:
            analysis = completion.get("completion_analysis", {})
            status = analysis.get("completion_status", "unknown")
            
            if status == "on_time":
                on_time_count += 1
            elif status == "early":
                early_count += 1
            elif status == "late":
                late_count += 1
        
        total_completions = len(recent_completions)
        
        return {
            "completions_count": total_completions,
            "on_time_rate": on_time_count / total_completions,
            "early_rate": early_count / total_completions,
            "late_rate": late_count / total_completions,
            "completion_trend": "improving" if early_count > late_count else "declining" if late_count > early_count else "stable"
        }
    
    def _calculate_overall_progress_score(self, 
                                        skill_trends: Dict[str, Any],
                                        velocity_trends: Dict[str, Any],
                                        milestone_trends: Dict[str, Any]) -> float:
        """Calculate overall progress score"""
        
        score = 0.5  # Base score
        
        # Factor in skill trends
        improving_skills = sum(1 for trend in skill_trends.values() if trend.get("trend") == TrendDirection.IMPROVING)
        total_skills = len(skill_trends)
        
        if total_skills > 0:
            skill_score = improving_skills / total_skills
            score += skill_score * 0.3
        
        # Factor in velocity trends
        if velocity_trends.get("trend") == TrendDirection.IMPROVING:
            score += 0.2
        elif velocity_trends.get("trend") == TrendDirection.DECLINING:
            score -= 0.1
        
        # Factor in milestone trends
        on_time_rate = milestone_trends.get("on_time_rate", 0.5)
        score += (on_time_rate - 0.5) * 0.2
        
        return max(0.0, min(1.0, score))
    
    def _generate_progress_insights(self, 
                                  skill_trends: Dict[str, Any],
                                  velocity_trends: Dict[str, Any],
                                  milestone_trends: Dict[str, Any],
                                  overall_score: float) -> List[str]:
        """Generate progress insights"""
        
        insights = []
        
        # Overall performance insight
        if overall_score >= 0.8:
            insights.append("Excellent progress! You're consistently improving across multiple areas.")
        elif overall_score >= 0.6:
            insights.append("Good progress overall with room for optimization in some areas.")
        elif overall_score >= 0.4:
            insights.append("Moderate progress. Consider reviewing your learning approach.")
        else:
            insights.append("Progress is below expectations. It may be time to reassess your learning strategy.")
        
        # Skill-specific insights
        improving_skills = [name for name, trend in skill_trends.items() if trend.get("trend") == TrendDirection.IMPROVING]
        plateau_skills = [name for name, trend in skill_trends.items() if trend.get("trend") == TrendDirection.STABLE]
        
        if improving_skills:
            insights.append(f"Strong improvement in: {', '.join(improving_skills[:3])}")
        
        if plateau_skills:
            insights.append(f"Skills needing attention: {', '.join(plateau_skills[:3])}")
        
        # Velocity insights
        if velocity_trends.get("trend") == TrendDirection.IMPROVING:
            insights.append("Your learning velocity is increasing - great momentum!")
        elif velocity_trends.get("trend") == TrendDirection.DECLINING:
            insights.append("Learning velocity has decreased. Consider adjusting your approach.")
        
        # Milestone insights
        on_time_rate = milestone_trends.get("on_time_rate", 0.5)
        if on_time_rate >= 0.8:
            insights.append("Excellent milestone completion rate - you're staying on track!")
        elif on_time_rate < 0.5:
            insights.append("Milestone completion is behind schedule. Consider adjusting timelines.")
        
        return insights
    
    def _generate_progress_recommendations(self, insights: List[str]) -> List[str]:
        """Generate actionable recommendations based on insights"""
        
        recommendations = [
            "Continue with your current learning plan and maintain consistency",
            "Focus on practical application of newly learned skills",
            "Seek feedback from peers or mentors on your progress",
            "Document your learning journey and celebrate achievements"
        ]
        
        # Add specific recommendations based on insights
        if any("plateau" in insight.lower() or "attention" in insight.lower() for insight in insights):
            recommendations.extend([
                "Try different learning resources for skills that have plateaued",
                "Consider pair programming or collaborative learning",
                "Take on challenging projects that stretch your abilities"
            ])
        
        if any("velocity" in insight.lower() and "decreased" in insight.lower() for insight in insights):
            recommendations.extend([
                "Review your time allocation for learning activities",
                "Consider if learning fatigue is affecting your progress",
                "Break down complex topics into smaller, manageable chunks"
            ])
        
        if any("milestone" in insight.lower() and "behind" in insight.lower() for insight in insights):
            recommendations.extend([
                "Reassess milestone deadlines for realism",
                "Break large milestones into smaller, achievable goals",
                "Prioritize the most critical learning objectives"
            ])
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    def _calculate_learning_consistency(self, snapshots: List[ProgressSnapshot]) -> float:
        """Calculate learning consistency score"""
        
        if len(snapshots) < 3:
            return 0.5
        
        # Calculate consistency based on regular activity
        timestamps = [s.timestamp for s in snapshots]
        timestamps.sort()
        
        # Calculate intervals between snapshots
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).days
            intervals.append(interval)
        
        if not intervals:
            return 0.5
        
        # Consistency is higher when intervals are regular
        avg_interval = sum(intervals) / len(intervals)
        interval_variance = sum((interval - avg_interval) ** 2 for interval in intervals) / len(intervals)
        
        # Normalize consistency score (lower variance = higher consistency)
        consistency = 1.0 / (1.0 + interval_variance / max(1, avg_interval))
        
        return min(1.0, consistency)
    
    async def _calculate_milestone_completion_rate(self, developer_id: str) -> float:
        """Calculate milestone completion rate"""
        
        current_plan = self.learning_plans.get(developer_id)
        if not current_plan or not current_plan.milestones:
            return 0.0
        
        total_milestones = len(current_plan.milestones)
        completed_milestones = sum(1 for m in current_plan.milestones if m.completed)
        
        return completed_milestones / total_milestones
    
    def _calculate_average_engagement(self, snapshots: List[ProgressSnapshot]) -> float:
        """Calculate average engagement score from snapshots"""
        
        engagement_scores = []
        for snapshot in snapshots:
            engagement_data = snapshot.engagement_metrics
            if "consistency_score" in engagement_data:
                engagement_scores.append(engagement_data["consistency_score"])
        
        if not engagement_scores:
            return 0.5
        
        return sum(engagement_scores) / len(engagement_scores)
    
    def _determine_velocity_trend(self, snapshots: List[ProgressSnapshot]) -> TrendDirection:
        """Determine velocity trend from snapshots"""
        
        if len(snapshots) < 3:
            return TrendDirection.STABLE
        
        # Get velocity scores
        velocities = []
        for snapshot in snapshots:
            if "velocity_score" in snapshot.velocity_metrics:
                velocities.append(snapshot.velocity_metrics["velocity_score"])
        
        if len(velocities) < 3:
            return TrendDirection.STABLE
        
        # Calculate trend using simple linear regression slope
        n = len(velocities)
        sum_x = sum(range(n))
        sum_y = sum(velocities)
        sum_xy = sum(i * v for i, v in enumerate(velocities))
        sum_x2 = sum(i * i for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if slope > 0.05:
            return TrendDirection.IMPROVING
        elif slope < -0.05:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE
    
    def _generate_timeline_insights(self, 
                                  predictions: Dict[str, Any], 
                                  velocity: LearningVelocity) -> List[str]:
        """Generate insights for timeline predictions"""
        
        insights = []
        
        # Overall timeline insight
        total_weeks = max((p.get("weeks_to_target", 0) or 0) for p in predictions.values())
        if total_weeks <= 12:
            insights.append("Your learning goals are achievable within a reasonable timeframe.")
        elif total_weeks <= 24:
            insights.append("Your learning goals will require sustained effort over several months.")
        else:
            insights.append("Your learning goals are ambitious and may require timeline adjustments.")
        
        # Velocity-based insights
        if velocity.learning_consistency >= 0.8:
            insights.append("Your consistent learning pattern supports reliable timeline predictions.")
        else:
            insights.append("Improving learning consistency could help achieve targets faster.")
        
        if velocity.engagement_score >= 0.7:
            insights.append("High engagement levels suggest you'll likely meet your timeline goals.")
        else:
            insights.append("Consider strategies to increase engagement for better progress.")
        
        # Skill-specific insights
        fast_skills = [name for name, pred in predictions.items() 
                      if pred.get("weeks_to_target", 999) <= 8]
        slow_skills = [name for name, pred in predictions.items() 
                      if pred.get("weeks_to_target", 0) >= 20]
        
        if fast_skills:
            insights.append(f"Quick wins expected in: {', '.join(fast_skills[:3])}")
        
        if slow_skills:
            insights.append(f"Long-term focus needed for: {', '.join(slow_skills[:3])}")
        
        return insights
    
    async def _cleanup_old_snapshots(self):
        """Clean up old progress snapshots"""
        
        cutoff_date = datetime.now() - timedelta(days=self.snapshot_retention_days)
        
        for developer_id in self.progress_snapshots:
            self.progress_snapshots[developer_id] = [
                snapshot for snapshot in self.progress_snapshots[developer_id]
                if snapshot.timestamp >= cutoff_date
            ]
    
    async def _save_progress_data(self):
        """Save progress data to persistent storage"""
        # Implementation placeholder - would save to database
        logger.info("💾 Saving progress data to persistent storage")
    
    def _initialize_progress_rules(self) -> Dict[str, Any]:
        """Initialize progress tracking rules and thresholds"""
        return {
            "plateau_threshold_days": 30,
            "velocity_decline_threshold": 0.1,
            "milestone_overdue_grace_days": 3,
            "minimum_snapshots_for_analysis": 5,
            "engagement_low_threshold": 0.3,
            "consistency_low_threshold": 0.4
        } 
    
    # ===== Analytics Aggregation Methods =====
    
    async def get_developer_snapshots_for_analytics(self, 
                                                   developer_id: str,
                                                   time_period_days: int = 180) -> List[ProgressSnapshot]:
        """Get progress snapshots for analytics calculations"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period_days)
            
            snapshots = []
            for snapshot in self.progress_snapshots.get(developer_id, []):
                if start_date <= snapshot.timestamp <= end_date:
                    snapshots.append(snapshot)
            
            # Sort by timestamp
            snapshots.sort(key=lambda x: x.timestamp)
            
            logger.info(f"📊 Retrieved {len(snapshots)} snapshots for analytics for {developer_id}")
            return snapshots
            
        except Exception as e:
            logger.error(f"❌ Failed to get snapshots for analytics: {e}")
            return []
    
    async def calculate_skill_progression_stats(self, 
                                              developer_id: str,
                                              skill_name: str,
                                              time_period_days: int = 180) -> Dict[str, Any]:
        """Calculate detailed skill progression statistics"""
        try:
            snapshots = await self.get_developer_snapshots_for_analytics(developer_id, time_period_days)
            
            if len(snapshots) < 2:
                return {"error": "insufficient_data", "snapshots_count": len(snapshots)}
            
            # Extract skill level progression
            skill_progression = []
            for snapshot in snapshots:
                if skill_name in snapshot.skill_levels:
                    skill_progression.append({
                        "timestamp": snapshot.timestamp,
                        "level": snapshot.skill_levels[skill_name],
                        "velocity": snapshot.velocity_metrics.get(skill_name, 0.0)
                    })
            
            if len(skill_progression) < 2:
                return {"error": "insufficient_skill_data", "data_points": len(skill_progression)}
            
            # Calculate statistics
            levels = [point["level"] for point in skill_progression]
            velocities = [point["velocity"] for point in skill_progression]
            
            stats = {
                "total_improvement": levels[-1] - levels[0],
                "average_level": sum(levels) / len(levels),
                "peak_level": max(levels),
                "current_level": levels[-1],
                "average_velocity": sum(velocities) / len(velocities),
                "peak_velocity": max(velocities),
                "improvement_periods": self._identify_improvement_periods(skill_progression),
                "plateau_periods": self._identify_plateau_periods_detailed(skill_progression),
                "consistency_score": self._calculate_skill_consistency(levels),
                "trend_direction": self._determine_skill_trend(levels),
                "data_points": len(skill_progression),
                "time_span_days": (skill_progression[-1]["timestamp"] - skill_progression[0]["timestamp"]).days
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate skill progression stats: {e}")
            return {"error": str(e)}
    
    async def calculate_learning_efficiency_metrics(self, 
                                                   developer_id: str,
                                                   time_period_days: int = 180) -> Dict[str, Any]:
        """Calculate learning efficiency and effectiveness metrics"""
        try:
            snapshots = await self.get_developer_snapshots_for_analytics(developer_id, time_period_days)
            
            if len(snapshots) < 3:
                return {"error": "insufficient_data", "snapshots_count": len(snapshots)}
            
            # Calculate time-based efficiency metrics
            total_time_spent = 0
            total_skill_improvement = 0
            engagement_scores = []
            consistency_scores = []
            
            for i in range(1, len(snapshots)):
                prev_snapshot = snapshots[i-1]
                curr_snapshot = snapshots[i]
                
                # Calculate skill improvements
                skill_improvement = 0
                skill_count = 0
                for skill, level in curr_snapshot.skill_levels.items():
                    prev_level = prev_snapshot.skill_levels.get(skill, 0.0)
                    improvement = max(0, level - prev_level)
                    skill_improvement += improvement
                    skill_count += 1
                
                if skill_count > 0:
                    total_skill_improvement += skill_improvement / skill_count
                
                # Add time spent
                time_spent = curr_snapshot.engagement_metrics.get("time_spent_hours", 0)
                total_time_spent += time_spent
                
                # Collect engagement and consistency scores
                engagement = curr_snapshot.engagement_metrics.get("consistency_score", 0.7)
                engagement_scores.append(engagement)
                
                consistency = curr_snapshot.engagement_metrics.get("consistency_score", 0.7)
                consistency_scores.append(consistency)
            
            # Calculate efficiency metrics
            efficiency_metrics = {
                "skill_improvement_per_hour": (total_skill_improvement / max(total_time_spent, 1)) * 100,
                "total_skill_improvement": total_skill_improvement,
                "total_time_spent_hours": total_time_spent,
                "average_engagement": sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0,
                "engagement_consistency": self._calculate_consistency(engagement_scores),
                "learning_consistency": sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0,
                "efficiency_trend": self._calculate_efficiency_trend(snapshots),
                "peak_learning_periods": await self._identify_peak_learning_periods(snapshots),
                "learning_velocity_distribution": self._analyze_velocity_distribution(snapshots)
            }
            
            return efficiency_metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate learning efficiency: {e}")
            return {"error": str(e)}
    
    async def calculate_milestone_completion_analytics(self, 
                                                     developer_id: str,
                                                     time_period_days: int = 180) -> Dict[str, Any]:
        """Calculate milestone completion analytics"""
        try:
            snapshots = await self.get_developer_snapshots_for_analytics(developer_id, time_period_days)
            
            if not snapshots:
                return {"error": "no_data", "snapshots_count": 0}
            
            # Analyze milestone completion patterns
            all_milestones = set()
            milestone_completions_by_month = defaultdict(list)
            
            for snapshot in snapshots:
                # Group milestones by month
                month_key = snapshot.timestamp.strftime("%Y-%m")
                milestone_completions_by_month[month_key].extend(snapshot.milestone_completions)
                all_milestones.update(snapshot.milestone_completions)
            
            # Calculate completion rates and patterns
            total_milestones = len(all_milestones)
            completion_timeline = []
            
            for month, milestones in sorted(milestone_completions_by_month.items()):
                completion_timeline.append({
                    "month": month,
                    "milestones_completed": len(set(milestones)),
                    "completion_rate": len(set(milestones)) / max(total_milestones, 1),
                    "milestone_list": list(set(milestones))
                })
            
            # Calculate analytics
            completion_analytics = {
                "total_milestones": total_milestones,
                "completion_timeline": completion_timeline,
                "average_milestones_per_month": total_milestones / max(len(milestone_completions_by_month), 1),
                "milestone_completion_acceleration": self._calculate_milestone_acceleration(completion_timeline),
                "consistency_in_completion": self._calculate_milestone_consistency(completion_timeline),
                "peak_completion_months": self._identify_peak_completion_months(completion_timeline),
                "completion_velocity_trend": self._analyze_completion_velocity_trend(completion_timeline)
            }
            
            return completion_analytics
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate milestone analytics: {e}")
            return {"error": str(e)}
    
    async def generate_comparative_analytics(self, 
                                           developer_id: str,
                                           comparison_group: List[str] = None,
                                           time_period_days: int = 180) -> Dict[str, Any]:
        """Generate comparative analytics against peer group"""
        try:
            # Get developer's data
            developer_snapshots = await self.get_developer_snapshots_for_analytics(developer_id, time_period_days)
            
            if not developer_snapshots:
                return {"error": "no_developer_data"}
            
            # For now, generate simulated peer comparison data
            # In practice, this would compare against real peer data
            developer_metrics = await self._calculate_aggregate_metrics(developer_snapshots)
            
            # Simulated peer benchmarks (would be calculated from real data)
            peer_benchmarks = {
                "average_skill_level": 0.65,
                "average_learning_velocity": 0.05,
                "average_milestone_completion_rate": 0.7,
                "average_engagement_score": 0.72,
                "average_consistency_score": 0.68
            }
            
            # Calculate comparative scores
            comparative_analytics = {
                "developer_metrics": developer_metrics,
                "peer_benchmarks": peer_benchmarks,
                "comparative_scores": {
                    "skill_level_percentile": self._calculate_percentile(
                        developer_metrics["average_skill_level"], 
                        peer_benchmarks["average_skill_level"]
                    ),
                    "learning_velocity_percentile": self._calculate_percentile(
                        developer_metrics["average_learning_velocity"],
                        peer_benchmarks["average_learning_velocity"]
                    ),
                    "milestone_completion_percentile": self._calculate_percentile(
                        developer_metrics["milestone_completion_rate"],
                        peer_benchmarks["average_milestone_completion_rate"]
                    ),
                    "engagement_percentile": self._calculate_percentile(
                        developer_metrics["engagement_score"],
                        peer_benchmarks["average_engagement_score"]
                    )
                },
                "strength_areas": self._identify_strength_areas(developer_metrics, peer_benchmarks),
                "improvement_opportunities": self._identify_improvement_opportunities(developer_metrics, peer_benchmarks),
                "overall_performance_score": self._calculate_overall_performance_score(developer_metrics, peer_benchmarks)
            }
            
            return comparative_analytics
            
        except Exception as e:
            logger.error(f"❌ Failed to generate comparative analytics: {e}")
            return {"error": str(e)}
    
    # ===== Helper Methods for Analytics =====
    
    def _identify_improvement_periods(self, skill_progression: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify periods of significant skill improvement"""
        improvement_periods = []
        improvement_threshold = 0.1  # 10% improvement threshold
        
        for i in range(1, len(skill_progression)):
            prev_level = skill_progression[i-1]["level"]
            curr_level = skill_progression[i]["level"]
            improvement = curr_level - prev_level
            
            if improvement > improvement_threshold:
                improvement_periods.append({
                    "start_date": skill_progression[i-1]["timestamp"],
                    "end_date": skill_progression[i]["timestamp"],
                    "improvement": improvement,
                    "start_level": prev_level,
                    "end_level": curr_level
                })
        
        return improvement_periods
    
    def _identify_plateau_periods_detailed(self, skill_progression: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify detailed plateau periods in skill progression"""
        plateau_periods = []
        plateau_threshold = 0.05  # 5% change threshold
        min_plateau_duration = 2  # Minimum 2 data points
        
        current_plateau = None
        
        for i in range(1, len(skill_progression)):
            prev_level = skill_progression[i-1]["level"]
            curr_level = skill_progression[i]["level"]
            change = abs(curr_level - prev_level)
            
            if change < plateau_threshold:
                if current_plateau is None:
                    current_plateau = {
                        "start_date": skill_progression[i-1]["timestamp"],
                        "start_level": prev_level,
                        "data_points": [skill_progression[i-1], skill_progression[i]]
                    }
                else:
                    current_plateau["data_points"].append(skill_progression[i])
            else:
                if current_plateau and len(current_plateau["data_points"]) >= min_plateau_duration:
                    current_plateau["end_date"] = current_plateau["data_points"][-1]["timestamp"]
                    current_plateau["end_level"] = current_plateau["data_points"][-1]["level"]
                    current_plateau["duration_days"] = (
                        current_plateau["end_date"] - current_plateau["start_date"]
                    ).days
                    plateau_periods.append(current_plateau)
                current_plateau = None
        
        return plateau_periods
    
    def _calculate_skill_consistency(self, levels: List[float]) -> float:
        """Calculate consistency score for skill progression"""
        if len(levels) < 2:
            return 0.0
        
        # Calculate variance in level changes
        changes = [levels[i] - levels[i-1] for i in range(1, len(levels))]
        if not changes:
            return 1.0
        
        # Lower variance = higher consistency
        import statistics
        variance = statistics.variance(changes) if len(changes) > 1 else 0.0
        consistency = max(0.0, 1.0 - (variance * 10))  # Scale appropriately
        
        return min(1.0, consistency)
    
    def _determine_skill_trend(self, levels: List[float]) -> str:
        """Determine overall trend direction for skill levels"""
        if len(levels) < 2:
            return "insufficient_data"
        
        first_half = levels[:len(levels)//2]
        second_half = levels[len(levels)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _calculate_efficiency_trend(self, snapshots: List[ProgressSnapshot]) -> str:
        """Calculate efficiency trend over time"""
        if len(snapshots) < 3:
            return "insufficient_data"
        
        # Calculate efficiency for each period
        efficiencies = []
        for i in range(1, len(snapshots)):
            prev_snapshot = snapshots[i-1]
            curr_snapshot = snapshots[i]
            
            # Simple efficiency calculation
            skill_change = 0
            for skill, level in curr_snapshot.skill_levels.items():
                prev_level = prev_snapshot.skill_levels.get(skill, 0.0)
                skill_change += max(0, level - prev_level)
            
            time_spent = curr_snapshot.engagement_metrics.get("time_spent_hours", 1)
            efficiency = skill_change / max(time_spent, 1)
            efficiencies.append(efficiency)
        
        # Determine trend
        if len(efficiencies) < 2:
            return "stable"
        
        first_half_avg = sum(efficiencies[:len(efficiencies)//2]) / max(len(efficiencies)//2, 1)
        second_half_avg = sum(efficiencies[len(efficiencies)//2:]) / max(len(efficiencies) - len(efficiencies)//2, 1)
        
        if second_half_avg > first_half_avg * 1.1:
            return "improving"
        elif second_half_avg < first_half_avg * 0.9:
            return "declining"
        else:
            return "stable"
    
    async def _identify_peak_learning_periods(self, snapshots: List[ProgressSnapshot]) -> List[Dict[str, Any]]:
        """Identify periods of peak learning performance"""
        if len(snapshots) < 3:
            return []
        
        peak_periods = []
        velocities = []
        
        # Calculate velocity for each period
        for i in range(1, len(snapshots)):
            velocity = 0
            for skill, level in snapshots[i].skill_levels.items():
                prev_level = snapshots[i-1].skill_levels.get(skill, 0.0)
                velocity += max(0, level - prev_level)
            velocities.append((snapshots[i].timestamp, velocity))
        
        if not velocities:
            return peak_periods
        
        # Find periods above average velocity
        avg_velocity = sum(v[1] for v in velocities) / len(velocities)
        peak_threshold = avg_velocity * 1.5  # 50% above average
        
        for timestamp, velocity in velocities:
            if velocity > peak_threshold:
                peak_periods.append({
                    "date": timestamp,
                    "velocity": velocity,
                    "above_average_factor": velocity / avg_velocity if avg_velocity > 0 else 1.0
                })
        
        return peak_periods
    
    def _analyze_velocity_distribution(self, snapshots: List[ProgressSnapshot]) -> Dict[str, Any]:
        """Analyze the distribution of learning velocities"""
        all_velocities = []
        
        for snapshot in snapshots:
            for velocity in snapshot.velocity_metrics.values():
                all_velocities.append(velocity)
        
        if not all_velocities:
            return {"error": "no_velocity_data"}
        
        import statistics
        
        return {
            "mean": statistics.mean(all_velocities),
            "median": statistics.median(all_velocities),
            "std_deviation": statistics.stdev(all_velocities) if len(all_velocities) > 1 else 0.0,
            "min": min(all_velocities),
            "max": max(all_velocities),
            "percentile_75": statistics.quantiles(all_velocities, n=4)[2] if len(all_velocities) > 3 else max(all_velocities),
            "percentile_25": statistics.quantiles(all_velocities, n=4)[0] if len(all_velocities) > 3 else min(all_velocities)
        }
    
    # Additional helper methods for analytics calculations...
    async def _calculate_aggregate_metrics(self, snapshots: List[ProgressSnapshot]) -> Dict[str, Any]:
        """Calculate aggregate metrics from snapshots"""
        if not snapshots:
            return {}
        
        # Calculate averages across all snapshots
        all_skill_levels = []
        all_velocities = []
        all_engagement_scores = []
        total_milestones = 0
        
        for snapshot in snapshots:
            all_skill_levels.extend(snapshot.skill_levels.values())
            all_velocities.extend(snapshot.velocity_metrics.values())
            all_engagement_scores.append(snapshot.engagement_metrics.get("consistency_score", 0.7))
            total_milestones += len(snapshot.milestone_completions)
        
        return {
            "average_skill_level": sum(all_skill_levels) / len(all_skill_levels) if all_skill_levels else 0.0,
            "average_learning_velocity": sum(all_velocities) / len(all_velocities) if all_velocities else 0.0,
            "milestone_completion_rate": total_milestones / len(snapshots) if snapshots else 0.0,
            "engagement_score": sum(all_engagement_scores) / len(all_engagement_scores) if all_engagement_scores else 0.0,
            "total_snapshots": len(snapshots)
        }
    
    def _calculate_percentile(self, value: float, benchmark: float) -> float:
        """Calculate percentile score compared to benchmark"""
        if benchmark == 0:
            return 50.0 if value == 0 else (100.0 if value > 0 else 0.0)
        
        ratio = value / benchmark
        # Convert ratio to percentile (50th percentile = benchmark)
        if ratio >= 2.0:
            return 95.0
        elif ratio >= 1.5:
            return 80.0
        elif ratio >= 1.2:
            return 70.0
        elif ratio >= 1.0:
            return 60.0
        elif ratio >= 0.8:
            return 40.0
        elif ratio >= 0.5:
            return 20.0
        else:
            return 5.0 