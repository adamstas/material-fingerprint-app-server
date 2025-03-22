from sqlalchemy import Column, Integer, String, Enum, Float
from sqlalchemy.ext.declarative import declarative_base

from app.schemas.material import MaterialCategory

Base = declarative_base()

# class MaterialCategory(enum.Enum): # todo smazat toto, pouzivam ten ze schemas/material.py
#     FABRIC = "FABRIC"
#     LEATHER = "LEATHER"
#     WOOD = "WOOD"
#     METAL = "METAL"
#     PLASTIC = "PLASTIC"
#     PAPER = "PAPER"
#     COATING = "COATING"
#     UNCATEGORIZED = "UNCATEGORIZED"

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True) # todo pridat jeste nejake indexy?
    name = Column(String)
    category = Column(Enum(MaterialCategory))

     # todo image paths neukladam, budou vzdy stejne a jen se vezme server ID a za to specular a nonspecular treba

    characteristics_brightness = Column(Float)
    characteristics_color_vibrancy = Column(Float)
    characteristics_hardness = Column(Float)
    characteristics_checkered_pattern = Column(Float)
    characteristics_movement_effect = Column(Float)
    characteristics_multicolored = Column(Float)
    characteristics_naturalness = Column(Float)
    characteristics_pattern_complexity = Column(Float)
    characteristics_scale_of_pattern = Column(Float)
    characteristics_shininess = Column(Float)
    characteristics_sparkle = Column(Float)
    characteristics_striped_pattern = Column(Float)
    characteristics_surface_roughness = Column(Float)
    characteristics_thickness = Column(Float)
    characteristics_value = Column(Float)
    characteristics_warmth = Column(Float)