"""
Developer Intelligence Engine - Advanced skill tracking and personalized coaching

Orchestrates CodeBERT analysis to provide:
- Automatic skill assessment and tracking
- Personalized learning recommendations
- Developer pattern analysis and evolution
- Real-time coaching suggestions
"""

import logging
import asyncio
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import defaultdict

from .codebert_engine import CodeBERTEngine
from .models import (
    DeveloperSkillProfile, SkillTimeline, PatternAnalysis,
    SkillAssessment, LearningPlan, CoachingSession,
    CareerStage, SkillCategory, TrendDirection, CoachingTrigger
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


class DeveloperIntelligenceEngine:
    """
    Advanced developer intelligence engine using CodeBERT for skill tracking
    
    Provides comprehensive developer profiling, skill progression tracking,
    and personalized learning recommendations based on code analysis.
    """
    
    def __init__(self, 
                 codebert_engine: CodeBERTEngine,
                 data_directory: str = "./data/developer_intelligence",
                 skill_update_threshold: float = 0.1):
        """
        Initialize Developer Intelligence Engine
        
        Args:
            codebert_engine: CodeBERT engine for semantic analysis
            data_directory: Directory to store developer data
            skill_update_threshold: Minimum change to trigger skill updates
        """
        self.codebert = codebert_engine
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        self.skill_update_threshold = skill_update_threshold
        
        # In-memory storage for development (would use database in production)
        self.developer_profiles: Dict[str, DeveloperSkillProfile] = {}
        self.skill_timelines: Dict[str, List[SkillTimeline]] = defaultdict(list)
        self.coaching_sessions: Dict[str, List[CoachingSession]] = defaultdict(list)
        self.pattern_analyses: Dict[str, List[PatternAnalysis]] = defaultdict(list)
        
        # Skill categories and their assessment functions
        self.skill_categories = {
            SkillCategory.LANGUAGE: self._assess_language_skills,
            SkillCategory.FRAMEWORK: self._assess_framework_skills,
            SkillCategory.ARCHITECTURE: self._assess_architecture_skills,
            SkillCategory.TESTING: self._assess_testing_skills,
            SkillCategory.SECURITY: self._assess_security_skills,
            SkillCategory.DEVOPS: self._assess_devops_skills
        }
        
        # Golden source embeddings cache
        self.golden_source_cache = {}
        
        self.is_initialized = False
        logger.info("🧠 Developer Intelligence Engine initialized")
    
    async def initialize(self):
        """Initialize the Developer Intelligence Engine"""
        try:
            logger.info("🔄 Initializing Developer Intelligence Engine...")
            
            # Initialize CodeBERT engine
            if not self.codebert.is_initialized:
                await self.codebert.initialize()
            
            # Load existing developer data
            await self._load_existing_data()
            
            self.is_initialized = True
            logger.info("✅ Developer Intelligence Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Developer Intelligence Engine: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup Developer Intelligence Engine resources"""
        logger.info("🧹 Cleaning up Developer Intelligence Engine...")
        
        # Save current data
        await self._save_all_data()
        
        # Clear memory
        self.developer_profiles.clear()
        self.skill_timelines.clear()
        self.coaching_sessions.clear()
        self.pattern_analyses.clear()
        self.golden_source_cache.clear()
        
        self.is_initialized = False
        logger.info("✅ Developer Intelligence Engine cleanup complete")
    
    @timed(operation_name="developer_profile_analysis")
    async def analyze_developer_code(self, 
                                   developer_id: str, 
                                   code_snippets: List[str],
                                   file_paths: List[str] = None,
                                   commit_messages: List[str] = None) -> PatternAnalysis:
        """
        Analyze developer's code using CodeBERT for pattern recognition
        
        Args:
            developer_id: Developer identifier
            code_snippets: List of code snippets to analyze
            file_paths: Optional file paths for context
            commit_messages: Optional commit messages for context
            
        Returns:
            Pattern analysis results
        """
        if not self.is_initialized:
            raise RuntimeError("Developer Intelligence Engine not initialized")
        
        logger.info(f"🔍 Analyzing code patterns for developer: {developer_id}")
        
        try:
            # Use CodeBERT to analyze patterns
            pattern_data = await self.codebert.analyze_code_patterns(
                code_snippets, developer_id
            )
            
            # Create pattern analysis model
            pattern_analysis = PatternAnalysis(
                developer_id=developer_id,
                analysis_id=f"analysis_{developer_id}_{int(datetime.now().timestamp())}",
                analyzed_at=datetime.now(),
                dominant_patterns=pattern_data.get("dominant_patterns", []),
                architectural_preferences=pattern_data.get("architectural_patterns", {}),
                naming_conventions=self._analyze_naming_conventions(code_snippets),
                complexity_preferences=pattern_data.get("complexity_patterns", {}),
                language_proficiency=pattern_data.get("language_patterns", {}),
                framework_usage=self._detect_framework_usage(code_snippets),
                library_preferences=self._extract_library_preferences(code_snippets),
                error_handling_patterns=self._analyze_error_handling(code_snippets),
                testing_patterns=self._analyze_testing_patterns(code_snippets),
                documentation_style=self._analyze_documentation_style(code_snippets),
                code_embeddings=pattern_data.get("overall_embedding", []),
                pattern_embeddings={},
                similarity_to_golden_sources=await self._calculate_golden_source_similarity(
                    pattern_data.get("overall_embedding", [])
                ),
                peer_comparison={}
            )
            
            # Store the analysis
            self.pattern_analyses[developer_id].append(pattern_analysis)
            
            logger.info(f"✅ Pattern analysis completed for {developer_id}")
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze developer code: {e}")
            raise
    
    @timed(operation_name="skill_assessment")
    async def assess_developer_skills(self, 
                                    developer_id: str, 
                                    code_snippets: List[str],
                                    force_update: bool = False) -> Dict[str, SkillAssessment]:
        """
        Assess developer skills across multiple categories
        
        Args:
            developer_id: Developer identifier
            code_snippets: Recent code snippets for analysis
            force_update: Force skill reassessment
            
        Returns:
            Dictionary of skill assessments by category
        """
        logger.info(f"📏 Assessing skills for developer: {developer_id}")
        
        try:
            assessments = {}
            
            # Assess skills in each category
            for category, assess_func in self.skill_categories.items():
                category_assessments = await assess_func(
                    developer_id, code_snippets
                )
                assessments.update(category_assessments)
            
            # Update developer profile
            await self._update_developer_profile(developer_id, assessments, force_update)
            
            # Update skill timelines
            for skill_name, assessment in assessments.items():
                await self._update_skill_timeline(developer_id, skill_name, assessment)
            
            logger.info(f"✅ Assessed {len(assessments)} skills for {developer_id}")
            return assessments
            
        except Exception as e:
            logger.error(f"❌ Failed to assess developer skills: {e}")
            raise
    
    async def _assess_language_skills(self, 
                                    developer_id: str, 
                                    code_snippets: List[str]) -> Dict[str, SkillAssessment]:
        """Assess programming language skills"""
        assessments = {}
        
        # Detect languages in code
        languages = ["python", "javascript", "java", "typescript", "go", "rust"]
        
        for language in languages:
            lang_snippets = [code for code in code_snippets 
                           if self._detect_language_in_code(code, language)]
            
            if lang_snippets:
                # Use CodeBERT to assess skill level
                skill_data = await self.codebert.assess_skill_level(
                    lang_snippets, language
                )
                
                assessment = SkillAssessment(
                    skill_name=language,
                    category=SkillCategory.LANGUAGE,
                    level=skill_data["overall_level"],
                    confidence=skill_data["assessment_confidence"],
                    evidence=skill_data["evidence"],
                    assessed_at=datetime.now(),
                    assessment_method="codebert_semantic_analysis",
                    pattern_matches=[],
                    code_examples=lang_snippets[:3],  # Top 3 examples
                    similarity_to_experts=skill_data["golden_source_similarity"]
                )
                
                assessments[language] = assessment
        
        return assessments
    
    async def _assess_framework_skills(self, 
                                     developer_id: str, 
                                     code_snippets: List[str]) -> Dict[str, SkillAssessment]:
        """Assess framework and library skills"""
        assessments = {}
        
        # Framework patterns to detect
        frameworks = {
            "react": ["react", "jsx", "usestate", "useeffect"],
            "django": ["django", "models.model", "views", "urls.py"],
            "flask": ["flask", "app.route", "@app.", "request"],
            "express": ["express", "app.get", "app.post", "middleware"],
            "spring": ["@controller", "@service", "@autowired", "springframework"]
        }
        
        for framework, patterns in frameworks.items():
            framework_snippets = []
            pattern_count = 0
            
            for code in code_snippets:
                code_lower = code.lower()
                if any(pattern in code_lower for pattern in patterns):
                    framework_snippets.append(code)
                    pattern_count += sum(1 for pattern in patterns if pattern in code_lower)
            
            if framework_snippets:
                # Calculate skill level based on pattern usage and complexity
                skill_level = min(1.0, (pattern_count / len(patterns)) * 0.8 + 
                                len(framework_snippets) / max(10, len(code_snippets)) * 0.2)
                
                assessment = SkillAssessment(
                    skill_name=framework,
                    category=SkillCategory.FRAMEWORK,
                    level=skill_level,
                    confidence=0.7 if len(framework_snippets) >= 3 else 0.5,
                    evidence=[f"Uses {len(framework_snippets)} {framework} patterns"],
                    assessed_at=datetime.now(),
                    assessment_method="pattern_detection",
                    pattern_matches=[],
                    code_examples=framework_snippets[:2],
                    similarity_to_experts=0.0
                )
                
                assessments[framework] = assessment
        
        return assessments
    
    async def _assess_architecture_skills(self, 
                                        developer_id: str, 
                                        code_snippets: List[str]) -> Dict[str, SkillAssessment]:
        """Assess architectural and design pattern skills"""
        assessments = {}
        
        # Architecture patterns to detect
        arch_patterns = {
            "mvc": ["controller", "model", "view"],
            "clean_architecture": ["repository", "service", "entity"],
            "microservices": ["api", "service", "endpoint"],
            "design_patterns": ["factory", "singleton", "observer", "strategy"]
        }
        
        for pattern_name, keywords in arch_patterns.items():
            pattern_snippets = []
            keyword_matches = 0
            
            all_code = " ".join(code_snippets).lower()
            
            for keyword in keywords:
                if keyword in all_code:
                    keyword_matches += 1
                    pattern_snippets.extend([code for code in code_snippets 
                                           if keyword in code.lower()])
            
            if keyword_matches > 0:
                skill_level = min(1.0, keyword_matches / len(keywords))
                
                assessment = SkillAssessment(
                    skill_name=pattern_name,
                    category=SkillCategory.ARCHITECTURE,
                    level=skill_level,
                    confidence=0.6 if keyword_matches >= 2 else 0.4,
                    evidence=[f"Uses {keyword_matches}/{len(keywords)} {pattern_name} indicators"],
                    assessed_at=datetime.now(),
                    assessment_method="keyword_pattern_analysis",
                    pattern_matches=[],
                    code_examples=pattern_snippets[:2],
                    similarity_to_experts=0.0
                )
                
                assessments[pattern_name] = assessment
        
        return assessments
    
    async def _assess_testing_skills(self, 
                                   developer_id: str, 
                                   code_snippets: List[str]) -> Dict[str, SkillAssessment]:
        """Assess testing and quality assurance skills"""
        assessments = {}
        
        # Testing patterns
        test_indicators = ["test_", "def test", "assert", "unittest", "pytest", 
                          "it(", "describe(", "expect(", "@test"]
        
        test_snippets = []
        test_count = 0
        
        for code in code_snippets:
            if any(indicator in code.lower() for indicator in test_indicators):
                test_snippets.append(code)
                test_count += 1
        
        if test_snippets:
            # Calculate testing skill level
            test_ratio = len(test_snippets) / len(code_snippets)
            skill_level = min(1.0, test_ratio * 2)  # Scale up test ratio
            
            assessment = SkillAssessment(
                skill_name="testing",
                category=SkillCategory.TESTING,
                level=skill_level,
                confidence=0.8 if len(test_snippets) >= 3 else 0.6,
                evidence=[f"Has {len(test_snippets)} test-related code snippets"],
                assessed_at=datetime.now(),
                assessment_method="test_pattern_detection",
                pattern_matches=[],
                code_examples=test_snippets[:2],
                similarity_to_experts=0.0
            )
            
            assessments["testing"] = assessment
        
        return assessments
    
    async def _assess_security_skills(self, 
                                    developer_id: str, 
                                    code_snippets: List[str]) -> Dict[str, SkillAssessment]:
        """Assess security-related coding skills"""
        assessments = {}
        
        # Security patterns
        security_indicators = ["encrypt", "hash", "auth", "validate", "sanitize", 
                             "csrf", "xss", "sql injection", "secure"]
        
        security_snippets = []
        security_count = 0
        
        for code in code_snippets:
            code_lower = code.lower()
            if any(indicator in code_lower for indicator in security_indicators):
                security_snippets.append(code)
                security_count += 1
        
        if security_snippets:
            skill_level = min(1.0, len(security_snippets) / max(5, len(code_snippets)))
            
            assessment = SkillAssessment(
                skill_name="security",
                category=SkillCategory.SECURITY,
                level=skill_level,
                confidence=0.7,
                evidence=[f"Uses {len(security_snippets)} security-related patterns"],
                assessed_at=datetime.now(),
                assessment_method="security_pattern_detection",
                pattern_matches=[],
                code_examples=security_snippets[:2],
                similarity_to_experts=0.0
            )
            
            assessments["security"] = assessment
        
        return assessments
    
    async def _assess_devops_skills(self, 
                                  developer_id: str, 
                                  code_snippets: List[str]) -> Dict[str, SkillAssessment]:
        """Assess DevOps and infrastructure skills"""
        assessments = {}
        
        # DevOps patterns
        devops_indicators = ["docker", "kubernetes", "ci/cd", "pipeline", "deploy", 
                           "infrastructure", "terraform", "ansible"]
        
        devops_snippets = []
        
        for code in code_snippets:
            if any(indicator in code.lower() for indicator in devops_indicators):
                devops_snippets.append(code)
        
        if devops_snippets:
            skill_level = min(1.0, len(devops_snippets) / max(3, len(code_snippets)))
            
            assessment = SkillAssessment(
                skill_name="devops",
                category=SkillCategory.DEVOPS,
                level=skill_level,
                confidence=0.6,
                evidence=[f"Has {len(devops_snippets)} DevOps-related code"],
                assessed_at=datetime.now(),
                assessment_method="devops_pattern_detection",
                pattern_matches=[],
                code_examples=devops_snippets[:2],
                similarity_to_experts=0.0
            )
            
            assessments["devops"] = assessment
        
        return assessments
    
    def _detect_language_in_code(self, code: str, language: str) -> bool:
        """Detect if code snippet is in a specific language"""
        language_indicators = {
            "python": ["def ", "import ", "self.", "__init__", "python"],
            "javascript": ["function", "const ", "let ", "var ", "=>", "javascript"],
            "java": ["public class", "private ", "import java", "java"],
            "typescript": [": string", ": number", "interface ", "typescript"],
            "go": ["func ", "package ", "import (", "golang"],
            "rust": ["fn ", "let mut", "impl ", "rust"]
        }
        
        indicators = language_indicators.get(language, [])
        code_lower = code.lower()
        
        return any(indicator in code_lower for indicator in indicators)
    
    def _analyze_naming_conventions(self, code_snippets: List[str]) -> Dict[str, Any]:
        """Analyze naming convention preferences"""
        conventions = {
            "snake_case": 0,
            "camelCase": 0,
            "PascalCase": 0,
            "kebab-case": 0
        }
        
        import re
        
        for code in code_snippets:
            # Extract identifiers (simplified)
            identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
            
            for identifier in identifiers:
                if '_' in identifier and identifier.islower():
                    conventions["snake_case"] += 1
                elif any(c.isupper() for c in identifier[1:]) and identifier[0].islower():
                    conventions["camelCase"] += 1
                elif identifier[0].isupper() and any(c.isupper() for c in identifier[1:]):
                    conventions["PascalCase"] += 1
                elif '-' in identifier:
                    conventions["kebab-case"] += 1
        
        total = sum(conventions.values())
        if total > 0:
            conventions = {k: v/total for k, v in conventions.items()}
        
        # Determine preferred style
        preferred_style = max(conventions.items(), key=lambda x: x[1])[0] if conventions else "unknown"
        
        return {
            "style_distribution": conventions,
            "preferred_style": preferred_style,
            "consistency_score": max(conventions.values()) if conventions else 0.0
        }
    
    def _detect_framework_usage(self, code_snippets: List[str]) -> Dict[str, float]:
        """Detect framework usage patterns"""
        frameworks = {
            "react": 0, "vue": 0, "angular": 0, "django": 0, "flask": 0,
            "express": 0, "spring": 0, "fastapi": 0
        }
        
        all_code = " ".join(code_snippets).lower()
        
        # Framework detection patterns
        framework_patterns = {
            "react": ["react", "jsx", "usestate"],
            "vue": ["vue", "v-if", "v-for"],
            "angular": ["angular", "@component", "ngfor"],
            "django": ["django", "models.model", "views"],
            "flask": ["flask", "app.route", "@app"],
            "express": ["express", "app.get", "req."],
            "spring": ["spring", "@autowired", "@controller"],
            "fastapi": ["fastapi", "@app.get", "pydantic"]
        }
        
        for framework, patterns in framework_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in all_code)
            frameworks[framework] = matches / len(patterns) if patterns else 0
        
        return frameworks
    
    def _extract_library_preferences(self, code_snippets: List[str]) -> List[str]:
        """Extract commonly used libraries"""
        libraries = []
        import re
        
        for code in code_snippets:
            # Extract import statements
            import_matches = re.findall(r'import\s+(\w+)', code)
            from_matches = re.findall(r'from\s+(\w+)', code)
            require_matches = re.findall(r'require\([\'"](\w+)[\'"]\)', code)
            
            libraries.extend(import_matches + from_matches + require_matches)
        
        # Count frequency and return top libraries
        from collections import Counter
        library_counts = Counter(libraries)
        
        return [lib for lib, count in library_counts.most_common(10)]
    
    def _analyze_error_handling(self, code_snippets: List[str]) -> Dict[str, float]:
        """Analyze error handling patterns"""
        patterns = {
            "try_catch": 0,
            "if_else_validation": 0,
            "early_return": 0,
            "logging": 0
        }
        
        for code in code_snippets:
            code_lower = code.lower()
            
            if "try:" in code_lower and "except" in code_lower:
                patterns["try_catch"] += 1
            
            if "if " in code_lower and ("is none" in code_lower or "is not" in code_lower):
                patterns["if_else_validation"] += 1
            
            if "return" in code_lower and "if " in code_lower:
                patterns["early_return"] += 1
            
            if "log" in code_lower or "print" in code_lower:
                patterns["logging"] += 1
        
        total = len(code_snippets)
        if total > 0:
            patterns = {k: v/total for k, v in patterns.items()}
        
        return patterns
    
    def _analyze_testing_patterns(self, code_snippets: List[str]) -> Dict[str, float]:
        """Analyze testing methodology patterns"""
        patterns = {
            "unit_tests": 0,
            "integration_tests": 0,
            "mocking": 0,
            "assertions": 0
        }
        
        for code in code_snippets:
            code_lower = code.lower()
            
            if any(indicator in code_lower for indicator in ["def test_", "it(", "describe("]):
                patterns["unit_tests"] += 1
            
            if "integration" in code_lower or "e2e" in code_lower:
                patterns["integration_tests"] += 1
            
            if "mock" in code_lower or "stub" in code_lower:
                patterns["mocking"] += 1
            
            if "assert" in code_lower or "expect(" in code_lower:
                patterns["assertions"] += 1
        
        total = len(code_snippets)
        if total > 0:
            patterns = {k: v/total for k, v in patterns.items()}
        
        return patterns
    
    def _analyze_documentation_style(self, code_snippets: List[str]) -> Dict[str, Any]:
        """Analyze documentation and commenting style"""
        doc_metrics = {
            "has_docstrings": 0,
            "has_inline_comments": 0,
            "comment_density": 0.0,
            "documentation_quality": "low"
        }
        
        total_lines = 0
        comment_lines = 0
        
        for code in code_snippets:
            lines = code.split('\n')
            total_lines += len(lines)
            
            for line in lines:
                line_stripped = line.strip()
                
                # Check for docstrings
                if '"""' in line or "'''" in line:
                    doc_metrics["has_docstrings"] += 1
                
                # Check for comments
                if line_stripped.startswith('#') or '//' in line_stripped:
                    comment_lines += 1
                    doc_metrics["has_inline_comments"] += 1
        
        # Calculate comment density
        if total_lines > 0:
            doc_metrics["comment_density"] = comment_lines / total_lines
        
        # Determine documentation quality
        if doc_metrics["comment_density"] > 0.2 and doc_metrics["has_docstrings"] > 0:
            doc_metrics["documentation_quality"] = "high"
        elif doc_metrics["comment_density"] > 0.1:
            doc_metrics["documentation_quality"] = "medium"
        
        return doc_metrics
    
    async def _calculate_golden_source_similarity(self, embedding: List[float]) -> float:
        """Calculate similarity to golden source patterns"""
        if not embedding or not self.golden_source_cache:
            return 0.0
        
        try:
            embedding_array = np.array(embedding).reshape(1, -1)
            similarities = []
            
            for source_embeddings in self.golden_source_cache.values():
                if source_embeddings:
                    source_array = np.array(source_embeddings)
                    similarity = np.mean(np.dot(embedding_array, source_array.T))
                    similarities.append(similarity)
            
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            logger.debug(f"Failed to calculate golden source similarity: {e}")
            return 0.0
    
    async def _update_developer_profile(self, 
                                      developer_id: str, 
                                      assessments: Dict[str, SkillAssessment],
                                      force_update: bool = False):
        """Update or create developer profile"""
        # Implementation placeholder - would integrate with storage system
        logger.debug(f"Updating profile for developer {developer_id}")
    
    async def _update_skill_timeline(self, 
                                   developer_id: str, 
                                   skill_name: str, 
                                   assessment: SkillAssessment):
        """Update skill progression timeline"""
        # Implementation placeholder - would track skill changes over time
        logger.debug(f"Updating skill timeline for {developer_id}: {skill_name}")
    
    async def _load_existing_data(self):
        """Load existing developer data from storage"""
        # Implementation placeholder - would load from persistent storage
        logger.debug("Loading existing developer data")
    
    async def _save_all_data(self):
        """Save all developer data to storage"""
        # Implementation placeholder - would save to persistent storage
        logger.debug("Saving developer data") 