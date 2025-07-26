"""
DevEx Agent Knowledge Graph System

Provides sophisticated knowledge graph capabilities for golden source
management, semantic search, and contextual code evaluation.
"""

__version__ = "1.0.0"

from .core.service import KnowledgeGraphService
from .core.models import GoldenSourceConfig, KnowledgeQuery, SearchResults

__all__ = [
    "KnowledgeGraphService",
    "GoldenSourceConfig", 
    "KnowledgeQuery",
    "SearchResults"
] 