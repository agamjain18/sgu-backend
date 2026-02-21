import json
import os
import sys
import re
import csv
import io

# Configure exact path to import models and database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal, engine
import models

def slugify(text: str) -> str:
    # Lowercase, replace spaces with hyphens, remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

# 1. DROP ALL DATA AND RECREATE TABLES (Clean start)
print("Clearing database...")
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

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

# Manual splitting of combined names
def split_slash_names(name):
    if " / " in name:
        return [n.strip() for n in name.split(' / ')]
    return [name.strip()]

# Mapping for the main Products page categories
cat_map = {
    'Dairy Ingredients': 'Dairy',
    'Bakery': 'Bakery',
    'Confectionery': 'Confectionery',
    'Beverage': 'Beverage',
    'Ice Cream': 'Dairy',
    'Health & Nutrition': 'Nutritional',
    'Health': 'Nutritional',
    'All Categories': 'Food Ingredients',
    'Sauces': 'Food Ingredients',
    'Edible Fats': 'Food Ingredients'
}

def get_primary_category(ind_str):
    if "All Categories" in ind_str: return "Food Ingredients"
    parts = [x.strip() for x in ind_str.split(',')]
    for p in parts:
        for k, v in cat_map.items():
            if k in p: return v
    return "Food Ingredients"

industry_slug_map = {
    'Dairy': 'dairy',
    'Dairy Ingredients': 'dairy',
    'Health': 'health-nutrition',
    'Health & Nutrition': 'health-nutrition',
    'Beverage': 'beverages',
    'Ice Cream': 'ice-cream',
    'Ice Cream & Toppings': 'ice-cream',
    'Confectionery': 'confectionery',
    'Bakery': 'bakery',
    'Sauces': 'sauces-condiments',
    'Edible Fats': 'edible-fat',
    'Edible Fats & Others': 'edible-fat'
}

ALL_INDS = ['bakery', 'confectionery', 'ice-cream', 'beverages', 'dairy', 'health-nutrition', 'sauces-condiments', 'edible-fat']

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

reader = csv.reader(io.StringIO(csv_data))
items_data = []
for row in reader:
    if len(row) == 1:
        names = split_slash_names(row[0])
        for n in names: items_data.append({'name': n, 'raw_cat': last_raw_cat, 'ind_str': last_ind_str})
    else:
        name_col, raw_cat, ind_str = row
        last_ind_str = ind_str
        last_raw_cat = raw_cat
        names = split_slash_names(name_col)
        for n in names: items_data.append({'name': n, 'raw_cat': raw_cat.strip(), 'ind_str': ind_str.strip()})

db = SessionLocal()
c = 0

print("Populating tables...")
for item in items_data:
    name = item['name']
    slug = slugify(name)
    primary_cat = get_primary_category(item['ind_str'])
    img_url = pool[c % len(pool)]
    c += 1

    # 1. Add to Products table (for main catatlog)
    existing_p = db.query(models.Product).filter(models.Product.slug == slug).first()
    if not existing_p:
        db.add(models.Product(
            name=name, slug=slug, category=primary_cat, sku_name=name, status="Active",
            product_overview=f"Premium {name}.", country_of_origin="Various",
            quality="High Grade", generic_specs="[]", applications="",
            packaging="Standard 25kg bags", certifications="ISO, FSSAI",
            image=img_url
        ))

    # 2. Add to IndustryProducts table (for industry-specific pages)
    target_inds = []
    if item['ind_str'] == "All Categories":
        target_inds = ALL_INDS
    else:
        pieces = [x.strip() for x in item['ind_str'].split(',')]
        for piece in pieces:
            if piece in industry_slug_map:
                mapped = industry_slug_map[piece]
                target_inds.append(mapped)
    
    for t_ind in target_inds:
        db.add(models.IndustryProduct(
            industry=t_ind,
            category=item['raw_cat'],
            name=name,
            slug=slug,
            image=img_url,
            product_id_str=f"{t_ind}-{slugify(item['raw_cat'])}-{slug}"
        ))

db.commit()
db.close()
print("Database Rebuild Complete!")
