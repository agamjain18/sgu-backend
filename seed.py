from database import SessionLocal
import models
import auth

def seed_data():
    db = SessionLocal()
    
    # Seed products
    if db.query(models.Product).count() == 0:
        products = [
        { 
            "name": 'Premium Dutch Cocoa', 
            "sku_name": 'COCOA-P-001',
            "country_of_origin": 'Netherlands',
            "quality": 'Premium Extra Fine',
            "product_overview": 'High-quality Dutch-processed cocoa powder with a rich dark color and smooth flavor profile.',
            "generic_specs": 'Fat content: 20-22%, pH: 7.2-7.8, Fineness: 99.5% through 200 mesh.',
            "applications": 'Baking, Beverages, Confectionery, Dairy products.',
            "packaging": '25kg multi-layer paper bags with PE liner.',
            "certifications": 'FSSAI, ISO 22000, HACCP, Halal, Kosher',
            "category": 'Confectionery', 
            "status": 'Active', 
            "image": 'https://images.unsplash.com/photo-1599639957043-f3aa5c986398?w=500',
            "is_bestseller": True
        },
        { 
            "name": 'Whey Protein Isolate 90%', 
            "sku_name": 'WPI-90-USA',
            "country_of_origin": 'USA',
            "quality": 'Pharma Grade',
            "product_overview": 'Highly concentrated protein source with minimal fat and lactose content.',
            "generic_specs": 'Protein: Min 90%, Moisture: Max 5%, Ash: Max 4%',
            "applications": 'Nutritional supplements, Sports nutrition, Meal replacements.',
            "packaging": '20kg craft paper bags.',
            "certifications": 'FSSAI, GMP, ISO 9001',
            "category": 'Nutritional', 
            "status": 'Active', 
            "image": 'https://images.unsplash.com/photo-1623428187969-5da2dcea5ebf?w=500',
            "is_bestseller": False
        },
    ]

        for p in products:
            db_product = models.Product(**p)
            db.add(db_product)
        
        db.commit()
        print("Products seeded.")

    # Seed countries
    if db.query(models.Country).count() == 0:
        countries = [
            "Netherlands", "USA", "Indonesia", "Malaysia", "Brazil", 
            "India", "China", "Germany", "France", "Vietnam", 
            "Thailand", "Belgium", "Canada", "Singapore"
        ]
        for country_name in countries:
            db_country = models.Country(name=country_name)
            db.add(db_country)
        db.commit()
        print("Countries seeded.")

    # Seed settings
    if db.query(models.Setting).count() == 0:
        settings = [
            {"key": "facebook_url", "value": "#"},
            {"key": "instagram_url", "value": "#"},
            {"key": "linkedin_url", "value": "#"},
            {"key": "twitter_url", "value": "#"},
            {"key": "pinterest_url", "value": "#"},
        ]
        for s in settings:
            db_setting = models.Setting(**s)
            db.add(db_setting)
        db.commit()
        print("Settings seeded.")

    # Seed Admin User
    if db.query(models.User).count() == 0:
        admin_user = models.User(
            username="admin",
            email="admin@sgutrade.com",
            hashed_password=auth.get_password_hash("admin123")
        )
        db.add(admin_user)
        db.commit()
        print("Admin user seeded.")

    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    from database import engine
    models.Base.metadata.create_all(bind=engine)
    seed_data()
