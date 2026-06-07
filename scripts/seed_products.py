import os
import sys
import glob
import random
from decimal import Decimal

import pandas as pd
import django
from django.db import transaction

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# DJANGO SETUP 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amazon_clone.settings")
django.setup()

from store.models import Product, Category

# DATASET LOCATION 
BASE_PATH = r"C:\Users\Pranav Aggarwal\.cache\kagglehub\datasets\lokeshparab\amazon-products-dataset\versions\2"

SELLER_NAMES = [
    "PrimeEdge Retail",
    "TechNest Retail",
    "NovaCommerce",
    "Infinity Retail",
    "UrbanKart",
]

# CLEANING FUNCTIONS 

def clean_price(price):
    if pd.isna(price):
        return None

    price = str(price)
    price = (price.replace("₹", "").replace(",", "").strip())

    try:
        return float(price)
    except:
        return None


def clean_rating(rating):
    if pd.isna(rating):
        return 0
    try:
        return float(rating)
    except:
        return 0


def clean_reviews(value):
    if pd.isna(value):
        return 0

    value = str(value).replace(",", "")
    try:
        return int(value)
    except:
        return 0

# ---------------- DESCRIPTION GENERATOR ----------------
def generate_description(row):
    name = str(row["name"])
    category = str(row["sub_category"])

    return (
        f"{name} is a premium product in the {category} category. "
        f"It offers reliable performance, modern design and excellent value for money. "
        f"Available exclusively on Amazon."
    )


# ---------------- FEATURES GENERATOR ----------------

def generate_features(category):
    category = category.lower()
    if "air conditioner" in category:
        return [
            "Energy efficient cooling",
            "Low noise operation",
            "Powerful performance",
            "Durable build quality",
            "Modern design"
        ]

    if "refrigerator" in category:
        return [
            "Large storage capacity",
            "Efficient cooling system",
            "Energy saving operation",
            "Premium finish",
            "Long lasting performance"
        ]

    if "washing" in category:
        return [
            "Powerful cleaning performance",
            "Energy efficient design",
            "Easy to use controls",
            "Durable construction",
            "Modern technology"
        ]

    if "television" in category:
        return [
            "High quality display",
            "Immersive viewing experience",
            "Modern slim design",
            "Reliable performance",
            "Excellent picture quality"
        ]

    if "camera" in category:
        return [
            "High quality imaging",
            "Compact design",
            "Reliable performance",
            "Easy to use",
            "Premium build quality"
        ]

    if "headphone" in category or "speaker" in category:
        return [
            "Excellent sound quality",
            "Premium design",
            "Durable construction",
            "Comfortable usage",
            "Reliable performance"
        ]

    return [
        "High quality product",
        "Reliable performance",
        "Durable design",
        "Customer favorite",
        "Value for money"
    ]


# ---------------- SPECIFICATIONS ----------------

def generate_specifications(row):
    specs = {
        "Main Category": str(row["main_category"]),
        "Sub Category": str(row["sub_category"])
    }

    if pd.notna(row["ratings"]):
        specs["Rating"] = str(row["ratings"])

    return specs

# ---------------- SAMPLING RULE ----------------

def get_sample_size(total_rows):
    if total_rows <= 100:
        return total_rows

    if total_rows <= 500:
        return 100

    if total_rows <= 1000:
        return 250

    if total_rows <= 3000:
        return 500

    if total_rows <= 10000:
        return 750

    return 1000


print("Finding CSV files...")
csv_files = glob.glob(os.path.join(BASE_PATH, "*.csv"))
inserted_count = 0

print(f"Found {len(csv_files)} CSV files")
existing_names = set(Product.objects.values_list("name", flat=True))

category_cache = {}
for category in Category.objects.all():
    category_cache[category.name] = category

for file in csv_files:
        filename = os.path.basename(file)

        # Skip master file (contains duplicates)
        if filename == "Amazon-Products.csv":
            continue

        try:
            df = pd.read_csv(file)
        except Exception as e:
            print(f"Failed to read {filename}: {e}")
            continue

        total_rows = len(df)
        if total_rows == 0:
            continue

        sample_size = get_sample_size(total_rows)

        print(f"{filename}: {total_rows} rows -> inserting {sample_size}")
        sampled_df = df.sample(n=min(sample_size, total_rows), random_state=42)

        for _, row in sampled_df.iterrows():

            try:
                # ---------- PRODUCT NAME ----------
                if pd.isna(row["name"]):
                    continue

                product_name = str(row["name"]).strip()
                if product_name == "":
                    continue

                # Skip duplicates 
                if product_name in existing_names:
                    continue
                existing_names.add(product_name)

                # ---------- PRICE ----------
                price = clean_price(row["discount_price"])
                mrp = clean_price(row["actual_price"])

                if price is None or mrp is None:
                    continue

                if price <= 0 or mrp <= 0:
                    continue

                # ---------- IMAGE ----------
                image_url = ""
                if pd.notna(row["image"]):
                    image_url = str(row["image"]).strip()

                # ---------- CATEGORY ----------
                category_name = str(row["sub_category"]).strip()
                if category_name == "" or category_name.lower() == "nan":
                    category_name = str(row["main_category"]).strip()

                if category_name not in category_cache:
                    category_cache[category_name] = Category.objects.create(name=category_name)

                category_obj = category_cache[category_name]

                # ---------- DISCOUNT ----------
                discount_percent = 0
                if mrp > price:
                    discount_percent = round(((mrp - price) / mrp) * 100, 1)

                # ---------- FEATURES ----------
                features = generate_features(category_name)

                # ---------- DESCRIPTION ----------
                description = generate_description(row)

                # ---------- SPECIFICATIONS ----------
                specifications = generate_specifications(row)

                # ---------- RATINGS ----------
                rating = clean_rating(row["ratings"])

                # ---------- REVIEWS ----------
                num_reviews = clean_reviews(row["no_of_ratings"])

                Product.objects.create(
                    image_url = image_url,
                    name = product_name[:500],

                    price = Decimal(str(price)),
                    mrp = Decimal(str(mrp)),
                    discount_percent = discount_percent,

                    category = category_obj,
                    brand = product_name.split()[0][:100],

                    specifications = specifications,
                    description = description,
                    features = features,
                    rating = rating,

                    num_reviews = num_reviews,
                    popularity_score = random.randint(100, 10000),
                    seller = random.choice(SELLER_NAMES),

                    in_stock=True
                )

                inserted_count += 1
                if inserted_count % 500 == 0:
                    print(f"Inserted {inserted_count} products...")

            except Exception as e:
                print(product_name)
                print(e)
                print("-" * 50)

print()
print("=" * 50)
print(f"Done! Inserted {inserted_count} products.")
print("=" * 50)