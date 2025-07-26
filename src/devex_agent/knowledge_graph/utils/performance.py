"""
Performance Optimization Utilities - Parallel processing and advanced caching
"""

import asyncio
import logging
import time
import hashlib
import pickle
import os
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypeVar, Union
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    created_at: float
    access_count: int = 0
    last_accessed: float = 0

class AdvancedCache:
    """
    Advanced caching system with TTL, LRU eviction, and statistics
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.lock = threading.RLock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        logger.info(f"🧠 AdvancedCache initialized (max_size={max_size}, ttl={default_ttl}s)")
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a cache key from function name and arguments"""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_str = str(key_data)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                self.misses += 1
                return None
            
            # Check TTL
            if time.time() - entry.created_at > self.default_ttl:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                self.misses += 1
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            # Update LRU order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            self.hits += 1
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put value in cache"""
        with self.lock:
            current_time = time.time()
            
            # Create new entry
            entry = CacheEntry(
                value=value,
                created_at=current_time,
                last_accessed=current_time
            )
            
            # Check if we need to evict
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            self.cache[key] = entry
            
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self.access_order:
            return
        
        lru_key = self.access_order.pop(0)
        if lru_key in self.cache:
            del self.cache[lru_key]
            self.evictions += 1
            logger.debug(f"🗑️ Evicted LRU cache entry: {lru_key[:8]}...")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            logger.info("🧹 Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests) if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }

# Global cache instance
_global_cache = AdvancedCache()

def cached(ttl: Optional[float] = None, cache_instance: Optional[AdvancedCache] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds (uses cache default if None)
        cache_instance: Cache instance to use (uses global if None)
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or _global_cache
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = cache._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"🎯 Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            logger.debug(f"💸 Cache miss for {func.__name__}")
            result = await func(*args, **kwargs)
            cache.put(key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = cache._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"🎯 Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            logger.debug(f"💸 Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache.put(key, result, ttl)
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class ParallelProcessor:
    """
    Parallel processing utilities for performance optimization
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=min(4, self.max_workers))
        
        logger.info(f"⚡ ParallelProcessor initialized (max_workers={self.max_workers})")
    
    async def run_parallel_async(
        self, 
        tasks: List[Awaitable[T]], 
        max_concurrency: Optional[int] = None,
        return_exceptions: bool = False
    ) -> List[Union[T, Exception]]:
        """
        Run async tasks in parallel with controlled concurrency
        
        Args:
            tasks: List of awaitable tasks
            max_concurrency: Maximum number of concurrent tasks
            return_exceptions: Whether to return exceptions instead of raising
            
        Returns:
            List of results or exceptions
        """
        if not tasks:
            return []
        
        concurrency = min(max_concurrency or self.max_workers, len(tasks))
        
        logger.info(f"🚀 Running {len(tasks)} async tasks with concurrency={concurrency}")
        
        # Use semaphore to control concurrency
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_task(task):
            async with semaphore:
                return await task
        
        bounded_tasks = [bounded_task(task) for task in tasks]
        
        start_time = time.time()
        
        if return_exceptions:
            results = await asyncio.gather(*bounded_tasks, return_exceptions=True)
        else:
            results = await asyncio.gather(*bounded_tasks)
        
        duration = time.time() - start_time
        logger.info(f"✅ Completed {len(tasks)} tasks in {duration:.2f}s ({len(tasks)/duration:.1f} tasks/sec)")
        
        return results
    
    async def run_parallel_batch(
        self,
        items: List[Any],
        async_func: Callable[[Any], Awaitable[T]],
        batch_size: int = 10,
        max_concurrency: Optional[int] = None
    ) -> List[T]:
        """
        Process items in parallel batches
        
        Args:
            items: Items to process
            async_func: Async function to apply to each item
            batch_size: Size of each batch
            max_concurrency: Maximum concurrent batches
            
        Returns:
            List of results
        """
        if not items:
            return []
        
        # Create batches
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        async def process_batch(batch):
            tasks = [async_func(item) for item in batch]
            return await self.run_parallel_async(tasks, max_concurrency=len(batch))
        
        # Process batches in parallel
        batch_tasks = [process_batch(batch) for batch in batches]
        batch_results = await self.run_parallel_async(
            batch_tasks, 
            max_concurrency=max_concurrency
        )
        
        # Flatten results
        results = []
        for batch_result in batch_results:
            results.extend(batch_result)
        
        return results
    
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Run a blocking function in a thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_executor, func, *args, **kwargs)
    
    async def run_in_process(self, func: Callable, *args, **kwargs) -> Any:
        """Run a CPU-intensive function in a process pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_executor, func, *args, **kwargs)
    
    def cleanup(self):
        """Cleanup executors"""
        logger.info("🧹 Cleaning up parallel processors...")
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)

# Global parallel processor instance
_global_processor = ParallelProcessor()

async def run_parallel(tasks: List[Awaitable[T]], max_concurrency: Optional[int] = None) -> List[T]:
    """Convenience function for running tasks in parallel"""
    return await _global_processor.run_parallel_async(tasks, max_concurrency)

async def run_batch_parallel(
    items: List[Any], 
    async_func: Callable[[Any], Awaitable[T]], 
    batch_size: int = 10
) -> List[T]:
    """Convenience function for batch parallel processing"""
    return await _global_processor.run_parallel_batch(items, async_func, batch_size)

class PerformanceMonitor:
    """
    Monitor and track performance metrics
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.lock = threading.Lock()
    
    def record_duration(self, operation: str, duration: float):
        """Record operation duration"""
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation"""
        with self.lock:
            durations = self.metrics.get(operation, [])
            if not durations:
                return {}
            
            return {
                "count": len(durations),
                "total": sum(durations),
                "average": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations)
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations"""
        with self.lock:
            return {op: self.get_stats(op) for op in self.metrics.keys()}

def timed(monitor: Optional[PerformanceMonitor] = None, operation_name: Optional[str] = None):
    """
    Decorator to time function execution
    
    Args:
        monitor: PerformanceMonitor instance (creates new if None)
        operation_name: Name for the operation (uses function name if None)
    """
    perf_monitor = monitor or PerformanceMonitor()
    
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                perf_monitor.record_duration(op_name, duration)
                logger.debug(f"⏱️ {op_name} took {duration:.3f}s")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                perf_monitor.record_duration(op_name, duration)
                logger.debug(f"⏱️ {op_name} took {duration:.3f}s")
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global performance monitor
_global_monitor = PerformanceMonitor()

def get_cache_stats() -> Dict[str, Any]:
    """Get global cache statistics"""
    return _global_cache.get_stats()

def clear_cache():
    """Clear global cache"""
    _global_cache.clear()

def get_performance_stats() -> Dict[str, Dict[str, float]]:
    """Get global performance statistics"""
    return _global_monitor.get_all_stats()

def cleanup_performance_resources():
    """Cleanup global performance resources"""
    _global_processor.cleanup()
    _global_cache.clear() 