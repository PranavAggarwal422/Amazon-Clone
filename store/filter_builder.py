from collections import defaultdict

def build_filters(products):
    filters = []
    brands = sorted(set(p.brand for p in products if p.brand))
    categories = sorted(set(p.category.name for p in products))

    filters.append({"field_name": "Brand", "values": brands})

    filters.append({
        "field_name": "Category",
        "values": categories
    })

    return filters

