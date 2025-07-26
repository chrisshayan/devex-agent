"""
Core data models for the Knowledge Graph system
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union, Literal
from datetime import datetime
from enum import Enum

class SourceType(str, Enum):
    """Supported golden source types"""
    GITHUB = "github"
    CONFLUENCE = "confluence"
    DEEPWIKI = "deepwiki"
    FILE = "file"
    MCP = "mcp"

class Priority(str, Enum):
    """Source priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IngestionStatus(str, Enum):
    """Ingestion job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Source Configuration Models

class BaseSourceConfig(BaseModel):
    """Base configuration for all source types"""
    name: str = Field(..., description="Human-readable name for the source")
    description: Optional[str] = Field(None, description="Description of the source")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
class GitHubSourceConfig(BaseSourceConfig):
    """Configuration for GitHub repository sources"""
    repository: str = Field(..., description="Repository in format 'owner/repo'")
    branch: str = Field(default="main", description="Branch to analyze")
    include_patterns: List[str] = Field(default_factory=list, description="File patterns to include")
    exclude_patterns: List[str] = Field(default_factory=list, description="File patterns to exclude")
    access_token: Optional[str] = Field(None, description="GitHub access token for private repos")
    include_issues: bool = Field(default=True, description="Include GitHub issues")
    include_prs: bool = Field(default=True, description="Include pull requests")
    include_wiki: bool = Field(default=True, description="Include repository wiki")

class ConfluenceSourceConfig(BaseSourceConfig):
    """Configuration for Confluence sources"""
    base_url: str = Field(..., description="Confluence base URL")
    space_key: str = Field(..., description="Confluence space key")
    page_filter: Optional[str] = Field(None, description="CQL filter for pages")
    username: str = Field(..., description="Confluence username")
    api_token: str = Field(..., description="Confluence API token")
    include_attachments: bool = Field(default=True, description="Include page attachments")
    include_comments: bool = Field(default=False, description="Include page comments")

class DeepWikiSourceConfig(BaseSourceConfig):
    """Configuration for DeepWiki sources"""
    base_url: str = Field(..., description="DeepWiki base URL")
    category_filter: Optional[str] = Field(None, description="Category filter")
    api_key: Optional[str] = Field(None, description="API key if required")
    include_media: bool = Field(default=True, description="Include media files")

class FileSourceConfig(BaseSourceConfig):
    """Configuration for file system sources"""
    path: str = Field(..., description="Path to files or directory")
    include_extensions: List[str] = Field(default=[".md", ".txt", ".py"], description="File extensions to include")
    exclude_directories: List[str] = Field(default=[".git", "__pycache__"], description="Directories to exclude")
    recursive: bool = Field(default=True, description="Recursively scan subdirectories")

class MCPSourceConfig(BaseSourceConfig):
    """Configuration for MCP-based sources"""
    mcp_server: str = Field(..., description="MCP server identifier")
    connection_config: Dict[str, Any] = Field(default_factory=dict, description="MCP connection configuration")
    tools: List[str] = Field(default_factory=list, description="Specific MCP tools to use")

# Union type for all source configurations
SourceConfig = Union[GitHubSourceConfig, ConfluenceSourceConfig, DeepWikiSourceConfig, FileSourceConfig, MCPSourceConfig]

class GoldenSourceConfig(BaseModel):
    """Complete golden source configuration"""
    id: Optional[str] = Field(None, description="Unique identifier (auto-generated if not provided)")
    type: SourceType = Field(..., description="Type of the source")
    config: SourceConfig = Field(..., description="Source-specific configuration")
    priority: Priority = Field(default=Priority.MEDIUM, description="Source priority")
    auto_sync: bool = Field(default=True, description="Enable automatic synchronization")
    sync_interval: str = Field(default="6h", description="Sync interval (e.g., '1h', '6h', '1d')")
    enabled: bool = Field(default=True, description="Whether the source is enabled")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @validator('sync_interval')
    def validate_sync_interval(cls, v):
        """Validate sync interval format"""
        import re
        if not re.match(r'^\d+[hdw]$', v):
            raise ValueError('Sync interval must be in format like "1h", "6h", "1d", "1w"')
        return v

# Search and Query Models

class KnowledgeQuery(BaseModel):
    """Query for knowledge graph search"""
    query: str = Field(..., description="Search query text")
    developer_id: Optional[str] = Field(None, description="Developer context")
    current_file: Optional[str] = Field(None, description="Current file context")
    project_path: Optional[str] = Field(None, description="Project context")
    language: Optional[str] = Field(None, description="Programming language context")
    source_types: List[SourceType] = Field(default_factory=list, description="Limit search to specific source types")
    source_ids: List[str] = Field(default_factory=list, description="Limit search to specific sources")
    max_results: int = Field(default=10, description="Maximum number of results")
    include_relationships: bool = Field(default=True, description="Include relationship information")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity threshold")

class SearchResult(BaseModel):
    """Individual search result"""
    id: str = Field(..., description="Unique result identifier")
    source_id: str = Field(..., description="Source that contains this result")
    source_type: SourceType = Field(..., description="Type of source")
    title: str = Field(..., description="Result title")
    content: str = Field(..., description="Result content excerpt")
    url: Optional[str] = Field(None, description="URL to the original content")
    file_path: Optional[str] = Field(None, description="File path for code results")
    similarity_score: float = Field(..., description="Similarity score (0.0-1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="Related entities")

class SearchResults(BaseModel):
    """Search results container"""
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total number of results found")
    results: List[SearchResult] = Field(..., description="Search results")
    execution_time_ms: float = Field(..., description="Query execution time in milliseconds")
    sources_searched: List[str] = Field(..., description="Sources that were searched")
    suggestions: List[str] = Field(default_factory=list, description="Query suggestions")

# Ingestion Models

class IngestionJob(BaseModel):
    """Ingestion job tracking"""
    id: str = Field(..., description="Job identifier")
    source_id: str = Field(..., description="Source being ingested")
    status: IngestionStatus = Field(..., description="Job status")
    started_at: datetime = Field(..., description="Job start time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    progress: float = Field(default=0.0, description="Progress percentage (0.0-1.0)")
    items_processed: int = Field(default=0, description="Number of items processed")
    items_total: Optional[int] = Field(None, description="Total number of items to process")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Job metadata")

class IngestionResult(BaseModel):
    """Result of an ingestion operation"""
    job_id: str = Field(..., description="Job identifier")
    success: bool = Field(..., description="Whether ingestion succeeded")
    items_ingested: int = Field(..., description="Number of items successfully ingested")
    items_failed: int = Field(default=0, description="Number of items that failed")
    duration_seconds: float = Field(..., description="Ingestion duration in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Ingestion summary")

# Evaluation Models

class PatternMatch(BaseModel):
    """Pattern match result"""
    pattern_id: str = Field(..., description="Identifier of the matched pattern")
    pattern_name: str = Field(..., description="Human-readable pattern name")
    source_id: str = Field(..., description="Source containing the pattern")
    source_reference: str = Field(..., description="Reference to the source location")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    similarity_score: float = Field(..., description="Similarity score to current code")
    description: str = Field(..., description="Pattern description")

class EvaluationRecommendation(BaseModel):
    """Code evaluation recommendation"""
    type: Literal["enhancement", "refactoring", "security", "performance", "style"] = Field(..., description="Recommendation type")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    priority: Priority = Field(..., description="Recommendation priority")
    source_reference: Optional[str] = Field(None, description="Reference to golden source example")
    code_example: Optional[str] = Field(None, description="Example code snippet")
    diff_suggestion: Optional[str] = Field(None, description="Suggested code changes")

class EvaluationResult(BaseModel):
    """Result of code evaluation against golden sources"""
    developer_id: str = Field(..., description="Developer identifier")
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    evaluated_at: datetime = Field(..., description="Evaluation timestamp")
    overall_alignment_score: float = Field(..., description="Overall alignment score (0.0-1.0)")
    pattern_matches: List[PatternMatch] = Field(..., description="Identified pattern matches")
    recommendations: List[EvaluationRecommendation] = Field(..., description="Improvement recommendations")
    quality_score: float = Field(..., description="Overall quality score (0.0-1.0)")
    security_score: float = Field(..., description="Security score (0.0-1.0)")
    maintainability_score: float = Field(..., description="Maintainability score (0.0-1.0)")
    coverage_gaps: List[str] = Field(default_factory=list, description="Areas lacking golden source coverage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional evaluation metadata")

# Context Models

class DevelopmentContext(BaseModel):
    """Current development context"""
    developer_id: str = Field(..., description="Developer identifier")
    current_file: Optional[str] = Field(None, description="Currently edited file")
    project_path: Optional[str] = Field(None, description="Current project path")
    language: Optional[str] = Field(None, description="Current programming language")
    recent_files: List[str] = Field(default_factory=list, description="Recently edited files")
    active_branch: Optional[str] = Field(None, description="Current git branch")
    recent_commits: List[str] = Field(default_factory=list, description="Recent commit hashes")
    build_status: Optional[str] = Field(None, description="Latest build status")

class KnowledgeContext(BaseModel):
    """Contextual knowledge for current development"""
    relevant_sources: List[str] = Field(..., description="Relevant golden source IDs")
    similar_patterns: List[PatternMatch] = Field(..., description="Similar code patterns")
    recommendations: List[EvaluationRecommendation] = Field(..., description="Contextual recommendations")
    related_documentation: List[SearchResult] = Field(..., description="Related documentation")
    historical_examples: List[SearchResult] = Field(..., description="Historical code examples")
    context_score: float = Field(..., description="Relevance score of the context")

# Relationship Models

class RelationshipType(str, Enum):
    """Types of relationships between knowledge entities"""
    INHERITS_FROM = "inherits_from"
    DEPENDS_ON = "depends_on"
    SIMILAR_TO = "similar_to"
    RELATED_TO = "related_to"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"
    IMPLEMENTS = "implements"
    INSPIRED_BY = "inspired_by"

class KnowledgeRelationship(BaseModel):
    """Relationship between knowledge entities"""
    id: str = Field(..., description="Relationship identifier")
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    strength: float = Field(..., description="Relationship strength (0.0-1.0)")
    confidence: float = Field(..., description="Confidence in the relationship (0.0-1.0)")
    description: Optional[str] = Field(None, description="Human-readable description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp") 