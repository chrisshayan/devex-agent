"""
DevEx Agent ML Package

Machine learning enhancements for the Knowledge Graph system:
- CodeBERT integration for semantic code understanding
- Developer intelligence and skill tracking
- Learning path generation and progress tracking
- Expert career guidance with LLM integration
- Advanced analytics and progress tracking
"""

from .codebert_engine import CodeBERTEngine
from .developer_intelligence import DeveloperIntelligenceEngine
from .career_coach import ExpertCareerCoachLLM, CoachingContext
from .learning_path_engine import LearningPathEngine, LearningObjective, LearningPath
from .progress_tracker import ProgressTracker, ProgressSnapshot, LearningVelocity, ProgressAlert
from .analytics_service import AnalyticsService
from .models import (
    DeveloperSkillProfile, SkillTimeline, LearningPlan, LearningMilestone,
    CoachingSession, SkillAssessment, PatternAnalysis, LearningResource,
    CareerStage, SkillCategory, TimeAvailability, LearningStyle, CoachingTrigger,
    # Analytics models
    SkillProgressionTimeline, CodeQualityMetrics, LearningVelocityAnalytics,
    CoachingImpactAnalysis, DeveloperAnalyticsDashboard, DemoScenarioData
)

__all__ = [
    # Phase 1: Core ML engines
    "CodeBERTEngine",
    "DeveloperIntelligenceEngine",
    
    # Phase 2: Career coaching engines
    "ExpertCareerCoachLLM",
    "LearningPathEngine", 
    "ProgressTracker",
    
    # Phase 3: Analytics engines
    "AnalyticsService",
    
    # Helper classes
    "CoachingContext",
    "LearningObjective",
    "LearningPath",
    "ProgressSnapshot",
    "LearningVelocity",
    "ProgressAlert",
    
    # Core data models
    "DeveloperSkillProfile",
    "SkillTimeline", 
    "LearningPlan",
    "LearningMilestone",
    "CoachingSession",
    "SkillAssessment",
    "PatternAnalysis",
    "LearningResource",
    
    # Analytics models
    "SkillProgressionTimeline",
    "CodeQualityMetrics", 
    "LearningVelocityAnalytics",
    "CoachingImpactAnalysis",
    "DeveloperAnalyticsDashboard",
    "DemoScenarioData",
    
    # Enums
    "CareerStage",
    "SkillCategory", 
    "TimeAvailability",
    "LearningStyle",
    "CoachingTrigger"
] 