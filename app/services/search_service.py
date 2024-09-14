import redis
from app.models import Document
from app.config import Config
from app.services.document_service import search_documents as chroma_search

redis_client = Config.get_redis_client()

def search_documents(query, top_k=5, threshold=0.5):
    try:
        # Check cache first
        cache_key = f"search:{query}:{top_k}:{threshold}"
        cached_results = redis_client.get(cache_key)
        if cached_results:
            return eval(cached_results)
        
        # Use the ChromaDB search function
        results = chroma_search(query, top_k)
        
        # Filter results based on threshold
        filtered_results = [r for r in results if r['similarity'] >= threshold]
        
        # Cache the results
        redis_client.setex(cache_key, 3600, str(filtered_results))  # Cache for 1 hour
        
        return filtered_results
    except Exception as e:
        print(f"Error in search_documents: {str(e)}")
        raise