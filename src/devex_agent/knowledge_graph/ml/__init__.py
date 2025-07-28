"""
DevEx Agent ML Package

Machine learning enhancements for the Knowledge Graph system:
- CodeBERT integration for semantic code understanding
- Developer intelligence and skill tracking
- Personalized coaching and recommendations
- Learning path generation and progress tracking
- Expert career guidance with LLM integration
"""

from .codebert_engine import CodeBERTEngine
from .developer_intelligence import DeveloperIntelligenceEngine
from .career_coach import ExpertCareerCoachLLM, CoachingContext
from .learning_path_engine import LearningPathEngine, LearningObjective, LearningPath
from .progress_tracker import ProgressTracker, ProgressSnapshot, LearningVelocity, ProgressAlert
from .models import (
    DeveloperSkillProfile, SkillTimeline, LearningPlan, LearningMilestone,
    CoachingSession, SkillAssessment, PatternAnalysis, LearningResource,
    CareerStage, SkillCategory, TimeAvailability, LearningStyle, CoachingTrigger
)

__all__ = [
    # Phase 1: Core ML engines
    "CodeBERTEngine",
    "DeveloperIntelligenceEngine",
    
    # Phase 2: Career coaching engines
    "ExpertCareerCoachLLM",
    "LearningPathEngine", 
    "ProgressTracker",
    
    # Helper classes
    "CoachingContext",
    "LearningObjective",
    "LearningPath",
    "ProgressSnapshot",
    "LearningVelocity",
    "ProgressAlert",
    
    # Data models
    "DeveloperSkillProfile",
    "SkillTimeline", 
    "LearningPlan",
    "LearningMilestone",
    "CoachingSession",
    "SkillAssessment",
    "PatternAnalysis",
    "LearningResource",
    
    # Enums
    "CareerStage",
    "SkillCategory", 
    "TimeAvailability",
    "LearningStyle",
    "CoachingTrigger"
] 