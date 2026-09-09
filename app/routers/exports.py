from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db, SessionLocal
from app import models, schemas
import csv
import json
from pathlib import Path
from app.core.security import get_current_user
from app.core.authorization import ensure_warehouse_owned, ensure_export_owned
from fastapi.responses import FileResponse
from app.core.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_FORMATS = set(settings.ALLOWED_EXPORT_FORMATS)

@router.post("/", response_model=schemas.ExportJobRead, status_code=status.HTTP_201_CREATED)
def request_export(warehouse_id: int, format: str = "csv", background_tasks: BackgroundTasks | None = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    fmt = (format or "csv").lower()
    if fmt not in ALLOWED_FORMATS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid format: {format}. Allowed: {', '.join(sorted(ALLOWED_FORMATS))}")

    # ensure ownership
    ensure_warehouse_owned(db, warehouse_id, current_user)

    # create export job
    job = models.ExportJob(warehouse_id=warehouse_id, user_id=current_user.id, status=models.ExportJobStatus.pending)
    db.add(job)
    db.commit()
    db.refresh(job)

    def _do_export(job_id: int, fmt: str):
        # Use a separate DB session for background work
        bg_db = SessionLocal()
        jobdb = None
        try:
            jobdb = bg_db.get(models.ExportJob, job_id)
            # re-check ownership to be safe in background
            wh = bg_db.get(models.Warehouse, warehouse_id)
            if wh is None or wh.owner_id != current_user.id:
                jobdb.status = models.ExportJobStatus.failed
                bg_db.add(jobdb)
                bg_db.commit()
                logger.warning("Export aborted: ownership validation failed for job %s", job_id)
                return

            products = bg_db.query(models.Product).filter(models.Product.warehouse_id == warehouse_id).all()
            out_dir = Path(settings.EXPORT_DIR)
            out_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            file_path = out_dir / f"export_{job_id}_{timestamp}.{fmt}"
            if fmt == "csv":
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["id", "title", "status", "created_at"])
                    for p in products:
                        writer.writerow([p.id, p.title, p.status.value, p.created_at.isoformat()])
            else:
                with open(file_path, "w") as f:
                    json.dump([{"id": p.id, "title": p.title, "status": p.status.value, "created_at": p.created_at.isoformat()} for p in products], f)
            jobdb.file_path = str(file_path)
            jobdb.status = models.ExportJobStatus.completed
            logger.info("Export job %s completed, file=%s", job_id, file_path)
        except Exception as exc:
            logger.exception("Export job %s failed", job_id)
            if jobdb:
                jobdb.status = models.ExportJobStatus.failed
                bg_db.add(jobdb)
                bg_db.commit()
        finally:
            try:
                bg_db.close()
            except Exception:
                pass

    # BackgroundTasks should be provided by FastAPI; add the task if available
    if background_tasks is not None:
        background_tasks.add_task(_do_export, job.id, fmt)
    else:
        # Fall back to synchronous export (useful for tests)
        _do_export(job.id, fmt)

    return job

@router.get("/", response_model=list[schemas.ExportJobRead])
def list_exports(warehouse_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ensure_warehouse_owned(db, warehouse_id, current_user)
    rows = db.query(models.ExportJob).filter(models.ExportJob.warehouse_id == warehouse_id, models.ExportJob.user_id == current_user.id).order_by(models.ExportJob.created_at.desc()).all()
    return rows

@router.get("/{job_id}", response_model=schemas.ExportJobRead)
def get_export_status(warehouse_id: int, job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Verify ownership of warehouse and job
    ensure_warehouse_owned(db, warehouse_id, current_user)
    job = ensure_export_owned(db, job_id, current_user)
    # Also ensure job belongs to this warehouse
    if job.warehouse_id != warehouse_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    return job

@router.get("/download/{job_id}")
def download_export(warehouse_id: int, job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Verify ownership
    ensure_warehouse_owned(db, warehouse_id, current_user)
    job = ensure_export_owned(db, job_id, current_user)
    if job.warehouse_id != warehouse_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    if job.status != models.ExportJobStatus.completed or not job.file_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Export not ready")
    file_path = Path(job.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export file not found")
    return FileResponse(path=str(file_path), filename=file_path.name, media_type='application/octet-stream')
