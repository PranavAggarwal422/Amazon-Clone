import os
import cohere
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))


def rerank_products(query, products):
    documents = []

    for product in products:
        features_text = " ".join(product.features)
        specs_text = " ".join(f"{k}: {v}" for k, v in product.specifications.items())

        text = f"""
        Category: {product.category.name}

        Brand: {product.brand}

        Product Name:
        {product.name}

        Description:
        {product.description}

        Features:
        {features_text}

        Specifications:
        {specs_text}
        """
        
        documents.append(text)
      
    # Nothing to rerank
    if len(documents) == 0:
        return products

    try :   
        response = co.rerank(
            model="rerank-v3.5", 
            query=query, 
            documents=documents, 
            top_n=min(10, len(documents))
            )
        
    except Exception :
        return products 

    ranked_products = []

    for result in response.results:
        ranked_products.append(products[result.index])

    return ranked_products

