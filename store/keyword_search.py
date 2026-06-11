from django.db.models import Q
from store.models import Product


def keyword_search(query, top_k=100):
    products = Product.objects.filter(
        Q(name__icontains = query) |
        Q(description__icontains = query) |
        Q(brand__icontains = query)
    )[:top_k]

    return list(products)
