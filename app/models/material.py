from sqlalchemy import Column, String, Enum, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from app.schemas.material import MaterialCategory

Base = declarative_base()

class Material(Base):
    __tablename__ = "materials"

    id = Column(BigInteger, primary_key=True, index=True) # todo pridat jeste nejake indexy?
    name = Column(String)
    category = Column(Enum(MaterialCategory))

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