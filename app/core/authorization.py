from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app import models

def ensure_warehouse_owned(db: Session, warehouse_id: int, user: models.User) -> models.Warehouse:
    wh = db.get(models.Warehouse, warehouse_id)
    if wh is None or wh.owner_id != user.id:
        # Default policy: return 404 so we don't reveal existence of resources the user doesn't own
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return wh


def ensure_product_in_warehouse(db: Session, warehouse_id: int, product_id: int, user: models.User) -> models.Product:
    # Ensures both the warehouse is owned and the product exists in it
    wh = ensure_warehouse_owned(db, warehouse_id, user)
    product = db.get(models.Product, product_id)
    if product is None or product.warehouse_id != warehouse_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def ensure_export_owned(db: Session, job_id: int, user: models.User) -> models.ExportJob:
    job = db.get(models.ExportJob, job_id)
    if job is None or job.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    return job
