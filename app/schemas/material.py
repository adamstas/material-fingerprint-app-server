from typing import Optional, List

from pydantic import BaseModel
from app.schemas.material_category import MaterialCategory
from app.schemas.material_characteristics import MaterialCharacteristics

class MaterialRequest(BaseModel):
    name: str
    category: MaterialCategory
    store_in_db: bool # true when user wants to store images and analysed data in server DB

class MaterialResponse(BaseModel):
    id: int
    name: str
    category: MaterialCategory

    characteristics: MaterialCharacteristics

    class Config:
        orm_mode = True

class SimilarMaterialsRequest(BaseModel):
    characteristics: MaterialCharacteristics
    name: Optional[str] = None
    categories: Optional[List[MaterialCategory]] = None
