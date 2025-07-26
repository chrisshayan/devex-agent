"""
Relationship Engine - Advanced relationship discovery and pattern detection
"""

import logging
import re
import ast
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict, deque
import math

from ..core.models import RelationshipType, KnowledgeRelationship
from ..utils.performance import cached, timed, run_parallel, run_batch_parallel

logger = logging.getLogger(__name__)

class RelationshipEngine:
    """
    Advanced relationship discovery engine using graph algorithms
    
    Discovers and analyzes relationships between knowledge entities using:
    - Pattern detection algorithms
    - Semantic similarity analysis
    - Graph traversal and centrality algorithms
    - Code dependency analysis
    - Cross-reference discovery
    """
    
    def __init__(self, graph_store=None, vector_store=None):
        self.graph_store = graph_store
        self.vector_store = vector_store
        self.is_initialized = False
        
        # Analysis caches for performance
        self.similarity_cache = {}
        self.pattern_cache = {}
        self.dependency_cache = {}
        
        # Algorithm thresholds
        self.similarity_threshold = 0.7
        self.pattern_threshold = 0.6
        self.dependency_confidence_threshold = 0.5
        
        logger.info("🔗 RelationshipEngine initialized with advanced algorithms")
    
    async def initialize(self):
        """Initialize the relationship engine"""
        try:
            logger.info("🔄 Initializing Relationship Engine with graph algorithms...")
            self.is_initialized = True
            logger.info("✅ Relationship Engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Relationship Engine: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup relationship engine resources"""
        logger.info("🧹 Cleaning up Relationship Engine...")
        
        # Clear caches
        self.similarity_cache.clear()
        self.pattern_cache.clear()
        self.dependency_cache.clear()
        
        self.is_initialized = False
        logger.info("✅ Relationship Engine cleanup complete")
    
    @timed(operation_name="relationship_discovery")
    async def discover_relationships(self, source_id: str) -> int:
        """
        Discover relationships for all entities in a source using advanced algorithms
        
        Args:
            source_id: Source identifier to analyze
            
        Returns:
            int: Number of relationships discovered
        """
        if not self.is_initialized:
            raise RuntimeError("Relationship Engine not initialized")
        
        logger.info(f"🕸️ Starting parallel relationship discovery for source: {source_id}")
        
        try:
            # Get all entities for this source
            entities = await self._get_source_entities(source_id)
            if not entities:
                logger.info(f"No entities found for source: {source_id}")
                return 0
            
            logger.info(f"📊 Analyzing {len(entities)} entities for relationships using parallel processing")
            
            # Run all relationship discovery algorithms in parallel
            discovery_tasks = [
                self._discover_code_dependencies(entities, source_id),
                self._discover_semantic_similarities(entities, source_id),
                self._discover_design_patterns(entities, source_id),
                self._discover_cross_references(entities, source_id),
                self._discover_hierarchical_relationships(entities, source_id),
                self._discover_temporal_relationships(entities, source_id)
            ]
            
            logger.info("🚀 Running 6 relationship discovery algorithms in parallel...")
            relationship_results = await run_parallel(discovery_tasks, max_concurrency=6)
            
            # Flatten and store all discovered relationships
            all_relationships = []
            relationships_found = 0
            
            for relationships in relationship_results:
                all_relationships.extend(relationships)
                relationships_found += len(relationships)
            
            # Store relationships in parallel batches
            if all_relationships:
                logger.info(f"💾 Storing {len(all_relationships)} relationships in parallel batches...")
                
                async def store_relationship(relationship):
                    return await self.graph_store.store_relationship(relationship)
                
                await run_batch_parallel(
                    all_relationships, 
                    store_relationship, 
                    batch_size=20  # Process 20 relationships per batch
                )
            
            # Run graph analysis algorithms for additional insights
            await self._run_graph_analysis(source_id)
            
            logger.info(f"✅ Parallel relationship discovery completed for {source_id}: {relationships_found} relationships found")
            
        except Exception as e:
            logger.error(f"❌ Relationship discovery failed for {source_id}: {e}")
            raise
        
        return relationships_found
    
    async def _get_source_entities(self, source_id: str) -> List[Dict[str, Any]]:
        """Get all entities for a source from the graph store"""
        try:
            # This would query the graph store for all entities with the given source_id
            if hasattr(self.graph_store, 'get_entities_by_source'):
                return await self.graph_store.get_entities_by_source(source_id)
            else:
                # Fallback: get from in-memory store
                entities = []
                if hasattr(self.graph_store, 'source_entities'):
                    entity_ids = self.graph_store.source_entities.get(source_id, set())
                    for entity_id in entity_ids:
                        entity = await self.graph_store.get_entity(entity_id)
                        if entity:
                            entities.append(entity)
                return entities
        except Exception as e:
            logger.warning(f"Failed to get entities for source {source_id}: {e}")
            return []
    
    async def _discover_code_dependencies(self, entities: List[Dict[str, Any]], source_id: str) -> List[Dict[str, Any]]:
        """Discover code dependencies using AST analysis and import detection"""
        logger.info("🔍 Discovering code dependencies...")
        
        relationships = []
        code_entities = [e for e in entities if e.get('entity_type') in ['code_file', 'function', 'class']]
        
        for entity in code_entities:
            try:
                content = entity.get('properties', {}).get('content', '')
                file_path = entity.get('properties', {}).get('file_path', '')
                
                if not content:
                    continue
                
                # Detect programming language
                language = self._detect_language(file_path)
                
                # Extract dependencies based on language
                dependencies = await self._extract_dependencies(content, language, file_path)
                
                for dep in dependencies:
                    # Find matching entities
                    target_entities = await self._find_dependency_targets(dep, entities)
                    
                    for target in target_entities:
                        relationship = {
                            'id': f"dep_{entity['id']}_{target['id']}_{hashlib.md5(dep['name'].encode()).hexdigest()[:8]}",
                            'source_entity_id': entity['id'],
                            'target_entity_id': target['id'],
                            'relationship_type': RelationshipType.DEPENDS_ON,
                            'strength': dep['confidence'],
                            'confidence': dep['confidence'],
                            'description': f"Code dependency: {dep['type']} '{dep['name']}'",
                            'metadata': {
                                'dependency_type': dep['type'],
                                'dependency_name': dep['name'],
                                'language': language,
                                'source_line': dep.get('line_number'),
                                'source_path': file_path
                            },
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        }
                        relationships.append(relationship)
                        
            except Exception as e:
                logger.debug(f"Failed to analyze dependencies for entity {entity.get('id')}: {e}")
                continue
        
        logger.info(f"🔗 Found {len(relationships)} code dependency relationships")
        return relationships
    
    async def _extract_dependencies(self, content: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract dependencies from code content based on language"""
        dependencies = []
        
        try:
            if language == 'python':
                dependencies.extend(self._extract_python_dependencies(content))
            elif language in ['javascript', 'typescript']:
                dependencies.extend(self._extract_js_dependencies(content))
            elif language == 'java':
                dependencies.extend(self._extract_java_dependencies(content))
            elif language in ['cpp', 'c']:
                dependencies.extend(self._extract_c_dependencies(content))
            
            # Add generic patterns for all languages
            dependencies.extend(self._extract_generic_dependencies(content, language))
            
        except Exception as e:
            logger.debug(f"Failed to extract dependencies from {file_path}: {e}")
        
        return dependencies
    
    def _extract_python_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract Python import dependencies"""
        dependencies = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append({
                            'type': 'import',
                            'name': alias.name,
                            'confidence': 0.9,
                            'line_number': node.lineno
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        full_name = f"{module}.{alias.name}" if module else alias.name
                        dependencies.append({
                            'type': 'from_import',
                            'name': full_name,
                            'confidence': 0.9,
                            'line_number': node.lineno
                        })
                
                elif isinstance(node, ast.FunctionDef):
                    # Function calls within the function
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            dependencies.append({
                                'type': 'function_call',
                                'name': child.func.id,
                                'confidence': 0.7,
                                'line_number': child.lineno
                            })
        
        except SyntaxError:
            # Fallback to regex-based extraction for malformed Python
            import_patterns = [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import',
            ]
            
            for pattern in import_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    dependencies.append({
                        'type': 'import',
                        'name': match.group(1),
                        'confidence': 0.6,
                        'line_number': content[:match.start()].count('\n') + 1
                    })
        
        return dependencies
    
    def _extract_js_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract JavaScript/TypeScript dependencies"""
        dependencies = []
        
        # Import patterns
        patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                dependencies.append({
                    'type': 'import',
                    'name': match.group(1),
                    'confidence': 0.8,
                    'line_number': content[:match.start()].count('\n') + 1
                })
        
        return dependencies
    
    def _extract_java_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract Java import dependencies"""
        dependencies = []
        
        patterns = [
            r'import\s+(?:static\s+)?([a-zA-Z_][a-zA-Z0-9_\.\*]*);',
            r'package\s+([a-zA-Z_][a-zA-Z0-9_\.]*);',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                dep_type = 'package' if 'package' in pattern else 'import'
                dependencies.append({
                    'type': dep_type,
                    'name': match.group(1),
                    'confidence': 0.8,
                    'line_number': content[:match.start()].count('\n') + 1
                })
        
        return dependencies
    
    def _extract_c_dependencies(self, content: str) -> List[Dict[str, Any]]:
        """Extract C/C++ include dependencies"""
        dependencies = []
        
        patterns = [
            r'#include\s*<([^>]+)>',
            r'#include\s*"([^"]+)"',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                dependencies.append({
                    'type': 'include',
                    'name': match.group(1),
                    'confidence': 0.8,
                    'line_number': content[:match.start()].count('\n') + 1
                })
        
        return dependencies
    
    def _extract_generic_dependencies(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract generic dependencies using common patterns"""
        dependencies = []
        
        # Function/method calls
        function_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches = re.finditer(function_pattern, content)
        
        function_calls = {}
        for match in matches:
            func_name = match.group(1)
            if len(func_name) > 2:  # Ignore very short names
                function_calls[func_name] = function_calls.get(func_name, 0) + 1
        
        # Only include frequently called functions
        for func_name, count in function_calls.items():
            if count >= 2:  # Called at least twice
                dependencies.append({
                    'type': 'function_reference',
                    'name': func_name,
                    'confidence': min(0.8, 0.3 + (count * 0.1)),
                    'call_count': count
                })
        
        return dependencies
    
    async def _find_dependency_targets(self, dependency: Dict[str, Any], entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find entities that match a dependency"""
        targets = []
        dep_name = dependency['name'].lower()
        
        for entity in entities:
            entity_properties = entity.get('properties', {})
            
            # Check file path matches
            file_path = entity_properties.get('file_path', '').lower()
            if dep_name in file_path or file_path.replace('/', '.').replace('\\', '.') in dep_name:
                targets.append(entity)
                continue
            
            # Check title matches
            title = entity_properties.get('title', '').lower()
            if dep_name in title or title in dep_name:
                targets.append(entity)
                continue
            
            # Check content for class/function definitions
            content = entity_properties.get('content', '')
            if self._contains_definition(content, dep_name):
                targets.append(entity)
        
        return targets
    
    def _contains_definition(self, content: str, name: str) -> bool:
        """Check if content contains definition of a name"""
        patterns = [
            rf'class\s+{re.escape(name)}\s*[:\(]',
            rf'def\s+{re.escape(name)}\s*\(',
            rf'function\s+{re.escape(name)}\s*\(',
            rf'{re.escape(name)}\s*=\s*function',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    async def _discover_semantic_similarities(self, entities: List[Dict[str, Any]], source_id: str) -> List[Dict[str, Any]]:
        """Discover semantic similarities using vector embeddings"""
        logger.info("🔍 Discovering semantic similarities...")
        
        relationships = []
        
        try:
            # Get embeddings for all entities
            entity_vectors = await self._get_entity_embeddings(entities)
            
            # Compare all pairs of entities
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities[i+1:], i+1):
                    if entity1['id'] == entity2['id']:
                        continue
                    
                    # Calculate similarity
                    similarity = await self._calculate_semantic_similarity(
                        entity1, entity2, entity_vectors
                    )
                    
                    if similarity >= self.similarity_threshold:
                        relationship = {
                            'id': f"sim_{entity1['id']}_{entity2['id']}_{int(similarity*100)}",
                            'source_entity_id': entity1['id'],
                            'target_entity_id': entity2['id'],
                            'relationship_type': RelationshipType.SIMILAR_TO,
                            'strength': similarity,
                            'confidence': similarity,
                            'description': f"Semantically similar content (similarity: {similarity:.2f})",
                            'metadata': {
                                'similarity_score': similarity,
                                'similarity_type': 'semantic',
                                'algorithm': 'vector_cosine'
                            },
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        }
                        relationships.append(relationship)
                        
        except Exception as e:
            logger.warning(f"Failed to discover semantic similarities: {e}")
        
        logger.info(f"🔗 Found {len(relationships)} semantic similarity relationships")
        return relationships
    
    async def _get_entity_embeddings(self, entities: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Get or compute embeddings for entities"""
        embeddings = {}
        
        if not self.vector_store:
            return embeddings
        
        try:
            # Get embeddings from vector store if available
            for entity in entities:
                entity_id = entity['id']
                
                # Try to get from vector store
                vector_doc = await self.vector_store.get_document(entity_id)
                if vector_doc and 'embedding' in vector_doc:
                    embeddings[entity_id] = vector_doc['embedding']
                else:
                    # Generate embedding for content
                    content = entity.get('properties', {}).get('content', '')
                    if content:
                        # Use the vector store's embedding function
                        embedding = self.vector_store._generate_embeddings([content[:1000]])[0]
                        embeddings[entity_id] = embedding
                        
        except Exception as e:
            logger.debug(f"Failed to get embeddings: {e}")
        
        return embeddings
    
    async def _calculate_semantic_similarity(
        self, 
        entity1: Dict[str, Any], 
        entity2: Dict[str, Any], 
        entity_vectors: Dict[str, List[float]]
    ) -> float:
        """Calculate semantic similarity between two entities"""
        
        # Try vector similarity first
        if entity1['id'] in entity_vectors and entity2['id'] in entity_vectors:
            return self._cosine_similarity(
                entity_vectors[entity1['id']], 
                entity_vectors[entity2['id']]
            )
        
        # Fallback to text-based similarity
        content1 = entity1.get('properties', {}).get('content', '')
        content2 = entity2.get('properties', {}).get('content', '')
        
        if not content1 or not content2:
            return 0.0
        
        # Simple text similarity (Jaccard)
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def _discover_design_patterns(self, entities: List[Dict[str, Any]], source_id: str) -> List[Dict[str, Any]]:
        """Discover design patterns and architectural patterns"""
        logger.info("🔍 Discovering design patterns...")
        
        relationships = []
        
        # Define pattern signatures
        patterns = {
            'singleton': {
                'signatures': ['__new__', 'getInstance', 'instance', 'private constructor'],
                'description': 'Singleton pattern implementation'
            },
            'factory': {
                'signatures': ['create', 'factory', 'builder', 'make'],
                'description': 'Factory pattern implementation'
            },
            'observer': {
                'signatures': ['observer', 'notify', 'subscribe', 'listener', 'event'],
                'description': 'Observer pattern implementation'
            },
            'strategy': {
                'signatures': ['strategy', 'algorithm', 'execute', 'perform'],
                'description': 'Strategy pattern implementation'
            },
            'decorator': {
                'signatures': ['decorator', 'wrapper', 'wrap', '@'],
                'description': 'Decorator pattern implementation'
            }
        }
        
        # Analyze each entity for patterns
        for entity in entities:
            content = entity.get('properties', {}).get('content', '').lower()
            title = entity.get('properties', {}).get('title', '').lower()
            
            if not content:
                continue
            
            entity_patterns = []
            
            for pattern_name, pattern_info in patterns.items():
                score = 0
                matches = []
                
                for signature in pattern_info['signatures']:
                    if signature in content or signature in title:
                        score += 1
                        matches.append(signature)
                
                # Calculate confidence based on matches
                confidence = min(1.0, score / len(pattern_info['signatures']) * 2)
                
                if confidence >= self.pattern_threshold:
                    entity_patterns.append({
                        'pattern': pattern_name,
                        'confidence': confidence,
                        'matches': matches,
                        'description': pattern_info['description']
                    })
            
            # Create relationships between entities implementing the same pattern
            for pattern_info in entity_patterns:
                pattern_entities = await self._find_pattern_implementations(
                    pattern_info['pattern'], entities, patterns
                )
                
                for target_entity in pattern_entities:
                    if target_entity['id'] != entity['id']:
                        relationship = {
                            'id': f"pattern_{pattern_info['pattern']}_{entity['id']}_{target_entity['id']}",
                            'source_entity_id': entity['id'],
                            'target_entity_id': target_entity['id'],
                            'relationship_type': RelationshipType.IMPLEMENTS,
                            'strength': pattern_info['confidence'],
                            'confidence': pattern_info['confidence'],
                            'description': f"Both implement {pattern_info['pattern']} pattern",
                            'metadata': {
                                'pattern_type': pattern_info['pattern'],
                                'pattern_matches': pattern_info['matches'],
                                'pattern_description': pattern_info['description']
                            },
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        }
                        relationships.append(relationship)
        
        logger.info(f"🔗 Found {len(relationships)} design pattern relationships")
        return relationships
    
    async def _find_pattern_implementations(
        self, 
        pattern_name: str, 
        entities: List[Dict[str, Any]], 
        patterns: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find all entities that implement a specific pattern"""
        implementations = []
        pattern_info = patterns.get(pattern_name, {})
        signatures = pattern_info.get('signatures', [])
        
        for entity in entities:
            content = entity.get('properties', {}).get('content', '').lower()
            title = entity.get('properties', {}).get('title', '').lower()
            
            score = sum(1 for sig in signatures if sig in content or sig in title)
            confidence = score / len(signatures) if signatures else 0
            
            if confidence >= self.pattern_threshold:
                implementations.append(entity)
        
        return implementations
    
    async def _discover_cross_references(self, entities: List[Dict[str, Any]], source_id: str) -> List[Dict[str, Any]]:
        """Discover cross-references between different types of content"""
        logger.info("🔍 Discovering cross-references...")
        
        relationships = []
        
        # Group entities by type
        code_entities = [e for e in entities if e.get('entity_type') in ['code_file', 'function', 'class']]
        doc_entities = [e for e in entities if e.get('entity_type') in ['documentation', 'readme']]
        issue_entities = [e for e in entities if e.get('entity_type') == 'issue']
        pr_entities = [e for e in entities if e.get('entity_type') == 'pull_request']
        
        # Documentation to code references
        for doc in doc_entities:
            doc_content = doc.get('properties', {}).get('content', '')
            
            for code in code_entities:
                file_path = code.get('properties', {}).get('file_path', '')
                title = code.get('properties', {}).get('title', '')
                
                # Check if documentation mentions the code file
                if file_path and (file_path in doc_content or title in doc_content):
                    relationship = {
                        'id': f"docref_{doc['id']}_{code['id']}",
                        'source_entity_id': doc['id'],
                        'target_entity_id': code['id'],
                        'relationship_type': RelationshipType.RELATED_TO,
                        'strength': 0.8,
                        'confidence': 0.8,
                        'description': f"Documentation references code file",
                        'metadata': {
                            'reference_type': 'doc_to_code',
                            'mentioned_file': file_path
                        },
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                    relationships.append(relationship)
        
        # Issue to code references
        for issue in issue_entities:
            issue_content = issue.get('properties', {}).get('content', '')
            
            for code in code_entities:
                file_path = code.get('properties', {}).get('file_path', '')
                
                if file_path and file_path in issue_content:
                    relationship = {
                        'id': f"issueref_{issue['id']}_{code['id']}",
                        'source_entity_id': issue['id'],
                        'target_entity_id': code['id'],
                        'relationship_type': RelationshipType.RELATED_TO,
                        'strength': 0.9,
                        'confidence': 0.9,
                        'description': f"Issue mentions code file",
                        'metadata': {
                            'reference_type': 'issue_to_code',
                            'mentioned_file': file_path
                        },
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                    relationships.append(relationship)
        
        logger.info(f"🔗 Found {len(relationships)} cross-reference relationships")
        return relationships
    
    async def _discover_hierarchical_relationships(self, entities: List[Dict[str, Any]], source_id: str) -> List[Dict[str, Any]]:
        """Discover hierarchical relationships (inheritance, composition, etc.)"""
        logger.info("🔍 Discovering hierarchical relationships...")
        
        relationships = []
        
        for entity in entities:
            content = entity.get('properties', {}).get('content', '')
            language = entity.get('properties', {}).get('language', '')
            
            if not content:
                continue
            
            # Find inheritance relationships
            inherits = await self._find_inheritance_relationships(content, language, entities)
            for parent_entity in inherits:
                relationship = {
                    'id': f"inherits_{entity['id']}_{parent_entity['id']}",
                    'source_entity_id': entity['id'],
                    'target_entity_id': parent_entity['id'],
                    'relationship_type': RelationshipType.INHERITS_FROM,
                    'strength': 0.9,
                    'confidence': 0.9,
                    'description': f"Inherits from parent class/interface",
                    'metadata': {
                        'hierarchy_type': 'inheritance',
                        'language': language
                    },
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                relationships.append(relationship)
        
        logger.info(f"🔗 Found {len(relationships)} hierarchical relationships")
        return relationships
    
    async def _find_inheritance_relationships(
        self, 
        content: str, 
        language: str, 
        entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find inheritance relationships in code"""
        parents = []
        
        if language == 'python':
            # Find class definitions with inheritance
            class_pattern = r'class\s+\w+\s*\(\s*([^)]+)\s*\):'
            matches = re.finditer(class_pattern, content)
            
            for match in matches:
                parent_classes = [p.strip() for p in match.group(1).split(',')]
                for parent_class in parent_classes:
                    # Find entity with this parent class
                    for entity in entities:
                        entity_title = entity.get('properties', {}).get('title', '')
                        if parent_class in entity_title:
                            parents.append(entity)
        
        elif language == 'java':
            # Find class inheritance and interface implementation
            patterns = [
                r'class\s+\w+\s+extends\s+(\w+)',
                r'class\s+\w+\s+implements\s+([^{]+)',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    parent_name = match.group(1).strip()
                    for entity in entities:
                        entity_title = entity.get('properties', {}).get('title', '')
                        if parent_name in entity_title:
                            parents.append(entity)
        
        return parents
    
    async def _discover_temporal_relationships(self, entities: List[Dict[str, Any]], source_id: str) -> List[Dict[str, Any]]:
        """Discover temporal relationships (evolution, versioning)"""
        logger.info("🔍 Discovering temporal relationships...")
        
        relationships = []
        
        # Group entities by similarity and check for evolution
        similar_entities = defaultdict(list)
        
        for entity in entities:
            file_path = entity.get('properties', {}).get('file_path', '')
            if file_path:
                base_name = file_path.split('/')[-1].split('.')[0]
                similar_entities[base_name].append(entity)
        
        # Find superseding relationships
        for base_name, entity_group in similar_entities.items():
            if len(entity_group) < 2:
                continue
            
            # Sort by some temporal indicator (file modification time, version, etc.)
            sorted_entities = sorted(
                entity_group, 
                key=lambda e: e.get('properties', {}).get('modified_time', ''),
                reverse=True
            )
            
            # Create superseding relationships
            for i in range(len(sorted_entities) - 1):
                newer = sorted_entities[i]
                older = sorted_entities[i + 1]
                
                relationship = {
                    'id': f"supersedes_{newer['id']}_{older['id']}",
                    'source_entity_id': newer['id'],
                    'target_entity_id': older['id'],
                    'relationship_type': RelationshipType.SUPERSEDES,
                    'strength': 0.8,
                    'confidence': 0.7,
                    'description': f"Newer version supersedes older version",
                    'metadata': {
                        'temporal_type': 'version_evolution',
                        'base_name': base_name
                    },
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                relationships.append(relationship)
        
        logger.info(f"🔗 Found {len(relationships)} temporal relationships")
        return relationships
    
    async def _run_graph_analysis(self, source_id: str):
        """Run graph analysis algorithms for additional insights"""
        logger.info("📊 Running graph analysis algorithms...")
        
        try:
            # Get all relationships for this source
            relationships = await self._get_source_relationships(source_id)
            
            if not relationships:
                return
            
            # Build adjacency graph
            graph = self._build_adjacency_graph(relationships)
            
            # Run centrality analysis
            centrality_scores = self._calculate_centrality(graph)
            
            # Find communities/clusters
            communities = self._detect_communities(graph)
            
            # Store analysis results as metadata
            await self._store_graph_analysis_results(source_id, {
                'centrality_scores': centrality_scores,
                'communities': communities,
                'total_nodes': len(graph),
                'total_edges': len(relationships)
            })
            
        except Exception as e:
            logger.warning(f"Graph analysis failed: {e}")
    
    def _build_adjacency_graph(self, relationships: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """Build adjacency graph from relationships"""
        graph = defaultdict(set)
        
        for rel in relationships:
            source = rel['source_entity_id']
            target = rel['target_entity_id']
            graph[source].add(target)
            graph[target].add(source)  # Undirected graph
        
        return dict(graph)
    
    def _calculate_centrality(self, graph: Dict[str, Set[str]]) -> Dict[str, float]:
        """Calculate betweenness centrality for nodes"""
        centrality = {}
        nodes = list(graph.keys())
        
        for node in nodes:
            # Simple degree centrality for now
            degree = len(graph.get(node, set()))
            max_possible_degree = len(nodes) - 1
            centrality[node] = degree / max_possible_degree if max_possible_degree > 0 else 0.0
        
        return centrality
    
    def _detect_communities(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect communities using simple connected components"""
        visited = set()
        communities = []
        
        for node in graph:
            if node not in visited:
                community = []
                stack = [node]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        community.append(current)
                        stack.extend(graph.get(current, set()) - visited)
                
                if len(community) > 1:  # Only meaningful communities
                    communities.append(community)
        
        return communities
    
    async def _get_source_relationships(self, source_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for entities in a source"""
        # This would query the graph store for relationships
        # For now, return empty list as placeholder
        return []
    
    async def _store_graph_analysis_results(self, source_id: str, results: Dict[str, Any]):
        """Store graph analysis results"""
        logger.info(f"📊 Graph analysis for {source_id}: {results['total_nodes']} nodes, {results['total_edges']} edges")
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path"""
        if not file_path:
            return 'unknown'
        
        extension = file_path.split('.')[-1].lower()
        
        language_map = {
            'py': 'python', 'js': 'javascript', 'ts': 'typescript',
            'java': 'java', 'kt': 'kotlin', 'go': 'go', 'rs': 'rust',
            'cpp': 'cpp', 'cc': 'cpp', 'cxx': 'cpp', 'c': 'c', 'h': 'c',
            'cs': 'csharp', 'php': 'php', 'rb': 'ruby', 'swift': 'swift'
        }
        
        return language_map.get(extension, 'unknown')
    
    async def get_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific entity"""
        if not self.is_initialized:
            raise RuntimeError("Relationship Engine not initialized")
        
        logger.info(f"🔍 Getting relationships for entity: {entity_id}")
        
        try:
            # Get relationships from graph store
            relationships = await self.graph_store.get_relationships(entity_id)
            
            # Enrich with additional analysis
            enriched_relationships = []
            for rel in relationships:
                enriched_rel = dict(rel)
                
                # Add relationship strength analysis
                enriched_rel['strength_analysis'] = self._analyze_relationship_strength(rel)
                
                # Add path analysis
                enriched_rel['path_info'] = await self._analyze_relationship_path(entity_id, rel)
                
                enriched_relationships.append(enriched_rel)
            
            logger.info(f"📊 Found {len(enriched_relationships)} relationships for entity {entity_id}")
            return enriched_relationships
            
        except Exception as e:
            logger.error(f"Failed to get relationships for entity {entity_id}: {e}")
            return []
    
    def _analyze_relationship_strength(self, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the strength and quality of a relationship"""
        strength = relationship.get('strength', 0.0)
        confidence = relationship.get('confidence', 0.0)
        rel_type = relationship.get('relationship_type', '')
        
        # Calculate composite strength score
        composite_score = (strength + confidence) / 2
        
        # Determine strength category
        if composite_score >= 0.8:
            category = 'strong'
        elif composite_score >= 0.6:
            category = 'moderate'
        elif composite_score >= 0.4:
            category = 'weak'
        else:
            category = 'very_weak'
        
        return {
            'composite_score': composite_score,
            'strength_category': category,
            'confidence_level': 'high' if confidence >= 0.7 else 'medium' if confidence >= 0.5 else 'low',
            'relationship_quality': self._assess_relationship_quality(rel_type, strength, confidence)
        }
    
    def _assess_relationship_quality(self, rel_type: str, strength: float, confidence: float) -> str:
        """Assess the quality of a relationship based on type and metrics"""
        if rel_type in [RelationshipType.DEPENDS_ON, RelationshipType.INHERITS_FROM]:
            return 'high' if strength >= 0.8 and confidence >= 0.8 else 'medium'
        elif rel_type in [RelationshipType.SIMILAR_TO, RelationshipType.RELATED_TO]:
            return 'high' if strength >= 0.7 else 'medium' if strength >= 0.5 else 'low'
        else:
            return 'medium'
    
    async def _analyze_relationship_path(self, entity_id: str, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the path and context of a relationship"""
        target_id = relationship.get('target_entity_id', '')
        
        # For now, return basic path info
        # In a full implementation, this would calculate shortest paths,
        # intermediate nodes, path strength, etc.
        return {
            'direct_connection': True,
            'path_length': 1,
            'intermediate_nodes': [],
            'path_strength': relationship.get('strength', 0.0)
        } 