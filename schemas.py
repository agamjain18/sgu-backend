from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    sku_name: str
    country_of_origin: str
    quality: str
    product_overview: str
    generic_specs: str
    applications: str
    packaging: str
    certifications: str
    category: str
    status: str
    image: Optional[str] = ""
    is_bestseller: bool = False

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
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
