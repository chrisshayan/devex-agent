"""
Search Engine - Handles semantic search across knowledge sources
"""

import logging
import time
from typing import Dict, List, Any, Optional

from ..core.models import (
    KnowledgeQuery, SearchResults, SearchResult, KnowledgeContext,
    EvaluationResult, PatternMatch, EvaluationRecommendation, DevelopmentContext,
    SourceType, Priority, RelationshipType
)

logger = logging.getLogger(__name__)

class SearchEngine:
    """
    Manages semantic search across knowledge sources
    
    Performs vector similarity search, enriches with graph relationships,
    and provides contextual knowledge for development workflows.
    """
    
    def __init__(self, vector_store=None, graph_store=None, relational_store=None):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.relational_store = relational_store
        self.is_initialized = False
        logger.info("🔍 SearchEngine initialized")
    
    async def initialize(self):
        """Initialize the search engine"""
        try:
            logger.info("🔄 Initializing Search Engine...")
            self.is_initialized = True
            logger.info("✅ Search Engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Search Engine: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup search engine resources"""
        logger.info("🧹 Cleaning up Search Engine...")
        self.is_initialized = False
        logger.info("✅ Search Engine cleanup complete")
    
    async def search(self, query: KnowledgeQuery) -> SearchResults:
        """Perform semantic search across knowledge sources"""
        start_time = time.time()
        logger.info(f"🔍 Searching for: '{query.query}' for {query.developer_id}")
        
        try:
            # Step 1: Vector similarity search across collections
            vector_results = await self._search_vector_store(query)
            
            # Step 2: Filter results by source constraints
            filtered_results = await self._filter_by_sources(vector_results, query)
            
            # Step 3: Enrich with graph relationships if requested
            if query.include_relationships:
                enriched_results = await self._enrich_with_relationships(filtered_results)
            else:
                enriched_results = filtered_results
            
            # Step 4: Apply context-based ranking
            ranked_results = await self._rank_by_context(enriched_results, query)
            
            # Step 5: Apply similarity threshold and limit results
            final_results = [
                r for r in ranked_results 
                if r.similarity_score >= query.similarity_threshold
            ][:query.max_results]
            
            execution_time = (time.time() - start_time) * 1000
            
            # Get list of sources that were searched
            sources_searched = list(set(r.source_id for r in final_results))
            
            search_results = SearchResults(
                query=query.query,
                results=final_results,
                total_results=len(final_results),
                execution_time_ms=execution_time,
                sources_searched=sources_searched,
                suggestions=await self._generate_search_suggestions(query, final_results)
            )
            
            logger.info(f"✅ Search completed: '{query.query}' - {len(final_results)} results in {execution_time:.1f}ms")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Search failed for '{query.query}': {e}")
            return SearchResults(
                query=query.query,
                results=[],
                total_results=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                sources_searched=[],
                suggestions=[],
                metadata={"error": str(e)}
            )
    
    async def _search_vector_store(self, query: KnowledgeQuery) -> List[SearchResult]:
        """Search the vector store for similar content"""
        if not self.vector_store:
            return []
        
        # Determine which collections to search
        if query.source_types:
            collection_types = self._map_source_types_to_collections(query.source_types)
        else:
            collection_types = ["code_chunks", "documentation", "patterns"]
        
        # Search across multiple collections
        all_results = []
        
        for collection_type in collection_types:
            try:
                # Build where filter
                where_filter = {}
                if query.source_ids:
                    where_filter["source_id"] = {"$in": query.source_ids}
                if query.language:
                    where_filter["language"] = query.language
                
                # Search this collection
                vector_results = await self.vector_store.search_similar(
                    query=query.query,
                    collection_type=collection_type,
                    limit=query.max_results * 2,  # Get more to allow for filtering
                    where_filter=where_filter if where_filter else None,
                    similarity_threshold=query.similarity_threshold * 0.8  # Lower threshold for initial search
                )
                
                # Convert to SearchResult objects
                for result in vector_results:
                    search_result = SearchResult(
                        id=result["id"],
                        source_id=result["metadata"].get("source_id", "unknown"),
                        source_type=self._infer_source_type(result["metadata"]),
                        title=result["metadata"].get("title", "Untitled"),
                        content=result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"],
                        url=result["metadata"].get("url"),
                        file_path=result["metadata"].get("file_path"),
                        similarity_score=result["similarity_score"],
                        metadata=result["metadata"],
                        relationships=[]  # Will be populated later if requested
                    )
                    all_results.append(search_result)
            
            except Exception as e:
                logger.warning(f"Failed to search collection {collection_type}: {e}")
                continue
        
        # Sort by similarity score
        all_results.sort(key=lambda r: r.similarity_score, reverse=True)
        
        return all_results
    
    def _map_source_types_to_collections(self, source_types: List[SourceType]) -> List[str]:
        """Map source types to vector store collection types"""
        type_mapping = {
            SourceType.GITHUB: ["code_chunks", "documentation"],
            SourceType.FILE: ["code_chunks", "documentation"],
            SourceType.CONFLUENCE: ["documentation"],
            SourceType.DEEPWIKI: ["documentation"],
            SourceType.MCP: ["documentation", "patterns"]
        }
        
        collections = set()
        for source_type in source_types:
            collections.update(type_mapping.get(source_type, ["documentation"]))
        
        return list(collections)
    
    def _infer_source_type(self, metadata: Dict[str, Any]) -> SourceType:
        """Infer source type from metadata"""
        source_type_str = metadata.get("source_type")
        if source_type_str:
            try:
                return SourceType(source_type_str)
            except ValueError:
                pass
        
        # Fallback inference based on other metadata
        if "github.com" in metadata.get("url", ""):
            return SourceType.GITHUB
        elif metadata.get("file_path"):
            return SourceType.FILE
        else:
            return SourceType.FILE  # Default fallback
    
    async def _filter_by_sources(self, results: List[SearchResult], query: KnowledgeQuery) -> List[SearchResult]:
        """Filter results by source constraints"""
        if not query.source_ids and not query.source_types:
            return results
        
        filtered = []
        for result in results:
            # Filter by specific source IDs
            if query.source_ids and result.source_id not in query.source_ids:
                continue
            
            # Filter by source types
            if query.source_types and result.source_type not in query.source_types:
                continue
            
            filtered.append(result)
        
        return filtered
    
    async def _enrich_with_relationships(self, results: List[SearchResult]) -> List[SearchResult]:
        """Enrich results with graph relationships"""
        if not self.graph_store:
            return results
        
        for result in results:
            try:
                # Get relationships for this entity
                relationships = await self.graph_store.get_relationships(
                    result.id,
                    relationship_types=["similar_to", "related_to", "depends_on"]
                )
                
                # Convert to the expected format
                result.relationships = [
                    {
                        "type": rel.get("relationship_type", "related_to"),
                        "target_id": rel.get("other_entity", {}).get("id", ""),
                        "target_title": rel.get("other_entity", {}).get("title", ""),
                        "strength": rel.get("strength", 0.5),
                        "description": rel.get("description", "")
                    }
                    for rel in relationships[:3]  # Limit to 3 relationships per result
                ]
            except Exception as e:
                logger.debug(f"Failed to get relationships for {result.id}: {e}")
                result.relationships = []
        
        return results
    
    async def _rank_by_context(self, results: List[SearchResult], query: KnowledgeQuery) -> List[SearchResult]:
        """Apply context-based ranking to results"""
        for result in results:
            context_boost = 0.0
            
            # Boost based on current file context
            if query.current_file and result.file_path:
                if query.current_file == result.file_path:
                    context_boost += 0.2  # Same file
                elif query.current_file.split('/')[-1] == result.file_path.split('/')[-1]:
                    context_boost += 0.1  # Same filename
            
            # Boost based on language context
            if query.language and result.metadata.get("language") == query.language:
                context_boost += 0.1
            
            # Boost based on project context
            if query.project_path and result.metadata.get("file_path", "").startswith(query.project_path):
                context_boost += 0.1
            
            # Apply boost (capped at 1.0)
            result.similarity_score = min(1.0, result.similarity_score + context_boost)
        
        # Re-sort by adjusted similarity score
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results
    
    async def _generate_search_suggestions(self, query: KnowledgeQuery, results: List[SearchResult]) -> List[str]:
        """Generate search suggestions based on results"""
        suggestions = []
        
        # Suggest related terms from results
        terms = set()
        for result in results[:5]:  # Analyze top 5 results
            # Extract potential terms from titles and metadata
            if result.title:
                terms.update(word.lower() for word in result.title.split() if len(word) > 3)
            
            language = result.metadata.get("language")
            if language:
                suggestions.append(f"language:{language}")
        
        # Add term-based suggestions
        for term in list(terms)[:3]:
            if term not in query.query.lower():
                suggestions.append(f"{query.query} {term}")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def get_contextual_knowledge(self, dev_context: DevelopmentContext, recent_changes=None) -> KnowledgeContext:
        """Get contextual knowledge for current development situation"""
        logger.info(f"🔍 Getting contextual knowledge for {dev_context.developer_id}")
        
        try:
            # Build context-aware search query
            context_query = await self._build_context_query(dev_context, recent_changes)
            
            # Search for relevant sources
            relevant_sources = await self._find_relevant_sources(dev_context)
            
            # Find similar patterns based on current context
            similar_patterns = await self._find_similar_patterns(dev_context)
            
            # Generate contextual recommendations
            recommendations = await self._generate_contextual_recommendations(dev_context, recent_changes)
            
            # Find related documentation
            related_docs = await self._find_related_documentation(dev_context)
            
            # Find historical examples
            historical_examples = await self._find_historical_examples(dev_context)
            
            # Calculate overall context relevance score
            context_score = self._calculate_context_score(
                relevant_sources, similar_patterns, related_docs
            )
            
            return KnowledgeContext(
                relevant_sources=relevant_sources,
                similar_patterns=similar_patterns,
                recommendations=recommendations,
                related_documentation=related_docs,
                historical_examples=historical_examples,
                context_score=context_score
            )
            
        except Exception as e:
            logger.error(f"Failed to get contextual knowledge: {e}")
            return KnowledgeContext(
                relevant_sources=[],
                similar_patterns=[],
                recommendations=[],
                related_documentation=[],
                historical_examples=[],
                context_score=0.0
            )
    
    async def _build_context_query(self, dev_context: DevelopmentContext, recent_changes=None) -> str:
        """Build a search query based on development context"""
        query_parts = []
        
        if dev_context.current_file:
            # Extract meaningful terms from file path
            file_name = dev_context.current_file.split('/')[-1].split('.')[0]
            query_parts.append(file_name)
        
        if dev_context.language:
            query_parts.append(dev_context.language)
        
        if recent_changes:
            # Extract terms from recent changes
            for change in recent_changes[:3]:
                description = change.get("description", "")
                if description:
                    # Extract key terms (simplified)
                    words = description.split()
                    query_parts.extend([w for w in words if len(w) > 4][:2])
        
        return " ".join(query_parts[:5])  # Limit query length
    
    async def _find_relevant_sources(self, dev_context: DevelopmentContext) -> List[str]:
        """Find source IDs relevant to the current context"""
        # This would query the relational store for sources related to the project/language
        if self.relational_store:
            try:
                sources = await self.relational_store.list_sources()
                relevant = []
                
                for source in sources:
                    if not source.enabled:
                        continue
                    
                    # Check if source is relevant to current context
                    if dev_context.language:
                        # Check if source config mentions the language
                        config_str = str(source.config).lower()
                        if dev_context.language.lower() in config_str:
                            relevant.append(source.id)
                    else:
                        # Include all enabled sources
                        relevant.append(source.id)
                
                return relevant[:10]  # Limit to 10 sources
            except Exception as e:
                logger.debug(f"Failed to get relevant sources: {e}")
        
        return []
    
    async def _find_similar_patterns(self, dev_context: DevelopmentContext) -> List[PatternMatch]:
        """Find code patterns similar to current context"""
        if not dev_context.current_file:
            return []
        
        # Search for patterns in the same language/context
        query = KnowledgeQuery(
            query=f"pattern {dev_context.language or 'code'}",
            language=dev_context.language,
            current_file=dev_context.current_file,
            max_results=5,
            similarity_threshold=0.6
        )
        
        search_results = await self.search(query)
        
        patterns = []
        for result in search_results.results:
            pattern = PatternMatch(
                pattern_id=result.id,
                pattern_name=result.title,
                source_id=result.source_id,
                source_reference=result.url or result.file_path or "",
                confidence=result.similarity_score,
                similarity_score=result.similarity_score,
                description=result.content[:200] + "..." if len(result.content) > 200 else result.content
            )
            patterns.append(pattern)
        
        return patterns
    
    async def _generate_contextual_recommendations(self, dev_context: DevelopmentContext, recent_changes=None) -> List[EvaluationRecommendation]:
        """Generate recommendations based on context"""
        recommendations = []
        
        # Language-specific recommendations
        if dev_context.language == "python":
            recommendations.append(EvaluationRecommendation(
                type="style",
                title="Follow PEP 8 style guidelines",
                description="Ensure code follows Python style guidelines for consistency",
                priority=Priority.LOW,
                source_reference="Python PEP 8"
            ))
        
        # File-based recommendations
        if dev_context.current_file:
            if "test" in dev_context.current_file.lower():
                recommendations.append(EvaluationRecommendation(
                    type="enhancement",
                    title="Comprehensive test coverage",
                    description="Ensure all edge cases and error conditions are tested",
                    priority=Priority.MEDIUM
                ))
        
        return recommendations
    
    async def _find_related_documentation(self, dev_context: DevelopmentContext) -> List[SearchResult]:
        """Find documentation related to current context"""
        if not dev_context.current_file and not dev_context.language:
            return []
        
        query = KnowledgeQuery(
            query=f"documentation {dev_context.language or ''} api guide",
            language=dev_context.language,
            source_types=[SourceType.GITHUB, SourceType.FILE, SourceType.CONFLUENCE],
            max_results=3,
            similarity_threshold=0.5
        )
        
        search_results = await self.search(query)
        return search_results.results
    
    async def _find_historical_examples(self, dev_context: DevelopmentContext) -> List[SearchResult]:
        """Find historical code examples relevant to context"""
        if not dev_context.language:
            return []
        
        query = KnowledgeQuery(
            query=f"example {dev_context.language} implementation",
            language=dev_context.language,
            source_types=[SourceType.GITHUB, SourceType.FILE],
            max_results=3,
            similarity_threshold=0.6
        )
        
        search_results = await self.search(query)
        return search_results.results
    
    def _calculate_context_score(self, relevant_sources: List[str], similar_patterns: List[PatternMatch], related_docs: List[SearchResult]) -> float:
        """Calculate overall context relevance score"""
        score = 0.0
        
        # Score based on number of relevant sources
        score += min(1.0, len(relevant_sources) / 5.0) * 0.3
        
        # Score based on pattern matches
        if similar_patterns:
            avg_pattern_score = sum(p.confidence for p in similar_patterns) / len(similar_patterns)
            score += avg_pattern_score * 0.4
        
        # Score based on documentation availability
        if related_docs:
            avg_doc_score = sum(d.similarity_score for d in related_docs) / len(related_docs)
            score += avg_doc_score * 0.3
        
        return min(1.0, score)
    
    async def evaluate_code(self, developer_id: str, code_content: str, file_path=None, language=None, context=None) -> EvaluationResult:
        """Evaluate code against golden sources"""
        logger.info(f"⚖️ Evaluating code for {developer_id}: {file_path}")
        
        from datetime import datetime
        import hashlib
        
        try:
            # Search for similar code patterns
            pattern_query = KnowledgeQuery(
                query=f"code pattern {language or 'example'}",
                language=language,
                max_results=10,
                similarity_threshold=0.5
            )
            
            pattern_results = await self.search(pattern_query)
            
            # Convert search results to pattern matches
            pattern_matches = []
            for result in pattern_results.results:
                pattern = PatternMatch(
                    pattern_id=result.id,
                    pattern_name=result.title,
                    source_id=result.source_id,
                    source_reference=result.url or result.file_path or "",
                    confidence=result.similarity_score,
                    similarity_score=result.similarity_score,
                    description=f"Similar pattern found in {result.source_id}"
                )
                pattern_matches.append(pattern)
            
            # Generate recommendations based on patterns found
            recommendations = []
            if pattern_matches:
                avg_similarity = sum(p.similarity_score for p in pattern_matches) / len(pattern_matches)
                if avg_similarity < 0.7:
                    recommendations.append(EvaluationRecommendation(
                        type="enhancement",
                        title="Consider following established patterns",
                        description="Found similar patterns in golden sources that might provide guidance",
                        priority=Priority.MEDIUM,
                        source_reference=pattern_matches[0].source_reference
                    ))
            
            # Calculate scores based on pattern alignment
            overall_alignment = sum(p.similarity_score for p in pattern_matches) / max(len(pattern_matches), 1)
            quality_score = min(1.0, overall_alignment + 0.2)  # Baseline quality bonus
            security_score = 0.8  # Default score - would be enhanced with actual security analysis
            maintainability_score = quality_score  # Correlate with quality for now
            
            # Generate evaluation ID
            eval_id = f"eval_{developer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return EvaluationResult(
                developer_id=developer_id,
                evaluation_id=eval_id,
                evaluated_at=datetime.now(),
                overall_alignment_score=overall_alignment,
                pattern_matches=pattern_matches,
                recommendations=recommendations,
                quality_score=quality_score,
                security_score=security_score,
                maintainability_score=maintainability_score,
                coverage_gaps=["No security-specific patterns found"] if not pattern_matches else [],
                metadata={
                    "file_path": file_path,
                    "language": language,
                    "code_length": len(code_content),
                    "patterns_analyzed": len(pattern_matches)
                }
            )
            
        except Exception as e:
            logger.error(f"Code evaluation failed: {e}")
            return EvaluationResult(
                developer_id=developer_id,
                evaluation_id=f"eval_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                evaluated_at=datetime.now(),
                overall_alignment_score=0.5,  # Neutral score on error
                pattern_matches=[],
                recommendations=[],
                quality_score=0.5,
                security_score=0.5,
                maintainability_score=0.5,
                coverage_gaps=["Evaluation failed"],
                metadata={"error": str(e)}
            ) 