from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app import models, schemas
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.ProductRead)
def create_product(warehouse_id: int, p: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # ownership checks omitted in scaffold
    product = models.Product(title=p.title, status=p.status, warehouse_id=warehouse_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", response_model=List[schemas.ProductRead])
def list_products(warehouse_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    rows = db.query(models.Product).filter(models.Product.warehouse_id == warehouse_id).offset(skip).limit(limit).all()
    return rows
