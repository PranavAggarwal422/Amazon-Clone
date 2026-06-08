from store.semantic_search import collection
from store.models import Product


def get_similar_products(product, limit=6):
    results = collection.get(ids=[str(product.id)], include=["embeddings"])
    embedding = results["embeddings"][0]
    similar = collection.query(query_embeddings=[embedding], n_results=limit + 1)

    ids = []
    for pid in similar["ids"][0]:
        if int(pid) != product.id:
            ids.append(int(pid))

    products = Product.objects.in_bulk(ids)

    return [products[i] for i in ids if i in products][:limit]

