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

router = APIRouter()

@router.post("/", response_model=schemas.ExportJobRead, status_code=status.HTTP_201_CREATED)
def request_export(warehouse_id: int, format: str = "csv", background_tasks: BackgroundTasks = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # ensure ownership
    ensure_warehouse_owned(db, warehouse_id, current_user)

    # create export job
    job = models.ExportJob(warehouse_id=warehouse_id, user_id=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)

    def _do_export(job_id: int, fmt: str):
        # Use a separate DB session for background work
        bg_db = SessionLocal()
        jobdb = None
        try:
            jobdb = bg_db.get(models.ExportJob, job_id)
            products = bg_db.query(models.Product).filter(models.Product.warehouse_id == warehouse_id).all()
            out_dir = Path("/tmp/exports")
            out_dir.mkdir(parents=True, exist_ok=True)
            file_path = out_dir / f"export_{job_id}.{fmt}"
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
        except Exception:
            if jobdb:
                jobdb.status = models.ExportJobStatus.failed
        finally:
            if jobdb:
                bg_db.add(jobdb)
                bg_db.commit()
            bg_db.close()

    # BackgroundTasks should be provided by FastAPI; add the task if available
    if background_tasks is not None:
        background_tasks.add_task(_do_export, job.id, format)
    else:
        # Fall back to synchronous export (useful for tests)
        _do_export(job.id, format)

    return job

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
