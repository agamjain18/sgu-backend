import json
import os
import sys
import re
import csv
import io

# Configure exact path to import models and database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal
import models

def slugify(text: str) -> str:
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

# Mapping for the main Products page categories
cat_map = {
    'Dairy Ingredients': 'Dairy',
    'Bakery': 'Bakery',
    'Confectionery': 'Confectionery',
    'Beverage': 'Beverage',
    'Ice Cream': 'Dairy',
    'Health': 'Nutritional',
    'Health & Nutrition': 'Nutritional',
    'All Categories': 'Food Ingredients',
    'Sauces': 'Food Ingredients'
}

def get_primary_category(ind_str):
    if "All Categories" in ind_str: return "Food Ingredients"
    parts = [x.strip() for x in ind_str.split(',')]
    for p in parts:
        for k, v in cat_map.items():
            if k in p: return v
    return "Others"

# Unroll names like / 
def split_slash_names(name):
    if " / " in name:
        return [n.strip() for n in name.split(' / ')]
    return [name.strip()]

reader = csv.reader(io.StringIO(csv_data))
items = []
last_raw_cat = ""
for row in reader:
    if len(row) == 1:
        names = split_slash_names(row[0])
        for n in names:
            items.append({'name': n, 'ind': last_ind_str})
    else:
        name_col, raw_cat, ind_str = row
        last_ind_str = ind_str
        names = split_slash_names(name_col)
        for n in names:
            items.append({'name': n, 'ind': ind_str})

db = SessionLocal()

for item in items:
    name = item['name']
    slug = slugify(name)
    primary_cat = get_primary_category(item['ind'])
    
    existing = db.query(models.Product).filter(models.Product.slug == slug).first()
    if existing:
        existing.category = primary_cat
        # Fix any nulls
        if existing.sku_name is None: existing.sku_name = name
        if existing.status is None: existing.status = "Active"
    else:
        print(f"Adding: {name} as {primary_cat}")
        db.add(models.Product(
            name=name,
            slug=slug,
            category=primary_cat,
            sku_name=name,
            status="Active",
            product_overview=f"Premium {name}.",
            country_of_origin="Various",
            quality="High Grade",
            generic_specs="[]",
            applications="",
            packaging="Standard 25kg bags",
            certifications="ISO, FSSAI",
            image="https://images.unsplash.com/photo-1550989460-0adf9ea622e2?q=80&w=800&auto=format&fit=crop"
        ))

db.commit()
db.close()
print("Database Sync Complete with Vertical Mapping!")
