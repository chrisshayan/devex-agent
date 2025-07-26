"""
Confluence Connector - Fetches team documentation from Confluence
"""

import logging
import base64
import html
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
import re
from urllib.parse import urljoin, quote

from ..core.models import GoldenSourceConfig, ConfluenceSourceConfig

logger = logging.getLogger(__name__)

class ConfluenceConnector:
    """
    Connector for Confluence team documentation
    
    Fetches pages, attachments, and comments from Confluence spaces
    using the Confluence REST API with authentication.
    """
    
    def __init__(self, source_config: GoldenSourceConfig):
        self.source_config = source_config
        # Convert dict config to ConfluenceSourceConfig object
        self.confluence_config = ConfluenceSourceConfig(**source_config.config) if isinstance(source_config.config, dict) else source_config.config
        
        # Setup authentication
        self.base_url = self.confluence_config.base_url.rstrip('/')
        self.api_base = f"{self.base_url}/rest/api"
        
        # Create HTTP client with authentication
        auth_string = f"{self.confluence_config.username}:{self.confluence_config.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_header = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_header}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"🔌 Confluence connector initialized for: {self.base_url}")
        logger.info(f"📁 Target space: {self.confluence_config.space_key}")
    
    async def validate_config(self, config) -> bool:
        """Validate Confluence configuration by testing API access"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test authentication and space access
                space_url = f"{self.api_base}/space/{self.confluence_config.space_key}"
                
                response = await client.get(space_url, headers=self.headers)
                
                if response.status_code == 401:
                    logger.error("❌ Confluence authentication failed - check username and API token")
                    return False
                elif response.status_code == 404:
                    logger.error(f"❌ Confluence space '{self.confluence_config.space_key}' not found or not accessible")
                    return False
                elif response.status_code != 200:
                    logger.error(f"❌ Confluence API error: {response.status_code} - {response.text}")
                    return False
                
                space_data = response.json()
                logger.info(f"✅ Confluence space '{space_data['name']}' is accessible")
                return True
                
        except httpx.TimeoutException:
            logger.error("❌ Confluence connection timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to validate Confluence config: {e}")
            return False
    
    async def extract_content(self) -> Dict[str, Any]:
        """Extract content from Confluence space"""
        logger.info(f"📤 Extracting content from Confluence space: {self.confluence_config.space_key}")
        
        content_items = []
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # 1. Get space metadata
                space_metadata = await self._get_space_metadata(client)
                
                # 2. Extract pages from the space
                pages = await self._extract_pages(client)
                content_items.extend(pages)
                
                # 3. Extract attachments if enabled
                if self.confluence_config.include_attachments:
                    attachments = await self._extract_attachments(client, pages)
                    content_items.extend(attachments)
                
                # 4. Extract comments if enabled
                if self.confluence_config.include_comments:
                    comments = await self._extract_comments(client, pages)
                    content_items.extend(comments)
                
                logger.info(f"✅ Extracted {len(content_items)} items from Confluence space")
                
                return {
                    "content": content_items,
                    "metadata": {
                        "source": "confluence_connector",
                        "space_key": self.confluence_config.space_key,
                        "space_name": space_metadata.get("name", "Unknown"),
                        "base_url": self.base_url,
                        "extracted_at": datetime.now().isoformat(),
                        "total_items": len(content_items),
                        "include_attachments": self.confluence_config.include_attachments,
                        "include_comments": self.confluence_config.include_comments,
                        "page_filter": self.confluence_config.page_filter
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to extract content from Confluence: {e}")
            return {
                "content": [],
                "metadata": {"source": "confluence_connector", "error": str(e)},
                "error": str(e)
            }
    
    async def _get_space_metadata(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get space metadata"""
        try:
            space_url = f"{self.api_base}/space/{self.confluence_config.space_key}"
            response = await client.get(space_url, headers=self.headers)
            
            if response.status_code == 200:
                space_data = response.json()
                logger.info(f"📊 Space: {space_data['name']} ({space_data['type']})")
                return space_data
            else:
                logger.warning(f"Failed to get space metadata: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.warning(f"Failed to get space metadata: {e}")
            return {}
    
    async def _extract_pages(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Extract pages from Confluence space"""
        logger.info("📄 Extracting pages...")
        
        pages = []
        start = 0
        limit = 50  # Confluence API pagination limit
        
        try:
            while True:
                # Build CQL query for pages
                cql_query = f"space = {self.confluence_config.space_key} AND type = page"
                
                # Add custom page filter if specified
                if self.confluence_config.page_filter:
                    cql_query += f" AND ({self.confluence_config.page_filter})"
                
                # Query pages with content expansion
                search_url = f"{self.api_base}/content/search"
                params = {
                    'cql': cql_query,
                    'start': start,
                    'limit': limit,
                    'expand': 'body.storage,history.lastUpdated,space,ancestors,version,metadata.labels'
                }
                
                response = await client.get(search_url, headers=self.headers, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch pages: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                page_results = data.get('results', [])
                
                if not page_results:
                    break
                
                # Process each page
                for page_data in page_results:
                    try:
                        page_item = await self._process_page(page_data)
                        if page_item:
                            pages.append(page_item)
                    except Exception as e:
                        logger.warning(f"Failed to process page {page_data.get('id', 'unknown')}: {e}")
                        continue
                
                # Check if we have more pages
                if len(page_results) < limit:
                    break
                
                start += limit
                
                # Safety limit to prevent infinite loops
                if start >= 1000:  # Max 1000 pages
                    logger.warning(f"Reached maximum page limit (1000) for space {self.confluence_config.space_key}")
                    break
        
        except Exception as e:
            logger.error(f"Failed to extract pages: {e}")
        
        logger.info(f"📄 Extracted {len(pages)} pages")
        return pages
    
    async def _process_page(self, page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single Confluence page"""
        try:
            page_id = page_data['id']
            title = page_data['title']
            
            # Extract content from storage format (Confluence's internal format)
            content_html = ""
            if 'body' in page_data and 'storage' in page_data['body']:
                content_html = page_data['body']['storage']['value']
            
            # Convert HTML to plain text for better processing
            content_text = self._html_to_text(content_html)
            
            # Skip empty pages
            if not content_text.strip():
                logger.debug(f"Skipping empty page: {title}")
                return None
            
            # Generate unique ID
            unique_id = f"confluence_{self.confluence_config.space_key}_{page_id}"
            
            # Extract metadata
            space_info = page_data.get('space', {})
            version_info = page_data.get('version', {})
            history = page_data.get('history', {})
            
            # Build page URL
            page_url = f"{self.base_url}/pages/viewpage.action?pageId={page_id}"
            
            # Extract ancestors for navigation path
            ancestors = page_data.get('ancestors', [])
            breadcrumb = []
            for ancestor in ancestors:
                breadcrumb.append(ancestor.get('title', 'Unknown'))
            
            # Extract labels/tags
            labels = []
            metadata = page_data.get('metadata', {})
            if 'labels' in metadata:
                labels = [label['name'] for label in metadata['labels'].get('results', [])]
            
            # Get last updated info
            last_updated = None
            last_updated_by = None
            if history and 'lastUpdated' in history:
                last_updated_info = history['lastUpdated']
                last_updated = last_updated_info.get('when')
                if 'by' in last_updated_info:
                    last_updated_by = last_updated_info['by'].get('displayName', 'Unknown')
            
            return {
                "id": unique_id,
                "type": "documentation",
                "title": title,
                "content": content_text,
                "url": page_url,
                "metadata": {
                    "confluence_id": page_id,
                    "space_key": space_info.get('key', self.confluence_config.space_key),
                    "space_name": space_info.get('name', 'Unknown'),
                    "content_type": "confluence_page",
                    "version": version_info.get('number', 1),
                    "created_date": page_data.get('createdDate'),
                    "last_updated": last_updated,
                    "last_updated_by": last_updated_by,
                    "breadcrumb": breadcrumb,
                    "labels": labels,
                    "page_length": len(content_text),
                    "html_content": content_html[:1000] + "..." if len(content_html) > 1000 else content_html,  # Keep some HTML for reference
                    "extractable_links": self._extract_links(content_html),
                    "has_attachments": len(page_data.get('descendants', {}).get('attachment', [])) > 0 if 'descendants' in page_data else False
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to process page {page_data.get('id', 'unknown')}: {e}")
            return None
    
    async def _extract_attachments(self, client: httpx.AsyncClient, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract attachments from pages"""
        logger.info("📎 Extracting attachments...")
        
        attachments = []
        
        try:
            for page in pages:
                page_id = page['metadata']['confluence_id']
                
                # Get attachments for this page
                attachments_url = f"{self.api_base}/content/{page_id}/child/attachment"
                params = {
                    'expand': 'version,metadata,container'
                }
                
                response = await client.get(attachments_url, headers=self.headers, params=params)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                attachment_results = data.get('results', [])
                
                for attachment_data in attachment_results:
                    try:
                        attachment_item = await self._process_attachment(attachment_data, page)
                        if attachment_item:
                            attachments.append(attachment_item)
                    except Exception as e:
                        logger.warning(f"Failed to process attachment {attachment_data.get('id', 'unknown')}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Failed to extract attachments: {e}")
        
        logger.info(f"📎 Extracted {len(attachments)} attachments")
        return attachments
    
    async def _process_attachment(self, attachment_data: Dict[str, Any], parent_page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single attachment"""
        try:
            attachment_id = attachment_data['id']
            title = attachment_data['title']
            
            # Only process text-based attachments for now
            media_type = attachment_data.get('metadata', {}).get('mediaType', '')
            if not self._is_processable_attachment(media_type):
                logger.debug(f"Skipping non-text attachment: {title} ({media_type})")
                return None
            
            # Generate unique ID
            unique_id = f"confluence_attachment_{attachment_id}"
            
            # Build download URL
            download_link = attachment_data.get('_links', {}).get('download', '')
            if download_link:
                download_url = urljoin(self.base_url, download_link)
            else:
                download_url = f"{self.base_url}/download/attachments/{parent_page['metadata']['confluence_id']}/{quote(title)}"
            
            # Extract metadata
            version_info = attachment_data.get('version', {})
            metadata = attachment_data.get('metadata', {})
            container = attachment_data.get('container', {})
            
            return {
                "id": unique_id,
                "type": "document",
                "title": f"📎 {title} (from {parent_page['title']})",
                "content": f"Attachment: {title}\nParent Page: {parent_page['title']}\nMedia Type: {media_type}\nDownload URL: {download_url}",
                "url": download_url,
                "metadata": {
                    "confluence_id": attachment_id,
                    "parent_page_id": parent_page['metadata']['confluence_id'],
                    "parent_page_title": parent_page['title'],
                    "content_type": "confluence_attachment",
                    "media_type": media_type,
                    "file_size": metadata.get('fileSize', 0),
                    "version": version_info.get('number', 1),
                    "created_date": attachment_data.get('createdDate'),
                    "download_url": download_url,
                    "space_key": container.get('key', self.confluence_config.space_key)
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to process attachment {attachment_data.get('id', 'unknown')}: {e}")
            return None
    
    async def _extract_comments(self, client: httpx.AsyncClient, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract comments from pages"""
        logger.info("💬 Extracting comments...")
        
        comments = []
        
        try:
            for page in pages:
                page_id = page['metadata']['confluence_id']
                
                # Get comments for this page
                comments_url = f"{self.api_base}/content/{page_id}/child/comment"
                params = {
                    'expand': 'body.storage,version,history.lastUpdated,container',
                    'limit': 200  # Get up to 200 comments per page
                }
                
                response = await client.get(comments_url, headers=self.headers, params=params)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                comment_results = data.get('results', [])
                
                for comment_data in comment_results:
                    try:
                        comment_item = await self._process_comment(comment_data, page)
                        if comment_item:
                            comments.append(comment_item)
                    except Exception as e:
                        logger.warning(f"Failed to process comment {comment_data.get('id', 'unknown')}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Failed to extract comments: {e}")
        
        logger.info(f"💬 Extracted {len(comments)} comments")
        return comments
    
    async def _process_comment(self, comment_data: Dict[str, Any], parent_page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single comment"""
        try:
            comment_id = comment_data['id']
            title = comment_data.get('title', f"Comment on {parent_page['title']}")
            
            # Extract content from storage format
            content_html = ""
            if 'body' in comment_data and 'storage' in comment_data['body']:
                content_html = comment_data['body']['storage']['value']
            
            # Convert HTML to plain text
            content_text = self._html_to_text(content_html)
            
            # Skip empty comments
            if not content_text.strip():
                return None
            
            # Generate unique ID
            unique_id = f"confluence_comment_{comment_id}"
            
            # Extract metadata
            version_info = comment_data.get('version', {})
            history = comment_data.get('history', {})
            container = comment_data.get('container', {})
            
            # Get author info
            author_info = version_info.get('by', {})
            author_name = author_info.get('displayName', 'Unknown')
            
            # Get creation/update info
            created_date = comment_data.get('createdDate')
            last_updated = None
            if history and 'lastUpdated' in history:
                last_updated = history['lastUpdated'].get('when')
            
            return {
                "id": unique_id,
                "type": "conversation",
                "title": title,
                "content": content_text,
                "url": f"{parent_page['url']}#comment-{comment_id}",
                "metadata": {
                    "confluence_id": comment_id,
                    "parent_page_id": parent_page['metadata']['confluence_id'],
                    "parent_page_title": parent_page['title'],
                    "content_type": "confluence_comment",
                    "author": author_name,
                    "author_account_id": author_info.get('accountId', ''),
                    "version": version_info.get('number', 1),
                    "created_date": created_date,
                    "last_updated": last_updated,
                    "comment_length": len(content_text),
                    "space_key": container.get('key', self.confluence_config.space_key)
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to process comment {comment_data.get('id', 'unknown')}: {e}")
            return None
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text"""
        if not html_content:
            return ""
        
        try:
            # Unescape HTML entities
            text = html.unescape(html_content)
            
            # Remove Confluence-specific macros and structured content
            # Remove macro placeholders
            text = re.sub(r'<ac:structured-macro[^>]*>.*?</ac:structured-macro>', '', text, flags=re.DOTALL)
            text = re.sub(r'<ac:image[^>]*>.*?</ac:image>', '[IMAGE]', text, flags=re.DOTALL)
            text = re.sub(r'<ac:link[^>]*>.*?</ac:link>', '[LINK]', text, flags=re.DOTALL)
            
            # Remove HTML tags but keep content
            text = re.sub(r'<[^>]+>', '', text)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.debug(f"Failed to convert HTML to text: {e}")
            return html_content
    
    def _extract_links(self, html_content: str) -> List[Dict[str, str]]:
        """Extract links from HTML content"""
        links = []
        
        if not html_content:
            return links
        
        try:
            # Extract standard HTML links
            html_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', html_content, re.IGNORECASE)
            for url, text in html_links:
                links.append({"url": url, "text": text.strip()})
            
            # Extract Confluence-specific links
            ac_links = re.findall(r'<ac:link[^>]*>.*?<ri:page[^>]+ri:content-title=["\']([^"\']+)["\'][^>]*/>.*?</ac:link>', html_content, re.DOTALL)
            for page_title in ac_links:
                links.append({"url": f"confluence://page/{page_title}", "text": page_title})
            
        except Exception as e:
            logger.debug(f"Failed to extract links: {e}")
        
        return links[:10]  # Limit to 10 links to avoid overwhelming metadata
    
    def _is_processable_attachment(self, media_type: str) -> bool:
        """Check if attachment can be processed for content extraction"""
        processable_types = [
            'text/',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument',
            'application/vnd.oasis.opendocument'
        ]
        
        return any(media_type.startswith(ptype) for ptype in processable_types) 