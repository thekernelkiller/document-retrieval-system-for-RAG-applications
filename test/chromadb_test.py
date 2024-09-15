import chromadb
from chromadb.utils import embedding_functions
from app.models import Document  # Import your MongoDB model
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize the ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create embedding function (make sure this matches your document_service.py)
st_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L12-v2"
)

# Get the collection
collection = chroma_client.get_collection("documents")

# Get documents from MongoDB
mongo_docs = list(Document.find({}))
print(f"Total number of documents in MongoDB: {len(mongo_docs)}")

# Get all items in the ChromaDB collection
chroma_items = collection.get()
print(f"Total number of items in ChromaDB: {len(chroma_items['ids'])}")

# Check synchronization
mongo_ids = set(str(doc['_id']) for doc in mongo_docs)
chroma_ids = set(chroma_items['ids'])

print(f"Documents in MongoDB but not in ChromaDB: {len(mongo_ids - chroma_ids)}")
print(f"Documents in ChromaDB but not in MongoDB: {len(chroma_ids - mongo_ids)}")

# Print details of a few documents from both databases
num_docs_to_show = 5
print("\nSample documents:")
for i in range(min(num_docs_to_show, len(mongo_docs))):
    mongo_doc = mongo_docs[i]
    mongo_id = str(mongo_doc['_id'])
    print(f"\nDocument {i+1}:")
    print(f"MongoDB ID: {mongo_id}")
    print(f"MongoDB URL: {mongo_doc.get('url', 'N/A')}")
    print(f"MongoDB Text: {mongo_doc.get('text', 'N/A')[:100]}...")  # First 100 characters
    
    if mongo_id in chroma_ids:
        chroma_index = chroma_items['ids'].index(mongo_id)
        print(f"ChromaDB ID: {chroma_items['ids'][chroma_index]}")
        print(f"ChromaDB Metadata: {chroma_items['metadatas'][chroma_index]}")
        print(f"ChromaDB Document: {chroma_items['documents'][chroma_index][:100]}...")  # First 100 characters
    else:
        print("Document not found in ChromaDB")

# Perform a simple query
query_text = "news"  # Adjust this based on your actual data
query_results = collection.query(
    query_texts=[query_text],
    n_results=3
)

print("\nQuery Results:")
for i, (id, distance) in enumerate(zip(query_results['ids'][0], query_results['distances'][0])):
    print(f"\nResult {i + 1}:")
    print(f"ID: {id}")
    print(f"Distance: {distance}")
    print(f"Document: {query_results['documents'][0][i][:100]}...")  # First 100 characters

# Check the collection's schema
print("\nCollection Schema:")
print(collection.schema)