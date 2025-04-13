from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.repository.material_repository import MaterialRepository
from app.models.material import Material
from app.schemas.material_category import MaterialCategory


class SQLiteMaterialRepository(MaterialRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_material_by_id(self, material_id: int) -> Optional[Material]:
        return self.db.query(Material).get(material_id)

    def get_materials(self,
                      name_filter: Optional[str] = None,
                      categories: Optional[List[MaterialCategory]] = None) -> List[Material]:

        query = self.db.query(Material).order_by(func.lower(Material.name))

        if name_filter:
            query = query.filter(Material.name.contains(name_filter))

        if categories: # if categories are null then returned materials can have any category
            query = query.filter(Material.category.in_(categories))

        return query.all()

    def add_material(self, material: Material) -> Material:
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material) # reloads data from DB = material now has ID assigned from DB and so on
        return material