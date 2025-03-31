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