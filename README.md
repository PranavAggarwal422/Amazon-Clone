# Product Search & Recommendation Platform

An intelligent e-commerce platform built with Django that combines semantic search, keyword retrieval, reranking, and recommendation systems to improve product discovery.

## Features

### Hybrid Search
- Combines traditional keyword search with vector-based semantic search.
- Uses Sentence Transformers embeddings and ChromaDB for retrieval.

### Semantic Search
- Understands user intent instead of relying only on exact keywords.
- Retrieves similar products using embedding similarity.

### Cohere Reranking
- Improves search relevance using Cohere Rerank v3.5.
- Reorders retrieved products based on query context.

### Dynamic Faceted Filters
- Automatically generates filters from search results.
- Supports multi-select filtering without hardcoded values.

### Similar Products
- Embedding-based content recommendation system.
- Displays related products on product pages.

### Personalized Recommendations
- Generates recommendations from user purchase history.
- Builds a user profile using averaged product embeddings.

### Shopping Features
- User authentication
- Cart management
- Checkout flow
- Order history
- Order cancellation

---

## Tech Stack

### Backend
- Django

### Machine Learning
- Sentence Transformers (all-MiniLM-L6-v2)
- Cohere Rerank API

### Vector Database
- ChromaDB

### Database
- SQLite

### Frontend
- HTML
- CSS
- Bootstrap
- JavaScript

---

## ML/Search Architecture

```text
User Query
     |
     v
Keyword Search + Semantic Search
     |
     v
Merge Results
     |
     v
Cohere Rerank
     |
     v
Ranking based on rating, reviews and popularity_score
     |
     v
Dynamic Filters
     |
     v
Final Results
```

---

## Recommendation Pipeline

```text
User Purchase History
          |
          v
Retrieve Product Embeddings
          |
          v
Average Embeddings
          |
          v
Vector Similarity Search
          |
          v
Personalized Recommendations
```

---

## Dataset

- ~51,000 products across multiple categories.
- Includes electronics, fashion, appliances, sports, home products, and more.

---

## Key Highlights

- Built hybrid retrieval combining keyword and vector search.
- Implemented semantic product search using embeddings.
- Added Cohere reranking to improve relevance.
- Developed content-based and personalized recommendation systems.
- Supports dynamic filters generated from search results.

---

## Future Improvements

- Collaborative filtering
- Click-through rate optimization
- Learning-to-rank models
- Approximate nearest neighbor indexing
- Redis caching
- PostgreSQL deployment

---

## Run Locally

```bash
git clone https://github.com/PranavAggarwal422/Amazon-Clone.git

cd Amazon-Clone

pip install -r requirements.txt

python manage.py migrate

# Build vector database for semantic search python scripts/build_vector_db.py
python scripts/build_vector_db.py

python manage.py runserver
```

Note: The repository includes a pre-populated SQLite database containing ~51,000 products. The vector database used for semantic search is generated locally using build_vector_db.py and is intentionally excluded from version control.

--- 

## Author
Pranav Aggarwal
