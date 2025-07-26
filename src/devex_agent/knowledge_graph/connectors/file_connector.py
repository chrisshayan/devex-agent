"""
File System Connector - Fetches content from local files and directories
"""

import logging
import os
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from ..core.models import GoldenSourceConfig, FileSourceConfig
from ..utils.gitignore_filter import create_gitignore_filter

logger = logging.getLogger(__name__)

class FileConnector:
    """
    Connector for local file system sources
    
    Scans directories for files matching specified patterns and extracts
    content for ingestion into the knowledge graph.
    """
    
    def __init__(self, source_config: GoldenSourceConfig):
        self.source_config = source_config
        # Convert dict config to FileSourceConfig object
        self.file_config = FileSourceConfig(**source_config.config) if isinstance(source_config.config, dict) else source_config.config
        
        # Resolve the path
        self.base_path = Path(self.file_config.path).expanduser().resolve()
        
        # Initialize gitignore filter to respect project exclusions
        self.gitignore_filter = create_gitignore_filter(self.base_path)
        
        logger.info(f"🔌 File connector initialized for path: {self.base_path}")
        logger.info(f"🚫 GitIgnore filter loaded {self.gitignore_filter.get_exclusion_stats()['total_patterns']} patterns")
    
    async def validate_config(self, config) -> bool:
        """Validate file system configuration"""
        try:
            if not self.base_path.exists():
                logger.error(f"❌ Path does not exist: {self.base_path}")
                return False
            
            if not self.base_path.is_dir() and not self.base_path.is_file():
                logger.error(f"❌ Path is neither file nor directory: {self.base_path}")
                return False
            
            # Check read permissions
            if not os.access(self.base_path, os.R_OK):
                logger.error(f"❌ No read permission for path: {self.base_path}")
                return False
            
            logger.info(f"✅ File system path {self.base_path} is accessible")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to validate file config: {e}")
            return False
    
    async def extract_content(self) -> Dict[str, Any]:
        """Extract content from file system"""
        logger.info(f"📤 Extracting content from {self.base_path}")
        
        content_items = []
        
        try:
            if self.base_path.is_file():
                # Single file
                file_item = await self._process_single_file(self.base_path)
                if file_item:
                    content_items.append(file_item)
            else:
                # Directory - scan for files
                files = self._scan_directory()
                logger.info(f"📂 Found {len(files)} files to process")
                
                for file_path in files:
                    try:
                        file_item = await self._process_single_file(file_path)
                        if file_item:
                            content_items.append(file_item)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to process file {file_path}: {e}")
                        continue
            
            logger.info(f"✅ Extracted {len(content_items)} items from {self.base_path}")
            
            return {
                "content": content_items,
                "metadata": {
                    "source": "file_connector",
                    "base_path": str(self.base_path),
                    "extracted_at": datetime.now().isoformat(),
                    "total_items": len(content_items),
                    "recursive": self.file_config.recursive
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to extract content from {self.base_path}: {e}")
            return {
                "content": [],
                "metadata": {"source": "file_connector", "error": str(e)},
                "error": str(e)
            }
    
    def _scan_directory(self) -> List[Path]:
        """Scan directory for files matching patterns"""
        files = []
        
        try:
            if self.file_config.recursive:
                # Recursive scan
                pattern = "**/*"
                all_paths = self.base_path.rglob(pattern)
            else:
                # Non-recursive scan
                all_paths = self.base_path.iterdir()
            
            for path in all_paths:
                if not path.is_file():
                    continue
                
                # Check if file should be included
                if self._should_include_file(path):
                    files.append(path)
            
            logger.debug(f"📁 Scanned directory {self.base_path}: {len(files)} files match criteria")
            
        except Exception as e:
            logger.error(f"❌ Failed to scan directory {self.base_path}: {e}")
        
        return files
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included based on patterns and gitignore"""
        relative_path = file_path.relative_to(self.base_path)
        relative_str = str(relative_path)
        file_name = file_path.name
        
        # First check gitignore filter (respects .gitignore and common exclusions)
        if self.gitignore_filter.should_exclude(file_path):
            logger.debug(f"🚫 GitIgnore excluded: {relative_str}")
            return False
        
        # Check exclude directories (additional to gitignore)
        for exclude_dir in self.file_config.exclude_directories:
            if exclude_dir in relative_path.parts:
                logger.debug(f"🚫 Config excluded directory: {relative_str}")
                return False
        
        # Check file extensions
        file_extension = file_path.suffix.lower()
        if self.file_config.include_extensions:
            if file_extension not in self.file_config.include_extensions:
                logger.debug(f"🚫 Extension not in include list: {relative_str}")
                return False
        
        # Skip hidden files (unless specifically included in gitignore negation)
        if file_name.startswith('.') and not file_name.startswith('.gitignore'):
            logger.debug(f"🚫 Hidden file: {relative_str}")
            return False
        
        # Skip very large files (>10MB)
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                logger.debug(f"⏭️ Skipping large file: {relative_str}")
                return False
        except OSError:
            return False
        
        return True
    
    async def _process_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single file and extract its content"""
        try:
            # Generate unique ID based on file path and modification time
            stat = file_path.stat()
            id_source = f"{file_path}_{stat.st_mtime}_{stat.st_size}"
            file_id = hashlib.md5(id_source.encode()).hexdigest()
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception:
                    logger.warning(f"⚠️ Could not read file with any encoding: {file_path}")
                    return None
            
            # Skip empty files
            if not content.strip():
                return None
            
            # Limit content size
            if len(content) > 100000:  # 100KB limit
                content = content[:100000] + "\n... [Content truncated]"
            
            # Get relative path for display
            try:
                relative_path = file_path.relative_to(self.base_path)
            except ValueError:
                relative_path = file_path
            
            # Determine content type
            content_type = self._determine_content_type(file_path)
            
            # Extract basic metadata
            metadata = {
                "file_extension": file_path.suffix.lower(),
                "content_type": content_type,
                "size_bytes": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "encoding": "utf-8",
                "line_count": len(content.splitlines()),
                "character_count": len(content)
            }
            
            # Add language detection for code files
            if content_type == "code":
                metadata["language"] = self._detect_language(file_path)
            
            return {
                "id": f"file_{file_id}",
                "type": content_type,
                "title": str(relative_path),
                "content": content,
                "file_path": str(relative_path),
                "url": f"file://{file_path}",
                "metadata": metadata
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to process file {file_path}: {e}")
            return None
    
    def _determine_content_type(self, file_path: Path) -> str:
        """Determine the type of content based on file extension"""
        extension = file_path.suffix.lower()
        
        # Documentation files
        if extension in ['.md', '.rst', '.txt', '.adoc']:
            return "documentation"
        
        # Code files
        elif extension in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs', 
                          '.rb', '.php', '.cs', '.kt', '.swift', '.scala', '.r', '.m']:
            return "code_file"
        
        # Configuration files
        elif extension in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']:
            return "configuration"
        
        # Web files
        elif extension in ['.html', '.htm', '.css', '.scss', '.less']:
            return "web_content"
        
        # Data files
        elif extension in ['.sql', '.csv', '.xml']:
            return "data_file"
        
        # Shell scripts
        elif extension in ['.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat']:
            return "script"
        
        # Default
        else:
            return "document"
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        extension = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.kt': 'kotlin',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'objective-c',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'zsh',
            '.fish': 'fish',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.xml': 'xml'
        }
        
        return language_map.get(extension, 'text')
    
    def _extract_frontmatter(self, content: str) -> tuple[Optional[Dict[str, Any]], str]:
        """Extract YAML frontmatter from markdown files"""
        lines = content.split('\n')
        
        if len(lines) >= 3 and lines[0].strip() == '---':
            # Look for closing ---
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    # Found frontmatter
                    frontmatter_text = '\n'.join(lines[1:i])
                    remaining_content = '\n'.join(lines[i+1:])
                    
                    try:
                        import yaml
                        frontmatter = yaml.safe_load(frontmatter_text)
                        return frontmatter, remaining_content
                    except Exception as e:
                        logger.debug(f"Failed to parse frontmatter: {e}")
                        return None, content
        
        return None, content 