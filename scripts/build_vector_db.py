import os
import sys
import django
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazon_clone.settings")
django.setup()

from store.models import Product

print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")

# delete existing products if exists
try:
    client.delete_collection("products")
except:
    pass

# create new collection
collection = client.get_or_create_collection(name="products")

print(f"Total products: {Product.objects.count()}")
products = Product.objects.all()

documents = []
metadatas = []
ids = []

# Generate combined text for each product and prepare for embedding
for product in products:
    specs_text = " ".join(f"{k} {v}" for k, v in product.specifications.items())
    features_text = " ".join(product.features)

    combined_text = f"""
    Category: {product.category.name}

    Brand: {product.brand}

    Product Name: {product.name}

    Description: {product.description}

    Features: {features_text}

    Specifications: {specs_text}
    """

    documents.append(combined_text)
    metadatas.append({"product_id": str(product.id)})
    ids.append(str(product.id))

print("Generating embeddings...")
embeddings = model.encode(documents, show_progress_bar=True).tolist()

print("Saving to Chroma...")

BATCH_SIZE = 5000
for i in range(0, len(ids), BATCH_SIZE):
    collection.add(
        ids=ids[i:i + BATCH_SIZE],
        documents=documents[i:i + BATCH_SIZE],
        metadatas=metadatas[i:i + BATCH_SIZE],
        embeddings=embeddings[i:i + BATCH_SIZE]
    )

    print(f"Inserted {min(i + BATCH_SIZE, len(ids))}/{len(ids)}")

print("Done!")