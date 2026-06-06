import os
import random
from decimal import Decimal

import pandas as pd
import django
import ast


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazon_clone.settings")
django.setup()

from store.models import Product, Category

print("Reading parquet file...")
df = pd.read_parquet("data/full-00009-of-00010.parquet")

# Remove invalid rows
df = df[df["title"].notna()]
df = df[df["price"].notna()]
df = df[df["store"].notna()]

# Prefer popular products
df = df.sort_values("rating_number", ascending=False)

MIN_CATEGORY_SIZE = 15
MAX_PRODUCTS_PER_CATEGORY = 2000

seller_names = [
    "PrimeEdge Retail",
    "TechNest Retail",
    "NovaCommerce",
    "Infinity Retail"
]

USD_TO_INR = 90
count = 0

category_counts = df["main_category"].value_counts()
for category_name, total_products in category_counts.items():
    if total_products < MIN_CATEGORY_SIZE:
        continue

    category_df = df[df["main_category"] == category_name]

    # random sample if category too large
    if total_products > MAX_PRODUCTS_PER_CATEGORY:
        category_df = category_df.sample(n = MAX_PRODUCTS_PER_CATEGORY, random_state=42)

    category_obj, _ = Category.objects.get_or_create(name=category_name)
    print(f"Inserting {len(category_df)} products from {category_name}")

    for _, row in category_df.iterrows():
        try:
            # ---------------- PRICE ----------------
            price_value = row["price"]
            if pd.isna(price_value):
                continue
            if str(price_value).lower() == "none":
                continue
            price = float(price_value) * USD_TO_INR
            if price <= 0:
                continue

            discount = random.randint(5, 40)
            mrp = round(price / (1 - discount / 100), 2)

            # ---------------- DESCRIPTION ----------------
            description = ""
            if row["description"] is not None:
                description = " ".join(str(x) for x in row["description"])

            # ---------------- FEATURES ----------------
            features = []
            if row["features"] is not None:
                features = [str(x) for x in row["features"]]

            # ---------------- SPECIFICATIONS ----------------
            specifications = {}
            details = row["details"]

            if details is not None:
                try:
                    specifications = ast.literal_eval(str(details))
                except:
                    specifications = {}

            # Remove useless metadata
            REMOVE_KEYS = {
                "Best Sellers Rank",
                "Is Discontinued By Manufacturer"
            }
            specifications = {
                key: value
                for key, value in specifications.items()
                if key not in REMOVE_KEYS
            }

            # ---------------- IMAGE ----------------
            image_url = ""
            images = row["images"]

            if isinstance(images, dict):
                if "hi_res" in images:
                    for img in images["hi_res"]:
                        if img is not None:
                            image_url = str(img)
                            break

                if image_url == "" and "large" in images:
                    for img in images["large"]:
                        if img is not None:
                            image_url = str(img)
                            break

                if image_url == "" and "thumb" in images:
                    for img in images["thumb"]:
                        if img is not None:
                            image_url = str(img)
                            break

            # ---------- SKIP LOW QUALITY PRODUCTS ----------

            if image_url == "":
                continue
            if description.strip() == "":
                continue
            if len(features) == 0:
                continue
            if len(specifications) == 0:
                continue
            
            Product.objects.create(
                image_url = image_url,
                name = str(row["title"])[:500],

                price = Decimal(str(round(price, 2))),
                mrp = Decimal(str(mrp)),
                discount_percent = discount,

                category = category_obj,
                brand = str(row["store"])[:100],
                specifications = specifications,
                description = description,
                features = features,

                rating = float(row["average_rating"]) if pd.notna(row["average_rating"]) else 0,
                num_reviews = int(row["rating_number"]) if pd.notna(row["rating_number"]) else 0,
                popularity_score = random.randint(100, 10000),

                seller = random.choice(seller_names),
                in_stock = True
            )

            count += 1

        except Exception as e:
            print(e)

print()
print(f"Done! Inserted {count} high-quality products.")