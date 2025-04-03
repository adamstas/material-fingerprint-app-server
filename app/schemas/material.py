from pydantic import BaseModel
from app.schemas.material_category import MaterialCategory
from app.schemas.material_characteristics import MaterialCharacteristics

class MaterialCreate(BaseModel):
    name: str # todo je to v aplikaci nullable? at je to stejne i tady
    category: MaterialCategory
    store_in_db: bool # true when user wants to store images and analysed data in server DB

class MaterialResponse(BaseModel):
    id: int
    name: str
    category: MaterialCategory
    #store_in_db: bool = True # todo can be added back but it would have to be set in all responses and it has no use..

    # todo az zjistim, ktery je specular, tak zajistit, ze se posila prave ten

    characteristics: MaterialCharacteristics

    class Config:
        orm_mode = True
