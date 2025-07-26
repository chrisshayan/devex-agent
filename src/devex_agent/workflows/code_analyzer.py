"""
Code Analyzer - Sophisticated code analysis for DevEx Ambient Agent
Provides LLM-powered code analysis, pattern detection, and vector similarity search
"""

import ast
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import asyncio

from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pygments import highlight
from pygments.lexers import get_lexer_by_name

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Advanced code analyzer with LLM and vector search capabilities"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.llm = None
        self.vector_store = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\nclass ", "\n\ndef ", "\n\n", "\n", " ", ""]
        )
        
        # Initialize Tree-sitter parsers
        self.parsers = {}
        self._init_parsers()
        
        # Initialize LLM and vector store
        if openai_api_key:
            self._init_llm(openai_api_key)
            self._init_vector_store()
    
    def _init_parsers(self):
        """Initialize Tree-sitter parsers for different languages"""
        try:
            # Note: Tree-sitter parsers require specific initialization
            # For now, we'll skip Tree-sitter parsing and focus on LLM analysis
            logger.info("⚠️ Tree-sitter parsers disabled for compatibility")
            
        except Exception as e:
            logger.warning(f"Failed to initialize some parsers: {e}")
    
    def _init_llm(self, api_key: str):
        """Initialize OpenAI LLM"""
        try:
            self.llm = ChatOpenAI(
                api_key=api_key,
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=1000
            )
            logger.info("✅ Initialized OpenAI LLM")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
    
    def _init_vector_store(self):
        """Initialize ChromaDB vector store for code similarity search"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Initialize empty vector store
            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                persist_directory="./data/code_vectors"
            )
            logger.info("✅ Initialized ChromaDB vector store")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
    
    async def analyze_code_changes(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze code changes across multiple events"""
        file_changes = [e for e in events if e.get("type") == "file_changed"]
        
        if not file_changes:
            return {"analysis": "No code changes detected", "patterns": [], "suggestions": []}
        
        analysis_results = {
            "total_files": len(file_changes),
            "languages_detected": set(),
            "complexity_analysis": {},
            "pattern_detection": [],
            "quality_issues": [],
            "security_concerns": [],
            "performance_insights": [],
            "suggestions": []
        }
        
        for event in file_changes:
            file_path = event.get("file_path", "")
            file_name = Path(file_path).name if file_path else "unknown"
            
            # Detect language
            language = self._detect_language(file_path)
            analysis_results["languages_detected"].add(language)
            
            # Analyze file metadata
            metadata = event.get("metadata", {})
            lines_added = metadata.get("lines_added", 0)
            lines_deleted = metadata.get("lines_deleted", 0)
            
            # Perform complexity analysis
            complexity = self._analyze_complexity(lines_added, lines_deleted, metadata)
            analysis_results["complexity_analysis"][file_name] = complexity
            
            # Generate file-specific insights
            if self.llm:
                file_insights = await self._llm_analyze_file_change(event)
                analysis_results["pattern_detection"].extend(file_insights.get("patterns", []))
                analysis_results["quality_issues"].extend(file_insights.get("quality_issues", []))
                analysis_results["security_concerns"].extend(file_insights.get("security_concerns", []))
        
        # Convert set to list for JSON serialization
        analysis_results["languages_detected"] = list(analysis_results["languages_detected"])
        
        # Generate overall suggestions
        analysis_results["suggestions"] = await self._generate_code_suggestions(analysis_results)
        
        return analysis_results
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        if not file_path:
            return "unknown"
        
        extension = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".kt": "kotlin",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".sql": "sql",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml"
        }
        
        return language_map.get(extension, "unknown")
    
    def _analyze_complexity(self, lines_added: int, lines_deleted: int, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code complexity based on change metrics"""
        net_change = lines_added - lines_deleted
        total_change = lines_added + lines_deleted
        
        complexity_score = 0
        
        # Size-based complexity
        if total_change > 100:
            complexity_score += 3
        elif total_change > 50:
            complexity_score += 2
        elif total_change > 20:
            complexity_score += 1
        
        # Change type analysis
        change_type = metadata.get("change_type", "unknown")
        if change_type == "refactoring":
            complexity_score += 2
        elif change_type == "new_feature":
            complexity_score += 1
        
        # Function/class additions
        if metadata.get("function_added"):
            complexity_score += 1
        if metadata.get("class_added"):
            complexity_score += 2
        
        complexity_level = "low"
        if complexity_score >= 5:
            complexity_level = "high"
        elif complexity_score >= 3:
            complexity_level = "medium"
        
        return {
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "net_change": net_change,
            "total_change": total_change,
            "complexity_score": complexity_score,
            "complexity_level": complexity_level
        }
    
    async def _llm_analyze_file_change(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze individual file changes"""
        if not self.llm:
            return {"patterns": [], "quality_issues": [], "security_concerns": []}
        
        file_path = event.get("file_path", "unknown")
        description = event.get("description", "")
        metadata = event.get("metadata", {})
        
        prompt = f"""
Analyze this code change event for potential issues and patterns:

File: {Path(file_path).name}
Description: {description}
Metadata: {metadata}

Please identify:
1. Code quality concerns
2. Security issues
3. Performance implications
4. Common patterns or anti-patterns

Respond in JSON format with arrays for each category.
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content
            
            # Parse LLM response (simplified - would need better parsing in production)
            if "quality" in content.lower():
                quality_issues = ["Potential code quality concern detected"]
            else:
                quality_issues = []
            
            if "security" in content.lower():
                security_concerns = ["Potential security issue identified"]
            else:
                security_concerns = []
            
            if "pattern" in content.lower():
                patterns = ["Code pattern detected"]
            else:
                patterns = []
            
            return {
                "patterns": patterns,
                "quality_issues": quality_issues,
                "security_concerns": security_concerns,
                "llm_response": content
            }
        
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {"patterns": [], "quality_issues": [], "security_concerns": []}
    
    async def _generate_code_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable suggestions based on code analysis"""
        suggestions = []
        
        # Complexity-based suggestions
        high_complexity_files = [
            name for name, data in analysis["complexity_analysis"].items()
            if data["complexity_level"] == "high"
        ]
        
        if high_complexity_files:
            suggestions.append({
                "type": "complexity",
                "title": "Review high-complexity changes",
                "description": f"Files with high complexity: {', '.join(high_complexity_files[:3])}",
                "priority": "medium",
                "action": "code_review"
            })
        
        # Quality issue suggestions
        if analysis["quality_issues"]:
            suggestions.append({
                "type": "quality",
                "title": "Address code quality issues",
                "description": f"Found {len(analysis['quality_issues'])} potential quality concerns",
                "priority": "medium",
                "action": "quality_review"
            })
        
        # Security suggestions
        if analysis["security_concerns"]:
            suggestions.append({
                "type": "security",
                "title": "Review security implications",
                "description": f"Identified {len(analysis['security_concerns'])} security considerations",
                "priority": "high",
                "action": "security_review"
            })
        
        # Language-specific suggestions
        languages = analysis["languages_detected"]
        if len(languages) > 3:
            suggestions.append({
                "type": "focus",
                "title": "Multiple languages detected",
                "description": f"Working across {len(languages)} languages: {', '.join(languages)}",
                "priority": "low",
                "action": "focus_review"
            })
        
        return suggestions
    
    async def find_similar_code_patterns(self, code_snippet: str, language: str) -> List[Dict[str, Any]]:
        """Find similar code patterns using vector similarity search"""
        if not self.vector_store:
            return []
        
        try:
            # Create document for the code snippet
            doc = Document(
                page_content=code_snippet,
                metadata={"language": language, "type": "code_snippet"}
            )
            
            # Search for similar patterns
            similar_docs = self.vector_store.similarity_search(
                code_snippet, 
                k=5,
                filter={"language": language}
            )
            
            patterns = []
            for doc in similar_docs:
                patterns.append({
                    "content": doc.page_content[:200] + "...",
                    "similarity_score": 0.85,  # Placeholder - would get actual score
                    "metadata": doc.metadata
                })
            
            return patterns
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def add_code_to_vector_store(self, code_content: str, file_path: str, language: str):
        """Add code to vector store for future similarity searches"""
        if not self.vector_store:
            return
        
        try:
            # Split code into chunks
            chunks = self.text_splitter.split_text(code_content)
            
            # Create documents
            docs = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "file_path": file_path,
                        "language": language,
                        "chunk_id": i,
                        "timestamp": str(asyncio.get_event_loop().time())
                    }
                )
                docs.append(doc)
            
            # Add to vector store
            self.vector_store.add_documents(docs)
            logger.debug(f"Added {len(docs)} code chunks to vector store")
        
        except Exception as e:
            logger.error(f"Failed to add code to vector store: {e}")
    
    async def analyze_build_patterns(self, build_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze build patterns and failures"""
        if not build_events:
            return {"analysis": "No build events to analyze"}
        
        failed_builds = [e for e in build_events if e.get("metadata", {}).get("build_status") == "failed"]
        successful_builds = [e for e in build_events if e.get("metadata", {}).get("build_status") == "success"]
        
        analysis = {
            "total_builds": len(build_events),
            "successful_builds": len(successful_builds),
            "failed_builds": len(failed_builds),
            "success_rate": len(successful_builds) / len(build_events) if build_events else 0,
            "patterns": [],
            "recommendations": []
        }
        
        # Analyze failure patterns
        if failed_builds:
            error_types = {}
            for build in failed_builds:
                error_type = build.get("metadata", {}).get("error_type", "unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            analysis["failure_patterns"] = error_types
            
            # Generate recommendations
            if error_types.get("syntax_error", 0) > 1:
                analysis["recommendations"].append({
                    "type": "syntax",
                    "title": "Consider using a linter",
                    "description": "Multiple syntax errors detected - automated linting could help"
                })
        
        return analysis 