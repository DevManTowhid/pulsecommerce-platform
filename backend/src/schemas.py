from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from datetime import datetime

# --- USER SCHEMAS ---

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str  # Plain text password from the user during registration

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models

# --- PRODUCT SCHEMAS ---

class ProductBase(BaseModel):
    name: str
    price: float = Field(gt=0, description="The price must be greater than zero")
    category: Optional[str] = None
    stock: int = Field(default=0, ge=0)
    attributes: Optional[dict] = None  # Validates our JSON column

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True

# --- ORDER SCHEMAS (Preview) ---

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True