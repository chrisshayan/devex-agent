"""
GitIgnore Filter - Respects .gitignore patterns and common exclusions
"""

import logging
import re
import fnmatch
from typing import List, Set, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class GitIgnoreFilter:
    """
    Filter files based on .gitignore patterns and common development exclusions
    
    Supports:
    - Standard .gitignore patterns
    - Glob patterns (*, ?, [])
    - Negation patterns (!pattern)
    - Directory-specific patterns (dir/)
    - Common exclusions (node_modules, .venv, etc.)
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.patterns = []
        self.negation_patterns = []
        
        # Load patterns from .gitignore
        self._load_gitignore_patterns()
        
        # Add common development exclusions
        self._add_common_exclusions()
        
        logger.info(f"🚫 GitIgnoreFilter initialized with {len(self.patterns)} exclusion patterns")
    
    def _load_gitignore_patterns(self):
        """Load patterns from .gitignore files"""
        gitignore_files = [
            self.project_root / ".gitignore",
            self.project_root / ".git" / "info" / "exclude"
        ]
        
        for gitignore_file in gitignore_files:
            if gitignore_file.exists():
                try:
                    with open(gitignore_file, 'r', encoding='utf-8') as f:
                        lines = f.read().splitlines()
                    
                    for line in lines:
                        line = line.strip()
                        
                        # Skip empty lines and comments
                        if not line or line.startswith('#'):
                            continue
                        
                        # Handle negation patterns
                        if line.startswith('!'):
                            self.negation_patterns.append(line[1:])
                        else:
                            self.patterns.append(line)
                    
                    logger.debug(f"📄 Loaded {len(lines)} patterns from {gitignore_file}")
                    
                except Exception as e:
                    logger.warning(f"Failed to read {gitignore_file}: {e}")
    
    def _add_common_exclusions(self):
        """Add common development exclusions that should always be ignored"""
        common_patterns = [
            # Python
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "*.so",
            ".Python",
            "build/",
            "develop-eggs/",
            "dist/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "wheels/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",
            "MANIFEST",
            ".env",
            ".venv",
            "env/",
            "venv/",
            "ENV/",
            "env.bak/",
            "venv.bak/",
            
            # Node.js
            "node_modules/",
            "npm-debug.log*",
            "yarn-debug.log*",
            "yarn-error.log*",
            ".npm",
            ".eslintcache",
            
            # IDEs and editors
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db",
            
            # Version control
            ".git/",
            ".svn/",
            ".hg/",
            
            # Build artifacts
            "target/",
            "out/",
            "bin/",
            "obj/",
            "*.class",
            "*.jar",
            "*.war",
            "*.ear",
            
            # Logs
            "*.log",
            "logs/",
            
            # Temporary files
            "tmp/",
            "temp/",
            ".tmp/",
            ".temp/",
            
            # OS generated files
            ".DS_Store?",
            "ehthumbs.db",
            "Icon?",
            
            # Package managers
            ".yarn/",
            ".pnp.*",
            "composer.phar",
            "vendor/",
            
            # Database files
            "*.sqlite",
            "*.sqlite3",
            "*.db",
            
            # Coverage reports
            "htmlcov/",
            ".coverage",
            ".coverage.*",
            "coverage.xml",
            ".nyc_output",
            
            # Documentation builds
            "_build/",
            ".doctrees",
            "site/",
            
            # Cache directories
            ".cache/",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            
            # Large binary files (common extensions)
            "*.exe",
            "*.dll",
            "*.dmg",
            "*.pkg",
            "*.deb",
            "*.rpm",
            "*.msi",
            "*.zip",
            "*.tar.gz",
            "*.rar",
            "*.7z",
            
            # Media files
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.bmp",
            "*.ico",
            "*.svg",
            "*.mp4",
            "*.mp3",
            "*.wav",
            "*.avi",
            "*.mov",
            "*.wmv",
            "*.flv",
            
            # Font files
            "*.ttf",
            "*.otf",
            "*.woff",
            "*.woff2",
            "*.eot",
        ]
        
        self.patterns.extend(common_patterns)
        logger.debug(f"➕ Added {len(common_patterns)} common exclusion patterns")
    
    def should_exclude(self, file_path: Path) -> bool:
        """
        Check if a file should be excluded based on gitignore patterns
        
        Args:
            file_path: Path to check (can be absolute or relative to project_root)
            
        Returns:
            bool: True if file should be excluded
        """
        try:
            # Convert to relative path from project root
            if file_path.is_absolute():
                try:
                    relative_path = file_path.relative_to(self.project_root)
                except ValueError:
                    # File is outside project root, exclude it
                    return True
            else:
                relative_path = file_path
            
            path_str = str(relative_path)
            path_parts = relative_path.parts
            
            # Check if any pattern matches
            excluded = self._matches_patterns(path_str, path_parts)
            
            # Check negation patterns (! patterns)
            if excluded:
                for neg_pattern in self.negation_patterns:
                    if self._matches_pattern(path_str, path_parts, neg_pattern):
                        excluded = False
                        break
            
            return excluded
            
        except Exception as e:
            logger.debug(f"Error checking exclusion for {file_path}: {e}")
            return False  # Don't exclude on error
    
    def _matches_patterns(self, path_str: str, path_parts: tuple) -> bool:
        """Check if path matches any exclusion pattern"""
        for pattern in self.patterns:
            if self._matches_pattern(path_str, path_parts, pattern):
                return True
        return False
    
    def _matches_pattern(self, path_str: str, path_parts: tuple, pattern: str) -> bool:
        """Check if a path matches a specific gitignore pattern"""
        
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            # For directory patterns, check if any part of the path matches
            for i, part in enumerate(path_parts):
                if fnmatch.fnmatch(part, pattern):
                    return True
            return False
        
        # Handle patterns starting with /
        if pattern.startswith('/'):
            pattern = pattern[1:]
            # Root-relative patterns
            return fnmatch.fnmatch(path_str, pattern)
        
        # Handle patterns with **/ (match any number of directories)
        if '**/' in pattern:
            # Convert to regex for complex matching
            regex_pattern = pattern.replace('**/', '.*/')
            regex_pattern = regex_pattern.replace('*', '[^/]*')
            regex_pattern = regex_pattern.replace('?', '[^/]')
            try:
                return bool(re.search(regex_pattern, path_str))
            except re.error:
                # Fall back to simple matching
                pass
        
        # Check if the pattern matches the full path
        if fnmatch.fnmatch(path_str, pattern):
            return True
        
        # Check if the pattern matches any part of the path
        if '/' not in pattern:
            # Simple filename pattern - check against each part
            for part in path_parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
        
        # Check if pattern matches from any directory level
        path_segments = path_str.split('/')
        for i in range(len(path_segments)):
            subpath = '/'.join(path_segments[i:])
            if fnmatch.fnmatch(subpath, pattern):
                return True
        
        return False
    
    def filter_files(self, file_paths: List[Path]) -> List[Path]:
        """
        Filter a list of file paths, removing excluded ones
        
        Args:
            file_paths: List of file paths to filter
            
        Returns:
            List of file paths that should not be excluded
        """
        filtered = []
        excluded_count = 0
        
        for file_path in file_paths:
            if not self.should_exclude(file_path):
                filtered.append(file_path)
            else:
                excluded_count += 1
                logger.debug(f"🚫 Excluded: {file_path}")
        
        if excluded_count > 0:
            logger.info(f"🚫 Filtered out {excluded_count} files based on gitignore patterns")
        
        return filtered
    
    def get_exclusion_stats(self) -> dict:
        """Get statistics about exclusion patterns"""
        return {
            "total_patterns": len(self.patterns),
            "negation_patterns": len(self.negation_patterns),
            "gitignore_loaded": (
                (self.project_root / ".gitignore").exists() or
                (self.project_root / ".git" / "info" / "exclude").exists()
            ),
            "project_root": str(self.project_root)
        }


def create_gitignore_filter(project_root: Optional[Path] = None) -> GitIgnoreFilter:
    """
    Create a GitIgnoreFilter instance
    
    Args:
        project_root: Project root directory (defaults to current working directory)
        
    Returns:
        GitIgnoreFilter instance
    """
    if project_root is None:
        project_root = Path.cwd()
    
    return GitIgnoreFilter(project_root) 