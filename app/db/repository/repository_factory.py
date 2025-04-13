from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository.sqlite_material_repository import SQLiteMaterialRepository
from app.domain.repository.material_repository import MaterialRepository

def get_material_repository(db: Session = Depends(get_db)) -> MaterialRepository:
    return SQLiteMaterialRepository(db)