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

csv_data = """AAKG,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
Alcarnitine,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
BCAA 2:1:1 Instant Vegan,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
Beta Alanine,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
Citrulline Malate,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
Creatine Mono Hydrate,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
L-Arginine,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
L-Glutamine,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
L-Isoleucine,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
L-Valine,Amino Acids,"Bakery, Confectionery, Beverages, Health & Nutrition"
Alkalized Cocoa Powder,Cocoa,"Bakery, Confectionery, Ice Cream & Toppings, Beverages, Health & Nutrition"
Dark Brown Cocoa Powder,Cocoa,"Bakery, Confectionery, Ice Cream & Toppings, Beverages, Health & Nutrition"
Light Brown Cocoa Powder,Cocoa,"Bakery, Confectionery, Ice Cream & Toppings, Beverages, Health & Nutrition"
Natural Cocoa Powder,Cocoa,"Bakery, Confectionery, Ice Cream & Toppings, Beverages, Health & Nutrition"
Regular Brown Cocoa Powder,Cocoa,"Bakery, Confectionery, Ice Cream & Toppings, Beverages, Health & Nutrition"
Non GMO Soya Lecithin Liquid,Emulsifier,All Categories
Non GMO Soya Lecithin Powder,Emulsifier,All Categories
Non GMO Soya Lyso Lecithin Liquid,Emulsifier,All Categories
Non GMO Soya Lyso Lecithin Powder,Emulsifier,All Categories
Non GMO Sunflower Lecithin Liquid,Emulsifier,All Categories
Non GMO Sunflower Lecithin Powder,Emulsifier,All Categories
Non GMO Sunflower Lyso Lecithin Liquid,Emulsifier,All Categories
Non GMO Sunflower Lyso Lecithin Powder,Emulsifier,All Categories
Oat Fiber,Fiber,"Bakery, Ice Cream & Toppings, Health & Nutrition, Beverages"
Polydextrose,Fiber,"Bakery, Ice Cream & Toppings, Health & Nutrition, Beverages"
Soy Fiber,Fiber,"Bakery, Ice Cream & Toppings, Health & Nutrition, Beverages"
Wheat Fiber,Fiber,"Bakery, Ice Cream & Toppings, Health & Nutrition, Beverages"
Carrageenan (Dairy Grade),Gums / Thickening Agent,All Categories
Guar Gum,Gums / Thickening Agent,All Categories
Gum Acacia,Gums / Thickening Agent,All Categories
Pectin Jam Grade,Gums / Thickening Agent,All Categories
Pectin Jelly Grade,Gums / Thickening Agent,All Categories
Type II Collagen,Gums / Thickening Agent,"Health & Nutrition, Beverages"
Xanthan Gum,Gums / Thickening Agent,All Categories
Calcium Caseinate,Milk & Related Product,"Bakery, Health & Nutrition, Dairy, Ice Cream & Toppings"
Cheese Powder,Milk & Related Product,"Bakery, Confectionery, Sauces & Condiments, Dairy"
Skimmed Milk Powder,Milk & Related Product,All Categories
Whole Milk Powder,Milk & Related Product,All Categories
Calcium Propionate,Preservative,"Bakery, Dairy, Sauces & Condiments"
DATEM,Preservative,"Bakery, Edible Fats, Dairy"
DMG,Preservative,"Bakery, Confectionery, Ice Cream & Toppings, Dairy, Edible Fats"
PGMS,Preservative,"Bakery, Confectionery, Ice Cream & Toppings, Dairy, Edible Fats"
Potassium Sorbate,Preservative,All Categories
Sodium Benzoate,Preservative,All Categories
Sodium Propionate,Preservative,"Bakery, Dairy"
Sorbic Acid,Preservative,All Categories
Functional Whey Protein Concentrate 80%,Protein,"Dairy, Bakery, Health & Nutrition, Ice Cream & Toppings"
Instant Whey Protein Concentrate 80%,Protein,"Dairy, Bakery, Health & Nutrition, Ice Cream & Toppings"
Pea Protein Isolate,Protein,All Categories
Soya Protein Concentrate,Protein,All Categories
Soya Protein Isolate 90%,Protein,All Categories
Sweet Whey Powder (SWP),Protein,All Categories
Vital Wheat Gluten (VWG),Protein,"Bakery, Health & Nutrition, Sauces & Condiments"
Whey Protein Isolate,Protein,"Health & Nutrition, Dairy, Beverages"
Acesulfame K,Sweetener & Polyol,All Categories
Aspartame,Sweetener & Polyol,All Categories
Fructose,Sweetener & Polyol,All Categories
Maltitol,Sweetener & Polyol,All Categories
Monk Fruit Extract,Sweetener & Polyol,All Categories
Neotame,Sweetener & Polyol,All Categories
Stevia,Sweetener & Polyol,All Categories
Sucralose,Sweetener & Polyol,All Categories
Xylitol,Sweetener & Polyol,All Categories"""

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
    # Multiple logos for the brand/certification row
    logos = [
        "https://sgutrade.com/sgu/logo.png",
        "/sgu/download-removebg-preview (6).png", # FSSAI
        "/sgu/download-removebg-preview (5).png", # ISO
        "/sgu/download-removebg-preview (4).png"  # ISO 22000
    ]
    img_url = f"{pool[c % len(pool)]},{','.join(logos)}"
    c += 1

    # Generate category-based generic specs
    specs_templates = {
        "Amino Acids": [
            {"property": "Assay", "value": "99.0% - 101.0%"},
            {"property": "Physical Form", "value": "White Crystalline Powder"},
            {"property": "Heavy Metals", "value": "≤ 10ppm"},
            {"property": "Loss on Drying", "value": "≤ 0.5%"}
        ],
        "Cocoa": [
            {"property": "Fat Content", "value": "10% - 12%"},
            {"property": "pH Value", "value": "5.0 - 8.0"},
            {"property": "Fineness", "value": "≥ 99.5%"},
            {"property": "Moisture", "value": "≤ 5.0%"}
        ],
        "Emulsifier": [
            {"property": "Acid Value", "value": "≤ 3.0 mg KOH/g"},
            {"property": "Iodine Value", "value": "Dependent on Grade"},
            {"property": "Purity", "value": "Food Grade Standard"},
            {"property": "Appearance", "value": "Clear Liquid/Standard Powder"}
        ],
        "Gums / Thickening Agent": [
            {"property": "Viscosity", "value": "Standard Range"},
            {"property": "Ash Content", "value": "≤ 1.0%"},
            {"property": "pH (1% solution)", "value": "6.0 - 8.0"},
            {"property": "Mesh Size", "value": "80-200 Mesh"}
        ]
    }
    
    cat_specs = specs_templates.get(item['raw_cat'], [
        {"property": "Quality Grade", "value": "Food Grade (FCC)"},
        {"property": "Purity", "value": "≥ 99%"},
        {"property": "Packaging", "value": "25kg Paper Bag"},
        {"property": "Solubility", "value": "Standard Condition"}
    ])

    # 1. Add to Products table (for main catatlog)
    existing_p = db.query(models.Product).filter(models.Product.slug == slug).first()
    if not existing_p:
        db.add(models.Product(
            name=name, slug=slug, category=primary_cat, sku_name=name, status="Active",
            product_overview=f"Premium {name}.", country_of_origin="Various",
            quality="High Grade", generic_specs=json.dumps(cat_specs), applications="",
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

# 3. Re-seed the admin user (rebuild drops all tables including users!)
import auth as auth_module
existing_admin = db.query(models.User).filter(models.User.username == "admin").first()
if not existing_admin:
    admin_user = models.User(
        username="admin",
        email="admin@sgutrade.com",
        hashed_password=auth_module.get_password_hash("admin123")
    )
    db.add(admin_user)
    db.commit()
    print("Admin user re-created.")
else:
    print("Admin user already exists, skipping.")

db.close()
print("Database Rebuild Complete!")
