from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app import models, schemas
from app.core.security import get_current_user

router = APIRouter()

def _get_warehouse_for_user(db: Session, warehouse_id: int, user: models.User) -> models.Warehouse:
    wh = db.get(models.Warehouse, warehouse_id)
    if wh is None or wh.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return wh

@router.post("/", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(warehouse_id: int, p: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    wh = _get_warehouse_for_user(db, warehouse_id, current_user)
    product = models.Product(title=p.title, status=p.status, warehouse_id=warehouse_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", response_model=List[schemas.ProductRead])
def list_products(warehouse_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _get_warehouse_for_user(db, warehouse_id, current_user)
    rows = db.query(models.Product).filter(models.Product.warehouse_id == warehouse_id).offset(skip).limit(limit).all()
    return rows

@router.get("/{product_id}", response_model=schemas.ProductRead)
def read_product(warehouse_id: int, product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _get_warehouse_for_user(db, warehouse_id, current_user)
    product = db.get(models.Product, product_id)
    if product is None or product.warehouse_id != warehouse_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.ProductRead)
def update_product(warehouse_id: int, product_id: int, p: schemas.ProductUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _get_warehouse_for_user(db, warehouse_id, current_user)
    product = db.get(models.Product, product_id)
    if product is None or product.warehouse_id != warehouse_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if p.title is not None:
        product.title = p.title
    if p.status is not None:
        product.status = p.status
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(warehouse_id: int, product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _get_warehouse_for_user(db, warehouse_id, current_user)
    product = db.get(models.Product, product_id)
    if product is None or product.warehouse_id != warehouse_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(product)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
