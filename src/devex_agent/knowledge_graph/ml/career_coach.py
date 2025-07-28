"""
Expert Career Coach - LLM-powered personalized career guidance

Provides intelligent career coaching by:
- Analyzing developer skill profiles and patterns
- Generating personalized learning recommendations  
- Creating skill development roadmaps
- Offering real-time coding suggestions
- Tracking career progression over time
"""

import logging
import asyncio
import uuid
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from .models import (
    DeveloperSkillProfile, SkillAssessment, PatternAnalysis,
    LearningPlan, CoachingSession, LearningResource, LearningMilestone,
    CareerStage, SkillCategory, CoachingTrigger
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

# LLM integration
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class CoachingContext:
    """Context for coaching sessions"""
    developer_id: str
    current_skill_profile: Optional[DeveloperSkillProfile]
    recent_pattern_analysis: Optional[PatternAnalysis]
    current_code_context: Optional[Dict[str, Any]]
    learning_goals: List[str]
    time_availability: str
    career_stage: CareerStage
    trigger_type: CoachingTrigger


class ExpertCareerCoachLLM:
    """
    Expert Career Coach powered by LLM for personalized developer guidance
    
    Uses advanced language models to provide:
    - Personalized career advice based on skill assessments
    - Learning path recommendations aligned with career goals
    - Real-time coding suggestions and improvements
    - Skill gap analysis and development strategies
    - Resource recommendations tailored to learning style
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 model_name: str = "gpt-4-turbo-preview",
                 temperature: float = 0.7,
                 max_tokens: int = 2000):
        """
        Initialize Expert Career Coach
        
        Args:
            openai_api_key: OpenAI API key for LLM access
            model_name: LLM model to use
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response length
        """
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize LLM if available
        self.llm = None
        if LLM_AVAILABLE and openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    openai_api_key=openai_api_key
                )
                logger.info(f"🤖 Expert Career Coach initialized with {model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")
                self.llm = None
        else:
            logger.warning("LLM not available - Career Coach will use fallback responses")
        
        # Coaching session history
        self.coaching_history: Dict[str, List[CoachingSession]] = {}
        
        # Resource knowledge base
        self.resource_db = self._initialize_resource_db()
        
        self.is_initialized = False
        logger.info("🎯 Expert Career Coach Engine initialized")
    
    async def initialize(self):
        """Initialize the Career Coach engine"""
        try:
            logger.info("🔄 Initializing Expert Career Coach...")
            
            # Test LLM connection if available
            if self.llm:
                test_response = await self._test_llm_connection()
                if test_response:
                    logger.info("✅ LLM connection verified")
                else:
                    logger.warning("⚠️ LLM connection failed - using fallback mode")
                    self.llm = None
            
            self.is_initialized = True
            logger.info("✅ Expert Career Coach initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Expert Career Coach: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup Career Coach resources"""
        logger.info("🧹 Cleaning up Expert Career Coach...")
        self.coaching_history.clear()
        self.is_initialized = False
        logger.info("✅ Expert Career Coach cleanup complete")
    
    @timed(operation_name="coaching_session_generation")
    async def generate_coaching_session(self, 
                                      context: CoachingContext,
                                      specific_question: Optional[str] = None) -> CoachingSession:
        """
        Generate a personalized coaching session
        
        Args:
            context: Current coaching context
            specific_question: Optional specific question from developer
            
        Returns:
            CoachingSession: Personalized coaching session
        """
        if not self.is_initialized:
            raise RuntimeError("Expert Career Coach not initialized")
        
        logger.info(f"🎯 Generating coaching session for {context.developer_id}")
        
        try:
            # Build coaching prompt based on context
            coaching_prompt = await self._build_coaching_prompt(context, specific_question)
            
            # Generate coaching response using LLM
            coaching_response = await self._generate_llm_coaching_response(coaching_prompt, context)
            
            # Create coaching session object
            session = CoachingSession(
                session_id=f"coaching_{context.developer_id}_{int(datetime.now().timestamp())}",
                developer_id=context.developer_id,
                timestamp=datetime.now(),
                trigger_type=context.trigger_type,
                current_context=self._serialize_context(context),
                code_context=context.current_code_context,
                coaching_message=coaching_response["main_message"],
                skills_addressed=coaching_response.get("skills_addressed", []),
                action_items=coaching_response.get("action_items", []),
                learning_opportunities=coaching_response.get("learning_opportunities", []),
                immediate_suggestions=coaching_response.get("immediate_suggestions", []),
                long_term_recommendations=coaching_response.get("long_term_recommendations", []),
                resource_suggestions=coaching_response.get("resource_suggestions", []),
                follow_up_needed=coaching_response.get("follow_up_needed", False),
                next_check_in=coaching_response.get("next_check_in")
            )
            
            # Store in history
            if context.developer_id not in self.coaching_history:
                self.coaching_history[context.developer_id] = []
            self.coaching_history[context.developer_id].append(session)
            
            logger.info(f"✅ Coaching session generated for {context.developer_id}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to generate coaching session: {e}")
            # Return fallback session
            return self._generate_fallback_session(context, specific_question)
    
    async def _build_coaching_prompt(self, 
                                   context: CoachingContext, 
                                   specific_question: Optional[str] = None) -> str:
        """Build a comprehensive coaching prompt for the LLM"""
        
        # Get skill summary
        skill_summary = self._summarize_skills(context.current_skill_profile)
        
        # Get pattern insights
        pattern_insights = self._summarize_patterns(context.recent_pattern_analysis)
        
        # Build career context
        career_context = self._build_career_context(context)
        
        # Get coaching history context
        history_context = self._get_recent_coaching_history(context.developer_id)
        
        prompt_parts = [
            "You are an Expert Coding Career Coach with deep knowledge of software development, career progression, and learning strategies.",
            "",
            "## DEVELOPER PROFILE:",
            f"- Developer ID: {context.developer_id}",
            f"- Career Stage: {context.career_stage.value}",
            f"- Time Availability: {context.time_availability}",
            f"- Learning Goals: {', '.join(context.learning_goals)}",
            "",
            "## CURRENT SKILL ASSESSMENT:",
            skill_summary,
            "",
            "## CODING PATTERNS ANALYSIS:",
            pattern_insights,
            "",
            "## CAREER CONTEXT:",
            career_context,
            "",
            "## RECENT COACHING HISTORY:",
            history_context,
            "",
            "## CURRENT SITUATION:",
            f"Trigger: {context.trigger_type.value}",
        ]
        
        if context.current_code_context:
            prompt_parts.extend([
                "## CURRENT CODE CONTEXT:",
                json.dumps(context.current_code_context, indent=2),
                ""
            ])
        
        if specific_question:
            prompt_parts.extend([
                "## SPECIFIC QUESTION:",
                specific_question,
                ""
            ])
        
        prompt_parts.extend([
            "## YOUR TASK:",
            "Provide personalized, actionable career coaching that:",
            "1. Addresses the developer's current context and needs",
            "2. Builds on their strengths and addresses improvement areas",
            "3. Provides specific, actionable recommendations",
            "4. Suggests relevant learning resources and next steps",
            "5. Encourages continued growth and development",
            "",
            "Be encouraging, specific, and focus on practical next steps.",
            "Tailor your advice to their career stage and available time.",
            "",
            "Please respond in JSON format with the following structure:",
            "{",
            '  "main_message": "Your primary coaching message (2-3 paragraphs)",',
            '  "skills_addressed": ["skill1", "skill2"],',
            '  "action_items": ["Specific action 1", "Specific action 2"],',
            '  "learning_opportunities": ["Learning opportunity 1", "Learning opportunity 2"],',
            '  "immediate_suggestions": ["Quick win 1", "Quick win 2"],',
            '  "long_term_recommendations": ["Long-term goal 1", "Long-term goal 2"],',
            '  "resource_suggestions": [',
            '    {',
            '      "title": "Resource title",',
            '      "type": "course|book|tutorial|project",',
            '      "url": "https://example.com",',
            '      "difficulty": "beginner|intermediate|advanced",',
            '      "estimated_hours": 10,',
            '      "skills_covered": ["skill1", "skill2"],',
            '      "relevance_score": 0.9,',
            '      "personalization_reason": "Why this is relevant"',
            '    }',
            '  ],',
            '  "follow_up_needed": true,',
            '  "next_check_in": "2024-01-22T10:00:00Z"',
            "}"
        ])
        
        return "\n".join(prompt_parts)
    
    async def _generate_llm_coaching_response(self, 
                                            prompt: str, 
                                            context: CoachingContext) -> Dict[str, Any]:
        """Generate coaching response using LLM"""
        
        if not self.llm:
            return self._generate_fallback_response(context)
        
        try:
            # Create chat messages
            messages = [
                SystemMessage(content="You are an Expert Coding Career Coach. Always respond in valid JSON format."),
                HumanMessage(content=prompt)
            ]
            
            # Generate response
            response = await asyncio.to_thread(self.llm.invoke, messages)
            
            # Parse JSON response
            response_text = response.content.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            
            coaching_data = json.loads(response_text)
            
            # Validate and enhance response
            return self._validate_and_enhance_response(coaching_data, context)
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return self._generate_fallback_response(context)
        except Exception as e:
            logger.error(f"LLM coaching generation failed: {e}")
            return self._generate_fallback_response(context)
    
    def _summarize_skills(self, skill_profile: Optional[DeveloperSkillProfile]) -> str:
        """Summarize developer's current skill levels"""
        if not skill_profile:
            return "No skill profile available"
        
        summary_parts = []
        
        # Technical skills
        if skill_profile.technical_skills:
            top_skills = sorted(skill_profile.technical_skills.items(), 
                              key=lambda x: x[1], reverse=True)[:5]
            summary_parts.append("**Technical Skills (Top 5):**")
            for skill, level in top_skills:
                percentage = int(level * 100)
                summary_parts.append(f"- {skill}: {percentage}%")
        
        # Strengths and improvement areas
        if skill_profile.strength_areas:
            summary_parts.append(f"**Strengths:** {', '.join(skill_profile.strength_areas)}")
        
        if skill_profile.improvement_areas:
            summary_parts.append(f"**Improvement Areas:** {', '.join(skill_profile.improvement_areas)}")
        
        # Learning metrics
        summary_parts.append(f"**Learning Efficiency:** {int(skill_profile.learning_efficiency * 100)}%")
        summary_parts.append(f"**Consistency Score:** {int(skill_profile.consistency_score * 100)}%")
        
        return "\n".join(summary_parts)
    
    def _summarize_patterns(self, pattern_analysis: Optional[PatternAnalysis]) -> str:
        """Summarize developer's coding patterns"""
        if not pattern_analysis:
            return "No pattern analysis available"
        
        summary_parts = []
        
        # Language proficiency
        if pattern_analysis.language_proficiency:
            top_languages = sorted(pattern_analysis.language_proficiency.items(), 
                                 key=lambda x: x[1], reverse=True)[:3]
            summary_parts.append("**Primary Languages:**")
            for lang, score in top_languages:
                percentage = int(score * 100)
                summary_parts.append(f"- {lang}: {percentage}%")
        
        # Architecture preferences
        if pattern_analysis.architectural_preferences:
            arch_prefs = [f"{k}({int(v*100)}%)" 
                         for k, v in pattern_analysis.architectural_preferences.items() 
                         if v > 0.3]
            if arch_prefs:
                summary_parts.append(f"**Architecture Patterns:** {', '.join(arch_prefs)}")
        
        # Code quality indicators
        if pattern_analysis.error_handling_patterns:
            error_handling = max(pattern_analysis.error_handling_patterns.items(), 
                               key=lambda x: x[1])[0]
            summary_parts.append(f"**Error Handling Style:** {error_handling}")
        
        # Golden source similarity
        similarity = int(pattern_analysis.similarity_to_golden_sources * 100)
        summary_parts.append(f"**Alignment with Org Standards:** {similarity}%")
        
        return "\n".join(summary_parts)
    
    def _build_career_context(self, context: CoachingContext) -> str:
        """Build career progression context"""
        
        career_contexts = {
            CareerStage.JUNIOR: "Early career developer focusing on foundational skills and learning best practices",
            CareerStage.MID: "Mid-level developer building expertise and taking on more complex projects",
            CareerStage.SENIOR: "Senior developer leading projects and mentoring others",
            CareerStage.LEAD: "Technical lead managing teams and architectural decisions",
            CareerStage.PRINCIPAL: "Principal engineer setting technical direction and strategy",
            CareerStage.ARCHITECT: "Architect designing large-scale systems and technical vision"
        }
        
        context_parts = [
            f"**Current Stage:** {career_contexts.get(context.career_stage, 'Unknown')}",
            f"**Time Commitment:** {context.time_availability}",
        ]
        
        if context.learning_goals:
            context_parts.append(f"**Learning Goals:** {', '.join(context.learning_goals)}")
        
        return "\n".join(context_parts)
    
    def _get_recent_coaching_history(self, developer_id: str, limit: int = 3) -> str:
        """Get recent coaching history for context"""
        
        if developer_id not in self.coaching_history:
            return "No previous coaching sessions"
        
        recent_sessions = self.coaching_history[developer_id][-limit:]
        
        if not recent_sessions:
            return "No previous coaching sessions"
        
        history_parts = []
        for session in recent_sessions:
            days_ago = (datetime.now() - session.timestamp).days
            history_parts.append(f"- {days_ago} days ago: {session.coaching_message[:100]}...")
        
        return "\n".join(history_parts)
    
    def _validate_and_enhance_response(self, 
                                     coaching_data: Dict[str, Any], 
                                     context: CoachingContext) -> Dict[str, Any]:
        """Validate and enhance LLM response"""
        
        # Ensure required fields
        required_fields = ["main_message", "skills_addressed", "action_items"]
        for field in required_fields:
            if field not in coaching_data:
                coaching_data[field] = []
        
        # Enhance resource suggestions with our knowledge base
        if "resource_suggestions" in coaching_data:
            enhanced_resources = []
            for resource in coaching_data["resource_suggestions"]:
                if isinstance(resource, dict):
                    # Convert to LearningResource object
                    enhanced_resource = LearningResource(
                        resource_id=str(uuid.uuid4()),
                        title=resource.get("title", "Learning Resource"),
                        type=resource.get("type", "course"),
                        url=resource.get("url"),
                        difficulty=resource.get("difficulty", "intermediate"),
                        estimated_hours=resource.get("estimated_hours", 5),
                        skills_covered=resource.get("skills_covered", []),
                        relevance_score=resource.get("relevance_score", 0.8),
                        personalization_reason=resource.get("personalization_reason", "Recommended for your skill level")
                    )
                    enhanced_resources.append(enhanced_resource)
            
            coaching_data["resource_suggestions"] = enhanced_resources
        
        # Set reasonable defaults
        coaching_data.setdefault("follow_up_needed", True)
        coaching_data.setdefault("learning_opportunities", [])
        coaching_data.setdefault("immediate_suggestions", [])
        coaching_data.setdefault("long_term_recommendations", [])
        
        # Set next check-in if not provided
        if "next_check_in" not in coaching_data or not coaching_data["next_check_in"]:
            # Default to 1 week from now
            next_checkin = datetime.now() + timedelta(weeks=1)
            coaching_data["next_check_in"] = next_checkin
        
        return coaching_data
    
    def _generate_fallback_response(self, context: CoachingContext) -> Dict[str, Any]:
        """Generate fallback response when LLM is not available"""
        
        skill_suggestions = []
        action_items = []
        
        # Basic skill-based suggestions
        if context.current_skill_profile:
            if context.current_skill_profile.improvement_areas:
                skill_suggestions.extend([
                    f"Focus on improving {area}" 
                    for area in context.current_skill_profile.improvement_areas[:2]
                ])
            
            if context.current_skill_profile.recommended_focus:
                action_items.extend([
                    f"Practice {focus}" 
                    for focus in context.current_skill_profile.recommended_focus[:2]
                ])
        
        # Stage-specific advice
        stage_advice = {
            CareerStage.JUNIOR: "Focus on building strong fundamentals and learning from experienced developers",
            CareerStage.MID: "Take on more complex projects and start mentoring junior developers",
            CareerStage.SENIOR: "Lead technical initiatives and contribute to architectural decisions",
            CareerStage.LEAD: "Focus on team leadership and technical strategy",
            CareerStage.PRINCIPAL: "Drive technical vision and cross-team initiatives",
            CareerStage.ARCHITECT: "Shape organizational technical direction and long-term strategy"
        }
        
        main_message = stage_advice.get(
            context.career_stage, 
            "Continue developing your skills and seeking new challenges"
        )
        
        return {
            "main_message": main_message,
            "skills_addressed": skill_suggestions,
            "action_items": action_items or ["Continue regular practice", "Seek feedback on your code"],
            "learning_opportunities": ["Code review participation", "Technical documentation"],
            "immediate_suggestions": ["Review recent code for improvements"],
            "long_term_recommendations": ["Set specific learning goals", "Find a mentor"],
            "resource_suggestions": [],
            "follow_up_needed": True,
            "next_check_in": datetime.now() + timedelta(weeks=1)
        }
    
    def _generate_fallback_session(self, 
                                 context: CoachingContext, 
                                 specific_question: Optional[str] = None) -> CoachingSession:
        """Generate fallback coaching session"""
        
        fallback_response = self._generate_fallback_response(context)
        
        return CoachingSession(
            session_id=f"fallback_{context.developer_id}_{int(datetime.now().timestamp())}",
            developer_id=context.developer_id,
            timestamp=datetime.now(),
            trigger_type=context.trigger_type,
            current_context=self._serialize_context(context),
            code_context=context.current_code_context,
            coaching_message=fallback_response["main_message"],
            skills_addressed=fallback_response["skills_addressed"],
            action_items=fallback_response["action_items"],
            learning_opportunities=fallback_response["learning_opportunities"],
            immediate_suggestions=fallback_response["immediate_suggestions"],
            long_term_recommendations=fallback_response["long_term_recommendations"],
            resource_suggestions=fallback_response["resource_suggestions"],
            follow_up_needed=fallback_response["follow_up_needed"]
        )
    
    def _serialize_context(self, context: CoachingContext) -> Dict[str, Any]:
        """Serialize coaching context for storage"""
        return {
            "developer_id": context.developer_id,
            "career_stage": context.career_stage.value,
            "time_availability": context.time_availability,
            "learning_goals": context.learning_goals,
            "trigger_type": context.trigger_type.value,
            "has_skill_profile": context.current_skill_profile is not None,
            "has_pattern_analysis": context.recent_pattern_analysis is not None
        }
    
    async def _test_llm_connection(self) -> bool:
        """Test LLM connection"""
        try:
            test_messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Respond with 'OK' if you can hear me.")
            ]
            
            response = await asyncio.to_thread(self.llm.invoke, test_messages)
            return "ok" in response.content.lower()
            
        except Exception as e:
            logger.debug(f"LLM connection test failed: {e}")
            return False
    
    def _initialize_resource_db(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize knowledge base of learning resources"""
        return {
            "python": [
                {
                    "title": "Python for Everybody Specialization",
                    "type": "course",
                    "provider": "Coursera",
                    "difficulty": "beginner",
                    "estimated_hours": 40,
                    "url": "https://www.coursera.org/specializations/python"
                },
                {
                    "title": "Effective Python",
                    "type": "book", 
                    "provider": "Addison-Wesley",
                    "difficulty": "intermediate",
                    "estimated_hours": 20
                }
            ],
            "javascript": [
                {
                    "title": "JavaScript: The Definitive Guide",
                    "type": "book",
                    "provider": "O'Reilly",
                    "difficulty": "intermediate",
                    "estimated_hours": 30
                }
            ],
            "architecture": [
                {
                    "title": "Clean Architecture",
                    "type": "book",
                    "provider": "Prentice Hall",
                    "difficulty": "intermediate", 
                    "estimated_hours": 15
                }
            ]
        }
    
    async def get_coaching_history(self, developer_id: str, limit: int = 10) -> List[CoachingSession]:
        """Get coaching session history for a developer"""
        if developer_id not in self.coaching_history:
            return []
        
        return self.coaching_history[developer_id][-limit:]
    
    @cached(ttl=1800)  # Cache for 30 minutes  
    async def suggest_learning_resources(self, 
                                       skills: List[str], 
                                       difficulty_level: str = "intermediate",
                                       max_resources: int = 5) -> List[LearningResource]:
        """Suggest learning resources based on skills"""
        resources = []
        
        for skill in skills:
            skill_resources = self.resource_db.get(skill.lower(), [])
            for resource_data in skill_resources[:2]:  # Top 2 per skill
                resource = LearningResource(
                    resource_id=str(uuid.uuid4()),
                    title=resource_data["title"],
                    type=resource_data["type"],
                    url=resource_data.get("url"),
                    provider=resource_data.get("provider"),
                    difficulty=resource_data["difficulty"],
                    estimated_hours=resource_data.get("estimated_hours", 10),
                    skills_covered=[skill],
                    relevance_score=0.8,
                    personalization_reason=f"Recommended for {skill} skill development"
                )
                resources.append(resource)
        
        return resources[:max_resources] 