from app.services.document_service import collection
import logging
from chromadb.utils import embedding_functions
import re

# Initialize the embedding function (move this to the top of your file)
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L12-v2")

def search_documents(query, top_k=5, threshold=0.5):
    try:
        logging.info(f"Searching for query: '{query}' with top_k={top_k} and threshold={threshold}")
        
        all_docs = collection.get()
        logging.info(f"Total documents in collection: {len(all_docs['ids'])}")
        
        if len(all_docs['ids']) == 0:
            logging.warning("No documents found in the collection.")
            return []

        # Check if the query is short (less than 3 words)
        if len(query.split()) < 3:
            # Perform exact matching for short queries
            all_results = collection.get(
                include=['metadatas', 'documents']
            )
            
            filtered_results = []
            for i, doc in enumerate(all_results['documents']):
                if query.lower() in doc.lower():
                    # Simple relevance score based on word frequency
                    relevance = len(re.findall(re.escape(query), doc, re.IGNORECASE)) / len(doc.split())
                    filtered_results.append({
                        '_id': all_results['ids'][i],
                        'text': doc,
                        'url': all_results['metadatas'][i].get('url', 'N/A'),
                        'similarity': relevance  # Using relevance as similarity for consistency
                    })
            
            # Sort and limit results
            filtered_results.sort(key=lambda x: x['similarity'], reverse=True)
            filtered_results = filtered_results[:top_k]
        else:
            # Perform semantic search for longer queries
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

        logging.info(f"Filtered results: {filtered_results}")
        return filtered_results
    except Exception as e:
        logging.error(f"Error in search_documents: {str(e)}")
        raise