import logging
from app.models import Document
import chromadb
from chromadb.utils import embedding_functions

# Initialize Chroma client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create embedding function
st_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L12-v2"
)

# Get or create the collection with the embedding function
collection = chroma_client.get_or_create_collection(
    "documents",
    embedding_function=st_ef
)

def add_document(text, url):
    # Insert document into MongoDB
    doc_id = str(Document.insert({
        'text': text,
        'url': url,
    }))
    
    # Add to ChromaDB
    collection.add(
        documents=[text],
        metadatas=[{"url": url}],
        ids=[doc_id]
    )
    
    logging.info(f"Added document to MongoDB and ChromaDB with ID: {doc_id}")
    logging.debug(f"Document content: {text[:100]}...")  # Log first 100 characters
    return doc_id

def search_documents(query, top_k=5):
    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        formatted_results = []
        for i, doc_id in enumerate(results['ids'][0]):
            formatted_results.append({
                '_id': doc_id,
                'text': results['documents'][0][i],
                'url': results['metadatas'][0][i]['url'],
                'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return formatted_results
    except Exception as e:
        logging.error(f"Error in search_documents: {str(e)}")
        raise

def sync_mongodb_chromadb():
    mongo_docs = Document.find({})
    chroma_ids = set(collection.get()['ids'])
    
    for doc in mongo_docs:
        if str(doc['_id']) not in chroma_ids:
            collection.add(
                documents=[doc['text']],
                metadatas=[{"url": doc['url']}],
                ids=[str(doc['_id'])]
            )
            logging.info(f"Synced document {doc['_id']} to ChromaDB")

# Call this function when initializing the application
sync_mongodb_chromadb()