from pydantic import BaseModel
from app.schemas.material_category import MaterialCategory

class MaterialCreate(BaseModel):
    name: str # todo je to v aplikaci nullable? at je to stejne i tady
    category: MaterialCategory
    store_in_db: bool # true when user wants to store images and analysed data in server DB

class MaterialResponse(BaseModel):
    id: int
    name: str
    category: MaterialCategory
    #store_in_db: bool = True # todo can be added back but it would have to be set in all responses and it has no use..

    specular_image_base64: str # todo az zjistim, ktery je specular, tak zajistit, ze se posila prave ten

    characteristics_brightness: float # todo pozdeji lze pouzivat tridu MaterialCharacteristics namisto 16 floatu po jednom ale muselo by se to do ni rucne konvertovat pri kazdem endpointu..
    characteristics_color_vibrancy: float
    characteristics_hardness: float
    characteristics_checkered_pattern: float
    characteristics_movement_effect: float
    characteristics_multicolored: float
    characteristics_naturalness: float
    characteristics_pattern_complexity: float
    characteristics_scale_of_pattern: float
    characteristics_shininess: float
    characteristics_sparkle: float
    characteristics_striped_pattern: float
    characteristics_surface_roughness: float
    characteristics_thickness: float
    characteristics_value: float
    characteristics_warmth: float

    class Config:
        orm_mode = True
