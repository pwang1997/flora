from models.sources import SourceCreate
import repositories.sources.sources_repository as sources_repository
from models.sources import SourceRecord
from sqlalchemy.orm import Session


def list_sources(db: Session) -> list[SourceRecord]:
    return sources_repository.list_sources(db)

def create_source(db: Session, payload: SourceCreate) -> SourceRecord:
    return sources_repository.create_source(db, payload)

def delete_source(db: Session, source_id: str) -> bool:
    return sources_repository.delete_source(db, source_id)

def get_source(db: Session, source_id: str) -> SourceRecord:
    return sources_repository.get_source(db, source_id)

def get_source_by_path(db: Session, source_path: str) -> SourceRecord:
    return sources_repository.get_source_by_path(db, source_path)
