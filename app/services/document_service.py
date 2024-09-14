import chromadb
from chromadb.utils import embedding_functions
from app.models import Document
from app.config import Config
import logging

# Initialize ChromaDB client
client = chromadb.Client()

# Create a collection for documents
collection = client.create_collection("documents")

# Use BERT embedding function
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="bert-base-uncased")

def add_document(text, url):
    doc_id = Document.insert({'text': text, 'url': url})
    logging.info(f"Added document to MongoDB with ID: {doc_id}")
    
    # Add to ChromaDB collection
    collection.add(
        documents=[text],
        metadatas=[{"url": url}],
        ids=[str(doc_id)]
    )
    logging.info(f"Added document to ChromaDB with ID: {doc_id}")
    
    return doc_id

def search_documents(query, top_k=5):
    # Search in ChromaDB collection
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    formatted_results = []
    for i, (doc_id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
        doc = Document.find_one({'_id': doc_id})
        if doc:
            formatted_results.append({
                '_id': doc_id,
                'text': doc['text'],
                'url': doc['url'],
                'similarity': 1 - distance  # Convert distance to similarity
            })
    
    return formatted_results

# Function to load existing documents into ChromaDB
def load_documents_to_chroma():
    documents = Document.find({})
    texts = []
    metadatas = []
    ids = []
    for doc in documents:
        texts.append(doc['text'])
        metadatas.append({"url": doc['url']})
        ids.append(str(doc['_id']))
    
    if texts:
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

# Call this function when initializing the application
load_documents_to_chroma()