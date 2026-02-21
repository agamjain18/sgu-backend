import json
import re

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
Light Brown Cocoa,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
Dark Brown Cocoa,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
Regular Brown Cocoa,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
Alkalized Cocoa Powder,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
DM Cocoa,Cocoa,"Sauces, Health, Beverage, Ice Cream, Confectionery, Bakery"
BCAA 2:1:1 Instant Vegan,Amino Acids,"Health & Nutrition, Beverage"
Beta Alanine,Amino Acids,"Health & Nutrition, Beverage"
Citrulline Malate,Amino Acids,"Health & Nutrition, Beverage"
L-Arginine,Amino Acids,"Health & Nutrition, Beverage"
Alcarnitine,Amino Acids,"Health & Nutrition, Beverage"
Creatine Mono Hydrate,Amino Acids,"Health & Nutrition, Beverage"
L-Glutamine,Amino Acids,"Health & Nutrition, Beverage"
AAKG,Amino Acids,"Health & Nutrition, Beverage"
L-Isoleucine,Amino Acids,"Health & Nutrition, Beverage"
L-Valine,Amino Acids,"Health & Nutrition, Beverage"
Polydextrose,Fibers,Ice Cream & Toppings
Soy Fiber,Fibers,Ice Cream & Toppings
Gum Acacia,Fibers,Ice Cream & Toppings
Oat Fiber,Fibers,Ice Cream & Toppings
Wheat Fiber,Fibers,Ice Cream & Toppings
Non GMO Soya Lecithin (Powder/Liquid),Emulsifier,"Ice Cream, Confectionery, Edible Fats"
Non GMO Sunflower Lecithin (Powder/Liquid),Emulsifier,"Ice Cream, Confectionery, Edible Fats"
Full Fat Soya Flour / Grit,Fats,Edible Fats & Others
Soya Flour / Grit (Untoasted/Toasted),Fats,Edible Fats & Others
Textured Vegetable Protein (Square/Granules),Vegetable Protein,Edible Fats & Others"""

# Manual unrolling of / values
csv_data = csv_data.replace("PGMS / Datem / DMG", "PGMS\nDatem\nDMG")
csv_data = csv_data.replace("Maltitol / Acesulfame K", "Maltitol\nAcesulfame K")
csv_data = csv_data.replace("Sucralose / Stevia", "Sucralose\nStevia")
csv_data = csv_data.replace("Aspartame / Neotame / Xylitol", "Aspartame\nNeotame\nXylitol")

import csv
import io

reader = csv.reader(io.StringIO(csv_data))
parsed_products = []
last_cat = None
last_ind = None
for row in reader:
    if len(row) == 1:
        # It's a split product name, inherit cat and ind
        name = row[0]
        parsed_products.append({'name': name, 'cat': last_cat, 'ind': last_ind})
    else:
        name, cat, ind = row
        last_cat = cat
        last_ind = ind
        parsed_products.append({'name': name, 'cat': cat, 'ind': ind})

slug_mapping = {
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
    'Edible Fats & Others': 'edible-fat',
    'All Categories': 'ALL'
}

ALL_INDS = ['bakery', 'confectionery', 'ice-cream', 'beverages', 'dairy', 'health-nutrition', 'sauces-condiments', 'edible-fat']

industry_details = {
    "bakery": {
        "title": "Bakery",
        "description": "High performance functional food ingredients for breads, cakes, cookies and pastries.",
        "heroImg": "https://images.unsplash.com/photo-1517433627386-22442db5610e?q=80&w=1600&auto=format&fit=crop",
        "sections": []
    },
    "confectionery": {
        "title": "Confectionery",
        "description": "Solutions for candies, chocolates, coating, gum and sweet applications.",
        "heroImg": "https://images.unsplash.com/photo-1579621970588-a35d0e7ab9b6?q=80&w=1600&auto=format&fit=crop",
        "sections": []
    },
    "ice-cream": {
        "title": "Ice Cream & Toppings",
        "description": "Enhancing creaminess, mouthfeel and melting resistance for ice-cream manufacturers.",
        "heroImg": "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?q=80&w=1600&auto=format&fit=crop",
        "sections": []
    },
    "beverages": {
        "title": "Beverages",
        "description": "Stabilizers and functional solutions for juices, drinks and healthy beverages.",
        "heroImg": "https://images.unsplash.com/photo-1544145945-f90425340c7e?q=80&w=1600&auto=format&fit=crop",
        "sections": []
    },
    "dairy": {
        "title": "Dairy",
        "description": "Ingredients that improve texture, stability and nutrition in dairy products.",
        "heroImg": "https://images.unsplash.com/photo-1600017189874-ce7ab37f90db?q=80&w=1600&auto=format&fit=crop",
        "sections": []
    },
    "health-nutrition": {
        "title": "Health & Nutrition",
        "description": "Nutrition-focused products that boost overall health, performance, and daily balance.",
        "heroImg": "https://images.unsplash.com/photo-1505576399279-b4beaa2a61af?q=80&w=1600&auto=format&fit=crop",
        "sections": []
    },
    "sauces-condiments": {
        "title": "Sauces & Condiments",
        "description": "Innovative ingredient solutions for sauces, dressings, condiments and culinary applications.",
        "heroImg": "https://images.unsplash.com/photo-1558227691-41ea78d1f631?q=80&w=1600&auto=format&fit=crop",
        "sections": []
    },
    "edible-fat": {
        "title": "Edible Fat & Other Products",
        "description": "High-quality edible fats and versatile ingredient solutions for diverse food and bakery applications.",
        "heroImg": "https://images.unsplash.com/photo-1596647416395-5858cf0ae6df?q=80&w=1600&auto=format&fit=crop",
        "sections": []
    }
}

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

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text).strip('-')
    return text

industry_data_parsed = {ind: {"title": industry_details[ind]["title"], "description": industry_details[ind]["description"], "heroImg": industry_details[ind]["heroImg"], "sections": []} for ind in ALL_INDS}

# Track products per industry to build sections correctly
# Mapping: ind -> cat -> list of items
store = {ind: {} for ind in ALL_INDS}

c = 0
for p in parsed_products:
    name = p['name'].strip()
    cat = p['cat'].strip()
    inds_str = p['ind'].strip()
    
    target_inds = []
    if inds_str == "All Categories":
        target_inds = ALL_INDS
    else:
        # Split by comma
        pieces = [x.strip() for x in inds_str.split(',')]
        for piece in pieces:
            if piece in slug_mapping:
                mapped = slug_mapping[piece]
                if mapped == "ALL":
                    target_inds = ALL_INDS
                    break
                else:
                    target_inds.append(mapped)
                    
    # Insert product to specific industries
    for t_ind in target_inds:
        # Ensure cat exists
        if cat not in store[t_ind]:
            store[t_ind][cat] = []
        img_url = pool[c % len(pool)]
        c += 1
        store[t_ind][cat].append({
            "id": f"{t_ind}-{slugify(cat)}-{slugify(name)}",
            "name": name,
            "img": img_url,
            "slug": slugify(name)
        })

# Format the parsed structure
for ind in ALL_INDS:
    for cat, items in store[ind].items():
        if items:
            industry_data_parsed[ind]["sections"].append({
                "title": cat,
                "items": items
            })

with open('new_industry_data.json', 'w', encoding='utf-8') as f:
    json.dump(industry_data_parsed, f, indent=2)

print("Created new_industry_data.json")
