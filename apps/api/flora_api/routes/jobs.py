from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from flora_api.database import get_db
from flora_shared.models import JobModel
from flora_shared.schemas import Job

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobModel:
    job = db.get(JobModel, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
