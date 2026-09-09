from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import ProductStatus

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class WarehouseCreate(BaseModel):
    name: str

class WarehouseUpdate(BaseModel):
    name: Optional[str]

class WarehouseRead(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime
    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    title: str
    status: Optional[ProductStatus] = ProductStatus.in_stock

class ProductRead(BaseModel):
    id: int
    title: str
    status: ProductStatus
    warehouse_id: int
    created_at: datetime
    class Config:
        orm_mode = True

class ExportJobRead(BaseModel):
    id: int
    warehouse_id: int
    user_id: int
    status: str
    file_path: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True
