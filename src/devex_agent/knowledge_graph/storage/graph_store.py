"""
Graph Store Manager - Handles Neo4j graph database operations with fallback support
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict
import json

try:
    from neo4j import GraphDatabase, basic_auth
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logging.warning("Neo4j driver not available - Knowledge Graph will use in-memory fallback")

from ..core.models import RelationshipType, KnowledgeRelationship

logger = logging.getLogger(__name__)

class GraphStoreManager:
    """
    Manages graph database operations using Neo4j with in-memory fallback
    
    Provides functionality for storing, retrieving, and querying relationships
    between knowledge entities. Uses Neo4j when available, falls back to 
    in-memory storage for development.
    """
    
    def __init__(self, connection_url: Optional[str] = None, username: str = "neo4j", password: str = "password"):
        self.connection_url = connection_url or "bolt://localhost:7687"
        self.username = username
        self.password = password
        self.driver = None
        self.is_initialized = False
        
        # In-memory fallback storage
        self.entities: Dict[str, Dict[str, Any]] = {}  # entity_id -> entity_data
        self.relationships: Dict[str, KnowledgeRelationship] = {}  # relationship_id -> relationship
        self.entity_relationships: Dict[str, Set[str]] = defaultdict(set)  # entity_id -> set of relationship_ids
        self.source_entities: Dict[str, Set[str]] = defaultdict(set)  # source_id -> set of entity_ids
        
        logger.info("📊 GraphStoreManager initialized")
    
    async def initialize(self):
        """Initialize the graph store"""
        try:
            logger.info("🔄 Initializing Graph Store...")
            
            if NEO4J_AVAILABLE:
                await self._initialize_neo4j()
            else:
                await self._initialize_fallback()
            
            self.is_initialized = True
            logger.info("✅ Graph Store initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Graph Store: {e}")
            # Fall back to in-memory even if Neo4j was attempted
            await self._initialize_fallback()
            self.is_initialized = True
            logger.info("✅ Graph Store initialized with fallback mode")
    
    async def _initialize_neo4j(self):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                self.connection_url,
                auth=basic_auth(self.username, self.password)
            )
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]
                if test_value != 1:
                    raise Exception("Neo4j connection test failed")
            
            # Create indexes and constraints
            await self._create_neo4j_schema()
            
            logger.info("🔗 Connected to Neo4j successfully")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}")
            if self.driver:
                self.driver.close()
                self.driver = None
            raise
    
    async def _initialize_fallback(self):
        """Initialize in-memory fallback storage"""
        self.entities.clear()
        self.relationships.clear()
        self.entity_relationships.clear()
        self.source_entities.clear()
        logger.info("🧠 Initialized in-memory graph store (fallback mode)")
    
    async def _create_neo4j_schema(self):
        """Create Neo4j indexes and constraints"""
        if not self.driver:
            return
        
        schema_queries = [
            # Constraints
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT relationship_id IF NOT EXISTS FOR (r:Relationship) REQUIRE r.id IS UNIQUE",
            
            # Indexes
            "CREATE INDEX entity_source_id IF NOT EXISTS FOR (e:Entity) ON (e.source_id)",
            "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX relationship_type IF NOT EXISTS FOR (r:Relationship) ON (r.type)",
            "CREATE INDEX relationship_strength IF NOT EXISTS FOR (r:Relationship) ON (r.strength)",
        ]
        
        with self.driver.session() as session:
            for query in schema_queries:
                try:
                    session.run(query)
                except Exception as e:
                    # Constraints/indexes might already exist
                    logger.debug(f"Schema query failed (might already exist): {e}")
    
    async def cleanup(self):
        """Cleanup graph store resources"""
        logger.info("🧹 Cleaning up Graph Store...")
        
        if self.driver:
            self.driver.close()
            self.driver = None
        
        # Clear in-memory storage
        self.entities.clear()
        self.relationships.clear()
        self.entity_relationships.clear()
        self.source_entities.clear()
        
        self.is_initialized = False
        logger.info("✅ Graph Store cleanup complete")
    
    # Entity Management
    
    async def create_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: Dict[str, Any],
        source_id: str
    ) -> bool:
        """Create or update an entity"""
        if not self.is_initialized:
            raise RuntimeError("Graph Store not initialized")
        
        entity_data = {
            "id": entity_id,
            "type": entity_type,
            "source_id": source_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **properties
        }
        
        if self.driver:
            return await self._create_entity_neo4j(entity_data)
        else:
            return await self._create_entity_fallback(entity_data)
    
    async def _create_entity_neo4j(self, entity_data: Dict[str, Any]) -> bool:
        """Create entity in Neo4j"""
        query = """
        MERGE (e:Entity {id: $entity_id})
        SET e += $properties,
            e.updated_at = $updated_at
        RETURN e.id AS id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    entity_id=entity_data["id"],
                    properties=entity_data,
                    updated_at=datetime.now().isoformat()
                )
                created_id = result.single()["id"]
                logger.debug(f"📝 Created/updated entity in Neo4j: {created_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to create entity in Neo4j: {e}")
            return False
    
    async def _create_entity_fallback(self, entity_data: Dict[str, Any]) -> bool:
        """Create entity in fallback storage"""
        entity_id = entity_data["id"]
        source_id = entity_data["source_id"]
        
        self.entities[entity_id] = entity_data
        self.source_entities[source_id].add(entity_id)
        
        logger.debug(f"📝 Created/updated entity in fallback: {entity_id}")
        return True
    
    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID"""
        if not self.is_initialized:
            raise RuntimeError("Graph Store not initialized")
        
        if self.driver:
            return await self._get_entity_neo4j(entity_id)
        else:
            return self.entities.get(entity_id)
    
    async def _get_entity_neo4j(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity from Neo4j"""
        query = "MATCH (e:Entity {id: $entity_id}) RETURN e"
        
        try:
            with self.driver.session() as session:
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                if record:
                    return dict(record["e"])
                return None
        except Exception as e:
            logger.error(f"Failed to get entity from Neo4j: {e}")
            return None
    
    # Relationship Management
    
    async def store_relationship(self, relationship: Dict[str, Any]) -> str:
        """Store a relationship in the graph"""
        if not self.is_initialized:
            raise RuntimeError("Graph Store not initialized")
        
        # Ensure we have required fields
        relationship_id = relationship.get("id") or str(uuid.uuid4())
        relationship["id"] = relationship_id
        
        if "created_at" not in relationship:
            relationship["created_at"] = datetime.now().isoformat()
        relationship["updated_at"] = datetime.now().isoformat()
        
        if self.driver:
            success = await self._store_relationship_neo4j(relationship)
        else:
            success = await self._store_relationship_fallback(relationship)
        
        if success:
            logger.debug(f"📝 Stored relationship: {relationship_id}")
        
        return relationship_id
    
    async def _store_relationship_neo4j(self, relationship: Dict[str, Any]) -> bool:
        """Store relationship in Neo4j"""
        query = """
        MATCH (source:Entity {id: $source_id})
        MATCH (target:Entity {id: $target_id})
        MERGE (source)-[r:RELATED {id: $rel_id}]->(target)
        SET r += $properties,
            r.updated_at = $updated_at
        RETURN r.id AS id
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    source_id=relationship["source_entity_id"],
                    target_id=relationship["target_entity_id"],
                    rel_id=relationship["id"],
                    properties=relationship,
                    updated_at=datetime.now().isoformat()
                )
                created_id = result.single()["id"]
                return True
        except Exception as e:
            logger.error(f"Failed to store relationship in Neo4j: {e}")
            return False
    
    async def _store_relationship_fallback(self, relationship: Dict[str, Any]) -> bool:
        """Store relationship in fallback storage"""
        try:
            # Create KnowledgeRelationship object for validation
            rel_obj = KnowledgeRelationship(
                id=relationship["id"],
                source_entity_id=relationship["source_entity_id"],
                target_entity_id=relationship["target_entity_id"],
                relationship_type=RelationshipType(relationship.get("relationship_type", "related_to")),
                strength=relationship.get("strength", 0.5),
                confidence=relationship.get("confidence", 0.8),
                description=relationship.get("description"),
                metadata=relationship.get("metadata", {}),
                created_at=datetime.fromisoformat(relationship["created_at"]),
                updated_at=datetime.fromisoformat(relationship["updated_at"])
            )
            
            # Store in fallback
            rel_id = rel_obj.id
            self.relationships[rel_id] = rel_obj
            
            # Update entity relationship indexes
            self.entity_relationships[rel_obj.source_entity_id].add(rel_id)
            self.entity_relationships[rel_obj.target_entity_id].add(rel_id)
            
            return True
        except Exception as e:
            logger.error(f"Failed to store relationship in fallback: {e}")
            return False
    
    async def get_relationships(self, entity_id: str, relationship_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get relationships for an entity"""
        if not self.is_initialized:
            raise RuntimeError("Graph Store not initialized")
        
        if self.driver:
            return await self._get_relationships_neo4j(entity_id, relationship_types)
        else:
            return await self._get_relationships_fallback(entity_id, relationship_types)
    
    async def _get_relationships_neo4j(self, entity_id: str, relationship_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get relationships from Neo4j"""
        # Query for both incoming and outgoing relationships
        query = """
        MATCH (e:Entity {id: $entity_id})-[r:RELATED]-(other:Entity)
        WHERE $relationship_types IS NULL OR r.relationship_type IN $relationship_types
        RETURN r, other,
               CASE WHEN startNode(r).id = $entity_id THEN 'outgoing' ELSE 'incoming' END AS direction
        ORDER BY r.strength DESC, r.confidence DESC
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    entity_id=entity_id,
                    relationship_types=relationship_types
                )
                
                relationships = []
                for record in result:
                    rel_data = dict(record["r"])
                    other_entity = dict(record["other"])
                    direction = record["direction"]
                    
                    relationships.append({
                        **rel_data,
                        "other_entity": other_entity,
                        "direction": direction
                    })
                
                return relationships
        except Exception as e:
            logger.error(f"Failed to get relationships from Neo4j: {e}")
            return []
    
    async def _get_relationships_fallback(self, entity_id: str, relationship_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get relationships from fallback storage"""
        relationships = []
        
        for rel_id in self.entity_relationships.get(entity_id, set()):
            rel = self.relationships.get(rel_id)
            if not rel:
                continue
            
            # Filter by relationship type if specified
            if relationship_types and rel.relationship_type.value not in relationship_types:
                continue
            
            # Determine direction and other entity
            if rel.source_entity_id == entity_id:
                direction = "outgoing"
                other_entity_id = rel.target_entity_id
            else:
                direction = "incoming"
                other_entity_id = rel.source_entity_id
            
            # Get other entity data
            other_entity = self.entities.get(other_entity_id, {"id": other_entity_id})
            
            relationships.append({
                "id": rel.id,
                "relationship_type": rel.relationship_type.value,
                "strength": rel.strength,
                "confidence": rel.confidence,
                "description": rel.description,
                "metadata": rel.metadata,
                "created_at": rel.created_at.isoformat(),
                "updated_at": rel.updated_at.isoformat(),
                "other_entity": other_entity,
                "direction": direction
            })
        
        # Sort by strength and confidence
        relationships.sort(key=lambda r: (r["strength"], r["confidence"]), reverse=True)
        return relationships
    
    async def discover_relationships(self, source_id: str) -> int:
        """Discover relationships in a source using graph algorithms"""
        if not self.is_initialized:
            raise RuntimeError("Graph Store not initialized")
        
        if self.driver:
            return await self._discover_relationships_neo4j(source_id)
        else:
            return await self._discover_relationships_fallback(source_id)
    
    async def _discover_relationships_neo4j(self, source_id: str) -> int:
        """Discover relationships in Neo4j using graph algorithms"""
        # Example: Find entities that are similar based on shared properties
        query = """
        MATCH (e1:Entity {source_id: $source_id}), (e2:Entity {source_id: $source_id})
        WHERE e1.id <> e2.id 
        AND e1.type = e2.type
        AND NOT EXISTS((e1)-[:RELATED]-(e2))
        WITH e1, e2, 
             size([k IN keys(e1) WHERE k IN keys(e2) AND e1[k] = e2[k]]) AS shared_props
        WHERE shared_props > 2
        CREATE (e1)-[r:RELATED {
            id: randomUUID(),
            relationship_type: 'similar_to',
            strength: toFloat(shared_props) / 10.0,
            confidence: 0.6,
            description: 'Discovered based on shared properties',
            created_at: datetime(),
            updated_at: datetime(),
            discovered: true
        }]->(e2)
        RETURN count(r) AS relationships_created
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, source_id=source_id)
                count = result.single()["relationships_created"]
                logger.info(f"🕸️ Discovered {count} relationships in Neo4j for source: {source_id}")
                return count
        except Exception as e:
            logger.error(f"Failed to discover relationships in Neo4j: {e}")
            return 0
    
    async def _discover_relationships_fallback(self, source_id: str) -> int:
        """Discover relationships in fallback storage"""
        entities = list(self.source_entities.get(source_id, set()))
        relationships_created = 0
        
        # Simple similarity-based relationship discovery
        for i, entity_id1 in enumerate(entities):
            for entity_id2 in entities[i+1:]:
                entity1 = self.entities.get(entity_id1)
                entity2 = self.entities.get(entity_id2)
                
                if not entity1 or not entity2:
                    continue
                
                # Check if relationship already exists
                existing_rels = await self.get_relationships(entity_id1)
                if any(r["other_entity"]["id"] == entity_id2 for r in existing_rels):
                    continue
                
                # Calculate similarity based on shared properties
                shared_props = 0
                for key in entity1.keys():
                    if key in entity2 and entity1[key] == entity2[key]:
                        shared_props += 1
                
                # Create relationship if similarity is high enough
                if shared_props > 2:
                    strength = min(1.0, shared_props / 10.0)
                    
                    relationship = {
                        "id": str(uuid.uuid4()),
                        "source_entity_id": entity_id1,
                        "target_entity_id": entity_id2,
                        "relationship_type": "similar_to",
                        "strength": strength,
                        "confidence": 0.6,
                        "description": f"Discovered based on {shared_props} shared properties",
                        "metadata": {"discovered": True, "shared_properties": shared_props},
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    success = await self._store_relationship_fallback(relationship)
                    if success:
                        relationships_created += 1
        
        logger.info(f"🕸️ Discovered {relationships_created} relationships in fallback for source: {source_id}")
        return relationships_created
    
    async def remove_source_data(self, source_id: str):
        """Remove all data from a specific source"""
        if not self.is_initialized:
            return
        
        if self.driver:
            await self._remove_source_data_neo4j(source_id)
        else:
            await self._remove_source_data_fallback(source_id)
        
        logger.info(f"🗑️ Removed graph data for source: {source_id}")
    
    async def _remove_source_data_neo4j(self, source_id: str):
        """Remove source data from Neo4j"""
        query = """
        MATCH (e:Entity {source_id: $source_id})
        DETACH DELETE e
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, source_id=source_id)
                logger.debug(f"Removed entities and relationships for source: {source_id}")
        except Exception as e:
            logger.error(f"Failed to remove source data from Neo4j: {e}")
    
    async def _remove_source_data_fallback(self, source_id: str):
        """Remove source data from fallback storage"""
        entities_to_remove = list(self.source_entities.get(source_id, set()))
        
        # Remove relationships involving these entities
        relationships_to_remove = set()
        for entity_id in entities_to_remove:
            relationships_to_remove.update(self.entity_relationships.get(entity_id, set()))
        
        # Remove relationships
        for rel_id in relationships_to_remove:
            if rel_id in self.relationships:
                rel = self.relationships[rel_id]
                # Update entity relationship indexes
                self.entity_relationships[rel.source_entity_id].discard(rel_id)
                self.entity_relationships[rel.target_entity_id].discard(rel_id)
                # Remove relationship
                del self.relationships[rel_id]
        
        # Remove entities
        for entity_id in entities_to_remove:
            if entity_id in self.entities:
                del self.entities[entity_id]
            if entity_id in self.entity_relationships:
                del self.entity_relationships[entity_id]
        
        # Remove source mapping
        if source_id in self.source_entities:
            del self.source_entities[source_id]
    
    # Analytics and Queries
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        if not self.is_initialized:
            return {"error": "Graph Store not initialized"}
        
        if self.driver:
            return await self._get_statistics_neo4j()
        else:
            return await self._get_statistics_fallback()
    
    async def _get_statistics_neo4j(self) -> Dict[str, Any]:
        """Get statistics from Neo4j"""
        queries = {
            "total_entities": "MATCH (e:Entity) RETURN count(e) AS count",
            "total_relationships": "MATCH ()-[r:RELATED]->() RETURN count(r) AS count",
            "entities_by_type": "MATCH (e:Entity) RETURN e.type AS type, count(e) AS count",
            "relationships_by_type": "MATCH ()-[r:RELATED]->() RETURN r.relationship_type AS type, count(r) AS count"
        }
        
        stats = {}
        try:
            with self.driver.session() as session:
                for stat_name, query in queries.items():
                    result = session.run(query)
                    if stat_name in ["entities_by_type", "relationships_by_type"]:
                        stats[stat_name] = {record["type"]: record["count"] for record in result}
                    else:
                        stats[stat_name] = result.single()["count"]
        except Exception as e:
            logger.error(f"Failed to get statistics from Neo4j: {e}")
            stats = {"error": str(e)}
        
        return stats
    
    async def _get_statistics_fallback(self) -> Dict[str, Any]:
        """Get statistics from fallback storage"""
        entity_types = defaultdict(int)
        relationship_types = defaultdict(int)
        
        for entity in self.entities.values():
            entity_types[entity.get("type", "unknown")] += 1
        
        for relationship in self.relationships.values():
            relationship_types[relationship.relationship_type.value] += 1
        
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "entities_by_type": dict(entity_types),
            "relationships_by_type": dict(relationship_types),
            "storage_mode": "fallback"
        }
    
    async def find_similar_entities(
        self,
        entity_id: str,
        similarity_threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find entities similar to the given entity"""
        if not self.is_initialized:
            return []
        
        if self.driver:
            return await self._find_similar_neo4j(entity_id, similarity_threshold, limit)
        else:
            return await self._find_similar_fallback(entity_id, similarity_threshold, limit)
    
    async def _find_similar_neo4j(self, entity_id: str, similarity_threshold: float, limit: int) -> List[Dict[str, Any]]:
        """Find similar entities in Neo4j"""
        query = """
        MATCH (source:Entity {id: $entity_id})
        MATCH (target:Entity)
        WHERE source.id <> target.id AND source.type = target.type
        WITH source, target,
             size([k IN keys(source) WHERE k IN keys(target) AND source[k] = target[k]]) AS shared_props,
             size(keys(source)) + size(keys(target)) AS total_props
        WITH source, target, toFloat(shared_props * 2) / total_props AS similarity
        WHERE similarity >= $threshold
        RETURN target, similarity
        ORDER BY similarity DESC
        LIMIT $limit
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    entity_id=entity_id,
                    threshold=similarity_threshold,
                    limit=limit
                )
                
                similar_entities = []
                for record in result:
                    entity_data = dict(record["target"])
                    similarity = record["similarity"]
                    similar_entities.append({
                        "entity": entity_data,
                        "similarity_score": similarity
                    })
                
                return similar_entities
        except Exception as e:
            logger.error(f"Failed to find similar entities in Neo4j: {e}")
            return []
    
    async def _find_similar_fallback(self, entity_id: str, similarity_threshold: float, limit: int) -> List[Dict[str, Any]]:
        """Find similar entities in fallback storage"""
        source_entity = self.entities.get(entity_id)
        if not source_entity:
            return []
        
        similar_entities = []
        
        for other_id, other_entity in self.entities.items():
            if other_id == entity_id or other_entity.get("type") != source_entity.get("type"):
                continue
            
            # Calculate similarity based on shared properties
            shared_props = 0
            total_props = 0
            
            all_keys = set(source_entity.keys()) | set(other_entity.keys())
            for key in all_keys:
                if key in ["id", "created_at", "updated_at"]:  # Skip metadata keys
                    continue
                total_props += 1
                if key in source_entity and key in other_entity and source_entity[key] == other_entity[key]:
                    shared_props += 1
            
            if total_props > 0:
                similarity = shared_props / total_props
                if similarity >= similarity_threshold:
                    similar_entities.append({
                        "entity": other_entity,
                        "similarity_score": similarity
                    })
        
        # Sort by similarity and limit results
        similar_entities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_entities[:limit] 