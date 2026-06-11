import chromadb
from store.semantic_search import collection
from store.models import OrderItem, Product

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("products")

def get_personalized_recommendations(user, top_k=8):
    recent_order_items = (OrderItem.objects.filter(order__user=user).order_by("-order__created_at")[:5])
    purchased_ids = []
    print(recent_order_items)

    for item in recent_order_items:
        if item.product_id not in purchased_ids:
            purchased_ids.append(item.product_id)

    if len(purchased_ids) == 0:
        return []

    embeddings = []
    for pid in purchased_ids:
        result = collection.get(ids=[str(pid)], include=["embeddings"])
        embeddings_data = result["embeddings"]

        if embeddings_data is not None and len(embeddings_data) > 0:
            embeddings.append(embeddings_data[0])

    if len(embeddings) == 0:
        return []

    # average embedding
    dimension = len(embeddings[0])
    avg_embedding = []

    for i in range(dimension):
        avg_embedding.append(sum(e[i] for e in embeddings) / len(embeddings))

    results = collection.query(query_embeddings=[avg_embedding], n_results = top_k + len(purchased_ids))
    recommendation_ids = []

    for pid in results["ids"][0]:
        pid = int(pid)

        if pid not in purchased_ids:
            recommendation_ids.append(pid)

    products_dict = Product.objects.in_bulk(recommendation_ids)

    return [products_dict[pid] for pid in recommendation_ids if pid in products_dict][:top_k]

def get_similar_products(product, limit=6):
    results = collection.get(ids=[str(product.id)], include=["embeddings"])
    if len(results["embeddings"]) == 0:
        return []
    
    embedding = results["embeddings"][0]
    similar = collection.query(query_embeddings=[embedding], n_results=limit + 1)

    ids = []
    for pid in similar["ids"][0]:
        if int(pid) != product.id:
            ids.append(int(pid))

    products = Product.objects.in_bulk(ids)

    return [products[i] for i in ids if i in products][:limit]
