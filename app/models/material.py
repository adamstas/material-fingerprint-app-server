import sqlalchemy
from sqlalchemy import Column, String, Enum, Float, Integer, Boolean
from sqlalchemy.orm import declarative_base
from app.schemas.material import MaterialCategory

Base = sqlalchemy.orm.declarative_base()

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True) # SQLite Integer is handled as 64bit integer (https://sqlite.org/autoinc.html)
    name = Column(String, nullable=False, index=True)
    category = Column(Enum(MaterialCategory), nullable=False, index=True)

    is_original = Column(Boolean, nullable=False) # if the material is one of 347 original materials

    characteristics_brightness = Column(Float, nullable=False)
    characteristics_color_vibrancy = Column(Float, nullable=False)
    characteristics_hardness = Column(Float, nullable=False)
    characteristics_checkered_pattern = Column(Float, nullable=False)
    characteristics_movement_effect = Column(Float, nullable=False)
    characteristics_multicolored = Column(Float, nullable=False)
    characteristics_naturalness = Column(Float, nullable=False)
    characteristics_pattern_complexity = Column(Float, nullable=False)
    characteristics_scale_of_pattern = Column(Float, nullable=False)
    characteristics_shininess = Column(Float, nullable=False)
    characteristics_sparkle = Column(Float, nullable=False)
    characteristics_striped_pattern = Column(Float, nullable=False)
    characteristics_surface_roughness = Column(Float, nullable=False)
    characteristics_thickness = Column(Float, nullable=False)
    characteristics_value = Column(Float, nullable=False)
    characteristics_warmth = Column(Float, nullable=False)