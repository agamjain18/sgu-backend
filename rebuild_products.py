import os
import sys
import re

# Configure exact path to import models and database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal
import models

def slugify(text: str) -> str:
    # Lowercase, replace spaces with hyphens, remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

csv_data = """Skimmed Milk Powder,Milk & Related Product,Dairy Ingredients
Whole Milk Powder,Milk & Related Product,Dairy Ingredients
Cheese Powder,Milk & Related Product,Dairy Ingredients
Calcium Caseinate,Milk & Related Product,Dairy Ingredients
Calcium Propionate,Preservative,"Dairy, Health, Beverage, Ice Cream, Confectionery, Bakery"
Sodium Propionate,Preservative,"Dairy, Health, Beverage, Ice Cream, Confectionery, Bakery"
Potassium Sorbate,Preservative,"Dairy, Health, Beverage, Ice Cream, Confectionery, Bakery"
Sorbic Acid,Preservative,"Dairy, Health, Beverage, Ice Cream, Confectionery, Bakery"
Sodium Benzoate,Preservative,"Dairy, Health, Beverage, Ice Cream, Confectionery, Bakery"
PGMS / Datem / DMG,Preservative / Emulsifier,"Dairy, Health, Beverage, Ice Cream, Confectionery, Bakery"
Fructose,Sweetener & Polyol,"Dairy, Ice Cream, Confectionery, Bakery"
Monk Fruit Extract,Sweetener & Polyol,"Dairy, Ice Cream, Confectionery, Bakery"
Maltitol / Acesulfame K,Sweetener & Polyol,"Dairy, Ice Cream, Confectionery, Bakery"
Sucralose / Stevia,Sweetener & Polyol,"Dairy, Ice Cream, Confectionery, Bakery"
Aspartame / Neotame / Xylitol,Sweetener & Polyol,"Dairy, Ice Cream, Confectionery, Bakery"
Soya Protein Isolate 90 %,Protein,All Categories
Soya Protein Concentrate,Protein,All Categories
Functional Whey Protein Concentrate 80 %,Protein,All Categories
Instant Whey Protein Concentrate 80 %,Protein,All Categories
Whey Protein Isolate,Protein,All Categories
Pea Protein Isolate,Protein,All Categories
Vital Wheat Gluten (VWG),Protein,All Categories
Sweet Whey Powder (SWP),Protein,"Beverage, Ice Cream, Confectionery, Bakery"
Xanthan Gum,Gums/Thickening Agent,All Categories
Guar Gum,Gums/Thickening Agent,All Categories
Carrageenan (Dairy Grade),Gums/Thickening Agent,All Categories
Pectin (Jam / Jelly Grade),Gums/Thickening Agent,All Categories
Type II Collagen,Gums/Thickening Agent,All Categories
Natural Cocoa Powder,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
Light/Dark/Regular Brown Cocoa,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
Alkalized Cocoa Powder,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
DM Cocoa,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
BCAA 2:1:1 Instant Vegan,Amino Acids,"Health & Nutrition, Beverage"
Beta Alanine / Citrulline Malate,Amino Acids,"Health & Nutrition, Beverage"
L-Arginine / Alcarnitine,Amino Acids,"Health & Nutrition, Beverage"
Creatine Mono Hydrate,Amino Acids,"Health & Nutrition, Beverage"
L-Glutamine / AAKG,Amino Acids,"Health & Nutrition, Beverage"
L-Isoleucine / L-Valine,Amino Acids,"Health & Nutrition, Beverage"
Polydextrose / Soy Fiber,Fibers,Ice Cream & Toppings
Gum Acacia / Oat Fiber / Wheat Fiber,Fibers,Ice Cream & Toppings
Non GMO Soya Lecithin (Powder/Liquid),Emulsifier,"Ice Cream, Confectionery, Edible Fats"
Non GMO Sunflower Lecithin (Powder/Liquid),Emulsifier,"Ice Cream, Confectionery, Edible Fats"
Full Fat Soya Flour / Grit,Fats,Edible Fats & Others
Soya Flour / Grit (Untoasted/Toasted),Fats,Edible Fats & Others
Textured Vegetable Protein (Square/Granules),Vegetable Protein,Edible Fats & Others"""

import csv
import io

# Manual splitting of combined names from the specific formatting
def split_slash_names(name):
    # If the text has slash but isn't something like "(Powder/Liquid)", split it
    if " / " in name:
        return [n.strip() for n in name.split(' / ')]
    return [name.strip()]

reader = csv.reader(io.StringIO(csv_data))
parsed_products = []
last_cat = None
for row in reader:
    if len(row) == 1:
        names = split_slash_names(row[0])
        for n in names:
            parsed_products.append({'name': n, 'cat': last_cat})
    else:
        name_col, cat_col, ind_col = row
        last_cat = cat_col.strip()
        names = split_slash_names(name_col)
        for n in names:
            parsed_products.append({'name': n, 'cat': last_cat})

db = SessionLocal()

pool = [
    'https://images.unsplash.com/photo-1550989460-0adf9ea622e2?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1606313337699-2a9c11bdc6ce?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1610444385150-f6515a0de7bd?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1509440159596-0249088772ff?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1550583724-b2692b85b150?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1563636619-e9143da7973b?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1554522438-fb1c86db254c?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1557142046-c704a3adf364?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1605807646983-377bc5a76493?q=80&w=800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1495147466023-e62eaca9cf76?q=80&w=800&auto=format&fit=crop'
]

c = 0
for item in parsed_products:
    prod_name = item['name']
    prod_slug = slugify(prod_name)
    prod_cat = item['cat']
    
    existing = db.query(models.Product).filter(models.Product.slug == prod_slug).first()
    if not existing:
        img_url = pool[c % len(pool)]
        c += 1
        print(f"Adding product: {prod_name} | Cat: {prod_cat}")
        new_prod = models.Product(
            name=prod_name,
            slug=prod_slug,
            sku_name=prod_name,
            category=prod_cat, # EXACTLY the Product Category
            image=img_url,
            status='Active',
            product_overview=f"Premium {prod_name} for the food, beverage and nutrition industry.",
            country_of_origin="Various",
            quality="High Grade",
            generic_specs="[]",
            applications="",
            packaging="Standard 25kg bags",
            certifications="ISO, FSSAI",
            is_bestseller=False
        )
        db.add(new_prod)

try:
    db.commit()
    print("All products rebuilt successfully!")
except Exception as e:
    db.rollback()
    print("Error:", e)
finally:
    db.close()
