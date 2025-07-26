"""
ML Data Models for Developer Intelligence

Pydantic models for tracking developer skills, learning progress,
coaching interactions, and pattern analysis.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class SkillCategory(str, Enum):
    """Categories of skills tracked by the system"""
    TECHNICAL = "technical"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    DOMAIN = "domain"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    TESTING = "testing"
    DEVOPS = "devops"


class CareerStage(str, Enum):
    """Developer career stages for skill-appropriate coaching"""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    ARCHITECT = "architect"


class LearningStyle(str, Enum):
    """Learning preferences for personalized recommendations"""
    VISUAL = "visual"
    HANDS_ON = "hands_on"
    THEORETICAL = "theoretical"
    MIXED = "mixed"


class TimeAvailability(str, Enum):
    """Time availability for learning recommendations"""
    LOW = "low"        # < 2 hours/week
    MEDIUM = "medium"  # 2-5 hours/week
    HIGH = "high"      # > 5 hours/week


class TrendDirection(str, Enum):
    """Skill progression trends"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    FLUCTUATING = "fluctuating"


class CoachingTrigger(str, Enum):
    """Events that trigger coaching sessions"""
    MORNING_BRIEF = "morning_brief"
    REAL_TIME = "real_time"
    WEEKLY_REVIEW = "weekly_review"
    MANUAL = "manual"
    MILESTONE = "milestone"
    CODE_REVIEW = "code_review"


class SkillAssessment(BaseModel):
    """Individual skill assessment at a point in time"""
    skill_name: str = Field(..., description="Name of the skill")
    category: SkillCategory = Field(..., description="Skill category")
    level: float = Field(..., ge=0.0, le=1.0, description="Skill level (0.0-1.0)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Assessment confidence")
    evidence: List[str] = Field(default_factory=list, description="Evidence for this assessment")
    assessed_at: datetime = Field(..., description="Assessment timestamp")
    assessment_method: str = Field(..., description="How the skill was assessed")
    
    # CodeBERT analysis results
    pattern_matches: List[Dict[str, Any]] = Field(default_factory=list, description="Code patterns demonstrating this skill")
    code_examples: List[str] = Field(default_factory=list, description="Code snippets showing skill usage")
    similarity_to_experts: float = Field(default=0.0, description="Similarity to expert-level code")


class SkillTimeline(BaseModel):
    """Track skill progression over time"""
    developer_id: str = Field(..., description="Developer identifier")
    skill_name: str = Field(..., description="Skill being tracked")
    skill_category: SkillCategory = Field(..., description="Skill category")
    
    # Timeline data
    timeline_points: List[Dict[str, Any]] = Field(..., description="Skill assessments over time")
    trend: TrendDirection = Field(..., description="Overall trend direction")
    velocity: float = Field(..., description="Rate of change (skills/month)")
    acceleration: float = Field(default=0.0, description="Change in velocity")
    
    # Analysis
    milestone_events: List[Dict[str, Any]] = Field(default_factory=list, description="Key learning milestones")
    learning_patterns: Dict[str, Any] = Field(default_factory=dict, description="Identified learning patterns")
    prediction: Optional[Dict[str, Any]] = Field(None, description="Predicted future progression")
    
    # Metadata
    first_assessed: datetime = Field(..., description="First assessment date")
    last_updated: datetime = Field(..., description="Last update timestamp")


class PatternAnalysis(BaseModel):
    """Analysis of developer's coding patterns using CodeBERT"""
    developer_id: str = Field(..., description="Developer identifier")
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analyzed_at: datetime = Field(..., description="Analysis timestamp")
    
    # Code pattern insights
    dominant_patterns: List[Dict[str, Any]] = Field(..., description="Most common coding patterns")
    architectural_preferences: Dict[str, float] = Field(..., description="Architecture pattern usage")
    naming_conventions: Dict[str, Any] = Field(..., description="Naming style preferences")
    complexity_preferences: Dict[str, Any] = Field(..., description="Code complexity preferences")
    
    # Language and framework usage
    language_proficiency: Dict[str, float] = Field(..., description="Programming language skills")
    framework_usage: Dict[str, float] = Field(..., description="Framework familiarity")
    library_preferences: List[str] = Field(..., description="Commonly used libraries")
    
    # Code quality indicators
    error_handling_patterns: Dict[str, float] = Field(..., description="Error handling approaches")
    testing_patterns: Dict[str, float] = Field(..., description="Testing methodology usage")
    documentation_style: Dict[str, Any] = Field(..., description="Documentation practices")
    
    # Semantic embeddings
    code_embeddings: List[float] = Field(default_factory=list, description="CodeBERT embeddings for recent code")
    pattern_embeddings: Dict[str, List[float]] = Field(default_factory=dict, description="Pattern-specific embeddings")
    
    # Comparisons
    similarity_to_golden_sources: float = Field(..., description="Similarity to organizational standards")
    peer_comparison: Dict[str, float] = Field(default_factory=dict, description="Comparison to peers")


class DeveloperSkillProfile(BaseModel):
    """Comprehensive developer skill profile"""
    developer_id: str = Field(..., description="Developer identifier")
    profile_version: str = Field(default="1.0", description="Profile schema version")
    
    # Basic information
    career_stage: CareerStage = Field(..., description="Current career level")
    experience_years: float = Field(..., description="Years of programming experience")
    primary_languages: List[str] = Field(..., description="Main programming languages")
    focus_areas: List[str] = Field(..., description="Current learning focus areas")
    career_goals: List[str] = Field(..., description="Long-term career aspirations")
    
    # Learning preferences
    learning_style: LearningStyle = Field(..., description="Preferred learning approach")
    time_availability: TimeAvailability = Field(..., description="Available time for learning")
    preferred_resources: List[str] = Field(default_factory=list, description="Preferred learning resources")
    
    # Current skill levels (skill_name -> level)
    technical_skills: Dict[str, float] = Field(..., description="Technical skill levels (0.0-1.0)")
    soft_skills: Dict[str, float] = Field(..., description="Soft skill levels (0.0-1.0)")
    domain_knowledge: Dict[str, float] = Field(..., description="Domain-specific knowledge")
    
    # Skill progression metrics
    skill_velocity: Dict[str, float] = Field(..., description="Rate of skill improvement")
    learning_efficiency: float = Field(..., description="Overall learning efficiency")
    consistency_score: float = Field(..., description="Learning consistency")
    
    # Pattern analysis results
    coding_patterns: PatternAnalysis = Field(..., description="Latest pattern analysis")
    pattern_evolution: List[str] = Field(default_factory=list, description="How patterns have evolved")
    
    # Improvement areas
    strength_areas: List[str] = Field(..., description="Areas of strength")
    improvement_areas: List[str] = Field(..., description="Areas needing improvement")
    recommended_focus: List[str] = Field(..., description="AI-recommended focus areas")
    
    # Metadata
    created_at: datetime = Field(..., description="Profile creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")
    last_code_analysis: Optional[datetime] = Field(None, description="Last code analysis timestamp")
    total_commits_analyzed: int = Field(default=0, description="Total commits analyzed")


class LearningResource(BaseModel):
    """Learning resource recommendation"""
    resource_id: str = Field(..., description="Resource identifier")
    title: str = Field(..., description="Resource title")
    type: Literal["course", "book", "tutorial", "project", "documentation", "video"] = Field(..., description="Resource type")
    url: Optional[str] = Field(None, description="Resource URL")
    provider: Optional[str] = Field(None, description="Resource provider")
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(..., description="Difficulty level")
    estimated_hours: Optional[float] = Field(None, description="Estimated time to complete")
    skills_covered: List[str] = Field(..., description="Skills this resource covers")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance to developer")
    personalization_reason: str = Field(..., description="Why this resource is recommended")


class LearningMilestone(BaseModel):
    """Learning milestone with success criteria"""
    milestone_id: str = Field(..., description="Milestone identifier")
    title: str = Field(..., description="Milestone title")
    description: str = Field(..., description="Milestone description")
    skills_involved: List[str] = Field(..., description="Skills this milestone develops")
    success_criteria: List[str] = Field(..., description="Criteria for completion")
    estimated_duration: str = Field(..., description="Expected time to complete")
    deadline: Optional[datetime] = Field(None, description="Target completion date")
    completed: bool = Field(default=False, description="Whether milestone is completed")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    evidence: List[str] = Field(default_factory=list, description="Evidence of completion")


class LearningPlan(BaseModel):
    """Personalized learning plan from Career Coach"""
    plan_id: str = Field(..., description="Plan identifier")
    developer_id: str = Field(..., description="Developer this plan is for")
    generated_at: datetime = Field(..., description="Plan generation timestamp")
    version: str = Field(default="1.0", description="Plan version")
    
    # Learning objectives
    priority_skills: List[Dict[str, Any]] = Field(..., description="Top skills to focus on")
    learning_objectives: List[str] = Field(..., description="Specific learning goals")
    target_career_stage: Optional[CareerStage] = Field(None, description="Target career level")
    
    # Learning path
    learning_path: List[Dict[str, Any]] = Field(..., description="Step-by-step learning progression")
    milestones: List[LearningMilestone] = Field(..., description="Learning milestones")
    
    # Resources and activities
    recommended_resources: List[LearningResource] = Field(..., description="Recommended learning resources")
    practice_projects: List[Dict[str, Any]] = Field(..., description="Hands-on coding projects")
    mentorship_suggestions: List[str] = Field(default_factory=list, description="Mentorship recommendations")
    
    # Timeline and assessment
    estimated_duration: str = Field(..., description="Expected time to complete plan")
    next_review_date: datetime = Field(..., description="When to reassess plan")
    progress_criteria: List[str] = Field(..., description="How to measure progress")
    
    # Personalization
    personalization_factors: Dict[str, Any] = Field(..., description="Factors used for personalization")
    adaptation_history: List[Dict[str, Any]] = Field(default_factory=list, description="How plan has been adapted")
    
    # Status
    status: Literal["active", "completed", "paused", "cancelled"] = Field(default="active", description="Plan status")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall progress")


class CoachingSession(BaseModel):
    """Individual coaching interaction record"""
    session_id: str = Field(..., description="Session identifier")
    developer_id: str = Field(..., description="Developer receiving coaching")
    timestamp: datetime = Field(..., description="Session timestamp")
    
    # Context
    trigger_type: CoachingTrigger = Field(..., description="What triggered this coaching session")
    current_context: Dict[str, Any] = Field(..., description="Current development context")
    code_context: Optional[Dict[str, Any]] = Field(None, description="Code being worked on")
    
    # Coaching content
    coaching_message: str = Field(..., description="Main coaching message")
    skills_addressed: List[str] = Field(..., description="Skills covered in this session")
    action_items: List[str] = Field(..., description="Specific actions for developer")
    learning_opportunities: List[str] = Field(default_factory=list, description="Learning opportunities identified")
    
    # Recommendations
    immediate_suggestions: List[str] = Field(default_factory=list, description="Immediate code improvements")
    long_term_recommendations: List[str] = Field(default_factory=list, description="Long-term development suggestions")
    resource_suggestions: List[LearningResource] = Field(default_factory=list, description="Recommended resources")
    
    # Interaction
    developer_response: Optional[str] = Field(None, description="Developer's response or feedback")
    suggestions_accepted: List[str] = Field(default_factory=list, description="Which suggestions were accepted")
    suggestions_rejected: List[str] = Field(default_factory=list, description="Which suggestions were rejected")
    
    # Follow-up
    follow_up_needed: bool = Field(default=False, description="Whether follow-up is needed")
    next_check_in: Optional[datetime] = Field(None, description="When to check progress")
    related_sessions: List[str] = Field(default_factory=list, description="Related coaching session IDs")
    
    # Effectiveness
    effectiveness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Session effectiveness rating")
    developer_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="Developer satisfaction (1-5)")


class SkillEvolution(BaseModel):
    """Track how skills evolve over time"""
    developer_id: str = Field(..., description="Developer identifier")
    skill_name: str = Field(..., description="Skill being tracked")
    
    # Evolution metrics
    initial_level: float = Field(..., description="Starting skill level")
    current_level: float = Field(..., description="Current skill level")
    peak_level: float = Field(..., description="Highest achieved level")
    growth_rate: float = Field(..., description="Average growth rate")
    
    # Learning events
    learning_events: List[Dict[str, Any]] = Field(..., description="Events that contributed to learning")
    coaching_impact: Dict[str, float] = Field(..., description="Impact of coaching sessions")
    resource_effectiveness: Dict[str, float] = Field(..., description="Effectiveness of learning resources")
    
    # Predictions
    projected_level_3months: float = Field(..., description="Predicted level in 3 months")
    projected_level_6months: float = Field(..., description="Predicted level in 6 months")
    confidence_interval: Dict[str, float] = Field(..., description="Prediction confidence")
    
    # Analysis
    learning_plateau_periods: List[Dict[str, Any]] = Field(default_factory=list, description="Periods of slow growth")
    breakthrough_moments: List[Dict[str, Any]] = Field(default_factory=list, description="Significant improvement events")
    skill_correlations: Dict[str, float] = Field(default_factory=dict, description="Correlation with other skills") 