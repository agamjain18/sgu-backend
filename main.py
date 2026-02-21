from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import SessionLocal, engine, get_db
import os
import shutil
import json
from fastapi import File, UploadFile
import uuid
from datetime import datetime
import auth
import re
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi import Request


def slugify(text: str) -> str:
    # Lowercase, replace spaces with hyphens, remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

# Create the database tables
models.Base.metadata.create_all(bind=engine)

# Auto-migrate: Add missing columns if they don't exist
def migrate_db():
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('products')]
    
    with engine.connect() as conn:
        if 'is_bestseller' not in columns:
            print("Adding is_bestseller column...")
            conn.execute(text("ALTER TABLE products ADD COLUMN is_bestseller BOOLEAN DEFAULT 0"))
            conn.commit()
        if 'slug' not in columns:
            print("Adding slug column...")
            conn.execute(text("ALTER TABLE products ADD COLUMN slug VARCHAR"))
            conn.commit()
            # Generate slugs for existing products
            from sqlalchemy.orm import Session
            db = SessionLocal()
            products = db.query(models.Product).all()
            for p in products:
                if not p.slug:
                    p.slug = slugify(p.name)
            db.commit()
            db.close()
    print("Database migration check complete.")

migrate_db()

def migrate_industry_db():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if 'industry_products' not in inspector.get_table_names():
        print("Creating industry_products table...")
        models.IndustryProduct.__table__.create(engine)
    print("Industry database migration check complete.")

migrate_industry_db()

import logging
logging.basicConfig(filename='api_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = FastAPI(title="SGU Backend API", root_path="/sgu")
print("--- SGU Backend API is starting up on port 8022 ---")

from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SGU Backend API",
        "status": "Online",
        "version": "1.1.0",
        "documentation": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "message": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/uploads/{unique_filename}"}

# AUTH ENDPOINTS
@app.post("/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# PRODUCTS CRUD
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    product_dict = product.dict()
    if not product_dict.get('slug'):
        product_dict['slug'] = slugify(product_dict['name'])
    
    db_product = models.Product(**product_dict)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        products = db.query(models.Product).offset(skip).limit(limit).all()
        return products
    except Exception as e:
        logging.error(f"Error in read_products: {str(e)}")
        raise e

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.get("/products/slug/{slug}", response_model=schemas.Product)
def read_product_by_slug(slug: str, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.slug == slug).first()
    if db_product is None:
        # Fallback to search by ID if it's numeric
        if slug.isdigit():
            db_product = db.query(models.Product).filter(models.Product.id == int(slug)).first()
        
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.get("/industry-products/", response_model=List[schemas.IndustryProduct])
def read_industry_products(industry: str = None, db: Session = Depends(get_db)):
    query = db.query(models.IndustryProduct)
    if industry:
        query = query.filter(models.IndustryProduct.industry == industry)
    return query.all()

@app.post("/industry-products/", response_model=schemas.IndustryProduct)
def create_industry_product(product: schemas.IndustryProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    import re
    def slugify(text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        return text.strip('-')
    product_dict = product.dict()
    if not product_dict.get('slug'):
        product_dict['slug'] = slugify(product_dict.get('name', ''))
    if not product_dict.get('product_id_str'):
        product_dict['product_id_str'] = f"{product_dict.get('industry','')}-{slugify(product_dict.get('category',''))}-{product_dict.get('slug','')}"
    db_product = models.IndustryProduct(**product_dict)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/industry-products/{product_id}")
def delete_industry_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_product = db.query(models.IndustryProduct).filter(models.IndustryProduct.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Industry product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Industry product deleted successfully"}

@app.post("/industry-products/sync")
def sync_industry_products(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    try:
        # Clear existing
        db.query(models.IndustryProduct).delete()
        
        # Load the latest JSON
        json_path = os.path.join(os.path.dirname(__file__), "new_industry_data.json")
        if not os.path.exists(json_path):
             return {"message": "Data file not found"}
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for ind_slug, ind_obj in data.items():
            for section in ind_obj.get('sections', []):
                cat_name = section['title']
                for item in section['items']:
                    db.add(models.IndustryProduct(
                        industry=ind_slug,
                        category=cat_name,
                        name=item['name'],
                        slug=item['slug'],
                        image=item['img'],
                        product_id_str=item['id']
                    ))
        db.commit()
        return {"message": "Industry products synced successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/industry-products/bulk", response_model=List[schemas.IndustryProduct])
def bulk_create_industry_products(products: List[schemas.IndustryProductCreate], db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    results = []
    for product in products:
        product_dict = product.dict()
        if not product_dict.get('slug'):
            product_dict['slug'] = slugify(product_dict.get('name', ''))
        if not product_dict.get('product_id_str'):
            product_dict['product_id_str'] = f"{product_dict.get('industry','')}-{slugify(product_dict.get('category',''))}-{product_dict.get('slug','')}"
        db_product = models.IndustryProduct(**product_dict)
        db.add(db_product)
        results.append(db_product)
    db.commit()
    for r in results:
        db.refresh(r)
    return results

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_dict = product.dict()
    if not product_dict.get('slug'):
        product_dict['slug'] = slugify(product_dict['name'])
        
    for key, value in product_dict.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

# COUNTRIES CRUD
@app.get("/countries/", response_model=List[schemas.Country])
def read_countries(db: Session = Depends(get_db)):
    return db.query(models.Country).all()

@app.post("/countries/", response_model=schemas.Country)
def create_country(country: schemas.CountryCreate, db: Session = Depends(get_db)):
    db_country = models.Country(**country.dict())
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country

# INQUIRIES CRUD
@app.post("/inquiries/", response_model=schemas.Inquiry)
def create_inquiry(inquiry: schemas.InquiryCreate, db: Session = Depends(get_db)):
    db_inquiry = models.Inquiry(**inquiry.dict())
    if not db_inquiry.created_at:
        db_inquiry.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.add(db_inquiry)
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry

@app.get("/inquiries/", response_model=List[schemas.Inquiry])
def read_inquiries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Inquiry).order_by(models.Inquiry.id.desc()).offset(skip).limit(limit).all()

@app.delete("/inquiries/{inquiry_id}")
def delete_inquiry(inquiry_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_inquiry = db.query(models.Inquiry).filter(models.Inquiry.id == inquiry_id).first()
    if db_inquiry is None:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    db.delete(db_inquiry)
    db.commit()
    return {"message": "Inquiry deleted successfully"}

# SETTINGS CRUD
@app.get("/settings/", response_model=List[schemas.Setting])
def read_settings(db: Session = Depends(get_db)):
    return db.query(models.Setting).all()

@app.post("/settings/", response_model=schemas.Setting)
def update_setting(setting: schemas.SettingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_setting = db.query(models.Setting).filter(models.Setting.key == setting.key).first()
    if db_setting:
        db_setting.value = setting.value
    else:
        db_setting = models.Setting(**setting.dict())
        db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

# JOB POSITIONS
@app.get("/job-positions/", response_model=List[schemas.JobPosition])
def read_job_positions(active_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.JobPosition)
    if active_only:
        query = query.filter(models.JobPosition.is_active == True)
    return query.order_by(models.JobPosition.id.desc()).all()

@app.post("/job-positions/", response_model=schemas.JobPosition)
def create_job_position(position: schemas.JobPositionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    from datetime import datetime as dt
    position_dict = position.dict()
    if not position_dict.get('created_at'):
        position_dict['created_at'] = dt.now().strftime("%Y-%m-%d")
    db_position = models.JobPosition(**position_dict)
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

@app.put("/job-positions/{position_id}", response_model=schemas.JobPosition)
def update_job_position(position_id: int, position: schemas.JobPositionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_position = db.query(models.JobPosition).filter(models.JobPosition.id == position_id).first()
    if db_position is None:
        raise HTTPException(status_code=404, detail="Job position not found")
    for key, value in position.dict().items():
        setattr(db_position, key, value)
    db.commit()
    db.refresh(db_position)
    return db_position

@app.delete("/job-positions/{position_id}")
def delete_job_position(position_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_position = db.query(models.JobPosition).filter(models.JobPosition.id == position_id).first()
    if db_position is None:
        raise HTTPException(status_code=404, detail="Job position not found")
    db.delete(db_position)
    db.commit()
    return {"message": "Job position deleted successfully"}
