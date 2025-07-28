"""
Learning Path Engine - Generates personalized learning plans

Creates data-driven learning paths by:
- Analyzing skill gaps and improvement opportunities
- Sequencing learning objectives optimally  
- Recommending resources aligned with learning style
- Setting realistic milestones and timelines
- Adapting plans based on progress and feedback
"""

import logging
import asyncio
import uuid
import math
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass

from .models import (
    DeveloperSkillProfile, SkillAssessment, LearningPlan, LearningMilestone,
    LearningResource, CareerStage, SkillCategory, TimeAvailability, LearningStyle
)

# LLM integration for dynamic skill intelligence
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    from langchain.prompts import ChatPromptTemplate
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

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
class LearningObjective:
    """Individual learning objective within a plan"""
    objective_id: str
    skill_name: str
    skill_category: SkillCategory
    target_level: float
    current_level: float
    priority: int  # 1 (highest) to 5 (lowest)
    dependencies: List[str]  # Other objective IDs this depends on
    estimated_weeks: int
    difficulty: str  # beginner, intermediate, advanced


@dataclass
class LearningPath:
    """Sequenced learning path with dependencies"""
    path_id: str
    objectives: List[LearningObjective]
    total_duration_weeks: int
    difficulty_progression: str  # gradual, moderate, intensive
    parallel_tracks: List[List[str]]  # Objectives that can be done in parallel


class LearningPathEngine:
    """
    Advanced learning path generation engine
    
    Creates personalized learning plans by:
    - Analyzing skill gaps and career goals
    - Optimizing learning sequence with dependency resolution
    - Balancing difficulty progression and time constraints
    - Personalizing based on learning style and availability
    - Generating milestone-driven tracking systems
    """
    
    def __init__(self, 
                 resource_database: Optional[Dict[str, List[Dict[str, Any]]]] = None,
                 openai_api_key: Optional[str] = None,
                 use_llm_intelligence: bool = True):
        """
        Initialize Learning Path Engine
        
        Args:
            resource_database: External resource database for recommendations
            openai_api_key: OpenAI API key for LLM-powered skill intelligence
            use_llm_intelligence: Whether to use LLM for dynamic skill data generation
        """
        self.use_llm_intelligence = use_llm_intelligence and LLM_AVAILABLE
        
        # Initialize LLM if available and requested
        self.llm = None
        if self.use_llm_intelligence and openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    openai_api_key=openai_api_key,
                    model_name="gpt-4-turbo-preview",
                    temperature=0.3  # Lower temperature for more consistent skill data
                )
                logger.info("🤖 LLM-powered skill intelligence enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")
                self.use_llm_intelligence = False
        
        # Dynamic skill data (will be populated by LLM or fallback to static)
        self.skill_dependencies: Dict[str, List[str]] = {}
        self.time_estimates: Dict[str, int] = {}
        self.difficulty_rules: Dict[str, Any] = {}
        self.resource_db: Dict[str, List[Dict[str, Any]]] = resource_database or {}
        self.style_adaptations: Dict[LearningStyle, Dict[str, Any]] = {}
        
        # Caches for LLM-generated data
        self._llm_cache: Dict[str, Any] = {}
        
        self.is_initialized = False
        logger.info("📚 Learning Path Engine initialized with LLM intelligence" if self.use_llm_intelligence else "📚 Learning Path Engine initialized with static data")
    
    async def initialize(self):
        """Initialize the Learning Path Engine"""
        try:
            logger.info("🔄 Initializing Learning Path Engine...")
            
            # Initialize skill intelligence data
            if self.use_llm_intelligence and self.llm:
                logger.info("🤖 Generating skill intelligence using LLM...")
                await self._initialize_llm_skill_data()
            else:
                logger.info("📊 Using static skill data as fallback...")
                self._initialize_static_skill_data()
            
            self.is_initialized = True
            logger.info("✅ Learning Path Engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Learning Path Engine: {e}")
            # Fallback to static data if LLM initialization fails
            if self.use_llm_intelligence:
                logger.warning("🔄 Falling back to static skill data...")
                self._initialize_static_skill_data()
                self.is_initialized = True
            else:
                raise
    
    async def cleanup(self):
        """Cleanup Learning Path Engine resources"""
        logger.info("🧹 Cleaning up Learning Path Engine...")
        self.is_initialized = False
        logger.info("✅ Learning Path Engine cleanup complete")
    
    @timed(operation_name="learning_plan_generation")
    async def generate_learning_plan(self,
                                   developer_id: str,
                                   current_skills: Dict[str, SkillAssessment],
                                   target_skills: Dict[str, float],
                                   career_stage: CareerStage,
                                   time_availability: TimeAvailability,
                                   learning_style: LearningStyle,
                                   learning_goals: List[str],
                                   timeline_weeks: Optional[int] = None) -> LearningPlan:
        """
        Generate a comprehensive personalized learning plan
        
        Args:
            developer_id: Developer identifier
            current_skills: Current skill assessments
            target_skills: Target skill levels (skill_name -> target_level)
            career_stage: Current career stage
            time_availability: Available time for learning
            learning_style: Preferred learning approach
            learning_goals: Specific learning goals
            timeline_weeks: Optional target timeline in weeks
            
        Returns:
            LearningPlan: Comprehensive learning plan
        """
        if not self.is_initialized:
            raise RuntimeError("Learning Path Engine not initialized")
        
        logger.info(f"📋 Generating learning plan for {developer_id}")
        
        try:
            # Step 1: Analyze skill gaps
            skill_gaps = self._analyze_skill_gaps(current_skills, target_skills)
            
            # Step 2: Create learning objectives
            objectives = self._create_learning_objectives(skill_gaps, career_stage)
            
            # Step 3: Resolve dependencies and create optimal sequence
            learning_path = self._optimize_learning_sequence(objectives, timeline_weeks)
            
            # Step 4: Generate milestones
            milestones = self._generate_milestones(learning_path, time_availability)
            
            # Step 5: Recommend resources
            resources = await self._recommend_resources(
                objectives, learning_style, career_stage
            )
            
            # Step 6: Create practice projects
            practice_projects = self._generate_practice_projects(objectives, career_stage)
            
            # Step 7: Calculate timeline and progression
            timeline_analysis = self._calculate_timeline(learning_path, time_availability)
            
            # Step 8: Personalize based on learning style
            personalized_plan = await self._personalize_plan(
                learning_path, learning_style, time_availability
            )
            
            # Create final learning plan
            plan = LearningPlan(
                plan_id=f"plan_{developer_id}_{int(datetime.now().timestamp())}",
                developer_id=developer_id,
                generated_at=datetime.now(),
                priority_skills=self._extract_priority_skills(objectives),
                learning_objectives=learning_goals,
                target_career_stage=self._determine_target_career_stage(career_stage, target_skills),
                learning_path=personalized_plan["learning_steps"],
                milestones=milestones,
                recommended_resources=resources,
                practice_projects=practice_projects,
                estimated_duration=timeline_analysis["total_duration"],
                next_review_date=datetime.now() + timedelta(weeks=4),  # Monthly reviews
                progress_criteria=self._generate_progress_criteria(objectives),
                personalization_factors={
                    "learning_style": learning_style.value,
                    "time_availability": time_availability.value,
                    "career_stage": career_stage.value,
                    "skill_gap_count": len(skill_gaps),
                    "timeline_constraint": timeline_weeks
                },
                status="active",
                progress_percentage=0.0
            )
            
            logger.info(f"✅ Learning plan generated for {developer_id}: {len(objectives)} objectives, {timeline_analysis['total_duration']}")
            return plan
            
        except Exception as e:
            logger.error(f"❌ Failed to generate learning plan: {e}")
            raise
    
    def _analyze_skill_gaps(self, 
                          current_skills: Dict[str, SkillAssessment],
                          target_skills: Dict[str, float]) -> List[Dict[str, Any]]:
        """Analyze gaps between current and target skill levels"""
        gaps = []
        
        for skill_name, target_level in target_skills.items():
            current_assessment = current_skills.get(skill_name)
            current_level = current_assessment.level if current_assessment else 0.0
            
            if target_level > current_level:
                gap_size = target_level - current_level
                
                gap = {
                    "skill_name": skill_name,
                    "current_level": current_level,
                    "target_level": target_level,
                    "gap_size": gap_size,
                    "skill_category": current_assessment.category if current_assessment else SkillCategory.TECHNICAL,
                    "priority": self._calculate_gap_priority(skill_name, gap_size, current_assessment),
                    "confidence": current_assessment.confidence if current_assessment else 0.5
                }
                gaps.append(gap)
        
        # Sort by priority (higher priority first)
        gaps.sort(key=lambda x: x["priority"], reverse=True)
        
        logger.info(f"📊 Identified {len(gaps)} skill gaps")
        return gaps
    
    def _calculate_gap_priority(self, 
                              skill_name: str, 
                              gap_size: float, 
                              current_assessment: Optional[SkillAssessment]) -> int:
        """Calculate priority for addressing a skill gap"""
        
        # Base priority on gap size
        priority = int(gap_size * 10)
        
        # Adjust based on skill importance
        important_skills = {
            "python": 3, "javascript": 3, "java": 3,
            "testing": 4, "security": 5, "architecture": 4,
            "react": 2, "django": 2, "api_design": 4
        }
        
        skill_bonus = important_skills.get(skill_name.lower(), 0)
        priority += skill_bonus
        
        # Adjust based on current confidence
        if current_assessment and current_assessment.confidence < 0.6:
            priority += 2  # Higher priority for uncertain skills
        
        return min(10, max(1, priority))  # Clamp between 1-10
    
    def _create_learning_objectives(self, 
                                  skill_gaps: List[Dict[str, Any]], 
                                  career_stage: CareerStage) -> List[LearningObjective]:
        """Create specific learning objectives from skill gaps"""
        objectives = []
        
        for gap in skill_gaps:
            # Determine dependencies
            dependencies = self._get_skill_dependencies(gap["skill_name"])
            
            # Estimate learning time
            estimated_weeks = self._estimate_learning_time(
                gap["skill_name"], 
                gap["current_level"], 
                gap["target_level"],
                career_stage
            )
            
            # Determine difficulty level
            difficulty = self._determine_difficulty_level(gap["target_level"], career_stage)
            
            objective = LearningObjective(
                objective_id=f"obj_{gap['skill_name']}_{int(datetime.now().timestamp())}",
                skill_name=gap["skill_name"],
                skill_category=gap["skill_category"],
                target_level=gap["target_level"],
                current_level=gap["current_level"],
                priority=gap["priority"],
                dependencies=dependencies,
                estimated_weeks=estimated_weeks,
                difficulty=difficulty
            )
            
            objectives.append(objective)
        
        logger.info(f"🎯 Created {len(objectives)} learning objectives")
        return objectives
    
    def _get_skill_dependencies(self, skill_name: str) -> List[str]:
        """Get prerequisite skills for a given skill"""
        return self.skill_dependencies.get(skill_name.lower(), [])
    
    def _estimate_learning_time(self, 
                              skill_name: str, 
                              current_level: float, 
                              target_level: float,
                              career_stage: CareerStage) -> int:
        """Estimate learning time in weeks"""
        
        # Base time estimates (weeks to go from 0 to 1.0)
        base_times = self.time_estimates.get(skill_name.lower(), 12)
        
        # Calculate actual time needed
        level_gap = target_level - current_level
        base_weeks = int(base_times * level_gap)
        
        # Adjust for career stage (more experience = faster learning)
        stage_multipliers = {
            CareerStage.JUNIOR: 1.3,
            CareerStage.MID: 1.0,
            CareerStage.SENIOR: 0.8,
            CareerStage.LEAD: 0.7,
            CareerStage.PRINCIPAL: 0.6,
            CareerStage.ARCHITECT: 0.6
        }
        
        multiplier = stage_multipliers.get(career_stage, 1.0)
        adjusted_weeks = max(1, int(base_weeks * multiplier))
        
        return adjusted_weeks
    
    def _determine_difficulty_level(self, target_level: float, career_stage: CareerStage) -> str:
        """Determine difficulty level for learning objective"""
        
        # Career stage baseline difficulty tolerance
        stage_tolerance = {
            CareerStage.JUNIOR: 0.5,
            CareerStage.MID: 0.7,
            CareerStage.SENIOR: 0.8,
            CareerStage.LEAD: 0.9,
            CareerStage.PRINCIPAL: 0.9,
            CareerStage.ARCHITECT: 1.0
        }
        
        tolerance = stage_tolerance.get(career_stage, 0.7)
        
        if target_level <= tolerance * 0.6:
            return "beginner"
        elif target_level <= tolerance * 0.8:
            return "intermediate"
        else:
            return "advanced"
    
    def _optimize_learning_sequence(self, 
                                  objectives: List[LearningObjective], 
                                  timeline_weeks: Optional[int] = None) -> LearningPath:
        """Optimize the sequence of learning objectives using dependency resolution"""
        
        # Create dependency graph
        obj_map = {obj.objective_id: obj for obj in objectives}
        
        # Topological sort to resolve dependencies
        sorted_objectives = self._topological_sort(objectives)
        
        # Identify parallel learning opportunities
        parallel_tracks = self._identify_parallel_tracks(sorted_objectives)
        
        # Calculate total duration
        total_duration = self._calculate_path_duration(sorted_objectives, parallel_tracks)
        
        # Adjust for timeline constraints
        if timeline_weeks and total_duration > timeline_weeks:
            sorted_objectives = self._compress_timeline(sorted_objectives, timeline_weeks)
            total_duration = timeline_weeks
        
        # Determine difficulty progression
        difficulty_progression = self._analyze_difficulty_progression(sorted_objectives)
        
        path = LearningPath(
            path_id=f"path_{int(datetime.now().timestamp())}",
            objectives=sorted_objectives,
            total_duration_weeks=total_duration,
            difficulty_progression=difficulty_progression,
            parallel_tracks=parallel_tracks
        )
        
        logger.info(f"🛤️ Optimized learning sequence: {total_duration} weeks, {len(parallel_tracks)} parallel tracks")
        return path
    
    def _topological_sort(self, objectives: List[LearningObjective]) -> List[LearningObjective]:
        """Sort objectives respecting dependencies using topological sort"""
        
        # Create adjacency list and in-degree count
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        obj_map = {obj.skill_name: obj for obj in objectives}
        
        # Initialize in-degree
        for obj in objectives:
            in_degree[obj.skill_name] = 0
        
        # Build graph
        for obj in objectives:
            for dep_skill in obj.dependencies:
                if dep_skill in obj_map:
                    graph[dep_skill].append(obj.skill_name)
                    in_degree[obj.skill_name] += 1
        
        # Kahn's algorithm
        queue = [skill for skill in obj_map.keys() if in_degree[skill] == 0]
        result = []
        
        while queue:
            # Sort by priority to handle same-level dependencies
            queue.sort(key=lambda skill: obj_map[skill].priority, reverse=True)
            current = queue.pop(0)
            result.append(obj_map[current])
            
            # Update dependencies
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Add any remaining objectives (no dependencies)
        remaining = [obj for obj in objectives if obj not in result]
        result.extend(sorted(remaining, key=lambda x: x.priority, reverse=True))
        
        return result
    
    def _identify_parallel_tracks(self, objectives: List[LearningObjective]) -> List[List[str]]:
        """Identify objectives that can be learned in parallel"""
        parallel_tracks = []
        
        # Group by skill category - skills in different categories can often be learned in parallel
        category_groups = defaultdict(list)
        for obj in objectives:
            category_groups[obj.skill_category].append(obj.objective_id)
        
        # Create parallel tracks for independent categories
        independent_categories = [
            [SkillCategory.LANGUAGE, SkillCategory.FRAMEWORK],
            [SkillCategory.TESTING, SkillCategory.SECURITY],
            [SkillCategory.DEVOPS, SkillCategory.TOOL]
        ]
        
        for category_group in independent_categories:
            track = []
            for category in category_group:
                track.extend(category_groups.get(category, []))
            
            if len(track) > 1:
                parallel_tracks.append(track)
        
        return parallel_tracks
    
    def _calculate_path_duration(self, 
                                objectives: List[LearningObjective], 
                                parallel_tracks: List[List[str]]) -> int:
        """Calculate total duration considering parallel learning"""
        
        if not objectives:
            return 0
        
        # Simple calculation: sum of all weeks (could be optimized for true parallelism)
        total_weeks = sum(obj.estimated_weeks for obj in objectives)
        
        # Apply parallelism discount
        if parallel_tracks:
            # Assume 20% time savings from parallel learning
            parallel_savings = int(total_weeks * 0.2)
            total_weeks = max(total_weeks - parallel_savings, total_weeks // 2)
        
        return total_weeks
    
    def _compress_timeline(self, 
                         objectives: List[LearningObjective], 
                         target_weeks: int) -> List[LearningObjective]:
        """Compress learning timeline to fit target duration"""
        
        current_total = sum(obj.estimated_weeks for obj in objectives)
        compression_ratio = target_weeks / current_total
        
        # Compress each objective proportionally
        for obj in objectives:
            obj.estimated_weeks = max(1, int(obj.estimated_weeks * compression_ratio))
        
        # If still over, prioritize by removing lowest priority objectives
        while sum(obj.estimated_weeks for obj in objectives) > target_weeks:
            lowest_priority_obj = min(objectives, key=lambda x: x.priority)
            objectives.remove(lowest_priority_obj)
        
        return objectives
    
    def _analyze_difficulty_progression(self, objectives: List[LearningObjective]) -> str:
        """Analyze the difficulty progression of the learning path"""
        
        if len(objectives) < 2:
            return "single"
        
        difficulties = [obj.difficulty for obj in objectives]
        difficulty_levels = {"beginner": 1, "intermediate": 2, "advanced": 3}
        
        progression = [difficulty_levels.get(d, 2) for d in difficulties]
        
        # Calculate progression rate
        increase_count = sum(1 for i in range(1, len(progression)) 
                           if progression[i] > progression[i-1])
        
        progression_rate = increase_count / (len(progression) - 1) if len(progression) > 1 else 0
        
        if progression_rate >= 0.7:
            return "intensive"
        elif progression_rate >= 0.4:
            return "moderate"
        else:
            return "gradual"
    
    def _generate_milestones(self, 
                           learning_path: LearningPath, 
                           time_availability: TimeAvailability) -> List[LearningMilestone]:
        """Generate learning milestones for tracking progress"""
        milestones = []
        
        # Group objectives into milestone chunks
        milestone_size = 2 if time_availability == TimeAvailability.HIGH else 1
        
        for i in range(0, len(learning_path.objectives), milestone_size):
            chunk = learning_path.objectives[i:i + milestone_size]
            
            # Calculate milestone timing
            weeks_so_far = sum(obj.estimated_weeks for obj in learning_path.objectives[:i])
            milestone_duration = sum(obj.estimated_weeks for obj in chunk)
            
            milestone = LearningMilestone(
                milestone_id=f"milestone_{i//milestone_size + 1}",
                title=f"Milestone {i//milestone_size + 1}: {', '.join(obj.skill_name for obj in chunk)}",
                description=f"Complete learning objectives for {', '.join(obj.skill_name for obj in chunk)}",
                skills_involved=[obj.skill_name for obj in chunk],
                success_criteria=[
                    f"Achieve {obj.target_level:.1f} level in {obj.skill_name}" 
                    for obj in chunk
                ],
                estimated_duration=f"{milestone_duration} weeks",
                deadline=datetime.now() + timedelta(weeks=weeks_so_far + milestone_duration)
            )
            
            milestones.append(milestone)
        
        logger.info(f"🏁 Generated {len(milestones)} learning milestones")
        return milestones
    
    async def _recommend_resources(self, 
                                 objectives: List[LearningObjective],
                                 learning_style: LearningStyle,
                                 career_stage: CareerStage) -> List[LearningResource]:
        """Recommend learning resources based on objectives and preferences"""
        resources = []
        
        for obj in objectives:
            skill_resources = self.resource_db.get(obj.skill_name.lower(), [])
            
            # Filter by difficulty and career stage
            suitable_resources = [
                r for r in skill_resources 
                if self._is_resource_suitable(r, obj, learning_style, career_stage)
            ]
            
            # Take top 2 resources per objective
            for resource_data in suitable_resources[:2]:
                resource = LearningResource(
                    resource_id=str(uuid.uuid4()),
                    title=resource_data["title"],
                    type=resource_data["type"],
                    url=resource_data.get("url"),
                    provider=resource_data.get("provider"),
                    difficulty=resource_data["difficulty"],
                    estimated_hours=resource_data.get("estimated_hours", 10),
                    skills_covered=[obj.skill_name],
                    relevance_score=self._calculate_resource_relevance(resource_data, obj, learning_style),
                    personalization_reason=f"Matches your {learning_style.value} learning style and {obj.difficulty} level"
                )
                resources.append(resource)
        
        # Sort by relevance and remove duplicates
        resources.sort(key=lambda x: x.relevance_score, reverse=True)
        seen_titles = set()
        unique_resources = []
        
        for resource in resources:
            if resource.title not in seen_titles:
                unique_resources.append(resource)
                seen_titles.add(resource.title)
        
        logger.info(f"📚 Recommended {len(unique_resources)} learning resources")
        return unique_resources[:15]  # Top 15 resources
    
    def _is_resource_suitable(self, 
                            resource_data: Dict[str, Any], 
                            objective: LearningObjective,
                            learning_style: LearningStyle,
                            career_stage: CareerStage) -> bool:
        """Check if a resource is suitable for the objective and learner"""
        
        # Check difficulty match
        resource_difficulty = resource_data.get("difficulty", "intermediate")
        if resource_difficulty != objective.difficulty:
            return False
        
        # Check learning style preference
        style_preferences = self.style_adaptations.get(learning_style, {})
        preferred_types = style_preferences.get("preferred_resource_types", [])
        
        if preferred_types and resource_data.get("type") not in preferred_types:
            return False
        
        return True
    
    def _calculate_resource_relevance(self, 
                                    resource_data: Dict[str, Any], 
                                    objective: LearningObjective,
                                    learning_style: LearningStyle) -> float:
        """Calculate relevance score for a resource"""
        score = 0.8  # Base score
        
        # Boost for learning style match
        style_preferences = self.style_adaptations.get(learning_style, {})
        preferred_types = style_preferences.get("preferred_resource_types", [])
        
        if resource_data.get("type") in preferred_types:
            score += 0.2
        
        # Boost for difficulty match
        if resource_data.get("difficulty") == objective.difficulty:
            score += 0.1
        
        # Penalize for very long resources
        estimated_hours = resource_data.get("estimated_hours", 10)
        if estimated_hours > 50:
            score -= 0.1
        
        return min(1.0, score)
    
    def _generate_practice_projects(self, 
                                  objectives: List[LearningObjective],
                                  career_stage: CareerStage) -> List[Dict[str, Any]]:
        """Generate hands-on practice projects"""
        projects = []
        
        # Group objectives by category for project ideas
        category_groups = defaultdict(list)
        for obj in objectives:
            category_groups[obj.skill_category].append(obj.skill_name)
        
        # Generate projects based on skill combinations
        project_templates = self._get_project_templates(career_stage)
        
        for category, skills in category_groups.items():
            if len(skills) >= 2:  # Need multiple skills for a meaningful project
                template = project_templates.get(category)
                if template:
                    project = {
                        "project_id": str(uuid.uuid4()),
                        "title": template["title"].format(skills=", ".join(skills[:2])),
                        "description": template["description"],
                        "skills_practiced": skills,
                        "difficulty": self._determine_project_difficulty(skills, objectives),
                        "estimated_hours": template["estimated_hours"],
                        "deliverables": template["deliverables"],
                        "success_criteria": template["success_criteria"]
                    }
                    projects.append(project)
        
        logger.info(f"🛠️ Generated {len(projects)} practice projects")
        return projects
    
    def _get_project_templates(self, career_stage: CareerStage) -> Dict[SkillCategory, Dict[str, Any]]:
        """Get project templates based on career stage"""
        
        base_templates = {
            SkillCategory.LANGUAGE: {
                "title": "Multi-Language Code Converter using {skills}",
                "description": "Build a tool that converts code between different programming languages",
                "estimated_hours": 20,
                "deliverables": ["Working converter", "Test suite", "Documentation"],
                "success_criteria": ["Converts at least 80% of common patterns", "Has comprehensive tests"]
            },
            SkillCategory.FRAMEWORK: {
                "title": "Full-Stack Application with {skills}",
                "description": "Create a complete web application using modern frameworks",
                "estimated_hours": 40,
                "deliverables": ["Deployed application", "API documentation", "User guide"],
                "success_criteria": ["Functional CRUD operations", "Responsive design", "API integration"]
            },
            SkillCategory.TESTING: {
                "title": "Comprehensive Testing Suite for {skills}",
                "description": "Build a complete testing infrastructure with multiple testing approaches",
                "estimated_hours": 15,
                "deliverables": ["Test automation framework", "Performance tests", "Coverage report"],
                "success_criteria": ["90%+ code coverage", "Integration with CI/CD"]
            }
        }
        
        # Adjust complexity based on career stage
        stage_multipliers = {
            CareerStage.JUNIOR: 0.7,
            CareerStage.MID: 1.0,
            CareerStage.SENIOR: 1.3,
            CareerStage.LEAD: 1.5,
            CareerStage.PRINCIPAL: 1.7,
            CareerStage.ARCHITECT: 2.0
        }
        
        multiplier = stage_multipliers.get(career_stage, 1.0)
        
        # Scale project complexity
        for template in base_templates.values():
            template["estimated_hours"] = int(template["estimated_hours"] * multiplier)
        
        return base_templates
    
    def _determine_project_difficulty(self, 
                                    skills: List[str], 
                                    objectives: List[LearningObjective]) -> str:
        """Determine project difficulty based on involved skills"""
        
        # Get average target level of involved skills
        relevant_objectives = [obj for obj in objectives if obj.skill_name in skills]
        
        if not relevant_objectives:
            return "intermediate"
        
        avg_target_level = sum(obj.target_level for obj in relevant_objectives) / len(relevant_objectives)
        
        if avg_target_level <= 0.4:
            return "beginner"
        elif avg_target_level <= 0.7:
            return "intermediate"
        else:
            return "advanced"
    
    def _calculate_timeline(self, 
                          learning_path: LearningPath, 
                          time_availability: TimeAvailability) -> Dict[str, Any]:
        """Calculate detailed timeline analysis"""
        
        # Time availability to hours per week mapping
        hours_per_week = {
            TimeAvailability.LOW: 3,      # < 2 hours/week
            TimeAvailability.MEDIUM: 6,   # 2-5 hours/week
            TimeAvailability.HIGH: 12     # > 5 hours/week
        }
        
        weekly_hours = hours_per_week.get(time_availability, 6)
        
        return {
            "total_duration": f"{learning_path.total_duration_weeks} weeks",
            "weekly_time_commitment": f"{weekly_hours} hours/week",
            "total_time_investment": f"{learning_path.total_duration_weeks * weekly_hours} hours",
            "difficulty_progression": learning_path.difficulty_progression,
            "parallel_opportunities": len(learning_path.parallel_tracks),
            "milestone_frequency": "Every 2-3 weeks"
        }
    
    async def _personalize_plan(self, 
                       learning_path: LearningPath, 
                       learning_style: LearningStyle,
                       time_availability: TimeAvailability) -> Dict[str, Any]:
        """Personalize the learning plan based on individual preferences"""
        
        style_adaptations = self.style_adaptations.get(learning_style, {})
        
        learning_steps = []
        
        for i, objective in enumerate(learning_path.objectives):
            step = {
                "step_number": i + 1,
                "objective_id": objective.objective_id,
                "skill_name": objective.skill_name,
                "target_level": objective.target_level,
                "estimated_weeks": objective.estimated_weeks,
                "difficulty": objective.difficulty,
                "learning_approach": style_adaptations.get("approach", "balanced"),
                "recommended_study_pattern": style_adaptations.get("study_pattern", "regular"),
                "focus_areas": await self._get_skill_focus_areas(objective.skill_name),
                "prerequisite_check": objective.dependencies,
                "success_indicators": [
                    f"Can demonstrate {objective.skill_name} at {objective.target_level:.1f} level",
                    f"Completes hands-on exercises with {objective.difficulty} difficulty"
                ]
            }
            
            learning_steps.append(step)
        
        return {
            "learning_steps": learning_steps,
            "personalization_notes": style_adaptations.get("notes", ""),
            "recommended_schedule": style_adaptations.get("schedule_pattern", "flexible")
        }
    
    def _extract_priority_skills(self, objectives: List[LearningObjective]) -> List[Dict[str, Any]]:
        """Extract priority skills from objectives"""
        return [
            {
                "skill_name": obj.skill_name,
                "priority": obj.priority,
                "target_level": obj.target_level,
                "estimated_weeks": obj.estimated_weeks,
                "difficulty": obj.difficulty
            }
            for obj in sorted(objectives, key=lambda x: x.priority, reverse=True)[:5]
        ]
    
    def _determine_target_career_stage(self, 
                                     current_stage: CareerStage, 
                                     target_skills: Dict[str, float]) -> Optional[CareerStage]:
        """Determine target career stage based on skill targets"""
        
        # Calculate average target skill level
        avg_target = sum(target_skills.values()) / len(target_skills) if target_skills else 0.5
        
        # Map skill levels to career stages
        if avg_target >= 0.9:
            return CareerStage.ARCHITECT if current_stage != CareerStage.ARCHITECT else None
        elif avg_target >= 0.8:
            return CareerStage.PRINCIPAL
        elif avg_target >= 0.7:
            return CareerStage.LEAD
        elif avg_target >= 0.6:
            return CareerStage.SENIOR
        elif avg_target >= 0.4:
            return CareerStage.MID
        else:
            return None  # Stay at current stage
    
    def _generate_progress_criteria(self, objectives: List[LearningObjective]) -> List[str]:
        """Generate criteria for measuring learning progress"""
        criteria = [
            "Complete all assigned learning resources",
            "Demonstrate practical application of new skills",
            "Pass skill assessments with target confidence levels",
            "Complete hands-on practice projects",
            "Participate in code reviews showcasing new skills"
        ]
        
        # Add objective-specific criteria
        for obj in objectives[:3]:  # Top 3 objectives
            criteria.append(f"Achieve {obj.target_level:.1f} proficiency in {obj.skill_name}")
        
        return criteria
    
    async def _get_skill_focus_areas(self, skill_name: str) -> List[str]:
        """Get focus areas for a specific skill using LLM or static fallback"""
        
        if self.use_llm_intelligence and self.llm:
            return await self._get_skill_focus_areas_llm(skill_name)
        else:
            return self._get_skill_focus_areas_static(skill_name)
    
    @cached(ttl=86400)  # Cache for 24 hours
    async def _get_skill_focus_areas_llm(self, skill_name: str) -> List[str]:
        """Generate skill focus areas using LLM with SFIA framework principles"""
        
        # Check cache first
        cache_key = f"focus_areas_{skill_name.lower()}"
        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]
        
        prompt = ChatPromptTemplate.from_template("""
        You are an expert software engineering educator with deep knowledge of the SFIA framework and industry best practices.
        
        Generate 4-6 key focus areas for learning the skill: {skill_name}
        
        Focus areas should be:
        - Specific and actionable learning objectives
        - Progressive from foundational to advanced concepts
        - Aligned with industry needs and current practices
        - Based on SFIA competency levels where applicable
        
        For technical skills, consider:
        - Core syntax/concepts
        - Best practices and patterns
        - Integration with other technologies
        - Advanced/professional usage
        - Testing and debugging
        - Performance and optimization
        
        Return ONLY a JSON array of focus areas as strings:
        ["Focus Area 1", "Focus Area 2", "Focus Area 3", ...]
        
        Example for "python":
        ["Syntax and data structures", "Object-oriented programming", "Popular libraries and frameworks", "Testing and debugging", "Performance optimization", "Integration and deployment"]
        """)
        
        try:
            messages = prompt.format_messages(skill_name=skill_name)
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            focus_areas = json.loads(response.content.strip())
            
            # Validate it's a list of strings
            if isinstance(focus_areas, list) and all(isinstance(area, str) for area in focus_areas):
                # Cache the result
                self._llm_cache[cache_key] = focus_areas
                logger.info(f"🎯 Generated {len(focus_areas)} focus areas for {skill_name} via LLM")
                return focus_areas
            else:
                raise ValueError("Invalid focus areas format")
                
        except Exception as e:
            logger.error(f"Failed to generate focus areas for {skill_name} via LLM: {e}")
            # Fall back to static method
            return self._get_skill_focus_areas_static(skill_name)
    
    def _get_skill_focus_areas_static(self, skill_name: str) -> List[str]:
        """Static fallback for skill focus areas"""
        
        focus_areas = {
            "python": ["Syntax and semantics", "Object-oriented programming", "Libraries and frameworks", "Testing"],
            "javascript": ["ES6+ features", "Async programming", "DOM manipulation", "Framework integration"],
            "testing": ["Unit testing", "Integration testing", "Test automation", "Coverage analysis"],
            "security": ["Input validation", "Authentication", "Authorization", "Secure coding practices"],
            "architecture": ["Design patterns", "System design", "Scalability", "Performance optimization"],
            "devops": ["CI/CD pipelines", "Infrastructure as code", "Monitoring", "Deployment strategies"]
        }
        
        return focus_areas.get(skill_name.lower(), ["Core concepts", "Best practices", "Practical application"])
    
    # ===== LLM-Powered Skill Intelligence Methods =====
    
    async def _initialize_llm_skill_data(self):
        """Initialize all skill data using LLM intelligence"""
        try:
            # Generate skill dependencies using SFIA framework
            self.skill_dependencies = await self._generate_skill_dependencies_llm()
            
            # Generate time estimates using industry standards
            self.time_estimates = await self._generate_time_estimates_llm()
            
            # Generate learning resources using current market data
            if not self.resource_db:
                self.resource_db = await self._generate_learning_resources_llm()
            
            # Generate learning style adaptations
            self.style_adaptations = await self._generate_style_adaptations_llm()
            
            # Generate difficulty rules
            self.difficulty_rules = await self._generate_difficulty_rules_llm()
            
            logger.info("✅ LLM skill intelligence data generated successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate LLM skill data: {e}")
            raise
    
    @cached(ttl=86400)  # Cache for 24 hours
    async def _generate_skill_dependencies_llm(self) -> Dict[str, List[str]]:
        """Generate skill dependency graph using LLM with SFIA framework inspiration"""
        
        prompt = ChatPromptTemplate.from_template("""
        You are an expert software engineering career coach with deep knowledge of the SFIA (Skills Framework for the Information Age) framework.
        
        Generate a comprehensive skill dependency graph for software development skills. Each skill should list its prerequisite skills.
        
        Use the SFIA framework principles:
        - Foundation skills (Level 1-2): Basic programming, tools
        - Building skills (Level 3-4): Frameworks, methodologies  
        - Advanced skills (Level 5-6): Architecture, leadership
        - Expert skills (Level 7): Strategic, organizational
        
        Consider modern software development including:
        - Programming languages: Python, JavaScript, TypeScript, Java, Go, Rust, C++
        - Frontend: React, Vue, Angular, HTML, CSS
        - Backend: Django, Flask, Express, Spring, FastAPI
        - DevOps: Docker, Kubernetes, CI/CD, AWS, Azure, GCP
        - Databases: SQL, NoSQL, PostgreSQL, MongoDB
        - Testing: Unit testing, Integration testing, E2E testing
        - Security: Authentication, Authorization, Secure coding
        - Architecture: Microservices, System design, Design patterns
        - Data: Machine learning, Data science, Analytics
        
        Return ONLY a valid JSON object with skill names as keys and arrays of prerequisite skills as values.
        Use lowercase, underscore-separated skill names (e.g., "machine_learning", "api_design").
        
        Example format:
        {{
            "react": ["javascript", "html", "css"],
            "django": ["python", "web_development"],
            "kubernetes": ["docker", "devops_fundamentals", "linux"]
        }}
        """)
        
        try:
            messages = prompt.format_messages()
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            dependencies = json.loads(response.content.strip())
            
            logger.info(f"🔗 Generated {len(dependencies)} skill dependencies via LLM")
            return dependencies
            
        except Exception as e:
            logger.error(f"Failed to generate skill dependencies via LLM: {e}")
            # Return basic fallback
            return {
                "react": ["javascript", "html", "css"],
                "django": ["python"],
                "kubernetes": ["docker", "linux"]
            }
    
    @cached(ttl=86400)  # Cache for 24 hours
    async def _generate_time_estimates_llm(self) -> Dict[str, int]:
        """Generate learning time estimates using LLM with industry standards"""
        
        prompt = ChatPromptTemplate.from_template("""
        You are an expert software engineering educator with 15+ years of experience training developers.
        
        Generate realistic learning time estimates (in weeks) for a motivated developer to achieve professional competency in various software development skills.
        
        Consider:
        - These are estimates for reaching PROFESSIONAL COMPETENCY (able to use in work projects)
        - Assume 10-15 hours of focused learning per week
        - Factor in current industry complexity and learning curves
        - Base estimates on ZERO prior experience in that skill
        - Consider 2024 technology landscape and modern tooling
        
        Skills to estimate:
        - Programming languages: python, javascript, typescript, java, go, rust, cpp, csharp
        - Frontend: react, vue, angular, html, css, sass
        - Backend: django, flask, express, spring, fastapi, nodejs
        - DevOps: docker, kubernetes, aws, azure, gcp, terraform, ansible
        - Databases: sql, postgresql, mongodb, redis, elasticsearch  
        - Testing: unit_testing, integration_testing, e2e_testing, tdd
        - Security: authentication, authorization, secure_coding, penetration_testing
        - Architecture: microservices, system_design, design_patterns, distributed_systems
        - Data: machine_learning, data_science, analytics, big_data
        - Mobile: ios_development, android_development, react_native, flutter
        - Other: api_design, performance_optimization, monitoring, ci_cd
        
        Return ONLY a valid JSON object with skill names as keys and weeks as integer values.
        
        Example format:
        {{
            "python": 12,
            "javascript": 8,
            "react": 6,
            "docker": 4,
            "kubernetes": 10,
            "machine_learning": 16
        }}
        """)
        
        try:
            messages = prompt.format_messages()
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            time_estimates = json.loads(response.content.strip())
            
            # Convert values to integers and validate
            validated_estimates = {}
            for skill, weeks in time_estimates.items():
                try:
                    validated_estimates[skill] = max(1, int(weeks))  # Minimum 1 week
                except (ValueError, TypeError):
                    validated_estimates[skill] = 8  # Default fallback
            
            logger.info(f"⏱️ Generated time estimates for {len(validated_estimates)} skills via LLM")
            return validated_estimates
            
        except Exception as e:
            logger.error(f"Failed to generate time estimates via LLM: {e}")
            # Return basic fallback
            return {
                "python": 12, "javascript": 8, "react": 6, "docker": 4,
                "kubernetes": 10, "machine_learning": 16, "testing": 6
            }
    
    @cached(ttl=86400)  # Cache for 24 hours  
    async def _generate_learning_resources_llm(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate learning resources database using LLM with current market data"""
        
        prompt = ChatPromptTemplate.from_template("""
        You are a curated learning resource expert who stays current with the best educational content in software development.
        
        Generate high-quality, current learning resources for major software development skills.
        Focus on resources that are:
        - Currently available and maintained (2024)
        - Highly rated by the developer community
        - Practical and hands-on oriented
        - Suitable for different difficulty levels
        
        For each skill, provide 3-5 resources covering different difficulty levels and learning types.
        
        Resource types: book, course, documentation, tutorial, video, project, bootcamp, certification
        Difficulty levels: beginner, intermediate, advanced
        
        Skills to cover:
        - python, javascript, typescript, react, django, flask
        - docker, kubernetes, aws, testing, security
        - machine_learning, data_science, system_design
        - api_design, microservices, devops
        
        Return ONLY a valid JSON object in this exact format:
        {{
            "skill_name": [
                {{
                    "title": "Resource Title",
                    "type": "book|course|documentation|tutorial|video|project",
                    "difficulty": "beginner|intermediate|advanced", 
                    "estimated_hours": 20,
                    "provider": "Publisher/Platform",
                    "year": 2024,
                    "rating": 4.5,
                    "url": "https://example.com"
                }}
            ]
        }}
        
        Focus on well-known, reputable resources like:
        - O'Reilly books, Manning publications
        - Coursera, Udemy, Pluralsight courses  
        - Official documentation
        - freeCodeCamp, The Odin Project
        - YouTube channels from experts
        - GitHub learning repositories
        """)
        
        try:
            messages = prompt.format_messages()
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            resources = json.loads(response.content.strip())
            
            logger.info(f"📚 Generated learning resources for {len(resources)} skills via LLM")
            return resources
            
        except Exception as e:
            logger.error(f"Failed to generate learning resources via LLM: {e}")
            # Return basic fallback
            return {
                "python": [
                    {"title": "Python Crash Course", "type": "book", "difficulty": "beginner", "estimated_hours": 30},
                    {"title": "Effective Python", "type": "book", "difficulty": "intermediate", "estimated_hours": 20}
                ],
                "javascript": [
                    {"title": "JavaScript: The Definitive Guide", "type": "book", "difficulty": "intermediate", "estimated_hours": 35}
                ]
            }
    
    @cached(ttl=86400)  # Cache for 24 hours
    async def _generate_style_adaptations_llm(self) -> Dict[LearningStyle, Dict[str, Any]]:
        """Generate learning style adaptations using LLM with educational psychology principles"""
        
        prompt = ChatPromptTemplate.from_template("""
        You are an expert in educational psychology and personalized learning strategies for software developers.
        
        Generate detailed learning style adaptations for the four main learning styles:
        1. VISUAL: Learners who prefer diagrams, charts, visual examples
        2. HANDS_ON: Learners who prefer building, experimenting, trial-and-error  
        3. THEORETICAL: Learners who prefer understanding concepts first, reading, structured approaches
        4. MIXED: Learners who benefit from varied approaches
        
        For each style, provide:
        - preferred_resource_types: Array of resource types they prefer
        - approach: Learning approach that works best
        - study_pattern: How they should structure study sessions
        - schedule_pattern: When/how often they should study
        - notes: Key characteristics and tips
        
        Return ONLY a valid JSON object in this format:
        {{
            "VISUAL": {{
                "preferred_resource_types": ["video", "tutorial", "documentation"],
                "approach": "diagram_heavy",
                "study_pattern": "short_focused_sessions", 
                "schedule_pattern": "daily_small_chunks",
                "notes": "Prefers visual examples and diagrams"
            }},
            "HANDS_ON": {{ ... }},
            "THEORETICAL": {{ ... }},
            "MIXED": {{ ... }}
        }}
        """)
        
        try:
            messages = prompt.format_messages()
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            adaptations_raw = json.loads(response.content.strip())
            
            # Convert to enum-keyed dictionary
            from .models import LearningStyle
            adaptations = {}
            for style_name, data in adaptations_raw.items():
                try:
                    style_enum = LearningStyle(style_name.upper())
                    adaptations[style_enum] = data
                except ValueError:
                    logger.warning(f"Unknown learning style: {style_name}")
            
            logger.info(f"🎨 Generated learning style adaptations for {len(adaptations)} styles via LLM")
            return adaptations
            
        except Exception as e:
            logger.error(f"Failed to generate style adaptations via LLM: {e}")
            # Return basic fallback
            from .models import LearningStyle
            return {
                LearningStyle.VISUAL: {
                    "preferred_resource_types": ["video", "tutorial", "documentation"],
                    "approach": "diagram_heavy",
                    "study_pattern": "short_focused_sessions",
                    "schedule_pattern": "daily_small_chunks",
                    "notes": "Prefers visual examples and diagrams"
                },
                LearningStyle.HANDS_ON: {
                    "preferred_resource_types": ["project", "tutorial", "workshop"],
                    "approach": "practice_first",
                    "study_pattern": "project_based",
                    "schedule_pattern": "longer_practice_sessions",
                    "notes": "Learns best through building and experimenting"
                }
            }
    
    async def _generate_difficulty_rules_llm(self) -> Dict[str, Any]:
        """Generate difficulty progression rules using LLM with pedagogical best practices"""
        
        prompt = ChatPromptTemplate.from_template("""
        You are an expert in curriculum design and skill progression for software development education.
        
        Generate optimal difficulty progression rules based on educational best practices and cognitive load theory.
        
        Consider:
        - How quickly learners can progress between difficulty levels
        - Time bonuses/penalties for different experience levels
        - Whether advanced skills should require prerequisite validation
        - Optimal challenge progression to maintain motivation
        
        Return ONLY a valid JSON object with these specific keys:
        {{
            "max_difficulty_jump": 1,
            "beginner_time_bonus": 1.5,
            "intermediate_time_bonus": 1.2, 
            "advanced_prerequisite_check": true,
            "skill_plateau_threshold": 0.85,
            "retention_factor": 0.9
        }}
        
        Provide integer/float values for numerical fields and boolean for checks.
        """)
        
        try:
            messages = prompt.format_messages()
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            rules = json.loads(response.content.strip())
            
            logger.info("📐 Generated difficulty progression rules via LLM")
            return rules
            
        except Exception as e:
            logger.error(f"Failed to generate difficulty rules via LLM: {e}")
            # Return basic fallback
            return {
                "max_difficulty_jump": 1,
                "beginner_time_bonus": 1.5,
                "advanced_prerequisite_check": True
            }
    
    def _initialize_static_skill_data(self):
        """Fallback method to initialize with static skill data"""
        logger.info("📊 Initializing with static skill data...")
        
        self.skill_dependencies = self._initialize_skill_dependencies_static()
        self.time_estimates = self._initialize_time_estimates_static()
        self.difficulty_rules = self._initialize_difficulty_rules_static()
        if not self.resource_db:
            self.resource_db = self._initialize_default_resources_static()
        self.style_adaptations = self._initialize_style_adaptations_static()
    
    def _initialize_skill_dependencies_static(self) -> Dict[str, List[str]]:
        """Initialize skill dependency graph"""
        return {
            "react": ["javascript", "html", "css"],
            "django": ["python"],
            "flask": ["python"],
            "testing": ["programming_fundamentals"],
            "security": ["programming_fundamentals"],
            "architecture": ["programming_fundamentals", "software_design"],
            "devops": ["programming_fundamentals", "linux"],
            "machine_learning": ["python", "statistics", "mathematics"],
            "data_science": ["python", "statistics", "machine_learning"],
            "api_design": ["programming_fundamentals", "web_development"],
            "microservices": ["api_design", "architecture", "devops"]
        }
    
    def _initialize_time_estimates_static(self) -> Dict[str, int]:
        """Initialize learning time estimates (weeks to master from zero)"""
        return {
            "python": 12, "javascript": 10, "java": 14, "typescript": 8,
            "react": 8, "django": 10, "flask": 6, "express": 6,
            "testing": 6, "security": 8, "architecture": 12, "devops": 10,
            "machine_learning": 16, "data_science": 14, "api_design": 6,
            "microservices": 10, "docker": 4, "kubernetes": 8
        }
    
    def _initialize_difficulty_rules_static(self) -> Dict[str, Any]:
        """Initialize difficulty progression rules"""
        return {
            "max_difficulty_jump": 1,  # Can only jump 1 difficulty level at a time
            "beginner_time_bonus": 1.5,  # 50% extra time for beginners
            "advanced_prerequisite_check": True  # Advanced skills require prerequisites
        }
    
    def _initialize_default_resources_static(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize default learning resource database"""
        return {
            "python": [
                {"title": "Python Crash Course", "type": "book", "difficulty": "beginner", "estimated_hours": 30},
                {"title": "Effective Python", "type": "book", "difficulty": "intermediate", "estimated_hours": 20},
                {"title": "Python Architecture Patterns", "type": "book", "difficulty": "advanced", "estimated_hours": 25}
            ],
            "javascript": [
                {"title": "JavaScript: The Definitive Guide", "type": "book", "difficulty": "intermediate", "estimated_hours": 35},
                {"title": "You Don't Know JS", "type": "book", "difficulty": "advanced", "estimated_hours": 40}
            ],
            "react": [
                {"title": "React Documentation", "type": "documentation", "difficulty": "beginner", "estimated_hours": 15},
                {"title": "React Patterns", "type": "course", "difficulty": "intermediate", "estimated_hours": 25}
            ]
        }
    
    def _initialize_style_adaptations_static(self) -> Dict[LearningStyle, Dict[str, Any]]:
        """Initialize learning style adaptations"""
        return {
            LearningStyle.VISUAL: {
                "preferred_resource_types": ["video", "tutorial", "documentation"],
                "approach": "diagram_heavy",
                "study_pattern": "short_focused_sessions",
                "schedule_pattern": "daily_small_chunks",
                "notes": "Prefers visual examples and diagrams"
            },
            LearningStyle.HANDS_ON: {
                "preferred_resource_types": ["project", "tutorial", "workshop"],
                "approach": "practice_first",
                "study_pattern": "project_based",
                "schedule_pattern": "longer_practice_sessions", 
                "notes": "Learns best through building and experimenting"
            },
            LearningStyle.THEORETICAL: {
                "preferred_resource_types": ["book", "course", "documentation"],
                "approach": "concept_first",
                "study_pattern": "deep_study_sessions",
                "schedule_pattern": "scheduled_blocks",
                "notes": "Prefers understanding principles before practice"
            },
            LearningStyle.MIXED: {
                "preferred_resource_types": ["course", "project", "book"],
                "approach": "balanced",
                "study_pattern": "varied",
                "schedule_pattern": "flexible",
                "notes": "Benefits from varied learning approaches"
            }
        } 