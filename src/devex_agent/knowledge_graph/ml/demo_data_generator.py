"""
Demo Data Generator - Alex Chen's 18-Month Developer Journey

Generates realistic progression data for demonstrating the DevEx Agent's 
long-term value through a compelling developer transformation story.

The narrative follows Alex Chen's journey from Junior Developer to Senior Engineer:
- Months 1-3: Foundation Building
- Months 4-9: Accelerated Learning  
- Months 10-15: Specialization & Leadership
- Months 16-18: Senior Contributor
"""

import logging
import asyncio
import uuid
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
from dataclasses import asdict

from .models import (
    DemoScenarioData, DeveloperSkillProfile, SkillAssessment, SkillCategory,
    CareerStage, LearningStyle, TimeAvailability, TrendDirection,
    LearningPlan, CoachingSession, PatternAnalysis, 
    LearningMilestone, LearningResource, CoachingTrigger, 
    SkillProgressionTimeline, CodeQualityMetrics,
    LearningVelocityAnalytics, CoachingImpactAnalysis, 
    DeveloperAnalyticsDashboard
)
from .progress_tracker import ProgressSnapshot, LearningVelocity, ProgressAlert

logger = logging.getLogger(__name__)


class AlexChenDemoGenerator:
    """
    Generate comprehensive demo data for Alex Chen's 18-month journey
    
    Creates realistic progression data that demonstrates:
    - Skill development over time
    - Code quality improvements
    - Learning velocity changes
    - Coaching impact and effectiveness
    - Career progression milestones
    """
    
    def __init__(self):
        """Initialize the demo data generator"""
        self.developer_id = "alex_chen"
        self.journey_start = datetime.now() - timedelta(days=540)  # 18 months ago
        self.journey_end = datetime.now()
        
        # Journey phases with different characteristics
        self.phases = {
            "foundation": {  # Months 1-3
                "start_month": 0,
                "end_month": 3,
                "learning_velocity": 0.3,
                "coaching_frequency": 2,  # sessions per month
                "skill_improvement_rate": 0.1,
                "code_quality_start": 0.4,
                "narrative": "Struggling Junior - Initial code quality issues, DevEx provides guidance"
            },
            "acceleration": {  # Months 4-9
                "start_month": 3,
                "end_month": 9,
                "learning_velocity": 0.6,
                "coaching_frequency": 3,
                "skill_improvement_rate": 0.15,
                "code_quality_improvement": 0.4,
                "narrative": "Accelerated Learner - DevEx coaching shows clear impact"
            },
            "leadership": {  # Months 10-15
                "start_month": 9,
                "end_month": 15,
                "learning_velocity": 0.45,
                "coaching_frequency": 2.5,
                "skill_improvement_rate": 0.12,
                "focus_shift": "architecture_and_mentoring",
                "narrative": "Emerging Leader - DevEx guides towards leadership opportunities"
            },
            "senior": {  # Months 16-18
                "start_month": 15,
                "end_month": 18,
                "learning_velocity": 0.4,
                "coaching_frequency": 2,
                "skill_improvement_rate": 0.08,
                "focus": "technical_leadership",
                "narrative": "Senior Contributor - DevEx identifies principal engineer potential"
            }
        }
        
        # Core skills and their progression curves
        self.skills = {
            "python": {
                "category": SkillCategory.LANGUAGE,
                "start_level": 0.4,
                "target_level": 0.9,
                "curve": "steady_growth"
            },
            "javascript": {
                "category": SkillCategory.LANGUAGE,
                "start_level": 0.3,
                "target_level": 0.75,
                "curve": "early_plateau_then_growth"
            },
            "react": {
                "category": SkillCategory.FRAMEWORK,
                "start_level": 0.0,
                "target_level": 0.8,
                "curve": "delayed_start_rapid_growth"
            },
            "testing": {
                "category": SkillCategory.TESTING,
                "start_level": 0.2,
                "target_level": 0.85,
                "curve": "consistent_growth"
            },
            "architecture": {
                "category": SkillCategory.ARCHITECTURE,
                "start_level": 0.1,
                "target_level": 0.8,
                "curve": "late_accelerated_growth"
            },
            "mentoring": {
                "category": SkillCategory.SOFT_SKILL,
                "start_level": 0.0,
                "target_level": 0.7,
                "curve": "leadership_phase_growth"
            },
            "git": {
                "category": SkillCategory.TOOL,
                "start_level": 0.5,
                "target_level": 0.85,
                "curve": "early_improvement"
            }
        }
        
        # Coaching themes by phase
        self.coaching_themes = {
            "foundation": ["code_quality", "best_practices", "debugging", "git_workflow"],
            "acceleration": ["testing", "architecture_patterns", "react_development", "performance"],
            "leadership": ["system_design", "mentoring", "code_review", "technical_leadership"],
            "senior": ["architecture_strategy", "team_leadership", "knowledge_sharing", "innovation"]
        }
        
        logger.info("🎭 Alex Chen Demo Generator initialized")
    
    async def generate_complete_demo_scenario(self) -> DemoScenarioData:
        """Generate the complete 18-month demo scenario"""
        logger.info("🚀 Generating Alex Chen's complete 18-month journey...")
        
        try:
            # Generate all components
            developer_profile = self._generate_developer_profile()
            monthly_snapshots = self._generate_monthly_snapshots()
            milestone_completions = self._generate_milestone_completions()
            coaching_sessions = self._generate_coaching_sessions()
            code_quality_evolution = self._generate_code_quality_evolution()
            skill_assessments = self._generate_skill_assessments()
            learning_plans = self._generate_learning_plans()
            learning_velocity_data = self._generate_learning_velocity_data()
            career_milestones = self._generate_career_milestones()
            promotion_timeline = self._generate_promotion_timeline()
            narrative_arc = self._generate_narrative_arc()
            demo_highlights = self._generate_demo_highlights()
            
            # Create complete scenario
            scenario = DemoScenarioData(
                scenario_id="alex_chen_18_month_journey",
                scenario_name="Alex Chen: Junior to Senior Developer Journey",
                developer_profile=developer_profile,
                timeline_duration_months=18,
                monthly_snapshots=[asdict(snapshot) for snapshot in monthly_snapshots],
                milestone_completions=milestone_completions,
                coaching_sessions=coaching_sessions,
                code_quality_evolution=code_quality_evolution,
                skill_assessments=skill_assessments,
                learning_plans=learning_plans,
                learning_velocity_data=[asdict(velocity) for velocity in learning_velocity_data],
                career_milestones=career_milestones,
                promotion_timeline=promotion_timeline,
                narrative_arc=narrative_arc,
                demo_highlights=demo_highlights,
                created_at=datetime.now(),
                scenario_version="1.0"
            )
            
            logger.info("✅ Complete demo scenario generated successfully")
            return scenario
            
        except Exception as e:
            logger.error(f"❌ Failed to generate demo scenario: {e}")
            raise
    
    def _generate_developer_profile(self) -> DeveloperSkillProfile:
        """Generate Alex Chen's developer profile"""
        return DeveloperSkillProfile(
            developer_id=self.developer_id,
            profile_version="1.0",
            career_stage=CareerStage.SENIOR,  # Final state
            experience_years=3.5,  # After 18-month journey
            primary_languages=["python", "javascript", "typescript"],
            focus_areas=["full_stack_development", "system_architecture", "team_leadership"],
            career_goals=["technical_leadership", "system_architecture", "mentoring"],
            learning_style=LearningStyle.MIXED,
            time_availability=TimeAvailability.MEDIUM,
            preferred_resources=["hands_on_projects", "coding_challenges", "technical_books"],
            technical_skills={
                "python": 0.9,
                "javascript": 0.75,
                "react": 0.8,
                "testing": 0.85,
                "architecture": 0.8,
                "git": 0.85
            },
            soft_skills={
                "mentoring": 0.7,
                "communication": 0.8,
                "leadership": 0.65,
                "collaboration": 0.85
            },
            domain_knowledge={
                "web_development": 0.85,
                "system_design": 0.75,
                "devops": 0.6,
                "security": 0.65
            },
            skill_velocity={
                "python": 0.05,
                "javascript": 0.03,
                "react": 0.06,
                "testing": 0.04,
                "architecture": 0.08
            },
            learning_efficiency=0.82,
            consistency_score=0.78,
            coding_patterns=self._generate_final_pattern_analysis(),
            pattern_evolution=["procedural_to_oop", "monolith_to_modular", "basic_to_advanced_patterns"],
            strength_areas=["python_development", "system_architecture", "testing", "mentoring"],
            improvement_areas=["devops", "advanced_security", "performance_optimization"],
            recommended_focus=["principal_engineer_skills", "advanced_architecture", "team_leadership"],
            created_at=self.journey_start,
            last_updated=self.journey_end,
            last_code_analysis=self.journey_end - timedelta(days=1),
            total_commits_analyzed=486  # ~27 commits per month average
        )
    
    def _generate_monthly_snapshots(self) -> List[ProgressSnapshot]:
        """Generate monthly progress snapshots"""
        snapshots = []
        
        for month in range(18):
            snapshot_date = self.journey_start + timedelta(days=month * 30)
            phase = self._get_phase_for_month(month)
            
            # Calculate skill levels for this month
            skill_levels = {}
            for skill_name, skill_config in self.skills.items():
                level = self._calculate_skill_level_for_month(skill_name, skill_config, month)
                skill_levels[skill_name] = level
            
            # Generate velocity metrics
            velocity_metrics = {}
            for skill_name in skill_levels:
                base_velocity = self.phases[phase]["learning_velocity"]
                skill_velocity = base_velocity * (0.8 + random.random() * 0.4)
                velocity_metrics[skill_name] = skill_velocity
            
            # Calculate milestone completions
            milestone_completions = self._get_milestones_for_month(month)
            
            # Calculate learning plan progress
            learning_plan_progress = min(1.0, (month + 1) * 0.05 + 0.1)
            
            # Generate engagement metrics
            engagement_metrics = {
                "sessions_completed": month * 2 + random.randint(0, 3),
                "time_spent_hours": (month + 1) * 8 + random.randint(-5, 10),
                "consistency_score": max(0.5, min(1.0, 0.6 + month * 0.02 + random.uniform(-0.1, 0.1))),
                "coaching_participation": 0.7 + month * 0.015,
                "resource_usage": {
                    "documentation": random.randint(20, 50),
                    "tutorials": random.randint(5, 15),
                    "coding_exercises": random.randint(10, 30)
                }
            }
            
            snapshot = ProgressSnapshot(
                snapshot_id=f"snapshot_{self.developer_id}_{month:02d}",
                developer_id=self.developer_id,
                timestamp=snapshot_date,
                skill_levels=skill_levels,
                milestone_completions=milestone_completions,
                learning_plan_progress=learning_plan_progress,
                velocity_metrics=velocity_metrics,
                engagement_metrics=engagement_metrics,
                notes=f"Month {month + 1}: {self.phases[phase]['narrative']}"
            )
            snapshots.append(snapshot)
        
        return snapshots
    
    def _generate_coaching_sessions(self) -> List[CoachingSession]:
        """Generate coaching sessions throughout the journey"""
        sessions = []
        session_id_counter = 1
        
        for month in range(18):
            phase = self._get_phase_for_month(month)
            sessions_this_month = int(self.phases[phase]["coaching_frequency"])
            
            # Add some variance to session frequency
            if random.random() < 0.3:
                sessions_this_month += random.randint(-1, 1)
            sessions_this_month = max(1, sessions_this_month)
            
            for session_num in range(sessions_this_month):
                session_date = (self.journey_start + 
                              timedelta(days=month * 30 + session_num * (30 // sessions_this_month)))
                
                # Select coaching theme based on phase
                theme = random.choice(self.coaching_themes[phase])
                
                # Generate session effectiveness based on phase and progression
                base_effectiveness = 0.6 + (month * 0.015)  # Improves over time
                effectiveness = min(0.95, base_effectiveness + random.uniform(-0.1, 0.1))
                
                # Generate suggestions and acceptance
                total_suggestions = random.randint(2, 5)
                acceptance_rate = 0.65 + (month * 0.008)  # Improves over time
                suggestions_accepted = int(total_suggestions * acceptance_rate)
                
                session = CoachingSession(
                    session_id=f"coaching_{self.developer_id}_{session_id_counter:03d}",
                    developer_id=self.developer_id,
                    timestamp=session_date,
                    trigger_type=CoachingTrigger.WEEKLY_REVIEW,
                    current_context={
                        "phase": phase,
                        "month": month + 1,
                        "primary_focus": theme,
                        "recent_activity": f"Working on {theme} improvements"
                    },
                    code_context={
                        "current_project": self._get_project_for_month(month),
                        "complexity_level": min(10, 3 + month // 2),
                        "languages_used": self._get_languages_for_month(month)
                    },
                    coaching_message=self._generate_coaching_message(theme, month, phase),
                    skills_addressed=self._get_skills_for_theme(theme),
                    action_items=self._generate_action_items(theme, month),
                    learning_opportunities=self._generate_learning_opportunities(theme),
                    immediate_suggestions=self._generate_immediate_suggestions(theme),
                    long_term_recommendations=self._generate_long_term_recommendations(theme, month),
                    resource_suggestions=self._generate_resource_suggestions(theme),
                    suggestions_accepted=[f"suggestion_{i}" for i in range(suggestions_accepted)],
                    follow_up_needed=random.choice([True, False]),
                    next_check_in=session_date + timedelta(days=7),
                    effectiveness_score=effectiveness,
                    developer_satisfaction=min(5, int(effectiveness * 5) + random.randint(0, 1))
                )
                
                sessions.append(session)
                session_id_counter += 1
        
        return sessions
    
    def _generate_code_quality_evolution(self) -> List[CodeQualityMetrics]:
        """Generate code quality evolution over time"""
        quality_metrics = []
        
        # Generate quarterly quality assessments
        for quarter in range(6):  # 6 quarters in 18 months
            quarter_start = self.journey_start + timedelta(days=quarter * 90)
            quarter_end = quarter_start + timedelta(days=90)
            
            # Calculate improvement based on phase
            month = quarter * 3
            phase = self._get_phase_for_month(month)
            
            # Base quality scores with improvement over time
            base_complexity = 0.4 + (quarter * 0.08)  # Improving complexity
            base_patterns = 0.3 + (quarter * 0.12)    # Pattern adoption
            base_security = 0.5 + (quarter * 0.07)    # Security improvement
            base_maintainability = 0.45 + (quarter * 0.09)
            base_test_coverage = 0.2 + (quarter * 0.11)  # Major improvement area
            
            # Generate timeline data for each dimension
            complexity_timeline = self._generate_quality_timeline(
                "complexity", quarter_start, quarter_end, base_complexity
            )
            patterns_timeline = self._generate_quality_timeline(
                "patterns", quarter_start, quarter_end, base_patterns
            )
            security_timeline = self._generate_quality_timeline(
                "security", quarter_start, quarter_end, base_security
            )
            maintainability_timeline = self._generate_quality_timeline(
                "maintainability", quarter_start, quarter_end, base_maintainability
            )
            test_coverage_timeline = self._generate_quality_timeline(
                "test_coverage", quarter_start, quarter_end, base_test_coverage
            )
            
            # Golden source similarity improvement
            golden_source_similarity = self._generate_golden_source_timeline(
                quarter_start, quarter_end, 0.5 + (quarter * 0.08)
            )
            
            # Overall trend calculation
            all_scores = [base_complexity, base_patterns, base_security, 
                         base_maintainability, base_test_coverage]
            if quarter > 0:
                prev_quarter_avg = 0.4 + ((quarter - 1) * 0.08)
                current_avg = sum(all_scores) / len(all_scores)
                trend = TrendDirection.IMPROVING if current_avg > prev_quarter_avg else TrendDirection.STABLE
            else:
                trend = TrendDirection.IMPROVING
            
            metrics = CodeQualityMetrics(
                developer_id=self.developer_id,
                metric_id=f"quality_{self.developer_id}_q{quarter + 1}",
                complexity_timeline=complexity_timeline,
                pattern_adoption_timeline=patterns_timeline,
                security_score_timeline=security_timeline,
                maintainability_timeline=maintainability_timeline,
                test_coverage_timeline=test_coverage_timeline,
                documentation_timeline=self._generate_quality_timeline(
                    "documentation", quarter_start, quarter_end, 0.3 + (quarter * 0.1)
                ),
                golden_source_similarity=golden_source_similarity,
                quality_trend=trend,
                improvement_rate=0.08 + (quarter * 0.01),
                assessment_period_start=quarter_start,
                assessment_period_end=quarter_end,
                total_commits_analyzed=27 * 3  # ~27 commits per month
            )
            
            quality_metrics.append(metrics)
        
        return quality_metrics
    
    def _generate_milestone_completions(self) -> List[Dict[str, Any]]:
        """Generate milestone completion events"""
        milestones = [
            {"month": 2, "milestone": "First Successful Code Review", "impact": "confidence_boost"},
            {"month": 4, "milestone": "Python Intermediate Proficiency", "impact": "skill_advancement"},
            {"month": 6, "milestone": "React Development Competency", "impact": "technology_expansion"},
            {"month": 8, "milestone": "Testing Best Practices Adoption", "impact": "quality_improvement"},
            {"month": 10, "milestone": "First Architecture Contribution", "impact": "responsibility_increase"},
            {"month": 12, "milestone": "Mentoring First Junior Developer", "impact": "leadership_development"},
            {"month": 14, "milestone": "System Design Leadership", "impact": "technical_leadership"},
            {"month": 16, "milestone": "Cross-Team Collaboration Lead", "impact": "organizational_impact"},
            {"month": 18, "milestone": "Senior Developer Promotion", "impact": "career_advancement"}
        ]
        
        completion_events = []
        for milestone in milestones:
            completion_date = self.journey_start + timedelta(days=milestone["month"] * 30)
            completion_events.append({
                "milestone_id": f"milestone_{milestone['month']:02d}",
                "milestone_name": milestone["milestone"],
                "completion_date": completion_date,
                "month": milestone["month"],
                "impact_type": milestone["impact"],
                "devex_contribution": self._get_devex_contribution_for_milestone(milestone["milestone"]),
                "skills_demonstrated": self._get_skills_for_milestone(milestone["milestone"]),
                "evidence": [
                    f"Code review approval for {milestone['milestone'].lower()}",
                    f"Peer recognition for {milestone['milestone'].lower()}",
                    f"Manager feedback on {milestone['milestone'].lower()}"
                ]
            })
        
        return completion_events
    
    def _generate_skill_assessments(self) -> List[SkillAssessment]:
        """Generate skill assessments throughout the journey"""
        assessments = []
        
        # Generate assessments every 2 months
        for month in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]:
            assessment_date = self.journey_start + timedelta(days=month * 30)
            
            for skill_name, skill_config in self.skills.items():
                level = self._calculate_skill_level_for_month(skill_name, skill_config, month)
                confidence = min(0.95, 0.6 + (month * 0.02))
                
                assessment = SkillAssessment(
                    skill_name=skill_name,
                    category=skill_config["category"],
                    level=level,
                    confidence=confidence,
                    evidence=self._generate_skill_evidence(skill_name, month),
                    assessed_at=assessment_date,
                    assessment_method="codebert_analysis",
                    pattern_matches=self._generate_pattern_matches(skill_name, month),
                    code_examples=self._generate_code_examples(skill_name, month),
                    similarity_to_experts=min(0.9, 0.3 + (month * 0.035))
                )
                assessments.append(assessment)
        
        return assessments
    
    def _generate_learning_plans(self) -> List[LearningPlan]:
        """Generate learning plans for different phases"""
        plans = []
        
        # Generate plans for each phase
        for phase_name, phase_config in self.phases.items():
            plan_start = self.journey_start + timedelta(days=phase_config["start_month"] * 30)
            
            plan = LearningPlan(
                plan_id=f"plan_{self.developer_id}_{phase_name}",
                developer_id=self.developer_id,
                generated_at=plan_start,
                version="1.0",
                priority_skills=self._get_priority_skills_for_phase(phase_name),
                learning_objectives=self._get_learning_objectives_for_phase(phase_name),
                target_career_stage=self._get_target_career_stage_for_phase(phase_name),
                learning_path=self._generate_learning_path_for_phase(phase_name),
                milestones=self._generate_milestones_for_phase(phase_name),
                recommended_resources=self._generate_resources_for_phase(phase_name),
                practice_projects=self._generate_projects_for_phase(phase_name),
                estimated_duration=f"{phase_config['end_month'] - phase_config['start_month']} months",
                next_review_date=plan_start + timedelta(days=30),
                progress_criteria=self._generate_progress_criteria_for_phase(phase_name),
                personalization_factors={
                    "learning_style": "mixed",
                    "time_availability": "medium",
                    "career_stage": "junior" if phase_name == "foundation" else "mid",
                    "phase": phase_name
                },
                status="completed" if phase_name != "senior" else "active",
                progress_percentage=100.0 if phase_name != "senior" else 75.0
            )
            plans.append(plan)
        
        return plans
    
    def _generate_learning_velocity_data(self) -> List[LearningVelocity]:
        """Generate learning velocity data"""
        velocity_data = []
        
        # Generate monthly velocity data
        for month in range(18):
            velocity_date = self.journey_start + timedelta(days=month * 30)
            phase = self._get_phase_for_month(month)
            
            velocity = LearningVelocity(
                developer_id=self.developer_id,
                time_period="monthly",
                skills_improved=self._calculate_skills_improved_for_month(month),
                average_skill_increase=self.phases[phase]["skill_improvement_rate"],
                learning_consistency=min(0.95, 0.6 + (month * 0.02)),
                milestone_completion_rate=self._calculate_milestone_rate_for_month(month),
                engagement_score=min(0.95, 0.65 + (month * 0.015)),
                velocity_trend=self._determine_velocity_trend_for_month(month)
            )
            velocity_data.append(velocity)
        
        return velocity_data
    
    # Helper methods for data generation...
    
    def _get_phase_for_month(self, month: int) -> str:
        """Get the phase name for a given month"""
        for phase_name, phase_config in self.phases.items():
            if phase_config["start_month"] <= month < phase_config["end_month"]:
                return phase_name
        return "senior"  # Default to senior for months 15+
    
    def _calculate_skill_level_for_month(self, skill_name: str, skill_config: dict, month: int) -> float:
        """Calculate skill level for a specific month"""
        start_level = skill_config["start_level"]
        target_level = skill_config["target_level"]
        curve = skill_config["curve"]
        
        # Calculate progress (0.0 to 1.0) based on curve type
        if curve == "steady_growth":
            progress = month / 18.0
        elif curve == "early_plateau_then_growth":
            if month < 6:
                progress = month / 18.0 * 0.3  # Slow initial growth
            else:
                progress = 0.3 + ((month - 6) / 12.0) * 0.7  # Faster later growth
        elif curve == "delayed_start_rapid_growth":
            if month < 3:
                progress = 0.0
            else:
                progress = ((month - 3) / 15.0) ** 1.5  # Accelerated growth after delay
        elif curve == "consistent_growth":
            progress = month / 18.0
        elif curve == "late_accelerated_growth":
            if month < 9:
                progress = (month / 18.0) * 0.4
            else:
                progress = 0.4 + ((month - 9) / 9.0) * 0.6
        elif curve == "leadership_phase_growth":
            if month < 9:
                progress = 0.0
            else:
                progress = ((month - 9) / 9.0) ** 0.8
        elif curve == "early_improvement":
            if month < 6:
                progress = (month / 6.0) * 0.8
            else:
                progress = 0.8 + ((month - 6) / 12.0) * 0.2
        else:
            progress = month / 18.0
        
        # Apply some random variation
        progress += random.uniform(-0.05, 0.05)
        progress = max(0.0, min(1.0, progress))
        
        # Calculate final level
        level = start_level + (target_level - start_level) * progress
        return min(0.95, max(0.0, level))
    
    def _generate_final_pattern_analysis(self) -> PatternAnalysis:
        """Generate final pattern analysis for Alex's profile"""
        return PatternAnalysis(
            developer_id=self.developer_id,
            analysis_id=f"pattern_{self.developer_id}_final",
            analyzed_at=self.journey_end,
            dominant_patterns=[
                {"pattern": "MVC Architecture", "frequency": 0.85, "quality": "high"},
                {"pattern": "Dependency Injection", "frequency": 0.78, "quality": "high"},
                {"pattern": "Test-Driven Development", "frequency": 0.82, "quality": "high"},
                {"pattern": "RESTful API Design", "frequency": 0.88, "quality": "high"}
            ],
            architectural_preferences={
                "microservices": 0.75,
                "layered_architecture": 0.85,
                "event_driven": 0.65,
                "modular_design": 0.9
            },
            naming_conventions={
                "consistency": 0.92,
                "clarity": 0.88,
                "convention_adherence": 0.9
            },
            complexity_preferences={
                "cyclomatic_complexity": 6.2,  # Down from 15
                "cognitive_complexity": 4.8,
                "nesting_depth": 2.3
            },
            language_proficiency={
                "python": 0.9,
                "javascript": 0.75,
                "typescript": 0.7,
                "sql": 0.65
            },
            framework_usage={
                "react": 0.8,
                "django": 0.85,
                "fastapi": 0.7,
                "pytest": 0.85
            },
            library_preferences=[
                "requests", "pandas", "numpy", "pytest", "black", "mypy",
                "react", "axios", "lodash", "jest"
            ],
            error_handling_patterns={
                "try_catch_usage": 0.85,
                "specific_exception_handling": 0.8,
                "logging_integration": 0.9,
                "graceful_degradation": 0.75
            },
            testing_patterns={
                "unit_test_coverage": 0.85,
                "integration_testing": 0.75,
                "test_organization": 0.9,
                "mocking_usage": 0.8
            },
            documentation_style={
                "docstring_coverage": 0.85,
                "inline_comments": 0.8,
                "readme_quality": 0.9,
                "api_documentation": 0.8
            },
            code_embeddings=[],  # Would be populated with actual CodeBERT embeddings
            pattern_embeddings={},
            similarity_to_golden_sources=0.82,
            peer_comparison={
                "above_average": 0.85,
                "similar_experience_level": 0.9,
                "senior_level_comparison": 0.72
            }
        )
    
    # Additional helper methods for generating various types of data...
    # (Implementation continues with specific data generation for each component)
    
    def _generate_career_milestones(self) -> List[Dict[str, Any]]:
        """Generate career milestone achievements"""
        return [
            {
                "milestone": "First Successful Pull Request",
                "date": (self.journey_start + timedelta(days=30)).isoformat(),
                "impact": "confidence_building",
                "devex_role": "provided_code_review_guidance"
            },
            {
                "milestone": "Led First Technical Discussion",
                "date": (self.journey_start + timedelta(days=300)).isoformat(),
                "impact": "leadership_emergence",
                "devex_role": "coaching_on_communication_skills"
            },
            {
                "milestone": "Promoted to Senior Developer",
                "date": (self.journey_start + timedelta(days=510)).isoformat(),
                "impact": "career_advancement",
                "devex_role": "identified_promotion_readiness"
            }
        ]
    
    def _generate_promotion_timeline(self) -> List[Dict[str, Any]]:
        """Generate career advancement timeline"""
        return [
            {
                "date": self.journey_start.isoformat(),
                "role": "Junior Developer",
                "level": "L1",
                "salary_band": "junior",
                "responsibilities": ["basic_coding", "bug_fixes", "simple_features"]
            },
            {
                "date": (self.journey_start + timedelta(days=270)).isoformat(),
                "role": "Mid-Level Developer",
                "level": "L2",
                "salary_band": "mid",
                "responsibilities": ["feature_development", "code_review", "testing"]
            },
            {
                "date": (self.journey_start + timedelta(days=510)).isoformat(),
                "role": "Senior Developer",
                "level": "L3",
                "salary_band": "senior",
                "responsibilities": ["system_design", "mentoring", "technical_leadership"]
            }
        ]
    
    def _generate_narrative_arc(self) -> List[Dict[str, Any]]:
        """Generate narrative arc with key story moments"""
        return [
            {
                "act": 1,
                "title": "The Struggling Junior",
                "timeframe": "Months 1-3",
                "key_moment": "First major code review failure leads to DevEx intervention",
                "emotion": "frustration_to_hope",
                "devex_role": "gentle_guidance_and_encouragement"
            },
            {
                "act": 2,
                "title": "The Accelerated Learner",
                "timeframe": "Months 4-9",
                "key_moment": "Successfully implements complex React feature with DevEx coaching",
                "emotion": "confidence_building",
                "devex_role": "strategic_skill_development"
            },
            {
                "act": 3,
                "title": "The Emerging Leader",
                "timeframe": "Months 10-15",
                "key_moment": "Takes ownership of architecture decisions and mentors junior",
                "emotion": "pride_and_responsibility",
                "devex_role": "leadership_pathway_guidance"
            },
            {
                "act": 4,
                "title": "The Senior Contributor",
                "timeframe": "Months 16-18",
                "key_moment": "Promotion to Senior Developer and technical leadership role",
                "emotion": "achievement_and_vision",
                "devex_role": "principal_engineer_preparation"
            }
        ]
    
    def _generate_demo_highlights(self) -> List[Dict[str, Any]]:
        """Generate key highlights for demo presentation"""
        return [
            {
                "highlight": "78% Suggestion Acceptance Rate",
                "category": "coaching_effectiveness",
                "timeframe": "18_months",
                "visual": "trend_line_chart",
                "impact": "high"
            },
            {
                "highlight": "Career Progression: 1.8x Faster Than Average",
                "category": "career_acceleration",
                "timeframe": "18_months",
                "visual": "timeline_comparison",
                "impact": "very_high"
            },
            {
                "highlight": "Code Quality: 60% Improvement",
                "category": "technical_excellence",
                "timeframe": "foundation_to_senior",
                "visual": "before_after_metrics",
                "impact": "high"
            },
            {
                "highlight": "Test Coverage: 20% → 85%",
                "category": "quality_metrics",
                "timeframe": "12_months",
                "visual": "progress_bar_animation",
                "impact": "very_high"
            }
        ]
    
    # Additional helper methods...
    def _get_milestones_for_month(self, month: int) -> List[str]:
        """Get milestones completed in a specific month"""
        milestone_months = {2, 4, 6, 8, 10, 12, 14, 16, 18}
        if month + 1 in milestone_months:
            return [f"milestone_{month + 1:02d}"]
        return []
    
    def _get_project_for_month(self, month: int) -> str:
        """Get the main project for a specific month"""
        projects = [
            "User Authentication System", "Dashboard Widgets", "API Integration",
            "React Component Library", "Testing Framework Setup", "Performance Optimization",
            "Microservices Architecture", "Team Mentoring", "System Design Leadership",
            "Cross-Team Integration", "Architecture Documentation", "Technical Strategy",
            "Innovation Lab Project", "Principal Engineer Preparation", "Team Leadership",
            "Advanced Architecture", "Organizational Impact", "Knowledge Sharing Platform"
        ]
        return projects[month] if month < len(projects) else "Advanced Technical Leadership"
    
    def _get_languages_for_month(self, month: int) -> List[str]:
        """Get programming languages being used in a specific month"""
        base_languages = ["python"]
        if month >= 2:
            base_languages.append("javascript")
        if month >= 6:
            base_languages.append("typescript")
        if month >= 12:
            base_languages.extend(["sql", "bash"])
        return base_languages
    
    def _get_devex_contribution_for_milestone(self, milestone_name: str) -> Dict[str, Any]:
        """Get DevEx agent contribution for achieving a milestone"""
        # Map milestone names to specific DevEx contributions
        contributions = {
            "First Code Review": {
                "coaching_sessions": 3,
                "suggestions_provided": 15,
                "suggestions_accepted": 12,
                "key_improvements": [
                    "Code formatting and style consistency",
                    "Error handling best practices",
                    "Documentation standards"
                ],
                "ai_insights": [
                    "Detected similar patterns in company golden sources",
                    "Recommended specific Python style guide adoption",
                    "Identified code smell patterns early"
                ],
                "impact_score": 0.75
            },
            "React Proficiency": {
                "coaching_sessions": 8,
                "suggestions_provided": 32,
                "suggestions_accepted": 28,
                "key_improvements": [
                    "Component composition patterns",
                    "State management optimization",
                    "Performance best practices"
                ],
                "ai_insights": [
                    "Guided towards modern React patterns from golden sources",
                    "Identified anti-patterns before code review",
                    "Suggested appropriate testing strategies"
                ],
                "impact_score": 0.85
            },
            "Testing Champion": {
                "coaching_sessions": 12,
                "suggestions_provided": 45,
                "suggestions_accepted": 40,
                "key_improvements": [
                    "Test-driven development adoption",
                    "Mock and stub strategies",
                    "Integration testing patterns"
                ],
                "ai_insights": [
                    "Recommended testing frameworks based on team patterns",
                    "Identified gaps in test coverage automatically",
                    "Suggested refactoring for better testability"
                ],
                "impact_score": 0.90
            },
            "Tech Lead Role": {
                "coaching_sessions": 15,
                "suggestions_provided": 60,
                "suggestions_accepted": 52,
                "key_improvements": [
                    "Architecture decision documentation",
                    "Code review leadership",
                    "Technical mentoring skills"
                ],
                "ai_insights": [
                    "Analyzed leadership patterns from successful tech leads",
                    "Provided communication templates for technical decisions",
                    "Identified opportunities for knowledge sharing"
                ],
                "impact_score": 0.88
            },
            "Architecture Design": {
                "coaching_sessions": 18,
                "suggestions_provided": 75,
                "suggestions_accepted": 65,
                "key_improvements": [
                    "System design principles",
                    "Scalability considerations",
                    "Technology selection criteria"
                ],
                "ai_insights": [
                    "Referenced architecture patterns from golden sources",
                    "Identified potential bottlenecks early in design",
                    "Suggested modern architectural approaches"
                ],
                "impact_score": 0.92
            },
            "Senior Developer": {
                "coaching_sessions": 25,
                "suggestions_provided": 100,
                "suggestions_accepted": 85,
                "key_improvements": [
                    "Cross-functional collaboration",
                    "Strategic technical thinking",
                    "Organization-wide impact"
                ],
                "ai_insights": [
                    "Identified opportunities for broader technical influence",
                    "Guided towards senior-level responsibilities",
                    "Provided career progression roadmap"
                ],
                "impact_score": 0.95
            }
        }
        
        # Return specific contribution or default
        return contributions.get(milestone_name, {
            "coaching_sessions": 5,
            "suggestions_provided": 20,
            "suggestions_accepted": 15,
            "key_improvements": ["General coding improvements", "Best practices adoption"],
            "ai_insights": ["Pattern recognition from golden sources", "Automated code analysis"],
            "impact_score": 0.70
        })
    
    def _get_skills_for_milestone(self, milestone_name: str) -> List[str]:
        """Get skills demonstrated by achieving a milestone"""
        skill_mapping = {
            "First Code Review": [
                "Python fundamentals",
                "Code documentation",
                "Version control",
                "Peer collaboration"
            ],
            "React Proficiency": [
                "JavaScript",
                "React",
                "Component design",
                "Frontend development",
                "State management"
            ],
            "Testing Champion": [
                "Test-driven development",
                "Unit testing",
                "Integration testing",
                "Quality assurance",
                "Testing frameworks"
            ],
            "Tech Lead Role": [
                "Technical leadership",
                "Code review",
                "Architecture decisions",
                "Team mentoring",
                "Communication"
            ],
            "Architecture Design": [
                "System design",
                "Architecture patterns",
                "Scalability planning",
                "Technology evaluation",
                "Documentation"
            ],
            "Senior Developer": [
                "Technical strategy",
                "Cross-functional collaboration",
                "Organizational impact",
                "Knowledge sharing",
                "Innovation leadership"
            ]
        }
        
        return skill_mapping.get(milestone_name, [
            "Problem solving",
            "Technical communication",
            "Continuous learning"
        ])
    
    def _generate_coaching_message(self, theme: str, month: int, phase: str) -> str:
        """Generate a coaching message for a specific theme and timeline"""
        messages = {
            "Code Quality": [
                f"Great progress on code quality this month! Your attention to detail in {phase} shows real growth.",
                f"I've noticed improvements in your error handling patterns. Let's focus on expanding these practices.",
                f"Your code structure is becoming more maintainable. Consider exploring advanced design patterns next.",
                f"The consistency in your naming conventions shows discipline. Ready for some architecture challenges?"
            ],
            "Testing": [
                f"Your testing coverage has improved significantly during {phase}. Well done!",
                f"I see you're embracing test-driven development. Let's explore integration testing strategies.",
                f"Your unit tests are becoming more comprehensive. Time to dive into mocking frameworks.",
                f"Testing automation is your next frontier. Your foundation is solid for advanced techniques."
            ],
            "Architecture": [
                f"Your architectural thinking is evolving nicely in {phase}. Keep pushing boundaries!",
                f"I notice you're considering scalability more often. That's senior-level thinking emerging.",
                f"Your component design shows understanding of separation of concerns. Excellent progress!",
                f"You're ready to tackle microservices architecture. Your foundation is rock-solid."
            ],
            "Performance": [
                f"Performance optimization is becoming second nature to you during {phase}.",
                f"Your profiling skills have improved dramatically. Time to explore advanced optimization techniques.",
                f"I see you're thinking about performance early in the design phase. That's mature engineering!",
                f"Your understanding of complexity analysis is impressive. Ready for distributed systems challenges?"
            ],
            "Security": [
                f"Security awareness is growing stronger each month. Your {phase} work shows this clearly.",
                f"Your threat modeling approach is becoming more sophisticated. Keep building on this!",
                f"I notice you're proactively considering security implications. That's expert-level thinking.",
                f"Your security practices are setting a great example for the team. Time to mentor others!"
            ],
            "Leadership": [
                f"Your leadership qualities are emerging naturally during {phase}. People are starting to notice.",
                f"The way you're mentoring junior developers shows real emotional intelligence.",
                f"Your technical decisions are becoming more strategic. That's leadership in action.",
                f"You're ready to take on more architectural responsibility. Your judgment has matured significantly."
            ]
        }
        
        theme_messages = messages.get(theme, [
            f"Your growth in {theme} during {phase} is noteworthy. Keep building on this momentum!",
            f"I see consistent improvement in {theme}. You're developing real expertise here.",
            f"Your approach to {theme} is becoming more sophisticated. Ready for the next challenge?",
            f"The progress you've made in {theme} shows dedication and natural aptitude."
        ])
        
        # Select message based on month for progression
        message_index = min(month // 3, len(theme_messages) - 1)
        base_message = theme_messages[message_index]
        
        # Add personalized touch based on timeline
        if month < 6:
            return f"{base_message} As you continue in your {phase}, focus on building strong fundamentals."
        elif month < 12:
            return f"{base_message} Your {phase} experience is showing - you're thinking more strategically now."
        else:
            return f"{base_message} Your {phase} expertise is evident - time to share this knowledge with others."
    
    def _get_skills_for_theme(self, theme: str) -> List[str]:
        """Get skills associated with a coaching theme"""
        skill_mapping = {
            "Code Quality": [
                "Code review",
                "Refactoring",
                "Clean code practices",
                "Documentation",
                "Static analysis"
            ],
            "Testing": [
                "Unit testing",
                "Test-driven development",
                "Integration testing",
                "Mock frameworks",
                "Test automation"
            ],
            "Architecture": [
                "System design",
                "Design patterns",
                "Microservices",
                "Scalability",
                "Component design"
            ],
            "Performance": [
                "Performance optimization",
                "Profiling",
                "Caching strategies",
                "Database optimization",
                "Algorithm efficiency"
            ],
            "Security": [
                "Security best practices",
                "Threat modeling",
                "Secure coding",
                "Authentication",
                "Data protection"
            ],
            "Leadership": [
                "Technical mentoring",
                "Decision making",
                "Communication",
                "Team collaboration",
                "Strategic thinking"
            ]
        }
        
        return skill_mapping.get(theme, [
            "Problem solving",
            "Technical communication",
            "Continuous learning"
        ])
    
    def _generate_action_items(self, theme: str, month: int) -> List[str]:
        """Generate action items for a coaching theme"""
        action_mapping = {
            "Code Quality": [
                "Review and refactor the authentication module",
                "Add comprehensive documentation to core utilities",
                "Implement consistent error handling patterns",
                "Set up automated code quality checks"
            ],
            "Testing": [
                "Increase test coverage to 80% for new features",
                "Write integration tests for the API endpoints",
                "Implement property-based testing for data validation",
                "Set up automated testing pipeline"
            ],
            "Architecture": [
                "Design the user service architecture",
                "Create architectural decision records (ADRs)",
                "Implement dependency injection patterns",
                "Review and optimize service boundaries"
            ],
            "Performance": [
                "Profile the dashboard loading performance",
                "Implement caching for frequently accessed data",
                "Optimize database queries in the user module",
                "Set up performance monitoring dashboards"
            ],
            "Security": [
                "Conduct security review of authentication flow",
                "Implement input validation for all endpoints",
                "Set up automated security scanning",
                "Review and update access control policies"
            ],
            "Leadership": [
                "Mentor a junior developer on React best practices",
                "Lead the architecture review session",
                "Present technical decisions to the product team",
                "Organize a knowledge sharing session"
            ]
        }
        
        base_actions = action_mapping.get(theme, [
            f"Research best practices in {theme}",
            f"Apply {theme} improvements to current project",
            f"Share {theme} learnings with the team"
        ])
        
        # Return 2-3 actions, varying by month
        num_actions = 2 + (month // 6)
        return base_actions[:min(num_actions, len(base_actions))]
    
    def _generate_learning_opportunities(self, theme: str) -> List[str]:
        """Generate learning opportunities for a theme"""
        opportunity_mapping = {
            "Code Quality": [
                "Explore advanced refactoring techniques",
                "Study clean architecture principles",
                "Learn about static analysis tools",
                "Practice code review best practices"
            ],
            "Testing": [
                "Dive deeper into test-driven development",
                "Explore property-based testing",
                "Learn behavior-driven development (BDD)",
                "Study testing in microservices architecture"
            ],
            "Architecture": [
                "Study Domain-Driven Design (DDD)",
                "Explore event-driven architecture",
                "Learn about CQRS patterns",
                "Research microservices communication patterns"
            ],
            "Performance": [
                "Learn advanced caching strategies",
                "Study database optimization techniques",
                "Explore distributed systems performance",
                "Practice performance profiling tools"
            ],
            "Security": [
                "Study OWASP security guidelines",
                "Learn about secure coding practices",
                "Explore security testing methodologies",
                "Research zero-trust architecture"
            ],
            "Leadership": [
                "Develop technical communication skills",
                "Practice mentoring techniques",
                "Learn about technical decision frameworks",
                "Study team leadership methodologies"
            ]
        }
        
        return opportunity_mapping.get(theme, [
            f"Deepen understanding of {theme} principles",
            f"Explore advanced {theme} techniques",
            f"Connect with {theme} expert community"
        ])
    
    def _generate_immediate_suggestions(self, theme: str) -> List[str]:
        """Generate immediate actionable suggestions"""
        suggestion_mapping = {
            "Code Quality": [
                "Run a code formatter on your recent changes",
                "Add docstrings to your public methods",
                "Extract that complex function into smaller, focused functions"
            ],
            "Testing": [
                "Write a test for the edge case you just fixed",
                "Add assertions to verify the error handling path",
                "Create a test data factory for your domain objects"
            ],
            "Architecture": [
                "Sketch out the component relationships before coding",
                "Define clear interfaces between your modules",
                "Consider the single responsibility principle for this class"
            ],
            "Performance": [
                "Profile this function to identify bottlenecks",
                "Consider caching this frequently accessed data",
                "Review the database queries in this module"
            ],
            "Security": [
                "Validate and sanitize this user input",
                "Review the authentication logic in this endpoint",
                "Consider the principle of least privilege here"
            ],
            "Leadership": [
                "Share this technical insight with the team",
                "Offer to pair with a junior developer on this",
                "Document your decision-making process"
            ]
        }
        
        return suggestion_mapping.get(theme, [
            f"Apply {theme} best practices to current work",
            f"Research {theme} solutions for this use case"
        ])
    
    def _generate_long_term_recommendations(self, theme: str, month: int) -> List[str]:
        """Generate long-term development recommendations"""
        recommendation_mapping = {
            "Code Quality": [
                "Build a personal code quality checklist",
                "Establish team coding standards and guidelines",
                "Implement automated code quality gates",
                "Mentor others on clean code practices"
            ],
            "Testing": [
                "Develop a comprehensive testing strategy",
                "Champion test-driven development adoption",
                "Build automated testing infrastructure",
                "Create testing workshops for the team"
            ],
            "Architecture": [
                "Develop system design expertise",
                "Lead architectural decision processes",
                "Create architectural documentation standards",
                "Become the go-to person for design reviews"
            ],
            "Performance": [
                "Become the team's performance expert",
                "Establish performance monitoring practices",
                "Lead performance optimization initiatives",
                "Create performance budgets and guidelines"
            ],
            "Security": [
                "Develop security expertise and awareness",
                "Lead security review processes",
                "Establish secure development practices",
                "Become a security champion for the team"
            ],
            "Leadership": [
                "Develop technical mentoring skills",
                "Take on cross-team technical initiatives",
                "Build consensus-building abilities",
                "Prepare for technical leadership roles"
            ]
        }
        
        base_recommendations = recommendation_mapping.get(theme, [
            f"Develop deep expertise in {theme}",
            f"Share {theme} knowledge with the broader team",
            f"Lead {theme} initiatives across projects"
        ])
        
        # Return more strategic recommendations as months progress
        if month < 6:
            return base_recommendations[:2]
        elif month < 12:
            return base_recommendations[:3]
        else:
            return base_recommendations
    
    def _generate_resource_suggestions(self, theme: str) -> List[LearningResource]:
        """Generate learning resource suggestions for a theme"""
        resource_mapping = {
            "Code Quality": [
                {
                    "resource_id": "clean_code_book",
                    "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
                    "type": "book",
                    "provider": "Robert C. Martin",
                    "difficulty": "intermediate",
                    "estimated_hours": 20.0,
                    "skills_covered": ["Clean code practices", "Refactoring", "Code review"],
                    "relevance_score": 0.95,
                    "personalization_reason": "Perfect for developing code quality instincts"
                },
                {
                    "resource_id": "refactoring_course",
                    "title": "Refactoring: Improving the Design of Existing Code",
                    "type": "course",
                    "provider": "Pluralsight",
                    "difficulty": "intermediate",
                    "estimated_hours": 8.0,
                    "skills_covered": ["Refactoring", "Design patterns"],
                    "relevance_score": 0.90,
                    "personalization_reason": "Hands-on practice with refactoring techniques"
                }
            ],
            "Testing": [
                {
                    "resource_id": "tdd_course",
                    "title": "Test-Driven Development: The Practical Guide",
                    "type": "course",
                    "provider": "Udemy",
                    "difficulty": "beginner",
                    "estimated_hours": 12.0,
                    "skills_covered": ["Test-driven development", "Unit testing"],
                    "relevance_score": 0.92,
                    "personalization_reason": "Structured approach to learning TDD methodology"
                }
            ],
            "Architecture": [
                {
                    "resource_id": "system_design_course",
                    "title": "System Design Fundamentals",
                    "type": "course",
                    "provider": "System Design Interview",
                    "difficulty": "intermediate",
                    "estimated_hours": 15.0,
                    "skills_covered": ["System design", "Scalability", "Architecture patterns"],
                    "relevance_score": 0.93,
                    "personalization_reason": "Essential for developing architectural thinking"
                }
            ],
            "Performance": [
                {
                    "resource_id": "performance_optimization",
                    "title": "High Performance Python",
                    "type": "book",
                    "provider": "O'Reilly Media",
                    "difficulty": "advanced",
                    "estimated_hours": 25.0,
                    "skills_covered": ["Performance optimization", "Profiling", "Caching"],
                    "relevance_score": 0.88,
                    "personalization_reason": "Deep dive into Python performance techniques"
                }
            ],
            "Security": [
                {
                    "resource_id": "secure_coding",
                    "title": "Secure Coding Practices",
                    "type": "tutorial",
                    "provider": "OWASP",
                    "difficulty": "intermediate",
                    "estimated_hours": 10.0,
                    "skills_covered": ["Secure coding", "Threat modeling", "Security best practices"],
                    "relevance_score": 0.91,
                    "personalization_reason": "Industry-standard security practices"
                }
            ],
            "Leadership": [
                {
                    "resource_id": "tech_leadership",
                    "title": "The Manager's Path: A Guide for Tech Leaders",
                    "type": "book",
                    "provider": "Camille Fournier",
                    "difficulty": "intermediate",
                    "estimated_hours": 15.0,
                    "skills_covered": ["Technical leadership", "Mentoring", "Team management"],
                    "relevance_score": 0.94,
                    "personalization_reason": "Roadmap for transitioning to technical leadership"
                }
            ]
        }
        
        theme_resources = resource_mapping.get(theme, [
            {
                "resource_id": f"{theme.lower()}_general",
                "title": f"Introduction to {theme}",
                "type": "course",
                "provider": "Generic Provider",
                "difficulty": "beginner",
                "estimated_hours": 8.0,
                "skills_covered": [theme],
                "relevance_score": 0.75,
                "personalization_reason": f"Foundation building in {theme}"
            }
        ])
        
        # Convert to LearningResource objects
        learning_resources = []
        for resource_data in theme_resources:
            learning_resources.append(
                LearningResource(**resource_data)
            )
        
        return learning_resources
    
    def _generate_quality_timeline(self, dimension: str, start_date: datetime, end_date: datetime, base_score: float) -> List[Dict[str, Any]]:
        """Generate quality timeline for a specific dimension"""
        timeline = []
        current_date = start_date
        
        # Calculate total days for progression
        total_days = (end_date - start_date).days
        
        while current_date <= end_date:
            # Calculate progression based on elapsed time
            days_elapsed = (current_date - start_date).days
            progress_ratio = days_elapsed / max(total_days, 1)
            
            # Generate realistic improvement curve with some variance
            improvement = progress_ratio * 0.3  # Maximum 30% improvement over period
            
            # Add some realistic variance based on dimension and date
            variance_seed = hash(f"{dimension}_{current_date.strftime('%Y%m%d')}")
            variance = (variance_seed % 10) * 0.01  # ±5% variance
            
            # Calculate final score with bounds checking
            score = min(0.95, max(0.1, base_score + improvement + variance))
            
            # Determine trend based on previous week
            if len(timeline) > 0:
                prev_score = timeline[-1]["score"]
                if score > prev_score + 0.02:
                    trend = "improving"
                elif score < prev_score - 0.02:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "improving"  # First data point
            
            timeline.append({
                "timestamp": current_date,
                "score": round(score, 3),
                "trend": trend,
                "dimension": dimension,
                "notes": self._generate_quality_notes(dimension, score, progress_ratio)
            })
            
            # Move to next week
            current_date += timedelta(days=7)
        
        return timeline
    
    def _generate_golden_source_timeline(self, start_date: datetime, end_date: datetime, base_similarity: float) -> List[Dict[str, Any]]:
        """Generate timeline showing similarity to golden sources"""
        timeline = []
        current_date = start_date
        
        # Calculate total days for progression
        total_days = (end_date - start_date).days
        
        while current_date <= end_date:
            # Calculate progression - gradual improvement in alignment with golden sources
            days_elapsed = (current_date - start_date).days
            progress_ratio = days_elapsed / max(total_days, 1)
            
            # Simulate learning from golden sources with diminishing returns
            improvement = progress_ratio * 0.25 * (1 - progress_ratio * 0.3)
            
            # Add realistic variance
            variance_seed = hash(f"golden_source_{current_date.strftime('%Y%m%d')}")
            variance = ((variance_seed % 10) - 5) * 0.008  # ±4% variance
            
            # Calculate similarity score
            similarity = min(0.92, max(0.3, base_similarity + improvement + variance))
            
            # Determine which golden source patterns were learned
            learned_patterns = []
            if similarity > 0.6:
                learned_patterns.append("Error handling patterns")
            if similarity > 0.7:
                learned_patterns.append("Code organization principles")
            if similarity > 0.8:
                learned_patterns.append("Testing methodologies")
            if similarity > 0.85:
                learned_patterns.append("Architecture patterns")
            
            timeline.append({
                "timestamp": current_date,
                "similarity_score": round(similarity, 3),
                "patterns_learned": learned_patterns,
                "golden_source_influences": self._get_golden_source_influences(similarity),
                "alignment_areas": [
                    "Code style consistency",
                    "Best practices adoption", 
                    "Architecture alignment",
                    "Security practices"
                ]
            })
            
            # Move to next week
            current_date += timedelta(days=7)
        
        return timeline
    
    def _generate_quality_notes(self, dimension: str, score: float, progress_ratio: float) -> str:
        """Generate contextual notes for quality improvements"""
        note_templates = {
            "complexity": {
                0.3: "Starting to break down monolithic functions",
                0.5: "Consistently applying single responsibility principle",
                0.7: "Creating well-structured, modular code",
                0.9: "Writing highly maintainable, clean architecture"
            },
            "patterns": {
                0.3: "Learning basic design patterns",
                0.5: "Applying factory and observer patterns",
                0.7: "Using advanced patterns like strategy and decorator",
                0.9: "Implementing complex architectural patterns"
            },
            "security": {
                0.3: "Basic input validation implemented",
                0.5: "Proper authentication and authorization",
                0.7: "Advanced security measures in place",
                0.9: "Security-first development approach"
            },
            "maintainability": {
                0.3: "Adding basic documentation and comments",
                0.5: "Consistent code structure and naming",
                0.7: "Comprehensive documentation and testing",
                0.9: "Exemplary code maintainability standards"
            },
            "test_coverage": {
                0.3: "Writing basic unit tests",
                0.5: "Achieving 60%+ test coverage",
                0.7: "Comprehensive testing including edge cases",
                0.9: "Exemplary testing practices with 90%+ coverage"
            },
            "documentation": {
                0.3: "Adding inline comments to complex logic",
                0.5: "Comprehensive function and class documentation",
                0.7: "Complete API documentation and examples",
                0.9: "Industry-leading documentation standards"
            }
        }
        
        dimension_notes = note_templates.get(dimension, {})
        
        # Find the appropriate note based on score
        for threshold in sorted(dimension_notes.keys(), reverse=True):
            if score >= threshold:
                return dimension_notes[threshold]
        
        return f"Making progress in {dimension}"
    
    def _get_golden_source_influences(self, similarity_score: float) -> List[str]:
        """Get list of golden source influences based on similarity score"""
        influences = []
        
        if similarity_score > 0.4:
            influences.append("Company Python style guide")
        if similarity_score > 0.5:
            influences.append("Team's React component patterns")
        if similarity_score > 0.6:
            influences.append("Senior developer code reviews")
        if similarity_score > 0.7:
            influences.append("Open source best practices")
        if similarity_score > 0.8:
            influences.append("Industry-standard architecture patterns")
        if similarity_score > 0.85:
            influences.append("Expert-level implementation techniques")
        
        return influences
    
    def _generate_skill_evidence(self, skill_name: str, month: int) -> List[str]:
        """Generate evidence for skill assessments"""
        evidence_mapping = {
            "Python": [
                "Implemented clean, Pythonic code with proper error handling",
                "Used advanced Python features like decorators and context managers",
                "Wrote comprehensive unit tests with pytest",
                "Applied PEP 8 style guidelines consistently"
            ],
            "JavaScript": [
                "Built interactive frontend components with modern ES6+ syntax",
                "Implemented async/await patterns for API communication",
                "Created reusable utility functions and modules",
                "Applied proper error handling and input validation"
            ],
            "React": [
                "Developed component-based architecture with hooks",
                "Implemented state management with useState and useEffect",
                "Created reusable components with proper prop validation",
                "Applied React best practices for performance optimization"
            ],
            "TypeScript": [
                "Added strong typing to existing JavaScript codebase",
                "Created custom type definitions and interfaces",
                "Implemented generic functions and advanced type features",
                "Integrated TypeScript with build tools and linting"
            ],
            "Testing": [
                "Achieved 80%+ test coverage on new features",
                "Wrote unit, integration, and end-to-end tests",
                "Implemented test-driven development practices",
                "Created mock data and fixtures for testing"
            ],
            "Architecture": [
                "Designed scalable microservices architecture",
                "Applied design patterns like Factory and Observer",
                "Created architectural decision records (ADRs)",
                "Implemented separation of concerns principles"
            ],
            "Performance": [
                "Optimized database queries reducing response time by 40%",
                "Implemented caching strategies for frequently accessed data",
                "Profiled application performance and identified bottlenecks",
                "Applied lazy loading and code splitting techniques"
            ],
            "Security": [
                "Implemented secure authentication and authorization",
                "Applied input validation and SQL injection prevention",
                "Conducted security code reviews and threat modeling",
                "Integrated security scanning into CI/CD pipeline"
            ],
            "Team Collaboration": [
                "Led code review sessions with constructive feedback",
                "Mentored junior developers on best practices",
                "Facilitated technical discussions and decision making",
                "Created comprehensive documentation for team projects"
            ],
            "Problem Solving": [
                "Debugged complex production issues efficiently",
                "Broke down large problems into manageable components",
                "Applied systematic troubleshooting methodologies",
                "Created innovative solutions to technical challenges"
            ]
        }
        
        base_evidence = evidence_mapping.get(skill_name, [
            f"Demonstrated proficiency in {skill_name} through code review",
            f"Applied {skill_name} best practices in project development",
            f"Showed continuous improvement in {skill_name} over time"
        ])
        
        # Progress evidence based on month
        progressive_evidence = []
        if month < 6:
            progressive_evidence = [
                f"Learning foundational {skill_name} concepts",
                f"Applying basic {skill_name} patterns in simple use cases"
            ]
        elif month < 12:
            progressive_evidence = [
                f"Confidently using intermediate {skill_name} features",
                f"Teaching {skill_name} concepts to other team members"
            ]
        else:
            progressive_evidence = [
                f"Leading {skill_name} architecture decisions",
                f"Mentoring others on advanced {skill_name} techniques"
            ]
        
        # Combine base evidence with progressive evidence
        all_evidence = base_evidence + progressive_evidence
        
        # Return 2-4 pieces of evidence based on skill maturity
        num_evidence = 2 + (month // 6)
        return all_evidence[:min(num_evidence, len(all_evidence))]
    
    def _generate_pattern_matches(self, skill_name: str, month: int) -> List[Dict[str, Any]]:
        """Generate pattern matches for skill assessments"""
        pattern_templates = {
            "Python": [
                {
                    "pattern_name": "Context Manager Usage",
                    "pattern_type": "pythonic_patterns",
                    "description": "Proper use of context managers for resource handling",
                    "confidence": 0.85
                },
                {
                    "pattern_name": "List Comprehensions",
                    "pattern_type": "data_processing",
                    "description": "Efficient data processing with list comprehensions",
                    "confidence": 0.90
                },
                {
                    "pattern_name": "Exception Handling",
                    "pattern_type": "error_handling",
                    "description": "Proper exception handling with specific exception types",
                    "confidence": 0.80
                }
            ],
            "JavaScript": [
                {
                    "pattern_name": "Promise Chaining",
                    "pattern_type": "async_patterns",
                    "description": "Proper async/await and promise handling",
                    "confidence": 0.85
                },
                {
                    "pattern_name": "Module Pattern",
                    "pattern_type": "organization",
                    "description": "ES6 module imports/exports for code organization",
                    "confidence": 0.90
                },
                {
                    "pattern_name": "Arrow Functions",
                    "pattern_type": "modern_syntax",
                    "description": "Appropriate use of arrow functions and lexical scope",
                    "confidence": 0.85
                }
            ],
            "React": [
                {
                    "pattern_name": "Custom Hooks",
                    "pattern_type": "hooks_pattern",
                    "description": "Creation and usage of custom React hooks",
                    "confidence": 0.85
                },
                {
                    "pattern_name": "Component Composition",
                    "pattern_type": "architectural",
                    "description": "Proper component composition over inheritance",
                    "confidence": 0.90
                },
                {
                    "pattern_name": "State Management",
                    "pattern_type": "state_patterns",
                    "description": "Effective state management with hooks",
                    "confidence": 0.85
                }
            ],
            "TypeScript": [
                {
                    "pattern_name": "Interface Design",
                    "pattern_type": "type_definition",
                    "description": "Well-designed interfaces and type definitions",
                    "confidence": 0.90
                },
                {
                    "pattern_name": "Generic Functions",
                    "pattern_type": "advanced_types",
                    "description": "Proper use of generics for type safety",
                    "confidence": 0.85
                },
                {
                    "pattern_name": "Type Guards",
                    "pattern_type": "type_safety",
                    "description": "Implementation of type guards for runtime safety",
                    "confidence": 0.80
                }
            ],
            "Testing": [
                {
                    "pattern_name": "Test Structure",
                    "pattern_type": "test_organization",
                    "description": "Well-organized test suites with clear structure",
                    "confidence": 0.90
                },
                {
                    "pattern_name": "Mock Usage",
                    "pattern_type": "test_doubles",
                    "description": "Appropriate use of mocks and stubs",
                    "confidence": 0.85
                },
                {
                    "pattern_name": "Edge Case Testing",
                    "pattern_type": "test_coverage",
                    "description": "Comprehensive edge case and error condition testing",
                    "confidence": 0.80
                }
            ]
        }
        
        # Get patterns for the skill or default patterns
        skill_patterns = pattern_templates.get(skill_name, [
            {
                "pattern_name": f"{skill_name} Best Practices",
                "pattern_type": "general",
                "description": f"Following {skill_name} coding standards and conventions",
                "confidence": 0.75
            }
        ])
        
        # Adjust confidence based on month progression
        confidence_multiplier = 0.6 + (month * 0.02)  # Start at 60%, increase by 2% per month
        
        patterns = []
        for pattern in skill_patterns:
            adjusted_pattern = pattern.copy()
            adjusted_pattern["confidence"] = min(0.95, pattern["confidence"] * confidence_multiplier)
            adjusted_pattern["month_detected"] = month + 1
            adjusted_pattern["evidence_strength"] = "strong" if adjusted_pattern["confidence"] > 0.8 else "moderate"
            patterns.append(adjusted_pattern)
        
        # Return 1-3 patterns based on skill maturity
        num_patterns = 1 + (month // 8)
        return patterns[:min(num_patterns, len(patterns))]
    
    def _generate_code_examples(self, skill_name: str, month: int) -> List[str]:
        """Generate code examples for skill assessments"""
        code_examples = {
            "Python": [
                "def process_data(data: List[Dict]) -> Dict[str, Any]:",
                "with open('config.json') as f: config = json.load(f)",
                "result = [item['value'] for item in data if item.get('active')]",
                "try: response = api_call() except APIError as e: logger.error(f'API failed: {e}')"
            ],
            "JavaScript": [
                "const fetchUserData = async (userId) => { const response = await fetch(`/api/users/${userId}`); return response.json(); }",
                "const processItems = items => items.filter(item => item.active).map(item => ({ ...item, processed: true }));",
                "export class UserService { constructor(apiClient) { this.apiClient = apiClient; } }",
                "const debounce = (func, delay) => { let timeoutId; return (...args) => { clearTimeout(timeoutId); timeoutId = setTimeout(() => func.apply(this, args), delay); }; };"
            ],
            "React": [
                "const useLocalStorage = (key, initialValue) => { const [value, setValue] = useState(() => { const item = localStorage.getItem(key); return item ? JSON.parse(item) : initialValue; }); }",
                "const UserProfile = ({ userId }) => { const [user, setUser] = useState(null); useEffect(() => { fetchUser(userId).then(setUser); }, [userId]); return user ? <div>{user.name}</div> : <Loading />; };",
                "const Button = ({ children, variant = 'primary', onClick, ...props }) => { return <button className={`btn btn-${variant}`} onClick={onClick} {...props}>{children}</button>; };",
                "const useDebounce = (value, delay) => { const [debouncedValue, setDebouncedValue] = useState(value); useEffect(() => { const handler = setTimeout(() => setDebouncedValue(value), delay); return () => clearTimeout(handler); }, [value, delay]); return debouncedValue; };"
            ],
            "TypeScript": [
                "interface ApiResponse<T> { data: T; status: number; message: string; }",
                "type UserRole = 'admin' | 'user' | 'guest'; interface User { id: string; name: string; role: UserRole; }",
                "function processArray<T>(items: T[], predicate: (item: T) => boolean): T[] { return items.filter(predicate); }",
                "const isUser = (obj: any): obj is User => { return obj && typeof obj.id === 'string' && typeof obj.name === 'string'; };"
            ],
            "Testing": [
                "describe('UserService', () => { beforeEach(() => { userService = new UserService(mockApiClient); }); it('should fetch user data', async () => { const user = await userService.getUser('123'); expect(user).toMatchObject({ id: '123' }); }); });",
                "const mockApiClient = { get: jest.fn().mockResolvedValue({ data: { id: '123', name: 'John' } }) };",
                "test('should handle API errors gracefully', async () => { mockApiClient.get.mockRejectedValueOnce(new Error('Network error')); await expect(userService.getUser('123')).rejects.toThrow('Network error'); });",
                "it('should validate user input', () => { const result = validateUser({ name: '', email: 'invalid' }); expect(result.errors).toContain('Name is required'); expect(result.errors).toContain('Invalid email format'); });"
            ],
            "Architecture": [
                "// Factory Pattern: class UserFactory { static createUser(type, data) { switch(type) { case 'admin': return new AdminUser(data); case 'regular': return new RegularUser(data); } } }",
                "// Observer Pattern: class EventEmitter { constructor() { this.listeners = {}; } on(event, callback) { this.listeners[event] = this.listeners[event] || []; this.listeners[event].push(callback); } }",
                "// Dependency Injection: class UserController { constructor(userService, emailService) { this.userService = userService; this.emailService = emailService; } }",
                "// Command Pattern: class CreateUserCommand { constructor(userData) { this.userData = userData; } execute() { return this.userService.create(this.userData); } }"
            ]
        }
        
        skill_examples = code_examples.get(skill_name, [
            f"// Example {skill_name} implementation",
            f"// {skill_name} best practices applied here",
            f"// Clean, maintainable {skill_name} code"
        ])
        
        # Return 1-3 code examples based on skill maturity
        num_examples = 1 + (month // 9)
        return skill_examples[:min(num_examples, len(skill_examples))]
    
    def _get_priority_skills_for_phase(self, phase_name: str) -> List[Dict[str, Any]]:
        """Get priority skills for each learning phase"""
        priority_skills_mapping = {
            "foundation": [
                {"skill": "Python", "target_level": 0.6, "priority": 1},
                {"skill": "Code Quality", "target_level": 0.5, "priority": 1},
                {"skill": "Version Control", "target_level": 0.7, "priority": 2},
                {"skill": "Testing", "target_level": 0.4, "priority": 2},
                {"skill": "Documentation", "target_level": 0.5, "priority": 3}
            ],
            "acceleration": [
                {"skill": "JavaScript", "target_level": 0.8, "priority": 1},
                {"skill": "React", "target_level": 0.7, "priority": 1},
                {"skill": "Testing", "target_level": 0.7, "priority": 2},
                {"skill": "Architecture", "target_level": 0.5, "priority": 2},
                {"skill": "Performance", "target_level": 0.6, "priority": 3}
            ],
            "leadership": [
                {"skill": "Architecture", "target_level": 0.8, "priority": 1},
                {"skill": "Team Collaboration", "target_level": 0.8, "priority": 1},
                {"skill": "Mentoring", "target_level": 0.6, "priority": 2},
                {"skill": "Technical Leadership", "target_level": 0.7, "priority": 2},
                {"skill": "System Design", "target_level": 0.7, "priority": 3}
            ],
            "senior": [
                {"skill": "Technical Strategy", "target_level": 0.9, "priority": 1},
                {"skill": "Cross-functional Leadership", "target_level": 0.8, "priority": 1},
                {"skill": "Innovation", "target_level": 0.7, "priority": 2},
                {"skill": "Organizational Impact", "target_level": 0.8, "priority": 2},
                {"skill": "Knowledge Sharing", "target_level": 0.9, "priority": 3}
            ]
        }
        
        return priority_skills_mapping.get(phase_name, [
            {"skill": "General Programming", "target_level": 0.6, "priority": 1}
        ])
    
    def _get_learning_objectives_for_phase(self, phase_name: str) -> List[str]:
        """Get learning objectives for each phase"""
        objectives_mapping = {
            "foundation": [
                "Master Python programming fundamentals",
                "Understand clean code principles and best practices",
                "Learn git version control and collaborative development",
                "Write basic unit tests and understand TDD",
                "Develop consistent documentation habits"
            ],
            "acceleration": [
                "Build proficiency in JavaScript and modern ES6+ features",
                "Master React development and component-based architecture",
                "Implement comprehensive testing strategies",
                "Understand basic software architecture patterns",
                "Optimize code performance and identify bottlenecks"
            ],
            "leadership": [
                "Design scalable system architectures",
                "Lead technical discussions and code reviews",
                "Mentor junior developers effectively",
                "Make strategic technical decisions",
                "Communicate complex technical concepts clearly"
            ],
            "senior": [
                "Drive technical strategy and innovation",
                "Lead cross-functional technical initiatives",
                "Foster a culture of technical excellence",
                "Influence organizational technical direction",
                "Build and share institutional knowledge"
            ]
        }
        
        return objectives_mapping.get(phase_name, [
            f"Continue professional development in {phase_name} phase"
        ])
    
    def _get_target_career_stage_for_phase(self, phase_name: str) -> Optional[CareerStage]:
        """Get target career stage for each phase"""
        stage_mapping = {
            "foundation": CareerStage.JUNIOR,
            "acceleration": CareerStage.MID,
            "leadership": CareerStage.SENIOR,
            "senior": CareerStage.LEAD
        }
        
        return stage_mapping.get(phase_name)
    
    def _generate_learning_path_for_phase(self, phase_name: str) -> List[Dict[str, Any]]:
        """Generate learning path steps for each phase"""
        learning_paths = {
            "foundation": [
                {
                    "step": 1,
                    "title": "Python Fundamentals",
                    "description": "Master basic Python syntax, data structures, and control flow",
                    "estimated_weeks": 3,
                    "skills": ["Python", "Problem Solving"],
                    "activities": ["Complete Python tutorial", "Build simple projects", "Practice coding challenges"]
                },
                {
                    "step": 2,
                    "title": "Code Quality Basics",
                    "description": "Learn clean code principles and basic refactoring",
                    "estimated_weeks": 2,
                    "skills": ["Code Quality", "Documentation"],
                    "activities": ["Read Clean Code chapters", "Practice refactoring exercises", "Write meaningful comments"]
                },
                {
                    "step": 3,
                    "title": "Version Control & Collaboration",
                    "description": "Master git workflows and collaborative development",
                    "estimated_weeks": 2,
                    "skills": ["Version Control", "Team Collaboration"],
                    "activities": ["Learn git commands", "Practice branching", "Participate in code reviews"]
                },
                {
                    "step": 4,
                    "title": "Testing Introduction",
                    "description": "Understand unit testing and TDD basics",
                    "estimated_weeks": 3,
                    "skills": ["Testing", "Quality Assurance"],
                    "activities": ["Write first unit tests", "Practice TDD workflow", "Learn testing frameworks"]
                }
            ],
            "acceleration": [
                {
                    "step": 1,
                    "title": "JavaScript Mastery",
                    "description": "Deep dive into modern JavaScript and ES6+ features",
                    "estimated_weeks": 4,
                    "skills": ["JavaScript", "Frontend Development"],
                    "activities": ["Learn async/await", "Master array methods", "Understand closures and scope"]
                },
                {
                    "step": 2,
                    "title": "React Development",
                    "description": "Build modern React applications with hooks and best practices",
                    "estimated_weeks": 5,
                    "skills": ["React", "Component Design"],
                    "activities": ["Create React components", "Master hooks", "Build complete applications"]
                },
                {
                    "step": 3,
                    "title": "Advanced Testing",
                    "description": "Implement comprehensive testing strategies",
                    "estimated_weeks": 3,
                    "skills": ["Testing", "Quality Assurance"],
                    "activities": ["Integration testing", "E2E testing", "Test automation"]
                },
                {
                    "step": 4,
                    "title": "Architecture Fundamentals",
                    "description": "Learn basic software architecture patterns",
                    "estimated_weeks": 4,
                    "skills": ["Architecture", "System Design"],
                    "activities": ["Study design patterns", "Implement MVC", "Learn component architecture"]
                }
            ],
            "leadership": [
                {
                    "step": 1,
                    "title": "System Architecture",
                    "description": "Design scalable and maintainable systems",
                    "estimated_weeks": 6,
                    "skills": ["Architecture", "System Design"],
                    "activities": ["Design microservices", "Learn distributed systems", "Practice system design"]
                },
                {
                    "step": 2,
                    "title": "Technical Leadership",
                    "description": "Develop technical leadership and decision-making skills",
                    "estimated_weeks": 4,
                    "skills": ["Technical Leadership", "Decision Making"],
                    "activities": ["Lead technical discussions", "Make architecture decisions", "Present to stakeholders"]
                },
                {
                    "step": 3,
                    "title": "Mentoring & Coaching",
                    "description": "Learn to effectively mentor and guide junior developers",
                    "estimated_weeks": 4,
                    "skills": ["Mentoring", "Team Collaboration"],
                    "activities": ["Mentor junior developers", "Conduct code reviews", "Provide constructive feedback"]
                }
            ],
            "senior": [
                {
                    "step": 1,
                    "title": "Technical Strategy",
                    "description": "Drive organizational technical direction and innovation",
                    "estimated_weeks": 4,
                    "skills": ["Technical Strategy", "Innovation"],
                    "activities": ["Develop technical roadmaps", "Evaluate new technologies", "Lead technical initiatives"]
                },
                {
                    "step": 2,
                    "title": "Cross-functional Leadership",
                    "description": "Lead technical initiatives across multiple teams",
                    "estimated_weeks": 5,
                    "skills": ["Cross-functional Leadership", "Communication"],
                    "activities": ["Coordinate with product teams", "Align technical and business goals", "Manage stakeholders"]
                },
                {
                    "step": 3,
                    "title": "Knowledge Institutionalization",
                    "description": "Build and share institutional technical knowledge",
                    "estimated_weeks": 3,
                    "skills": ["Knowledge Sharing", "Documentation"],
                    "activities": ["Create technical documentation", "Run engineering talks", "Build internal training"]
                }
            ]
        }
        
        return learning_paths.get(phase_name, [
            {
                "step": 1,
                "title": f"Continue {phase_name} development",
                "description": f"Focus on {phase_name}-specific skills",
                "estimated_weeks": 4,
                "skills": ["General Development"],
                "activities": ["Practice relevant skills", "Seek feedback", "Apply learnings"]
            }
        ])
    
    def _generate_milestones_for_phase(self, phase_name: str) -> List[LearningMilestone]:
        """Generate learning milestones for each phase"""
        milestone_templates = {
            "foundation": [
                {
                    "milestone_id": f"foundation_milestone_1",
                    "title": "First Successful Code Review",
                    "description": "Complete first code review with positive feedback",
                    "skills_involved": ["Python", "Code Quality", "Collaboration"],
                    "success_criteria": ["Code review approved", "No major refactoring needed", "Positive peer feedback"],
                    "estimated_duration": "4 weeks"
                },
                {
                    "milestone_id": f"foundation_milestone_2",
                    "title": "Basic Testing Competency",
                    "description": "Write comprehensive tests for a feature",
                    "skills_involved": ["Testing", "Python", "Quality Assurance"],
                    "success_criteria": ["Tests cover main functionality", "Tests pass consistently", "Test quality feedback"],
                    "estimated_duration": "6 weeks"
                }
            ],
            "acceleration": [
                {
                    "milestone_id": f"acceleration_milestone_1",
                    "title": "React Component Library",
                    "description": "Build reusable React component library",
                    "skills_involved": ["React", "JavaScript", "Component Design"],
                    "success_criteria": ["Components are reusable", "Good documentation", "Used by team"],
                    "estimated_duration": "8 weeks"
                },
                {
                    "milestone_id": f"acceleration_milestone_2",
                    "title": "Performance Optimization",
                    "description": "Successfully optimize application performance",
                    "skills_involved": ["Performance", "JavaScript", "Analysis"],
                    "success_criteria": ["Measurable performance gains", "Monitoring implemented", "Best practices applied"],
                    "estimated_duration": "6 weeks"
                }
            ],
            "leadership": [
                {
                    "milestone_id": f"leadership_milestone_1",
                    "title": "Architecture Decision Leadership",
                    "description": "Lead a significant architecture decision",
                    "skills_involved": ["Architecture", "Technical Leadership", "Communication"],
                    "success_criteria": ["Decision documented", "Team consensus achieved", "Implementation successful"],
                    "estimated_duration": "10 weeks"
                },
                {
                    "milestone_id": f"leadership_milestone_2",
                    "title": "Junior Developer Mentoring",
                    "description": "Successfully mentor a junior developer",
                    "skills_involved": ["Mentoring", "Technical Leadership", "Communication"],
                    "success_criteria": ["Mentee shows growth", "Positive feedback", "Continued relationship"],
                    "estimated_duration": "12 weeks"
                }
            ],
            "senior": [
                {
                    "milestone_id": f"senior_milestone_1",
                    "title": "Technical Strategy Implementation",
                    "description": "Successfully implement a technical strategy initiative",
                    "skills_involved": ["Technical Strategy", "Leadership", "Innovation"],
                    "success_criteria": ["Strategy adopted", "Measurable impact", "Team alignment"],
                    "estimated_duration": "16 weeks"
                },
                {
                    "milestone_id": f"senior_milestone_2",
                    "title": "Knowledge Sharing Platform",
                    "description": "Create knowledge sharing platform for the organization",
                    "skills_involved": ["Knowledge Sharing", "Technical Leadership", "Innovation"],
                    "success_criteria": ["Platform widely used", "Knowledge base grows", "Team learning improves"],
                    "estimated_duration": "12 weeks"
                }
            ]
        }
        
        milestones_data = milestone_templates.get(phase_name, [])
        milestones = []
        
        for milestone_data in milestones_data:
            milestone = LearningMilestone(**milestone_data)
            milestones.append(milestone)
        
        return milestones
    
    def _generate_resources_for_phase(self, phase_name: str) -> List[LearningResource]:
        """Generate learning resources for each phase"""
        resources_mapping = {
            "foundation": [
                {
                    "resource_id": "python_crash_course",
                    "title": "Python Crash Course",
                    "type": "book",
                    "provider": "No Starch Press",
                    "difficulty": "beginner",
                    "estimated_hours": 40.0,
                    "skills_covered": ["Python", "Programming Fundamentals"],
                    "relevance_score": 0.95,
                    "personalization_reason": "Perfect introduction to Python for beginners"
                },
                {
                    "resource_id": "clean_code_principles",
                    "title": "Clean Code Principles for Beginners",
                    "type": "course",
                    "provider": "Codecademy",
                    "difficulty": "beginner",
                    "estimated_hours": 12.0,
                    "skills_covered": ["Code Quality", "Best Practices"],
                    "relevance_score": 0.90,
                    "personalization_reason": "Essential for developing good coding habits"
                }
            ],
            "acceleration": [
                {
                    "resource_id": "react_complete_guide",
                    "title": "React - The Complete Guide",
                    "type": "course",
                    "provider": "Udemy",
                    "difficulty": "intermediate",
                    "estimated_hours": 48.0,
                    "skills_covered": ["React", "JavaScript", "Frontend"],
                    "relevance_score": 0.95,
                    "personalization_reason": "Comprehensive React learning for intermediate developers"
                },
                {
                    "resource_id": "testing_javascript",
                    "title": "Testing JavaScript Applications",
                    "type": "course",
                    "provider": "Testing Library",
                    "difficulty": "intermediate",
                    "estimated_hours": 20.0,
                    "skills_covered": ["Testing", "JavaScript", "Quality"],
                    "relevance_score": 0.90,
                    "personalization_reason": "Advanced testing strategies for modern web apps"
                }
            ],
            "leadership": [
                {
                    "resource_id": "system_design_interview",
                    "title": "System Design Interview Guide",
                    "type": "book",
                    "provider": "System Design Interview",
                    "difficulty": "advanced",
                    "estimated_hours": 30.0,
                    "skills_covered": ["System Design", "Architecture"],
                    "relevance_score": 0.95,
                    "personalization_reason": "Essential for technical leadership roles"
                },
                {
                    "resource_id": "technical_leadership",
                    "title": "Becoming a Technical Leader",
                    "type": "book",
                    "provider": "Dorset House",
                    "difficulty": "intermediate",
                    "estimated_hours": 15.0,
                    "skills_covered": ["Technical Leadership", "Management"],
                    "relevance_score": 0.90,
                    "personalization_reason": "Develop leadership skills for senior roles"
                }
            ],
            "senior": [
                {
                    "resource_id": "staff_engineer_path",
                    "title": "Staff Engineer: Leadership Beyond the Management Track",
                    "type": "book",
                    "provider": "O'Reilly Media",
                    "difficulty": "advanced",
                    "estimated_hours": 25.0,
                    "skills_covered": ["Technical Strategy", "Leadership"],
                    "relevance_score": 0.95,
                    "personalization_reason": "Guide for reaching principal engineer level"
                },
                {
                    "resource_id": "technology_strategy",
                    "title": "Technology Strategy Patterns",
                    "type": "book",
                    "provider": "O'Reilly Media",
                    "difficulty": "advanced",
                    "estimated_hours": 35.0,
                    "skills_covered": ["Technical Strategy", "Innovation"],
                    "relevance_score": 0.90,
                    "personalization_reason": "Strategic thinking for senior technical roles"
                }
            ]
        }
        
        resources_data = resources_mapping.get(phase_name, [])
        resources = []
        
        for resource_data in resources_data:
            resource = LearningResource(**resource_data)
            resources.append(resource)
        
        return resources
    
    def _generate_projects_for_phase(self, phase_name: str) -> List[Dict[str, Any]]:
        """Generate practice projects for each phase"""
        projects_mapping = {
            "foundation": [
                {
                    "project_id": "personal_budget_tracker",
                    "title": "Personal Budget Tracker",
                    "description": "Build a command-line budget tracking application",
                    "skills_practiced": ["Python", "File I/O", "Data Structures"],
                    "difficulty": "beginner",
                    "estimated_hours": 20,
                    "deliverables": ["Working CLI application", "Unit tests", "Documentation"],
                    "success_criteria": ["App handles user input", "Data persists", "Code is clean"]
                },
                {
                    "project_id": "simple_web_scraper",
                    "title": "Simple Web Scraper",
                    "description": "Create a web scraper for job listings",
                    "skills_practiced": ["Python", "Web APIs", "Data Processing"],
                    "difficulty": "beginner",
                    "estimated_hours": 15,
                    "deliverables": ["Scraper script", "CSV output", "Error handling"],
                    "success_criteria": ["Extracts job data", "Handles errors gracefully", "Exports to CSV"]
                }
            ],
            "acceleration": [
                {
                    "project_id": "task_management_app",
                    "title": "Task Management Web App",
                    "description": "Build a full-stack task management application",
                    "skills_practiced": ["React", "JavaScript", "API Design", "Testing"],
                    "difficulty": "intermediate",
                    "estimated_hours": 60,
                    "deliverables": ["React frontend", "Backend API", "Test suite", "Deployment"],
                    "success_criteria": ["CRUD operations work", "Responsive design", "Comprehensive tests"]
                },
                {
                    "project_id": "performance_dashboard",
                    "title": "Performance Monitoring Dashboard",
                    "description": "Create a dashboard for monitoring app performance",
                    "skills_practiced": ["React", "Data Visualization", "Performance", "Real-time Updates"],
                    "difficulty": "intermediate",
                    "estimated_hours": 40,
                    "deliverables": ["Dashboard interface", "Real-time charts", "Performance metrics"],
                    "success_criteria": ["Real-time data display", "Interactive charts", "Performance insights"]
                }
            ],
            "leadership": [
                {
                    "project_id": "microservices_architecture",
                    "title": "Microservices Architecture Design",
                    "description": "Design and implement a microservices architecture",
                    "skills_practiced": ["System Design", "Architecture", "DevOps", "Leadership"],
                    "difficulty": "advanced",
                    "estimated_hours": 100,
                    "deliverables": ["Architecture documentation", "Service implementations", "Deployment pipeline"],
                    "success_criteria": ["Services communicate properly", "Scalable design", "Production ready"]
                },
                {
                    "project_id": "team_code_standards",
                    "title": "Team Code Standards Initiative",
                    "description": "Lead implementation of team-wide code standards",
                    "skills_practiced": ["Technical Leadership", "Process Design", "Team Collaboration"],
                    "difficulty": "advanced",
                    "estimated_hours": 50,
                    "deliverables": ["Code standards document", "Automated checks", "Team training"],
                    "success_criteria": ["Team adoption", "Improved code quality", "Automated enforcement"]
                }
            ],
            "senior": [
                {
                    "project_id": "technical_strategy_roadmap",
                    "title": "Technical Strategy Roadmap",
                    "description": "Develop comprehensive technical strategy for the organization",
                    "skills_practiced": ["Technical Strategy", "Innovation", "Stakeholder Management"],
                    "difficulty": "advanced",
                    "estimated_hours": 80,
                    "deliverables": ["Strategy document", "Roadmap presentation", "Implementation plan"],
                    "success_criteria": ["Stakeholder buy-in", "Clear roadmap", "Implementation begins"]
                },
                {
                    "project_id": "knowledge_sharing_platform",
                    "title": "Internal Knowledge Sharing Platform",
                    "description": "Build platform for sharing technical knowledge across teams",
                    "skills_practiced": ["Innovation", "Full-stack Development", "User Experience"],
                    "difficulty": "advanced",
                    "estimated_hours": 120,
                    "deliverables": ["Platform application", "Content management", "Usage analytics"],
                    "success_criteria": ["Active user adoption", "Growing content base", "Measurable impact"]
                }
            ]
        }
        
        return projects_mapping.get(phase_name, [
            {
                "project_id": f"{phase_name}_general_project",
                "title": f"General {phase_name.title()} Project",
                "description": f"Practice {phase_name}-level skills",
                "skills_practiced": ["General Programming"],
                "difficulty": "intermediate",
                "estimated_hours": 30,
                "deliverables": ["Working application"],
                "success_criteria": ["Meets requirements"]
            }
        ])
    
    def _generate_progress_criteria_for_phase(self, phase_name: str) -> List[str]:
        """Generate progress criteria for each phase"""
        criteria_mapping = {
            "foundation": [
                "Complete at least 80% of coding challenges successfully",
                "Pass peer code reviews with minimal revisions",
                "Demonstrate understanding of Python fundamentals",
                "Write basic unit tests for new features",
                "Contribute to team documentation regularly"
            ],
            "acceleration": [
                "Build and deploy a complete web application",
                "Achieve 80%+ test coverage on new features",
                "Lead junior developer pair programming sessions",
                "Contribute to architecture discussions meaningfully",
                "Optimize application performance measurably"
            ],
            "leadership": [
                "Successfully lead at least one technical initiative",
                "Mentor a junior developer to measurable improvement",
                "Make and document significant architecture decisions",
                "Present technical solutions to stakeholders",
                "Establish team best practices and standards"
            ],
            "senior": [
                "Drive adoption of new technologies or practices",
                "Influence technical direction across multiple teams",
                "Create and maintain technical strategy documentation",
                "Build consensus on complex technical decisions",
                "Establish knowledge sharing processes"
            ]
        }
        
        return criteria_mapping.get(phase_name, [
            f"Demonstrate proficiency in {phase_name} skills",
            f"Complete {phase_name} learning objectives",
            f"Show continued growth and improvement"
        ])
    
    # ... (Additional helper methods would continue here)
    
    def _calculate_skills_improved_for_month(self, month: int) -> int:
        """Calculate number of skills improved in a given month"""
        # Skills improvement follows phases and learning velocity
        phase = self._get_phase_for_month(month)
        
        # Base improvement based on phase
        phase_improvement = {
            "foundation": 2,      # 2 skills per month - building fundamentals
            "acceleration": 4,    # 4 skills per month - rapid learning phase
            "leadership": 3,      # 3 skills per month - focused specialization
            "senior": 2          # 2 skills per month - refinement and mastery
        }
        
        base_improvement = phase_improvement.get(phase, 2)
        
        # Add variance based on month progression within phase
        if phase == "foundation":
            # Gradual increase as developer gets comfortable
            if month == 0:
                return 1  # First month is slower
            elif month <= 2:
                return base_improvement
        elif phase == "acceleration":
            # Peak learning period with slight variance
            variance = [0, 1, 0, -1, 1, 0]  # months 3-8 variance
            month_in_phase = month - 3
            if 0 <= month_in_phase < len(variance):
                return base_improvement + variance[month_in_phase]
        elif phase == "leadership":
            # Steady improvement with focus shifts
            variance = [0, 1, 0, 1, -1, 0]  # months 9-14 variance
            month_in_phase = month - 9
            if 0 <= month_in_phase < len(variance):
                return base_improvement + variance[month_in_phase]
        elif phase == "senior":
            # Focus on fewer skills but deeper mastery
            return base_improvement
        
        return base_improvement
    
    def _calculate_milestone_rate_for_month(self, month: int) -> float:
        """Calculate milestone completion rate for a given month"""
        # Milestone months are typically 2, 4, 6, 8, 10, 12, 14, 16, 18
        milestone_months = {1, 3, 5, 7, 9, 11, 13, 15, 17}  # 0-indexed
        
        if month in milestone_months:
            # Month with milestone completion
            phase = self._get_phase_for_month(month)
            
            # Completion rate varies by phase
            phase_rates = {
                "foundation": 0.8,    # 80% - sometimes takes longer for first milestones
                "acceleration": 0.95, # 95% - high success rate during peak learning
                "leadership": 0.90,   # 90% - complex milestones but good capability
                "senior": 0.85       # 85% - challenging strategic milestones
            }
            
            base_rate = phase_rates.get(phase, 0.85)
            
            # Add slight variance based on specific month
            if month == 1:  # First milestone might be harder
                return 0.75
            elif month in [5, 7]:  # Mid-acceleration peak performance
                return 0.98
            
            return base_rate
        else:
            # Non-milestone month - measure ongoing progress rate
            phase = self._get_phase_for_month(month)
            
            # Progress rate for non-milestone months
            progress_rates = {
                "foundation": 0.65,   # Building up
                "acceleration": 0.80, # Strong progress
                "leadership": 0.75,   # Focused progress
                "senior": 0.70       # Strategic progress
            }
            
            return progress_rates.get(phase, 0.70)
    
    def _determine_velocity_trend_for_month(self, month: int) -> TrendDirection:
        """Determine velocity trend direction for a given month"""
        # Velocity trends follow the learning journey narrative
        
        if month <= 2:
            # Foundation phase - improving from low start
            return TrendDirection.IMPROVING
        elif month <= 8:
            # Acceleration phase - generally improving with some stability
            if month in [4, 6]:  # Some months show stability as skills consolidate
                return TrendDirection.STABLE
            else:
                return TrendDirection.IMPROVING
        elif month <= 14:
            # Leadership phase - stable improvement with occasional fluctuations
            if month in [10, 13]:  # Adjustment periods as focus shifts
                return TrendDirection.FLUCTUATING
            elif month in [11, 12]:  # Stable periods of consolidation
                return TrendDirection.STABLE
            else:
                return TrendDirection.IMPROVING
        else:
            # Senior phase - stable with focus on depth over breadth
            if month == 16:  # Initial senior role adjustment
                return TrendDirection.FLUCTUATING
            else:
                return TrendDirection.STABLE
    
    # ... (Additional helper methods would continue here)
    
    async def save_demo_data(self, scenario: DemoScenarioData, filepath: str = None):
        """Save demo data to file"""
        if not filepath:
            filepath = f"demo_data_{self.developer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump(scenario.dict(), f, indent=2, default=str)
            logger.info(f"✅ Demo data saved to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save demo data: {e}")
            raise


# Additional helper methods for the demo generator would continue here...
# This provides a comprehensive foundation for generating the Alex Chen demo data. 