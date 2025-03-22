from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.material import MaterialCreate, MaterialResponse, MaterialCategory
from app.models.material import Material
router = APIRouter()
@router.get("/materials", response_model=list[MaterialResponse])
def read_all_materials(db: Session = Depends(get_db)):
    return db.query(Material).all()

@router.get("/materials/search", response_model=list[MaterialResponse])
def search_materials(
    name: Optional[str] = None,
    categories: Optional[List[MaterialCategory]] = Query(None), # complex parameter, therefore must be Query(None) instead of just None
    db: Session = Depends(get_db)
):
    query = db.query(Material)

    if name:
        query = query.filter(Material.name.contains(name))

    if categories: # if categories are null then returned materials can have any category
        query = query.filter(Material.category.in_(categories))

    return query.all()

@router.post("/materials", response_model=MaterialResponse)
def create_material(
    material_data: MaterialCreate,
    #image1: UploadFile = File(...),
    #image2: UploadFile = File(...),

    # characteristics_brightness: float, # todo charakteristiky nejsou potreba, vytvori se az serverem a ulozi se do DB
    # characteristics_color_vibrancy: float,
    # characteristics_hardness: float,
    # characteristics_checkered_pattern: float,
    # characteristics_movement_effect: float,
    # characteristics_multicolored: float,
    # characteristics_naturalness: float,
    # characteristics_pattern_complexity: float,
    # characteristics_scale_of_pattern: float,
    # characteristics_shininess: float,
    # characteristics_sparkle: float,
    # characteristics_striped_pattern: float,
    # characteristics_surface_roughness: float,
    # characteristics_thickness: float,
    # characteristics_value: float,
    # characteristics_warmth: float,

    db: Session = Depends(get_db)
):

    # todo tady zavolat servicu a udelat 16 charakteristik

    material = Material(
        name = material_data.name,
        # characteristics_brightness=characteristics_brightness,
        # characteristics_color_vibrancy=characteristics_color_vibrancy,
        # characteristics_hardness=characteristics_hardness,
        # characteristics_checkered_pattern=characteristics_checkered_pattern,
        # characteristics_movement_effect=characteristics_movement_effect,
        # characteristics_multicolored=characteristics_multicolored,
        # characteristics_naturalness=characteristics_naturalness,
        # characteristics_pattern_complexity=characteristics_pattern_complexity,
        # characteristics_scale_of_pattern=characteristics_scale_of_pattern,
        # characteristics_shininess=characteristics_shininess,
        # characteristics_sparkle=characteristics_sparkle,
        # characteristics_striped_pattern=characteristics_striped_pattern,
        # characteristics_surface_roughness=characteristics_surface_roughness,
        # characteristics_thickness=characteristics_thickness,
        # characteristics_value=characteristics_value,
        # characteristics_warmth=characteristics_warmth,
        category = material_data.category
    )
    db.add(material)
    db.commit()
    db.refresh(material) # reloads data from DB = material now has ID assigned from DB and so on

    # material.image1_path = save_image(image1, material.id)
    # material.image2_path = save_image(image2, material.id)
    # db.commit()

    return material