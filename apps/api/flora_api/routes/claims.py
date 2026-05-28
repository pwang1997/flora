from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from flora_api.database import get_db
from flora_shared.models import ClaimModel
from flora_shared.schemas import Claim

router = APIRouter(tags=["claims"])


@router.get("/claims", response_model=list[Claim])
def list_claims(db: Session = Depends(get_db)) -> list[ClaimModel]:
    return db.query(ClaimModel).order_by(ClaimModel.created_at.desc()).all()
