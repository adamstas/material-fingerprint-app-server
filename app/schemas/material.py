from pydantic import BaseModel
from enum import Enum

class MaterialCategory(str, Enum): # todo pochpit, proc je tu pro validaci dulezity string
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    WOOD = "WOOD"
    METAL = "METAL"
    PLASTIC = "PLASTIC"
    PAPER = "PAPER"
    COATING = "COATING"
    UNCATEGORIZED = "UNCATEGORIZED"

class MaterialCreate(BaseModel):
    name: str # todo je to v aplikaci nullable? at je to stejne i tady
    category: MaterialCategory

    # todo dve fotky sem nebo ne? do DB se neukldaaji, ale v requestu musi byt..

    # characteristics_brightness: float
    # characteristics_color_vibrancy: float
    # characteristics_hardness: float
    # characteristics_checkered_pattern: float
    # characteristics_movement_effect: float
    # characteristics_multicolored: float
    # characteristics_naturalness: float
    # characteristics_pattern_complexity: float
    # characteristics_scale_of_pattern: float
    # characteristics_shininess: float
    # characteristics_sparkle: float
    # characteristics_striped_pattern: float
    # characteristics_surface_roughness: float
    # characteristics_thickness: float
    # characteristics_value: float
    # characteristics_warmth: float

class MaterialResponse(BaseModel):
    id: int
    name: str
    category: MaterialCategory
    # image1_path: str
    # image2_path: str
    #
    # characteristics_brightness: float
    # characteristics_color_vibrancy: float
    # characteristics_hardness: float
    # characteristics_checkered_pattern: float
    # characteristics_movement_effect: float
    # characteristics_multicolored: float
    # characteristics_naturalness: float
    # characteristics_pattern_complexity: float
    # characteristics_scale_of_pattern: float
    # characteristics_shininess: float
    # characteristics_sparkle: float
    # characteristics_striped_pattern: float
    # characteristics_surface_roughness: float
    # characteristics_thickness: float
    # characteristics_value: float
    # characteristics_warmth: float

    class Config:
        orm_mode = True
