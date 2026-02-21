from sqlalchemy import Column, Integer, String, Text, Float, Boolean
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, index=True, unique=True, nullable=True)
    sku_name = Column(String, index=True)
    country_of_origin = Column(String)
    quality = Column(String)
    product_overview = Column(Text)
    generic_specs = Column(Text)
    applications = Column(Text)
    packaging = Column(Text)
    certifications = Column(Text)
    category = Column(String, index=True)
    status = Column(String)
    image = Column(Text)
    is_bestseller = Column(Boolean, default=False)

class IndustryProduct(Base):
    __tablename__ = "industry_products"

    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, index=True) # e.g., bakery, dairy
    category = Column(String, index=True) # e.g., Protein, Fiber
    name = Column(String)
    slug = Column(String)
    image = Column(Text)
    product_id_str = Column(String) # For frontend ID consistency
class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    subject = Column(String)
    message = Column(Text)
    status = Column(String, default="Pending") # Pending, Reviewed, Responded
    created_at = Column(String) # For simplicity, storing as string

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
