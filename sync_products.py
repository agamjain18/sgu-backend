import json
import os
import sys

# Configure exact path to import models and database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal
import models
import re

def slugify(text: str) -> str:
    # Lowercase, replace spaces with hyphens, remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

with open('new_industry_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

db = SessionLocal()

for ind_slug, ind_data in data.items():
    sections = ind_data.get('sections', [])
    for section in sections:
        category_name = section['title']
        for item in section['items']:
            prod_name = item['name']
            prod_img = item['img']
            prod_slug = item['slug']
            
            # Check if product exists by slug
            existing = db.query(models.Product).filter(models.Product.slug == prod_slug).first()
            if existing:
                # Fix null values in existing to prevent 500 errors
                if existing.sku_name is None: existing.sku_name = prod_name
                if existing.generic_specs is None: existing.generic_specs = "[]"
                if existing.applications is None: existing.applications = ""
                if existing.packaging is None: existing.packaging = "Standard 25kg bags"
                if existing.certifications is None: existing.certifications = "ISO, FSSAI"
            else:
                print(f"Adding product: {prod_name}")
                new_prod = models.Product(
                    name=prod_name,
                    slug=prod_slug,
                    sku_name=prod_name,
                    category=category_name, # Map section to category
                    image=prod_img,
                    status='Active',
                    product_overview=f"Premium {prod_name} for the {ind_data['title']} industry.",
                    country_of_origin="Various",
                    quality="High Grade",
                    generic_specs="[]",
                    applications="",
                    packaging="Standard 25kg bags",
                    certifications="ISO, FSSAI"
                )
                db.add(new_prod)

try:
    db.commit()
    print("All products synced to database!")
except Exception as e:
    db.rollback()
    print("Error:", e)
finally:
    db.close()
