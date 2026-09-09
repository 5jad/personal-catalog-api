from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app import models, schemas
import csv
import json
from pathlib import Path

router = APIRouter()

def get_current_user_placeholder():
    raise HTTPException(status_code=501, detail="Not implemented: authentication dependency")

@router.post("/", response_model=schemas.ExportJobRead)
def request_export(warehouse_id: int, format: str = "csv", background_tasks: BackgroundTasks = Depends(), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_placeholder)):
    # create export job
    job = models.ExportJob(warehouse_id=warehouse_id, user_id=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)

    def _do_export(job_id: int, fmt: str):
        jobdb = db.get(models.ExportJob, job_id)
        try:
            products = db.query(models.Product).filter(models.Product.warehouse_id == warehouse_id).all()
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
            jobdb.status = models.ExportJobStatus.failed
        db.add(jobdb)
        db.commit()

    background_tasks.add_task(_do_export, job.id, format)
    return job
