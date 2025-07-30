"""
CodeBERT Engine - Core semantic code understanding using Microsoft CodeBERT models

Provides embeddings generation, semantic similarity, and code pattern analysis
using the CodeBERT family of models (CodeBERT, GraphCodeBERT, UniXcoder).
"""

import logging
import asyncio
import hashlib
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
import torch
from transformers import AutoModel, AutoTokenizer, AutoConfig
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pickle
import json

# Import performance utilities
try:
    from ..utils.performance import cached, timed, run_parallel
    PERFORMANCE_UTILS_AVAILABLE = True
except ImportError:
    PERFORMANCE_UTILS_AVAILABLE = False
    def cached(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def timed(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


class CodeBERTEngine:
    """
    Core CodeBERT engine for semantic code understanding
    
    Supports multiple CodeBERT models:
    - microsoft/codebert-base: General code understanding
    - microsoft/graphcodebert-base: Graph-enhanced code understanding  
    - microsoft/unixcoder-base: Unified encoder-decoder for code
    """
    
    def __init__(self, 
                 model_cache_dir: str = "./data/ml_models",
                 default_model: str = "microsoft/codebert-base",
                 device: str = "auto"):
        """
        Initialize CodeBERT engine
        
        Args:
            model_cache_dir: Directory to cache downloaded models
            default_model: Default model to use for operations
            device: Computing device ('auto', 'cpu', 'cuda')
        """
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Device configuration
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # Supported models
        self.supported_models = {
            "codebert": "microsoft/codebert-base",
            "graphcodebert": "microsoft/graphcodebert-base", 
            "unixcoder": "microsoft/unixcoder-base"
        }
        
        self.default_model = default_model
        
        # Model storage
        self.models = {}
        self.tokenizers = {}
        self.configs = {}
        
        # Embedding cache for performance
        self.embedding_cache = {}
        self.cache_max_size = 10000
        
        # Processing limits
        self.max_token_length = 512
        self.max_code_length = 4000  # characters
        
        self.is_initialized = False
        logger.info(f"🤖 CodeBERT Engine initialized (device: {self.device})")
    
    async def initialize(self, preload_models: List[str] = None):
        """
        Initialize the CodeBERT engine and optionally preload models
        
        Args:
            preload_models: List of model names to preload
        """
        try:
            logger.info("🔄 Initializing CodeBERT Engine...")
            
            # Preload specified models
            if preload_models:
                for model_name in preload_models:
                    await self._load_model(model_name)
            else:
                # Load default model
                await self._load_model(self.default_model)
            
            self.is_initialized = True
            logger.info("✅ CodeBERT Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize CodeBERT Engine: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup CodeBERT engine resources"""
        logger.info("🧹 Cleaning up CodeBERT Engine...")
        
        # Clear models from memory
        self.models.clear()
        self.tokenizers.clear()
        self.configs.clear()
        
        # Clear caches
        self.embedding_cache.clear()
        
        # Clear GPU memory if using CUDA
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_initialized = False
        logger.info("✅ CodeBERT Engine cleanup complete")
    
    async def _load_model(self, model_name: str):
        """Load a specific CodeBERT model"""
        try:
            if model_name in self.models:
                return  # Already loaded
            
            # Resolve model name
            resolved_name = self.supported_models.get(model_name, model_name)
            
            logger.info(f"📥 Loading model: {resolved_name}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                resolved_name,
                cache_dir=str(self.model_cache_dir)
            )
            
            # Load model configuration
            config = AutoConfig.from_pretrained(
                resolved_name,
                cache_dir=str(self.model_cache_dir)
            )
            
            # Load model
            model = AutoModel.from_pretrained(
                resolved_name,
                config=config,
                cache_dir=str(self.model_cache_dir)
            )
            
            # Move to device
            model = model.to(self.device)
            model.eval()  # Set to evaluation mode
            
            # Store
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            self.configs[model_name] = config
            
            logger.info(f"✅ Model loaded: {resolved_name} (device: {self.device})")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_name}: {e}")
            raise
    
    @timed(operation_name="codebert_embedding_generation")
    async def generate_embeddings(self, 
                                code_snippets: List[str], 
                                model_name: str = None,
                                batch_size: int = 8) -> List[List[float]]:
        """
        Generate CodeBERT embeddings for code snippets
        
        Args:
            code_snippets: List of code strings to embed
            model_name: Model to use (defaults to default_model)
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not self.is_initialized:
            raise RuntimeError("CodeBERT Engine not initialized")
        
        model_name = model_name or self.default_model
        
        # Ensure model is loaded
        if model_name not in self.models:
            await self._load_model(model_name)
        
        model = self.models[model_name]
        tokenizer = self.tokenizers[model_name]
        
        logger.info(f"🔮 Generating embeddings for {len(code_snippets)} code snippets")
        
        embeddings = []
        
        try:
            # Process in batches
            for i in range(0, len(code_snippets), batch_size):
                batch = code_snippets[i:i + batch_size]
                batch_embeddings = await self._generate_batch_embeddings(
                    batch, model, tokenizer
                )
                embeddings.extend(batch_embeddings)
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            raise
    
    async def _generate_batch_embeddings(self, 
                                       code_batch: List[str], 
                                       model, 
                                       tokenizer) -> List[List[float]]:
        """Generate embeddings for a batch of code snippets"""
        
        # Check cache first
        cached_embeddings = []
        uncached_codes = []
        uncached_indices = []
        
        for idx, code in enumerate(code_batch):
            cache_key = self._generate_cache_key(code)
            if cache_key in self.embedding_cache:
                cached_embeddings.append((idx, self.embedding_cache[cache_key]))
            else:
                uncached_codes.append(code)
                uncached_indices.append(idx)
        
        # Generate embeddings for uncached codes
        new_embeddings = []
        if uncached_codes:
            # Preprocess code
            processed_codes = [self._preprocess_code(code) for code in uncached_codes]
            
            # Tokenize
            inputs = tokenizer(
                processed_codes,
                padding=True,
                truncation=True,
                max_length=self.max_token_length,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embeddings
            with torch.no_grad():
                outputs = model(**inputs)
                
                # Extract embeddings (CLS token or mean pooling)
                if hasattr(outputs, 'last_hidden_state'):
                    # Use CLS token (first token)
                    embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                else:
                    # Fallback to pooler output
                    embeddings = outputs.pooler_output.cpu().numpy()
            
            # Convert to list and cache
            for idx, code, embedding in zip(uncached_indices, uncached_codes, embeddings):
                embedding_list = embedding.tolist()
                new_embeddings.append((idx, embedding_list))
                
                # Cache the embedding
                cache_key = self._generate_cache_key(code)
                self._add_to_cache(cache_key, embedding_list)
        
        # Combine cached and new embeddings
        all_embeddings = [(0, [0.0] * 768)] * len(code_batch)  # Initialize
        
        for idx, embedding in cached_embeddings + new_embeddings:
            all_embeddings[idx] = (idx, embedding)
        
        return [embedding for _, embedding in all_embeddings]
    
    def _preprocess_code(self, code: str) -> str:
        """Preprocess code for better CodeBERT understanding"""
        # Remove excessive whitespace
        code = " ".join(code.split())
        
        # Truncate if too long
        if len(code) > self.max_code_length:
            code = code[:self.max_code_length] + "..."
        
        return code
    
    def _generate_cache_key(self, code: str) -> str:
        """Generate cache key for code snippet"""
        return hashlib.md5(code.encode()).hexdigest()
    
    def _add_to_cache(self, key: str, embedding: List[float]):
        """Add embedding to cache with LRU eviction"""
        if len(self.embedding_cache) >= self.cache_max_size:
            # Remove oldest item (simple FIFO for now)
            oldest_key = next(iter(self.embedding_cache))
            del self.embedding_cache[oldest_key]
        
        self.embedding_cache[key] = embedding
    
    @cached(ttl=3600)  # Cache for 1 hour
    async def find_similar_code(self, 
                              query_code: str, 
                              candidate_codes: List[str],
                              threshold: float = 0.7,
                              top_k: int = 10,
                              model_name: str = None) -> List[Dict[str, Any]]:
        """
        Find semantically similar code snippets
        
        Args:
            query_code: Code to find similarities for
            candidate_codes: List of candidate code snippets
            threshold: Minimum similarity threshold
            top_k: Maximum number of results
            model_name: Model to use for embeddings
            
        Returns:
            List of similar code with similarity scores
        """
        logger.info(f"🔍 Finding similar code among {len(candidate_codes)} candidates")
        
        # Handle empty candidate codes
        if not candidate_codes:
            logger.info("No candidate codes provided for similarity comparison")
            return []
        
        try:
            # Generate embeddings
            all_codes = [query_code] + candidate_codes
            embeddings = await self.generate_embeddings(all_codes, model_name)
            
            # Validate embeddings
            if not embeddings or len(embeddings) < 2:
                logger.warning("Insufficient embeddings generated")
                return []
            
            query_embedding = np.array(embeddings[0]).reshape(1, -1)
            candidate_embeddings = np.array(embeddings[1:])
            
            # Ensure candidate_embeddings is 2D
            if candidate_embeddings.ndim == 1:
                candidate_embeddings = candidate_embeddings.reshape(1, -1)
            elif candidate_embeddings.size == 0:
                logger.warning("No valid candidate embeddings generated")
                return []
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
            
            # Create results
            results = []
            for idx, similarity in enumerate(similarities):
                if similarity >= threshold:
                    results.append({
                        "code": candidate_codes[idx],
                        "similarity_score": float(similarity),
                        "index": idx
                    })
            
            # Sort by similarity and take top_k
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            results = results[:top_k]
            
            logger.info(f"✅ Found {len(results)} similar code snippets")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to find similar code: {e}")
            return []
    
    async def analyze_code_patterns(self, 
                                  code_snippets: List[str],
                                  developer_id: str,
                                  model_name: str = None) -> Dict[str, Any]:
        """
        Analyze coding patterns in a collection of code snippets
        
        Args:
            code_snippets: List of code snippets to analyze
            developer_id: Developer identifier
            model_name: Model to use for analysis
            
        Returns:
            Pattern analysis results
        """
        logger.info(f"📊 Analyzing coding patterns for {len(code_snippets)} snippets")
        
        try:
            # Generate embeddings
            embeddings = await self.generate_embeddings(code_snippets, model_name)
            embeddings_array = np.array(embeddings)
            
            # Cluster analysis to find dominant patterns
            n_clusters = min(5, max(2, len(code_snippets) // 10))
            if len(embeddings) >= n_clusters:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(embeddings_array)
                
                # Analyze clusters
                cluster_analysis = {}
                for i in range(n_clusters):
                    cluster_codes = [code_snippets[j] for j, label in enumerate(cluster_labels) if label == i]
                    cluster_analysis[f"pattern_{i}"] = {
                        "code_count": len(cluster_codes),
                        "representative_code": cluster_codes[0] if cluster_codes else "",
                        "pattern_description": self._describe_pattern(cluster_codes)
                    }
            else:
                cluster_analysis = {"insufficient_data": "Not enough code snippets for clustering"}
            
            # Language and framework detection
            language_patterns = self._analyze_language_patterns(code_snippets)
            
            # Complexity analysis
            complexity_patterns = self._analyze_complexity_patterns(code_snippets)
            
            # Architecture patterns
            arch_patterns = self._analyze_architectural_patterns(code_snippets)
            
            # Calculate overall embeddings
            overall_embedding = np.mean(embeddings_array, axis=0).tolist()
            
            return {
                "developer_id": developer_id,
                "analysis_id": f"pattern_{developer_id}_{int(datetime.now().timestamp())}",
                "analyzed_at": datetime.now(),
                "total_snippets": len(code_snippets),
                "dominant_patterns": cluster_analysis,
                "language_patterns": language_patterns,
                "complexity_patterns": complexity_patterns,
                "architectural_patterns": arch_patterns,
                "overall_embedding": overall_embedding,
                "embedding_dimension": len(overall_embedding)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze code patterns: {e}")
            raise
    
    def _describe_pattern(self, code_snippets: List[str]) -> str:
        """Generate a description for a pattern cluster"""
        if not code_snippets:
            return "Empty pattern"
        
        # Simple heuristic-based pattern description
        all_code = " ".join(code_snippets).lower()
        
        if "class" in all_code and "def __init__" in all_code:
            return "Object-oriented class definitions"
        elif "def " in all_code:
            return "Function definitions"
        elif "import " in all_code:
            return "Import and dependency statements"
        elif "if " in all_code and "else" in all_code:
            return "Conditional logic patterns"
        elif "for " in all_code or "while " in all_code:
            return "Loop and iteration patterns"
        elif "try:" in all_code and "except" in all_code:
            return "Error handling patterns"
        else:
            return "General code patterns"
    
    def _analyze_language_patterns(self, code_snippets: List[str]) -> Dict[str, Any]:
        """Analyze programming language usage patterns"""
        patterns = {
            "python": 0, "javascript": 0, "java": 0, "typescript": 0,
            "go": 0, "rust": 0, "cpp": 0, "c": 0
        }
        
        for code in code_snippets:
            code_lower = code.lower()
            
            # Python indicators
            if any(indicator in code_lower for indicator in ["def ", "import ", "python", "self.", "__init__"]):
                patterns["python"] += 1
            
            # JavaScript indicators
            if any(indicator in code_lower for indicator in ["function", "const ", "let ", "var ", "=>"]):
                patterns["javascript"] += 1
            
            # Java indicators
            if any(indicator in code_lower for indicator in ["public class", "private ", "import java"]):
                patterns["java"] += 1
            
            # TypeScript indicators
            if any(indicator in code_lower for indicator in [": string", ": number", "interface "]):
                patterns["typescript"] += 1
        
        total = sum(patterns.values())
        if total > 0:
            patterns = {k: v/total for k, v in patterns.items()}
        
        return patterns
    
    def _analyze_complexity_patterns(self, code_snippets: List[str]) -> Dict[str, Any]:
        """Analyze code complexity patterns"""
        complexity_indicators = {
            "simple": 0,      # Short, straightforward code
            "moderate": 0,    # Medium complexity
            "complex": 0      # High complexity
        }
        
        for code in code_snippets:
            lines = len(code.split('\n'))
            nesting_level = max(code.count('    ' * i) for i in range(1, 6))
            
            if lines <= 10 and nesting_level <= 2:
                complexity_indicators["simple"] += 1
            elif lines <= 30 and nesting_level <= 4:
                complexity_indicators["moderate"] += 1
            else:
                complexity_indicators["complex"] += 1
        
        total = sum(complexity_indicators.values())
        if total > 0:
            complexity_indicators = {k: v/total for k, v in complexity_indicators.items()}
        
        return complexity_indicators
    
    def _analyze_architectural_patterns(self, code_snippets: List[str]) -> Dict[str, float]:
        """Analyze architectural pattern usage"""
        patterns = {
            "mvc": 0, "singleton": 0, "factory": 0, "observer": 0,
            "strategy": 0, "decorator": 0, "repository": 0
        }
        
        all_code = " ".join(code_snippets).lower()
        
        # Pattern detection heuristics
        if "controller" in all_code and "model" in all_code:
            patterns["mvc"] = 0.8
        
        if "instance" in all_code and "singleton" in all_code:
            patterns["singleton"] = 0.7
        
        if "factory" in all_code or "create" in all_code:
            patterns["factory"] = 0.6
        
        if "observer" in all_code or "notify" in all_code:
            patterns["observer"] = 0.6
        
        if "strategy" in all_code or "algorithm" in all_code:
            patterns["strategy"] = 0.5
        
        if "decorator" in all_code or "@" in all_code:
            patterns["decorator"] = 0.7
        
        if "repository" in all_code or "save" in all_code:
            patterns["repository"] = 0.6
        
        return patterns
    
    async def assess_skill_level(self, 
                               code_snippets: List[str],
                               skill_name: str,
                               golden_source_embeddings: Optional[List[List[float]]] = None) -> Dict[str, Any]:
        """
        Assess skill level based on code quality and similarity to golden sources
        
        Args:
            code_snippets: Developer's code snippets
            skill_name: Skill being assessed
            golden_source_embeddings: Pre-computed golden source embeddings
            
        Returns:
            Skill assessment results
        """
        logger.info(f"📏 Assessing skill level for: {skill_name}")
        
        try:
            # Generate embeddings for developer's code
            dev_embeddings = await self.generate_embeddings(code_snippets)
            dev_embeddings_array = np.array(dev_embeddings)
            
            # Calculate skill indicators
            skill_indicators = {
                "code_quality": self._assess_code_quality(code_snippets),
                "pattern_sophistication": self._assess_pattern_sophistication(code_snippets),
                "consistency": self._assess_consistency(dev_embeddings_array),
                "complexity_handling": self._assess_complexity_handling(code_snippets)
            }
            
            # Compare with golden sources if available
            golden_source_similarity = 0.0
            if golden_source_embeddings:
                golden_array = np.array(golden_source_embeddings)
                similarities = cosine_similarity(dev_embeddings_array, golden_array)
                golden_source_similarity = float(np.mean(similarities))
            
            # Calculate overall skill level
            weights = {"code_quality": 0.3, "pattern_sophistication": 0.25, 
                      "consistency": 0.2, "complexity_handling": 0.25}
            
            overall_level = sum(indicator * weights[name] 
                              for name, indicator in skill_indicators.items())
            
            # Adjust based on golden source similarity
            if golden_source_similarity > 0:
                overall_level = (overall_level * 0.7) + (golden_source_similarity * 0.3)
            
            return {
                "skill_name": skill_name,
                "overall_level": float(np.clip(overall_level, 0.0, 1.0)),
                "skill_indicators": skill_indicators,
                "golden_source_similarity": golden_source_similarity,
                "assessment_confidence": self._calculate_confidence(len(code_snippets)),
                "assessment_method": "codebert_semantic_analysis",
                "assessed_at": datetime.now(),
                "evidence": self._generate_evidence(code_snippets, skill_indicators)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to assess skill level: {e}")
            raise
    
    def _assess_code_quality(self, code_snippets: List[str]) -> float:
        """Assess overall code quality"""
        quality_score = 0.0
        
        for code in code_snippets:
            # Basic quality indicators
            has_comments = "#" in code or "//" in code or "/*" in code
            proper_naming = not any(char.isdigit() for char in code.split()[0] if code.split())
            reasonable_length = 10 <= len(code.split('\n')) <= 100
            
            snippet_score = 0.0
            if has_comments:
                snippet_score += 0.3
            if proper_naming:
                snippet_score += 0.4
            if reasonable_length:
                snippet_score += 0.3
            
            quality_score += snippet_score
        
        return quality_score / len(code_snippets) if code_snippets else 0.0
    
    def _assess_pattern_sophistication(self, code_snippets: List[str]) -> float:
        """Assess sophistication of coding patterns"""
        sophistication_indicators = [
            "design pattern", "abstraction", "interface", "polymorphism",
            "inheritance", "composition", "dependency injection", "factory",
            "observer", "strategy", "decorator", "async", "await"
        ]
        
        total_indicators = 0
        found_indicators = 0
        
        for code in code_snippets:
            code_lower = code.lower()
            for indicator in sophistication_indicators:
                total_indicators += 1
                if indicator in code_lower:
                    found_indicators += 1
        
        return found_indicators / total_indicators if total_indicators > 0 else 0.0
    
    def _assess_consistency(self, embeddings_array: np.ndarray) -> float:
        """Assess consistency in coding style"""
        if len(embeddings_array) < 2:
            return 1.0
        
        # Calculate pairwise similarities
        similarities = cosine_similarity(embeddings_array)
        
        # Get upper triangle (excluding diagonal)
        upper_triangle = similarities[np.triu_indices_from(similarities, k=1)]
        
        # Consistency is the mean similarity
        consistency = float(np.mean(upper_triangle))
        
        return consistency
    
    def _assess_complexity_handling(self, code_snippets: List[str]) -> float:
        """Assess ability to handle complex code structures"""
        complexity_score = 0.0
        
        for code in code_snippets:
            # Complexity indicators
            has_error_handling = "try" in code and "except" in code
            has_loops = "for " in code or "while " in code
            has_conditionals = "if " in code
            has_functions = "def " in code or "function " in code
            
            snippet_score = sum([has_error_handling, has_loops, has_conditionals, has_functions]) / 4
            complexity_score += snippet_score
        
        return complexity_score / len(code_snippets) if code_snippets else 0.0
    
    def _calculate_confidence(self, sample_size: int) -> float:
        """Calculate assessment confidence based on sample size"""
        if sample_size >= 20:
            return 0.9
        elif sample_size >= 10:
            return 0.8
        elif sample_size >= 5:
            return 0.6
        else:
            return 0.4
    
    def _generate_evidence(self, code_snippets: List[str], skill_indicators: Dict[str, float]) -> List[str]:
        """Generate evidence for skill assessment"""
        evidence = []
        
        if skill_indicators["code_quality"] > 0.7:
            evidence.append("High code quality with good documentation and structure")
        
        if skill_indicators["pattern_sophistication"] > 0.6:
            evidence.append("Uses sophisticated design patterns and abstractions")
        
        if skill_indicators["consistency"] > 0.8:
            evidence.append("Demonstrates consistent coding style across projects")
        
        if skill_indicators["complexity_handling"] > 0.7:
            evidence.append("Effectively handles complex programming constructs")
        
        # Add specific code examples
        if len(code_snippets) > 0:
            evidence.append(f"Analysis based on {len(code_snippets)} code samples")
        
        return evidence 