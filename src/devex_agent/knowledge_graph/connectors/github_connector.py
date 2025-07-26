"""
GitHub Connector - Fetches content from GitHub repositories
"""

import logging
import asyncio
import base64
from typing import Dict, List, Any, Optional
import httpx
from datetime import datetime

from ..core.models import GoldenSourceConfig, GitHubSourceConfig

logger = logging.getLogger(__name__)

class GitHubConnector:
    """
    Connector for GitHub repositories
    
    Fetches code, documentation, issues, and other content from GitHub
    using the GitHub REST API.
    """
    
    def __init__(self, source_config: GoldenSourceConfig):
        self.source_config = source_config
        # Convert dict config to GitHubSourceConfig object
        self.github_config = GitHubSourceConfig(**source_config.config) if isinstance(source_config.config, dict) else source_config.config
        
        # GitHub API configuration
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DevEx-Agent/1.0"
        }
        
        # Add authentication if token is provided
        if self.github_config.access_token:
            self.headers["Authorization"] = f"token {self.github_config.access_token}"
        
        logger.info(f"🔌 GitHub connector initialized for {self.github_config.repository}")
    
    async def validate_config(self, config) -> bool:
        """Validate GitHub configuration by testing repository access"""
        try:
            async with httpx.AsyncClient() as client:
                repo_url = f"{self.base_url}/repos/{self.github_config.repository}"
                response = await client.get(repo_url, headers=self.headers)
                
                if response.status_code == 200:
                    logger.info(f"✅ GitHub repository {self.github_config.repository} is accessible")
                    return True
                elif response.status_code == 404:
                    logger.error(f"❌ Repository {self.github_config.repository} not found")
                    return False
                elif response.status_code == 401:
                    logger.error(f"❌ Authentication failed for {self.github_config.repository}")
                    return False
                else:
                    logger.error(f"❌ GitHub API error: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Failed to validate GitHub config: {e}")
            return False
    
    async def extract_content(self) -> Dict[str, Any]:
        """Extract content from GitHub repository"""
        logger.info(f"📤 Extracting content from {self.github_config.repository}")
        
        content_items = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 1. Extract repository metadata
                repo_metadata = await self._get_repository_metadata(client)
                if repo_metadata:
                    content_items.append(repo_metadata)
                
                # 2. Extract file content
                file_content = await self._extract_file_content(client)
                content_items.extend(file_content)
                
                # 3. Extract README and documentation
                readme_content = await self._extract_readme(client)
                if readme_content:
                    content_items.append(readme_content)
                
                # 4. Extract issues if enabled
                if self.github_config.include_issues:
                    issues_content = await self._extract_issues(client)
                    content_items.extend(issues_content)
                
                # 5. Extract pull requests if enabled
                if self.github_config.include_prs:
                    prs_content = await self._extract_pull_requests(client)
                    content_items.extend(prs_content)
                
                # 6. Extract wiki if enabled
                if self.github_config.include_wiki:
                    wiki_content = await self._extract_wiki(client)
                    content_items.extend(wiki_content)
            
            logger.info(f"✅ Extracted {len(content_items)} items from {self.github_config.repository}")
            
            return {
                "content": content_items,
                "metadata": {
                    "source": "github_connector",
                    "repository": self.github_config.repository,
                    "branch": self.github_config.branch,
                    "extracted_at": datetime.now().isoformat(),
                    "total_items": len(content_items)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to extract content from {self.github_config.repository}: {e}")
            return {
                "content": [],
                "metadata": {"source": "github_connector", "error": str(e)},
                "error": str(e)
            }
    
    async def _get_repository_metadata(self, client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
        """Get repository metadata"""
        try:
            repo_url = f"{self.base_url}/repos/{self.github_config.repository}"
            response = await client.get(repo_url, headers=self.headers)
            
            if response.status_code == 200:
                repo_data = response.json()
                
                return {
                    "id": f"repo_metadata_{self.github_config.repository.replace('/', '_')}",
                    "type": "repository_metadata",
                    "title": repo_data.get("name", ""),
                    "content": f"""
# {repo_data.get('name', 'Repository')}

**Description:** {repo_data.get('description', 'No description')}

**Language:** {repo_data.get('language', 'Unknown')}
**Stars:** {repo_data.get('stargazers_count', 0)}
**Forks:** {repo_data.get('forks_count', 0)}
**Open Issues:** {repo_data.get('open_issues_count', 0)}

**Topics:** {', '.join(repo_data.get('topics', []))}

**Homepage:** {repo_data.get('homepage', 'None')}
**Clone URL:** {repo_data.get('clone_url', '')}

**Created:** {repo_data.get('created_at', '')}
**Updated:** {repo_data.get('updated_at', '')}
                    """.strip(),
                    "file_path": "repository_metadata",
                    "url": repo_data.get("html_url", ""),
                    "metadata": {
                        "language": repo_data.get("language"),
                        "stars": repo_data.get("stargazers_count", 0),
                        "forks": repo_data.get("forks_count", 0),
                        "topics": repo_data.get("topics", []),
                        "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None
                    }
                }
        except Exception as e:
            logger.warning(f"Failed to get repository metadata: {e}")
        
        return None
    
    async def _extract_file_content(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Extract file content from repository"""
        content_items = []
        
        try:
            # Get repository tree
            tree_url = f"{self.base_url}/repos/{self.github_config.repository}/git/trees/{self.github_config.branch}"
            response = await client.get(f"{tree_url}?recursive=1", headers=self.headers)
            
            if response.status_code != 200:
                logger.warning(f"Failed to get repository tree: {response.status_code}")
                return content_items
            
            tree_data = response.json()
            files = [item for item in tree_data.get("tree", []) if item["type"] == "blob"]
            
            # Filter files based on patterns
            filtered_files = self._filter_files(files)
            
            # Process files in batches to avoid rate limiting
            batch_size = 10
            for i in range(0, len(filtered_files), batch_size):
                batch = filtered_files[i:i + batch_size]
                batch_results = await asyncio.gather(
                    *[self._process_file(client, file_info) for file_info in batch],
                    return_exceptions=True
                )
                
                for result in batch_results:
                    if isinstance(result, dict):
                        content_items.append(result)
                
                # Rate limiting - wait between batches
                if i + batch_size < len(filtered_files):
                    await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Failed to extract file content: {e}")
        
        return content_items
    
    def _filter_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter files based on include/exclude patterns"""
        filtered = []
        
        for file_info in files:
            file_path = file_info["path"]
            
            # Check exclude patterns first
            if any(self._matches_pattern(file_path, pattern) for pattern in self.github_config.exclude_patterns):
                continue
            
            # Check include patterns (if specified)
            if self.github_config.include_patterns:
                if any(self._matches_pattern(file_path, pattern) for pattern in self.github_config.include_patterns):
                    filtered.append(file_info)
            else:
                # If no include patterns, include all non-excluded files
                filtered.append(file_info)
        
        return filtered
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    async def _process_file(self, client: httpx.AsyncClient, file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single file"""
        try:
            file_path = file_info["path"]
            
            # Get file content
            content_url = f"{self.base_url}/repos/{self.github_config.repository}/contents/{file_path}"
            response = await client.get(content_url, headers=self.headers)
            
            if response.status_code != 200:
                return None
            
            content_data = response.json()
            
            # Decode base64 content
            if content_data.get("encoding") == "base64":
                try:
                    file_content = base64.b64decode(content_data["content"]).decode('utf-8')
                except UnicodeDecodeError:
                    # Skip binary files
                    return None
            else:
                file_content = content_data.get("content", "")
            
            # Skip very large files
            if len(file_content) > 100000:  # 100KB limit
                file_content = file_content[:100000] + "\n... [Content truncated]"
            
            return {
                "id": f"file_{file_path.replace('/', '_')}",
                "type": "code_file",
                "title": file_path,
                "content": file_content,
                "file_path": file_path,
                "url": content_data.get("html_url", ""),
                "metadata": {
                    "language": self._detect_language(file_path),
                    "size": content_data.get("size", 0),
                    "sha": content_data.get("sha", "")
                }
            }
        
        except Exception as e:
            logger.warning(f"Failed to process file {file_info.get('path', 'unknown')}: {e}")
            return None
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        extension = file_path.split('.')[-1].lower() if '.' in file_path else ""
        
        language_map = {
            "py": "python", "js": "javascript", "ts": "typescript",
            "java": "java", "kt": "kotlin", "go": "go", "rs": "rust",
            "cpp": "cpp", "c": "c", "cs": "csharp", "php": "php",
            "rb": "ruby", "swift": "swift", "sql": "sql",
            "md": "markdown", "txt": "text", "yml": "yaml", "yaml": "yaml",
            "json": "json", "xml": "xml", "html": "html", "css": "css"
        }
        
        return language_map.get(extension, "unknown")
    
    async def _extract_readme(self, client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
        """Extract README content"""
        readme_files = ["README.md", "README.rst", "README.txt", "README"]
        
        for readme_file in readme_files:
            try:
                content_url = f"{self.base_url}/repos/{self.github_config.repository}/contents/{readme_file}"
                response = await client.get(content_url, headers=self.headers)
                
                if response.status_code == 200:
                    content_data = response.json()
                    
                    if content_data.get("encoding") == "base64":
                        readme_content = base64.b64decode(content_data["content"]).decode('utf-8')
                        
                        return {
                            "id": f"readme_{readme_file.replace('.', '_')}",
                            "type": "documentation",
                            "title": f"README - {self.github_config.repository}",
                            "content": readme_content,
                            "file_path": readme_file,
                            "url": content_data.get("html_url", ""),
                            "metadata": {
                                "document_type": "readme",
                                "language": "markdown" if readme_file.endswith('.md') else "text"
                            }
                        }
            except Exception as e:
                logger.debug(f"README {readme_file} not found or accessible: {e}")
                continue
        
        return None
    
    async def _extract_issues(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Extract GitHub issues"""
        content_items = []
        
        try:
            issues_url = f"{self.base_url}/repos/{self.github_config.repository}/issues"
            response = await client.get(f"{issues_url}?state=all&per_page=50", headers=self.headers)
            
            if response.status_code == 200:
                issues = response.json()
                
                for issue in issues:
                    # Skip pull requests (they appear in issues API)
                    if "pull_request" in issue:
                        continue
                    
                    content_items.append({
                        "id": f"issue_{issue['number']}",
                        "type": "issue",
                        "title": f"Issue #{issue['number']}: {issue['title']}",
                        "content": f"""
# Issue #{issue['number']}: {issue['title']}

**State:** {issue['state']}
**Author:** {issue['user']['login']}
**Created:** {issue['created_at']}
**Updated:** {issue['updated_at']}

**Labels:** {', '.join([label['name'] for label in issue.get('labels', [])])}

**Body:**
{issue.get('body', 'No description provided.')}
                        """.strip(),
                        "url": issue['html_url'],
                        "metadata": {
                            "issue_number": issue['number'],
                            "state": issue['state'],
                            "author": issue['user']['login'],
                            "labels": [label['name'] for label in issue.get('labels', [])],
                            "comments": issue.get('comments', 0)
                        }
                    })
        
        except Exception as e:
            logger.warning(f"Failed to extract issues: {e}")
        
        return content_items
    
    async def _extract_pull_requests(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Extract GitHub pull requests"""
        content_items = []
        
        try:
            prs_url = f"{self.base_url}/repos/{self.github_config.repository}/pulls"
            response = await client.get(f"{prs_url}?state=all&per_page=30", headers=self.headers)
            
            if response.status_code == 200:
                prs = response.json()
                
                for pr in prs:
                    content_items.append({
                        "id": f"pr_{pr['number']}",
                        "type": "pull_request",
                        "title": f"PR #{pr['number']}: {pr['title']}",
                        "content": f"""
# Pull Request #{pr['number']}: {pr['title']}

**State:** {pr['state']}
**Author:** {pr['user']['login']}
**Created:** {pr['created_at']}
**Updated:** {pr['updated_at']}

**Base:** {pr['base']['ref']} ← **Head:** {pr['head']['ref']}

**Body:**
{pr.get('body', 'No description provided.')}
                        """.strip(),
                        "url": pr['html_url'],
                        "metadata": {
                            "pr_number": pr['number'],
                            "state": pr['state'],
                            "author": pr['user']['login'],
                            "base_branch": pr['base']['ref'],
                            "head_branch": pr['head']['ref'],
                            "merged": pr.get('merged', False)
                        }
                    })
        
        except Exception as e:
            logger.warning(f"Failed to extract pull requests: {e}")
        
        return content_items
    
    async def _extract_wiki(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Extract GitHub wiki pages"""
        content_items = []
        
        try:
            # GitHub wikis are in a separate git repository
            wiki_url = f"{self.base_url}/repos/{self.github_config.repository}/contents"
            
            # Try to access wiki via API (this may not work for all repositories)
            response = await client.get(f"{wiki_url}?ref=wiki", headers=self.headers)
            
            if response.status_code == 200:
                logger.info(f"📚 Found wiki content for {self.github_config.repository}")
                # Process wiki files if accessible
                # This is a simplified implementation
        
        except Exception as e:
            logger.debug(f"Wiki not accessible or not available: {e}")
        
        return content_items 