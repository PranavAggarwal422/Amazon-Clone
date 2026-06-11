import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path = "chroma_db")

try:
    collection = client.get_collection("products")
except Exception:
    collection = None

def semantic_search(query, top_k = 100):
    if collection is None:
        return []
    
    query_embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    product_ids = [int(product_id) for product_id in results["ids"][0]]
    distances = results["distances"][0]
    return list(zip(product_ids, distances))

