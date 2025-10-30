"""
Simple in-memory cache for API responses.
Stores responses with a time-to-live (TTL) to reduce database load.
"""
from functools import wraps
from typing import Any, Callable
import time
from threading import Lock


class ResponseCache:
    """
    Thread-safe in-memory cache with expiration times.
    
    This cache stores API responses temporarily to avoid hitting
    the database for every request. Each cached item has a TTL
    (time to live) after which it's automatically invalidated.
    """
    
    def __init__(self):
        self._cache = {}
        self._lock = Lock()
    
    def get(self, key: str) -> tuple[bool, Any]:
        """
        Try to retrieve a cached value by key.
        
        Returns:
            (True, value) if cache hit and not expired
            (False, None) if cache miss or expired
        """
        with self._lock:
            if key in self._cache:
                cached_value, expiry_time = self._cache[key]
                
                # Check if the cached value is still valid
                if time.time() < expiry_time:
                    return True, cached_value
                else:
                    # Expired - clean it up
                    del self._cache[key]
            
            return False, None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Store a value in the cache with a TTL.
        
        Args:
            key: Cache key (usually derived from function name and args)
            value: The value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        with self._lock:
            expiry_time = time.time() + ttl
            self._cache[key] = (value, expiry_time)
    
    def clear(self):
        """Remove all cached values (used when data changes)"""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get the current number of cached items"""
        with self._lock:
            return len(self._cache)

# Global cache instance shared across all endpoints
cache = ResponseCache()


def cached(ttl: int = 300):
    """
    Decorator that caches the result of a function for a specified time.
    
    Works with both async and sync functions. The cache key is automatically
    generated from the function name and its arguments.
    
    Args:
        ttl: How long to keep the cached result, in seconds (default: 5 minutes)
    
    Example:
        @cached(ttl=300)
        async def get_alumni_stats():
            # This expensive operation will only run once every 5 minutes
            return calculate_statistics()
    """
    def decorator(func: Callable) -> Callable:
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build a unique cache key for this function call
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Check if we have a cached result
            cache_hit, cached_result = cache.get(cache_key)
            if cache_hit:
                return cached_result
            
            # No cache hit - run the actual function
            result = await func(*args, **kwargs)
            
            # Store the result for future requests
            cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Build a unique cache key for this function call
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Check if we have a cached result
            cache_hit, cached_result = cache.get(cache_key)
            if cache_hit:
                return cached_result
            
            # No cache hit - run the actual function
            result = func(*args, **kwargs)
            
            # Store the result for future requests
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Return the right wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
