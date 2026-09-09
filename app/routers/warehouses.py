from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app import models, schemas
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.WarehouseRead)
def create_warehouse(w: schemas.WarehouseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    wh = models.Warehouse(name=w.name, owner_id=current_user.id)
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh

@router.get("/", response_model=List[schemas.WarehouseRead])
def list_warehouses(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    rows = db.query(models.Warehouse).filter(models.Warehouse.owner_id == current_user.id).offset(skip).limit(limit).all()
    return rows
