from app.services.document_service import collection
import logging
from app.services.cache_service import get_cached_results, set_cached_results
from chromadb.utils import embedding_functions
from app.services.reranking import rerank_results
import re
import logging

ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L12-v2")

def search_documents(query, top_k=5, threshold=0.5):
    try:
        logging.info(f"Searching for query: '{query}' with top_k={top_k} and threshold={threshold}")
        
        cached_results = get_cached_results(query, top_k, threshold)
        if cached_results:
            logging.info("Returning cached results")
            return cached_results

        all_docs = collection.get()
        logging.info(f"Total documents in collection: {len(all_docs['ids'])}")
        
        if len(all_docs['ids']) == 0:
            logging.warning("No documents found in the collection.")
            return []

        if len(query.split()) < 3:
            all_results = collection.get(include=['metadatas', 'documents'])
            
            filtered_results = []
            for i, doc in enumerate(all_results['documents']):
                if query.lower() in doc.lower():
                    relevance = len(re.findall(re.escape(query), doc, re.IGNORECASE)) / len(doc.split())
                    filtered_results.append({
                        '_id': all_results['ids'][i],
                        'text': doc,
                        'url': all_results['metadatas'][i].get('url', 'N/A'),
                        'similarity': relevance
                    })
            
            filtered_results.sort(key=lambda x: x['similarity'], reverse=True)
            filtered_results = filtered_results[:top_k]
        else:
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                include=['metadatas', 'distances', 'documents']
            )

            filtered_results = []
            for i, (id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
                similarity = 1 - distance
                if similarity >= threshold:
                    filtered_results.append({
                        '_id': id,
                        'text': results['documents'][0][i],
                        'url': results['metadatas'][0][i].get('url', 'N/A'),
                        'similarity': similarity
                    })

        # Apply re-ranking
        reranked_results = rerank_results(filtered_results, query)

        logging.info(f"Re-ranked results: {reranked_results}")

        set_cached_results(query, top_k, threshold, reranked_results)

        return reranked_results
    except Exception as e:
        logging.error(f"Error in search_documents: {str(e)}")
        raise