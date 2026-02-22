from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    slug: Optional[str] = None
    sku_name: Optional[str] = ""
    country_of_origin: Optional[str] = ""
    quality: Optional[str] = ""
    product_overview: Optional[str] = ""
    generic_specs: Optional[str] = "[]"
    applications: Optional[str] = ""
    packaging: Optional[str] = ""
    certifications: Optional[str] = ""
    category: Optional[str] = "Others"
    status: Optional[str] = "Active"
    image: Optional[str] = ""
    is_bestseller: Optional[bool] = False
    industry: Optional[str] = "" # e.g. bakery, dairy

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

class IndustryProductBase(BaseModel):
    industry: str
    category: Optional[str] = ""
    name: str
    slug: Optional[str] = ""
    image: Optional[str] = ""
    product_id_str: Optional[str] = ""

class IndustryProductCreate(IndustryProductBase):
    pass

class IndustryProduct(IndustryProductBase):
    id: int

    class Config:
        from_attributes = True

class CountryBase(BaseModel):
    name: str

class CountryCreate(CountryBase):
    pass

class Country(CountryBase):
    id: int

    class Config:
        from_attributes = True

class InquiryBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: str
    status: Optional[str] = "Pending"
    created_at: Optional[str] = None

class InquiryCreate(InquiryBase):
    pass

class Inquiry(InquiryBase):
    id: int

    class Config:
        from_attributes = True

class SettingBase(BaseModel):
    key: str
    value: str

class SettingCreate(SettingBase):
    pass

class Setting(SettingBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class JobPositionBase(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = "Mumbai, India"
    type: Optional[str] = "Full-Time"
    description: Optional[str] = None
    requirements: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[str] = None

class JobPositionCreate(JobPositionBase):
    pass

class JobPosition(JobPositionBase):
    id: int

    class Config:
        from_attributes = True
