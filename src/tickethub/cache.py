import json
import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class InMemoryCache:
    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def _is_expired(self, entry: dict) -> bool:
        return time.time() > entry["expires_at"]
    
    def _cleanup_expired(self):
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry["expires_at"]
        ]
        for key in expired_keys:
            del self.cache[key]
    
    async def get(self, key: str) -> Optional[Any]:
        self._cleanup_expired()
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if self._is_expired(entry):
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit for key: {key}")
        return entry["value"]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at
        }
        logger.debug(f"Cache set for key: {key}, TTL: {ttl}s")
    
    async def delete(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted for key: {key}")
    
    async def clear(self) -> None:
        self.cache.clear()
        logger.debug("Cache cleared")
    
    def stats(self) -> dict:
        self._cleanup_expired()
        return {
            "total_keys": len(self.cache),
            "memory_usage_mb": len(json.dumps(self.cache)) / (1024 * 1024)
        }


# Global cache instance
cache = InMemoryCache(default_ttl=300)  # 5 minutes default TTL