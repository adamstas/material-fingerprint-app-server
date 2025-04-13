from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.material_category import MaterialCategory
from app.models.material import Material

class MaterialRepository(ABC):
    @abstractmethod
    def get_material_by_id(self, material_id: int) -> Optional[Material]:
        pass

    @abstractmethod
    def get_materials(self,
                      name_filter: Optional[str] = None,
                      categories: Optional[List[MaterialCategory]] = None) -> List[Material]:
        pass

    @abstractmethod
    def add_material(self, material: Material) -> Material:
        pass