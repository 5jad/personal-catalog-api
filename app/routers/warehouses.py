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
        # Do not reveal existence of other users' warehouses
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return wh

@router.post("/", response_model=schemas.WarehouseRead, status_code=status.HTTP_201_CREATED)
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

@router.get("/{warehouse_id}", response_model=schemas.WarehouseRead)
def read_warehouse(warehouse_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    wh = _get_warehouse_for_user(db, warehouse_id, current_user)
    return wh

@router.put("/{warehouse_id}", response_model=schemas.WarehouseRead)
def update_warehouse(warehouse_id: int, w: schemas.WarehouseUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    wh = _get_warehouse_for_user(db, warehouse_id, current_user)
    if w.name is not None:
        wh.name = w.name
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh

@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    wh = _get_warehouse_for_user(db, warehouse_id, current_user)
    db.delete(wh)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
