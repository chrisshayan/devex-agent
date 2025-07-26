"""
Knowledge Graph Connectors

Provides connectors for various golden source types:
- GitHub repositories
- Local file systems  
- Confluence spaces
- Future: DeepWiki, MCP adapters
"""

from .factory import ConnectorFactory
from .github_connector import GitHubConnector
from .file_connector import FileConnector
from .confluence_connector import ConfluenceConnector

__all__ = [
    "ConnectorFactory",
    "GitHubConnector", 
    "FileConnector",
    "ConfluenceConnector"
] 