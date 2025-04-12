from enum import Enum

class MaterialCategory(str, Enum):
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    WOOD = "WOOD"
    METAL = "METAL"
    PLASTIC = "PLASTIC"
    PAPER = "PAPER"
    COATING = "COATING"
    UNCATEGORIZED = "UNCATEGORIZED"