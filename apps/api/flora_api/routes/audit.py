from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from flora_api.database import get_db
from flora_shared.models import AuditEventModel
from flora_shared.schemas import AuditEvent

router = APIRouter(tags=["audit"])


@router.get("/audit", response_model=list[AuditEvent])
def list_audit_events(db: Session = Depends(get_db)) -> list[AuditEventModel]:
    return db.query(AuditEventModel).order_by(AuditEventModel.created_at.desc()).limit(100).all()
