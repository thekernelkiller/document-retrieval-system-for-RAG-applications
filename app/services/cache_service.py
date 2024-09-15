import json
from app.config import Config

# Get Redis client from Config
redis_client = Config.get_redis_client()

def get_cache_key(query, top_k, threshold):
    """Generate a unique cache key based on search parameters"""
    return f"search:{query}:{top_k}:{threshold}"

def get_cached_results(query, top_k, threshold):
    """Retrieve cached search results"""
    cache_key = get_cache_key(query, top_k, threshold)
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    return None

def set_cached_results(query, top_k, threshold, results):
    """Cache search results"""
    cache_key = get_cache_key(query, top_k, threshold)
    redis_client.setex(cache_key, Config.CACHE_EXPIRATION, json.dumps(results))

def clear_cache():
    """Clear all cached results"""
    redis_client.flushdb()