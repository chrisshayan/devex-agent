"""
Knowledge Graph Service - Central orchestrator for all knowledge graph operations
"""

import asyncio
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .models import (
    GoldenSourceConfig, KnowledgeQuery, SearchResults, IngestionResult,
    EvaluationResult, KnowledgeContext, DevelopmentContext, IngestionJob,
    IngestionStatus, SourceType, Priority
)
from ..storage.vector_store import VectorStoreManager
from ..storage.graph_store import GraphStoreManager
from ..storage.relational_store import RelationalStoreManager
from ..engines.ingestion_engine import IngestionEngine
from ..engines.search_engine import SearchEngine
from ..engines.relationship_engine import RelationshipEngine
from ..connectors.factory import ConnectorFactory
from ...config.settings import get_settings

logger = logging.getLogger(__name__)

# Import ML capabilities
try:
    from ..ml.codebert_engine import CodeBERTEngine
    from ..ml.developer_intelligence import DeveloperIntelligenceEngine
    from ..ml.career_coach import ExpertCareerCoachLLM, CoachingContext
    from ..ml.learning_path_engine import LearningPathEngine
    from ..ml.progress_tracker import ProgressTracker
    from ..ml.models import (
        DeveloperSkillProfile, SkillAssessment, PatternAnalysis,
        CoachingSession, LearningPlan, CoachingTrigger, CareerStage,
        TimeAvailability, LearningStyle
    )
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML capabilities not available - CodeBERT features will be disabled")

class KnowledgeGraphService:
    """
    Central service for Knowledge Graph operations
    
    Provides a unified interface for managing golden sources, performing
    semantic search, evaluating code against patterns, and maintaining
    knowledge relationships.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.is_initialized = False
        
        # Storage managers
        self.vector_store: Optional[VectorStoreManager] = None
        self.graph_store: Optional[GraphStoreManager] = None
        self.relational_store: Optional[RelationalStoreManager] = None
        
        # Core engines
        self.ingestion_engine: Optional[IngestionEngine] = None
        self.search_engine: Optional[SearchEngine] = None
        self.relationship_engine: Optional[RelationshipEngine] = None
        
        # ML engines
        self.codebert_engine: Optional[CodeBERTEngine] = None
        self.developer_intelligence: Optional[DeveloperIntelligenceEngine] = None
        
        # Phase 2: Career coaching engines
        self.career_coach: Optional[ExpertCareerCoachLLM] = None
        self.learning_path_engine: Optional[LearningPathEngine] = None
        self.progress_tracker: Optional[ProgressTracker] = None
        
        # Connector factory
        self.connector_factory: Optional[ConnectorFactory] = None
        
        # Active ingestion jobs
        self.active_jobs: Dict[str, IngestionJob] = {}
    
    async def initialize(self):
        """Initialize the Knowledge Graph Service"""
        try:
            logger.info("🔄 Initializing Knowledge Graph Service...")
            
            # Initialize storage layers
            self.vector_store = VectorStoreManager()
            await self.vector_store.initialize()
            
            self.graph_store = GraphStoreManager()
            await self.graph_store.initialize()
            
            self.relational_store = RelationalStoreManager()
            await self.relational_store.initialize()
            
            # Initialize engines
            self.ingestion_engine = IngestionEngine(
                vector_store=self.vector_store,
                graph_store=self.graph_store,
                relational_store=self.relational_store
            )
            
            self.search_engine = SearchEngine(
                vector_store=self.vector_store,
                graph_store=self.graph_store,
                relational_store=self.relational_store
            )
            
            self.relationship_engine = RelationshipEngine(
                graph_store=self.graph_store,
                vector_store=self.vector_store
            )
            
            # Initialize connector factory
            self.connector_factory = ConnectorFactory()
            
            # Initialize ML engines if available
            if ML_AVAILABLE:
                logger.info("🤖 Initializing ML capabilities...")
                
                # Phase 1: CodeBERT and Developer Intelligence
                self.codebert_engine = CodeBERTEngine()
                await self.codebert_engine.initialize()
                
                self.developer_intelligence = DeveloperIntelligenceEngine(
                    codebert_engine=self.codebert_engine
                )
                await self.developer_intelligence.initialize()
                
                # Phase 2: Career Coaching Engines
                logger.info("🎯 Initializing Phase 2 Career Coaching engines...")
                
                # Initialize Career Coach with OpenAI API key
                openai_api_key = getattr(self.settings, 'openai_api_key', None)
                self.career_coach = ExpertCareerCoachLLM(
                    openai_api_key=openai_api_key,
                    model_name="gpt-4-turbo-preview",
                    temperature=0.7
                )
                await self.career_coach.initialize()
                
                # Initialize Learning Path Engine
                self.learning_path_engine = LearningPathEngine(
                    openai_api_key=openai_api_key,
                    use_llm_intelligence=True
                )
                await self.learning_path_engine.initialize()
                
                # Initialize Progress Tracker
                self.progress_tracker = ProgressTracker(
                    snapshot_retention_days=365,
                    velocity_calculation_window_days=30
                )
                await self.progress_tracker.initialize()
                
                logger.info("✅ ML capabilities and Career Coaching engines initialized successfully")
            else:
                logger.info("⚠️ ML capabilities not available - continuing without CodeBERT and Career Coaching")
            
            self.is_initialized = True
            logger.info("✅ Knowledge Graph Service initialized successfully")
            
        except Exception as e:
            logger.error(
            f"❌ Failed to initialize Knowledge Graph Service: {e}"
        )
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up Knowledge Graph Service...")
        
        # Cancel active jobs
        for job_id in list(self.active_jobs.keys()):
            await self.cancel_ingestion_job(job_id)
        
        # Cleanup ML engines
        if self.developer_intelligence:
            await self.developer_intelligence.cleanup()
        if self.codebert_engine:
            await self.codebert_engine.cleanup()
            
        # Cleanup Phase 2 engines
        if self.progress_tracker:
            await self.progress_tracker.cleanup()
        if self.learning_path_engine:
            await self.learning_path_engine.cleanup()
        if self.career_coach:
            await self.career_coach.cleanup()
        
        # Cleanup storage managers
        if self.vector_store:
            await self.vector_store.cleanup()
        if self.graph_store:
            await self.graph_store.cleanup()
        if self.relational_store:
            await self.relational_store.cleanup()
        
        self.is_initialized = False
        logger.info("✅ Knowledge Graph Service cleanup complete")
    
    # Golden Source Management
    
    async def register_golden_source(self, source_config: GoldenSourceConfig) -> str:
        """
        Register a new golden source for ingestion
        
        Args:
            source_config: Configuration for the golden source
            
        Returns:
            str: Unique source identifier
        """
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        # Generate ID if not provided
        if not source_config.id:
            source_config.id = f"{source_config.type.value}_{uuid.uuid4().hex[:8]}"
        
        # Set timestamps
        now = datetime.now()
        source_config.created_at = now
        source_config.updated_at = now
        
        # Validate source configuration
        await self._validate_source_config(source_config)
        
        # Store in relational database
        await self.relational_store.create_source(source_config)
        
        logger.info(f"📚 Registered golden source: {source_config.id} ({source_config.type.value})")
        
        # Trigger initial ingestion if auto_sync is enabled
        if source_config.auto_sync:
            await self.ingest_source(source_config.id)
        
        return source_config.id
    
    async def update_golden_source(self, source_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing golden source configuration"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        updates["updated_at"] = datetime.now()
        success = await self.relational_store.update_source(source_id, updates)
        
        if success:
            logger.info(f"📝 Updated golden source: {source_id}")
        
        return success
    
    async def remove_golden_source(self, source_id: str) -> bool:
        """Remove a golden source and all its data"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        # Cancel any active ingestion
        if source_id in self.active_jobs:
            await self.cancel_ingestion_job(self.active_jobs[source_id].id)
        
        # Remove from all storage layers
        await self.vector_store.remove_source_data(source_id)
        await self.graph_store.remove_source_data(source_id)
        success = await self.relational_store.delete_source(source_id)
        
        if success:
            logger.info(f"🗑️ Removed golden source: {source_id}")
        
        return success
    
    async def list_golden_sources(self) -> List[GoldenSourceConfig]:
        """List all registered golden sources"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        return await self.relational_store.list_sources()
    
    async def get_golden_source(self, source_id: str) -> Optional[GoldenSourceConfig]:
        """Get a specific golden source configuration"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        return await self.relational_store.get_source(source_id)
    
    # Ingestion Operations
    
    async def ingest_source(self, source_id: str, force: bool = False) -> IngestionResult:
        """
        Ingest content from a golden source
        
        Args:
            source_id: Source identifier
            force: Force re-ingestion even if recently synced
            
        Returns:
            IngestionResult: Result of the ingestion operation
        """
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        # Get source configuration
        source_config = await self.get_golden_source(source_id)
        if not source_config:
            raise ValueError(f"Golden source not found: {source_id}")
        
        if not source_config.enabled:
            raise ValueError(f"Golden source is disabled: {source_id}")
        
        # Check if already ingesting
        if source_id in [job.source_id for job in self.active_jobs.values()]:
            raise ValueError(f"Ingestion already in progress for source: {source_id}")
        
        # Check if we need to ingest (unless forced)
        if not force and source_config.auto_sync:
            last_sync = await self.relational_store.get_last_sync_time(source_id)
            if last_sync:
                sync_interval = self._parse_sync_interval(source_config.sync_interval)
                if datetime.now() - last_sync < sync_interval:
                    logger.info(f"⏭️ Skipping ingestion for {source_id} - too recent")
                    return IngestionResult(
                        job_id="skipped",
                        success=True,
                        items_ingested=0,
                        duration_seconds=0.0,
                        summary={"status": "skipped", "reason": "too_recent"}
                    )
        
        # Create ingestion job
        job_id = f"ingest_{source_id}_{uuid.uuid4().hex[:8]}"
        job = IngestionJob(
            id=job_id,
            source_id=source_id,
            status=IngestionStatus.PENDING,
            started_at=datetime.now()
        )
        
        self.active_jobs[job_id] = job
        
        try:
            # Update job status
            job.status = IngestionStatus.RUNNING
            await self.relational_store.create_ingestion_job(job)
            
            logger.info(f"🚀 Starting ingestion for source: {source_id}")
            
            # Get appropriate connector
            connector = self.connector_factory.create_connector(source_config)
            
            # Run ingestion
            result = await self.ingestion_engine.ingest_source(
                source_config=source_config,
                connector=connector,
                job=job
            )
            
            # Update job completion
            job.status = IngestionStatus.COMPLETED if result.success else IngestionStatus.FAILED
            job.completed_at = datetime.now()
            job.progress = 1.0
            job.items_processed = result.items_ingested
            
            if not result.success:
                job.error_message = result.error_message
            
            await self.relational_store.update_ingestion_job(job)
            
            # Update last sync time
            if result.success:
                await self.relational_store.update_last_sync_time(source_id, datetime.now())
            
            logger.info(f"✅ Ingestion completed for {source_id}: {result.items_ingested} items")
            
            return result
            
        except Exception as e:
            # Update job with error
            job.status = IngestionStatus.FAILED
            job.completed_at = datetime.now()
            job.error_message = str(e)
            await self.relational_store.update_ingestion_job(job)
            
            logger.error(f"❌ Ingestion failed for {source_id}: {e}")
            raise
        
        finally:
            # Remove from active jobs
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
    
    async def get_ingestion_status(self, job_id: str) -> Optional[IngestionJob]:
        """Get the status of an ingestion job"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        # Check active jobs first
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Check database
        return await self.relational_store.get_ingestion_job(job_id)
    
    async def cancel_ingestion_job(self, job_id: str) -> bool:
        """Cancel an active ingestion job"""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        job.status = IngestionStatus.CANCELLED
        job.completed_at = datetime.now()
        
        await self.relational_store.update_ingestion_job(job)
        del self.active_jobs[job_id]
        
        logger.info(f"🛑 Cancelled ingestion job: {job_id}")
        return True
    
    # Search Operations
    
    async def search_knowledge(self, query: KnowledgeQuery) -> SearchResults:
        """
        Search across all knowledge sources
        
        Args:
            query: Search query with context
            
        Returns:
            SearchResults: Search results with metadata
        """
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        logger.info(f"🔍 Searching knowledge: '{query.query}' for {query.developer_id}")
        
        return await self.search_engine.search(query)
    
    async def get_relevant_context(
        self,
        developer_id: str,
        current_file: Optional[str] = None,
        project_path: Optional[str] = None,
        language: Optional[str] = None,
        recent_changes: Optional[List[Dict[str, Any]]] = None
    ) -> KnowledgeContext:
        """
        Get relevant knowledge context for current development situation
        
        Args:
            developer_id: Developer identifier
            current_file: Currently edited file
            project_path: Current project path
            language: Programming language
            recent_changes: Recent code changes
            
        Returns:
            KnowledgeContext: Contextual knowledge and recommendations
        """
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        # Build development context
        dev_context = DevelopmentContext(
            developer_id=developer_id,
            current_file=current_file,
            project_path=project_path,
            language=language
        )
        
        # Get contextual knowledge
        return await self.search_engine.get_contextual_knowledge(dev_context, recent_changes)
    
    # Code Evaluation
    
    async def evaluate_code_against_golden_sources(
        self,
        developer_id: str,
        code_content: str,
        file_path: Optional[str] = None,
        language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate code changes against golden source patterns
        
        Args:
            developer_id: Developer identifier
            code_content: Code to evaluate
            file_path: File path of the code
            language: Programming language
            context: Additional context
            
        Returns:
            EvaluationResult: Evaluation results with recommendations
        """
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        logger.info(f"⚖️ Evaluating code for {developer_id}: {file_path}")
        
        return await self.search_engine.evaluate_code(
            developer_id=developer_id,
            code_content=code_content,
            file_path=file_path,
            language=language,
            context=context or {}
        )
    
    async def evaluate_against_golden_sources(
        self,
        developer_id: str,
        recent_changes: List[Dict[str, Any]],
        analysis_context: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Evaluate recent changes against golden sources (for workflow integration)
        
        Args:
            developer_id: Developer identifier
            recent_changes: List of recent file changes
            analysis_context: Code analysis context
            
        Returns:
            EvaluationResult: Comprehensive evaluation result
        """
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        # Combine all changes into evaluation context
        combined_content = ""
        file_paths = []
        
        for change in recent_changes:
            if change.get("type") == "file_changed":
                file_path = change.get("file_path", "")
                file_paths.append(file_path)
                combined_content += f"\n# File: {file_path}\n"
                # In a real implementation, we'd read the actual file content
                combined_content += change.get("description", "")
        
        # Perform evaluation
        return await self.evaluate_code_against_golden_sources(
            developer_id=developer_id,
            code_content=combined_content,
            file_path="; ".join(file_paths),
            context={
                "analysis_context": analysis_context,
                "change_count": len(recent_changes),
                "file_paths": file_paths
            }
        )
    
    # Relationship Operations
    
    async def discover_relationships(self, source_id: str) -> int:
        """Discover and create relationships for a source"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        return await self.relationship_engine.discover_relationships(source_id)
    
    async def get_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get relationships for an entity"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        return await self.relationship_engine.get_relationships(entity_id)
    
    # Analytics and Monitoring
    
    async def get_usage_analytics(self, developer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get usage analytics and statistics"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        return await self.relational_store.get_analytics(developer_id)
    
    async def get_source_health(self, source_id: str) -> Dict[str, Any]:
        """Get health status of a golden source"""
        if not self.is_initialized:
            raise RuntimeError("Knowledge Graph Service not initialized")
        
        source = await self.get_golden_source(source_id)
        if not source:
            return {"status": "not_found"}
        
        # Get last sync info
        last_sync = await self.relational_store.get_last_sync_time(source_id)
        
        # Get item counts
        item_count = await self.vector_store.get_source_item_count(source_id)
        
        # Calculate health score
        health_score = 1.0
        status = "healthy"
        
        if not source.enabled:
            status = "disabled"
            health_score = 0.0
        elif not last_sync:
            status = "never_synced"
            health_score = 0.0
        elif last_sync < datetime.now() - timedelta(days=7):
            status = "stale"
            health_score = 0.5
        
        return {
            "source_id": source_id,
            "status": status,
            "health_score": health_score,
            "last_sync": last_sync.isoformat() if last_sync else None,
            "item_count": item_count,
            "enabled": source.enabled,
            "auto_sync": source.auto_sync
        }
    
    # Private Helper Methods
    
    async def _validate_source_config(self, source_config: GoldenSourceConfig):
        """Validate source configuration"""
        # Test connection using appropriate connector
        connector = self.connector_factory.create_connector(source_config)
        await connector.validate_config(source_config.config)
    
    def _parse_sync_interval(self, interval: str) -> timedelta:
        """Parse sync interval string to timedelta"""
        import re
        match = re.match(r'^(\d+)([hdw])$', interval)
        if not match:
            return timedelta(hours=6)  # Default
        
        value, unit = match.groups()
        value = int(value)
        
        if unit == 'h':
            return timedelta(hours=value)
        elif unit == 'd':
            return timedelta(days=value)
        elif unit == 'w':
            return timedelta(weeks=value)
        
        return timedelta(hours=6)  # Default
    
    async def sync_all_sources(self):
        """Sync all auto-sync enabled sources"""
        if not self.is_initialized:
            return
        
        sources = await self.list_golden_sources()
        sync_tasks = []
        
        for source in sources:
            if source.enabled and source.auto_sync:
                # Check if sync is due
                last_sync = await self.relational_store.get_last_sync_time(source.id)
                sync_interval = self._parse_sync_interval(source.sync_interval)
                
                if not last_sync or datetime.now() - last_sync >= sync_interval:
                    task = asyncio.create_task(self.ingest_source(source.id))
                    sync_tasks.append(task)
        
        if sync_tasks:
            logger.info(f"🔄 Starting sync for {len(sync_tasks)} sources")
            await asyncio.gather(*sync_tasks, return_exceptions=True)
            logger.info("✅ Source sync completed")
    
    # ===== Phase 2: Career Coaching Methods =====
    
    async def generate_coaching_session(self,
                                      developer_id: str,
                                      current_skill_profile: Optional[DeveloperSkillProfile] = None,
                                      recent_pattern_analysis: Optional[PatternAnalysis] = None,
                                      current_code_context: Optional[Dict[str, Any]] = None,
                                      learning_goals: List[str] = None,
                                      time_availability: str = "medium",
                                      career_stage: CareerStage = CareerStage.MID,
                                      trigger_type: CoachingTrigger = CoachingTrigger.MORNING_BRIEF,
                                      specific_question: Optional[str] = None) -> Optional[CoachingSession]:
        """
        Generate a personalized coaching session using the Expert Career Coach LLM
        
        Args:
            developer_id: Developer identifier
            current_skill_profile: Current skill assessment
            recent_pattern_analysis: Recent code pattern analysis
            current_code_context: Current coding context
            learning_goals: Developer's learning goals
            time_availability: Available time for learning
            career_stage: Current career stage
            trigger_type: What triggered this coaching session
            specific_question: Optional specific question from developer
            
        Returns:
            CoachingSession: Generated coaching session or None if not available
        """
        if not ML_AVAILABLE or not self.career_coach:
            logger.warning("Career coaching not available - ML engines not initialized")
            return None
        
        logger.info(f"🎯 Generating coaching session for developer: {developer_id}")
        
        try:
            # Build coaching context
            context = CoachingContext(
                developer_id=developer_id,
                current_skill_profile=current_skill_profile,
                recent_pattern_analysis=recent_pattern_analysis,
                current_code_context=current_code_context,
                learning_goals=learning_goals or [],
                time_availability=time_availability,
                career_stage=career_stage,
                trigger_type=trigger_type
            )
            
            # Generate coaching session
            coaching_session = await self.career_coach.generate_coaching_session(
                context=context,
                specific_question=specific_question
            )
            
            logger.info(f"✅ Coaching session generated for {developer_id}")
            return coaching_session
            
        except Exception as e:
            logger.error(f"❌ Failed to generate coaching session: {e}")
            raise
    
    async def generate_learning_plan(self,
                                   developer_id: str,
                                   current_skills: Dict[str, SkillAssessment],
                                   target_skills: Dict[str, float],
                                   career_stage: CareerStage,
                                   time_availability: TimeAvailability,
                                   learning_style: LearningStyle,
                                   learning_goals: List[str],
                                   timeline_weeks: Optional[int] = None) -> Optional[LearningPlan]:
        """
        Generate a personalized learning plan using the Learning Path Engine
        
        Args:
            developer_id: Developer identifier
            current_skills: Current skill assessments
            target_skills: Target skill levels
            career_stage: Current career stage
            time_availability: Available time for learning
            learning_style: Preferred learning approach
            learning_goals: Specific learning goals
            timeline_weeks: Optional target timeline
            
        Returns:
            LearningPlan: Generated learning plan or None if not available
        """
        if not ML_AVAILABLE or not self.learning_path_engine:
            logger.warning("Learning path generation not available - ML engines not initialized")
            return None
        
        logger.info(f"📋 Generating learning plan for developer: {developer_id}")
        
        try:
            learning_plan = await self.learning_path_engine.generate_learning_plan(
                developer_id=developer_id,
                current_skills=current_skills,
                target_skills=target_skills,
                career_stage=career_stage,
                time_availability=time_availability,
                learning_style=learning_style,
                learning_goals=learning_goals,
                timeline_weeks=timeline_weeks
            )
            
            logger.info(f"✅ Learning plan generated for {developer_id}: {len(learning_plan.learning_path)} steps")
            return learning_plan
            
        except Exception as e:
            logger.error(f"❌ Failed to generate learning plan: {e}")
            raise
    
    async def track_progress_snapshot(self,
                                    developer_id: str,
                                    current_skills: Dict[str, SkillAssessment],
                                    learning_plan: Optional[LearningPlan] = None,
                                    completed_milestones: List[str] = None,
                                    notes: Optional[str] = None) -> Optional[Any]:
        """
        Record a progress snapshot for tracking developer learning progress
        
        Args:
            developer_id: Developer identifier
            current_skills: Current skill assessments
            learning_plan: Current learning plan
            completed_milestones: Recently completed milestone IDs
            notes: Optional progress notes
            
        Returns:
            ProgressSnapshot: Recorded snapshot or None if not available
        """
        if not ML_AVAILABLE or not self.progress_tracker:
            logger.warning("Progress tracking not available - ML engines not initialized")
            return None
        
        logger.info(f"📈 Recording progress snapshot for developer: {developer_id}")
        
        try:
            snapshot = await self.progress_tracker.record_progress_snapshot(
                developer_id=developer_id,
                current_skills=current_skills,
                learning_plan=learning_plan,
                completed_milestones=completed_milestones or [],
                notes=notes
            )
            
            logger.info(f"✅ Progress snapshot recorded for {developer_id}")
            return snapshot
            
        except Exception as e:
            logger.error(f"❌ Failed to record progress snapshot: {e}")
            raise
    
    async def analyze_learning_progress(self,
                                      developer_id: str,
                                      time_period_days: int = 90) -> Optional[Dict[str, Any]]:
        """
        Analyze learning progress trends for a developer
        
        Args:
            developer_id: Developer identifier
            time_period_days: Analysis time period in days
            
        Returns:
            Dict containing trend analysis or None if not available
        """
        if not ML_AVAILABLE or not self.progress_tracker:
            logger.warning("Progress analysis not available - ML engines not initialized")
            return None
        
        logger.info(f"📊 Analyzing learning progress for developer: {developer_id}")
        
        try:
            progress_analysis = await self.progress_tracker.analyze_progress_trends(
                developer_id=developer_id,
                time_period_days=time_period_days
            )
            
            logger.info(f"✅ Progress analysis completed for {developer_id}")
            return progress_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze learning progress: {e}")
            raise
    
    async def predict_learning_timeline(self,
                                      developer_id: str,
                                      target_skills: Dict[str, float],
                                      confidence_level: float = 0.8) -> Optional[Dict[str, Any]]:
        """
        Predict learning timeline for target skills based on current velocity
        
        Args:
            developer_id: Developer identifier
            target_skills: Target skill levels
            confidence_level: Prediction confidence level
            
        Returns:
            Dict containing timeline predictions or None if not available
        """
        if not ML_AVAILABLE or not self.progress_tracker:
            logger.warning("Timeline prediction not available - ML engines not initialized")
            return None
        
        logger.info(f"🔮 Predicting learning timeline for developer: {developer_id}")
        
        try:
            timeline_prediction = await self.progress_tracker.predict_learning_timeline(
                developer_id=developer_id,
                target_skills=target_skills,
                confidence_level=confidence_level
            )
            
            logger.info(f"✅ Timeline prediction completed for {developer_id}")
            return timeline_prediction
            
        except Exception as e:
            logger.error(f"❌ Failed to predict learning timeline: {e}")
            raise
    
    async def get_coaching_history(self, 
                                 developer_id: str, 
                                 limit: int = 10) -> Optional[List[CoachingSession]]:
        """
        Get coaching session history for a developer
        
        Args:
            developer_id: Developer identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of coaching sessions or None if not available
        """
        if not ML_AVAILABLE or not self.career_coach:
            logger.warning("Coaching history not available - ML engines not initialized")
            return None
        
        try:
            coaching_history = await self.career_coach.get_coaching_history(
                developer_id=developer_id,
                limit=limit
            )
            
            logger.info(f"📚 Retrieved {len(coaching_history)} coaching sessions for {developer_id}")
            return coaching_history
            
        except Exception as e:
            logger.error(f"❌ Failed to get coaching history: {e}")
            return None
    
    async def get_progress_alerts(self,
                                developer_id: str,
                                include_resolved: bool = False) -> Optional[List[Any]]:
        """
        Get progress alerts for a developer
        
        Args:
            developer_id: Developer identifier
            include_resolved: Include resolved alerts
            
        Returns:
            List of progress alerts or None if not available
        """
        if not ML_AVAILABLE or not self.progress_tracker:
            logger.warning("Progress alerts not available - ML engines not initialized")
            return None
        
        try:
            alerts = await self.progress_tracker.get_progress_alerts(
                developer_id=developer_id,
                include_resolved=include_resolved
            )
            
            logger.info(f"🚨 Retrieved {len(alerts)} progress alerts for {developer_id}")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Failed to get progress alerts: {e}")
            return None
    
    # ===== ML & Developer Intelligence Methods =====
    
    async def analyze_developer_code(self, 
                                   developer_id: str, 
                                   code_snippets: List[str],
                                   file_paths: List[str] = None) -> Optional[Any]:
        """
        Analyze developer's code patterns using CodeBERT
        
        Args:
            developer_id: Developer identifier
            code_snippets: List of code snippets to analyze
            file_paths: Optional file paths for context
            
        Returns:
            Pattern analysis results or None if ML not available
        """
        if not ML_AVAILABLE or not self.developer_intelligence:
            logger.warning("ML capabilities not available for code analysis")
            return None
        
        logger.info(f"🔍 Analyzing code patterns for developer: {developer_id}")
        
        try:
            pattern_analysis = await self.developer_intelligence.analyze_developer_code(
                developer_id=developer_id,
                code_snippets=code_snippets,
                file_paths=file_paths or []
            )
            
            logger.info(f"✅ Code analysis completed for {developer_id}")
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze developer code: {e}")
            raise
    
    async def assess_developer_skills(self, 
                                    developer_id: str, 
                                    code_snippets: List[str]) -> Optional[Dict[str, Any]]:
        """
        Assess developer skills using CodeBERT analysis
        
        Args:
            developer_id: Developer identifier
            code_snippets: Recent code snippets for analysis
            
        Returns:
            Dictionary of skill assessments or None if ML not available
        """
        if not ML_AVAILABLE or not self.developer_intelligence:
            logger.warning("ML capabilities not available for skill assessment")
            return None
        
        logger.info(f"📏 Assessing skills for developer: {developer_id}")
        
        try:
            skill_assessments = await self.developer_intelligence.assess_developer_skills(
                developer_id=developer_id,
                code_snippets=code_snippets
            )
            
            logger.info(f"✅ Skill assessment completed for {developer_id}")
            return skill_assessments
            
        except Exception as e:
            logger.error(f"❌ Failed to assess developer skills: {e}")
            raise
    
    async def find_similar_code_patterns(self, 
                                       query_code: str, 
                                       developer_id: str = None,
                                       threshold: float = 0.7) -> Optional[List[Dict[str, Any]]]:
        """
        Find similar code patterns using CodeBERT semantic similarity
        
        Args:
            query_code: Code to find similarities for
            developer_id: Optional developer context
            threshold: Similarity threshold
            
        Returns:
            List of similar code patterns or None if ML not available
        """
        if not ML_AVAILABLE or not self.codebert_engine:
            logger.warning("ML capabilities not available for similarity search")
            return None
        
        logger.info("🔍 Finding similar code patterns using CodeBERT")
        
        try:
            # Get code from knowledge base (simplified - would query vector store)
            # For now, provide some sample candidate codes to avoid empty array issues
            candidate_codes = [
                "const [state, setState] = useState(null)",
                "useEffect(() => { fetchData() }, [])",
                "interface Props { id: string; name: string }",
                "async function fetchData() { try { const response = await fetch() } catch (e) {} }",
                "const Component = React.memo(({ props }) => { return <div>{props}</div> })"
            ]
            
            # Only proceed if we have candidate codes
            if not candidate_codes:
                logger.info("No candidate codes available for similarity comparison")
                return []
            
            similar_patterns = await self.codebert_engine.find_similar_code(
                query_code=query_code,
                candidate_codes=candidate_codes,
                threshold=threshold
            )
            
            logger.info(f"✅ Found {len(similar_patterns)} similar code patterns")
            return similar_patterns
            
        except Exception as e:
            logger.error(f"❌ Failed to find similar code patterns: {e}")
            return []
    
    async def generate_code_embeddings(self, code_snippets: List[str]) -> Optional[List[List[float]]]:
        """
        Generate CodeBERT embeddings for code snippets
        
        Args:
            code_snippets: List of code snippets
            
        Returns:
            List of embedding vectors or None if ML not available
        """
        if not ML_AVAILABLE or not self.codebert_engine:
            logger.warning("ML capabilities not available for embedding generation")
            return None
        
        logger.info(f"🔮 Generating CodeBERT embeddings for {len(code_snippets)} snippets")
        
        try:
            embeddings = await self.codebert_engine.generate_embeddings(code_snippets)
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to generate code embeddings: {e}")
            raise 