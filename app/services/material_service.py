from typing import Optional, List
from fastapi import UploadFile
from sqlalchemy.orm import Session

import app.core.config
from app.domain.fingerprinting.fingeprint_analyzer import FingerPrintAnalyzer
from app.models.material import Material
import numpy as np
from app.domain.similarity.material_similarity import calculate_similarity
from app.schemas.material import MaterialRequest
from app.schemas.material_category import MaterialCategory
from app.schemas.material_characteristics import MaterialCharacteristics
from app.services.image_service import save_image, process_image_upload

def get_material_vector_from_material(material: Material) -> np.array:
    return np.array([
        material.characteristics_brightness,
        material.characteristics_color_vibrancy,
        material.characteristics_hardness,
        material.characteristics_checkered_pattern,
        material.characteristics_movement_effect,
        material.characteristics_multicolored,
        material.characteristics_naturalness,
        material.characteristics_pattern_complexity,
        material.characteristics_scale_of_pattern,
        material.characteristics_shininess,
        material.characteristics_sparkle,
        material.characteristics_striped_pattern,
        material.characteristics_surface_roughness,
        material.characteristics_thickness,
        material.characteristics_value,
        material.characteristics_warmth
    ])

def get_material_vector_from_characteristics(material_characteristics: MaterialCharacteristics) -> np.array:
    return np.array([
        material_characteristics.brightness,
        material_characteristics.color_vibrancy,
        material_characteristics.hardness,
        material_characteristics.checkered_pattern,
        material_characteristics.movement_effect,
        material_characteristics.multicolored,
        material_characteristics.naturalness,
        material_characteristics.pattern_complexity,
        material_characteristics.scale_of_pattern,
        material_characteristics.shininess,
        material_characteristics.sparkle,
        material_characteristics.striped_pattern,
        material_characteristics.surface_roughness,
        material_characteristics.thickness,
        material_characteristics.value,
        material_characteristics.warmth
    ])

def calculate_similarity_for_vector(target_vector: np.array, db: Session):
    similarities = []
    for material in db.query(Material).all():
        vector = get_material_vector_from_material(material)
        similarity = calculate_similarity(target_vector, vector)
        similarities.append((material, similarity))

    # sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    return [material for material, _ in similarities]

def calculate_similarity_using_id(material_id: int, db: Session): # in Python int can handle large numbers like Long in Java
    target_material = db.query(Material).get(material_id)
    if not target_material:
        return []

    target_vector = get_material_vector_from_material(target_material)
    return calculate_similarity_for_vector(target_vector, db)

def calculate_similarity_using_characteristics(characteristics: MaterialCharacteristics, db: Session):
    target_vector = get_material_vector_from_characteristics(characteristics)
    return calculate_similarity_for_vector(target_vector, db)

def filter_materials(materials: List[Material], name: Optional[str], categories: Optional[List[MaterialCategory]]):
    if name:
        materials = [material for material in materials if name.lower() in material.name.lower()]

    if categories:
        materials = [material for material in materials if material.category in categories]

    return materials

def calculate_material_characteristics_and_process_all(
        material_data: MaterialRequest,
        specular_image_file: UploadFile,
        non_specular_image_file: UploadFile,
        db: Session
) -> (Material, str):

    specular_image = process_image_upload(specular_image_file)
    non_specular_image = process_image_upload(non_specular_image_file)

    analyzer = FingerPrintAnalyzer()
    ratings = analyzer.get_material_ratings(non_specular_image, specular_image)

    material = Material(
        name = material_data.name,
        category = material_data.category,
        is_original = False,
        characteristics_brightness=float(ratings.ratings[5]),
        characteristics_color_vibrancy=float(ratings.ratings[0]),
        characteristics_hardness=float(ratings.ratings[8]),
        characteristics_checkered_pattern=float(ratings.ratings[4]),
        characteristics_movement_effect=float(ratings.ratings[9]),
        characteristics_multicolored=float(ratings.ratings[13]),
        characteristics_naturalness=float(ratings.ratings[11]),
        characteristics_pattern_complexity=float(ratings.ratings[2]),
        characteristics_scale_of_pattern=float(ratings.ratings[10]),
        characteristics_shininess=float(ratings.ratings[6]),
        characteristics_sparkle=float(ratings.ratings[7]),
        characteristics_striped_pattern=float(ratings.ratings[3]),
        characteristics_surface_roughness=float(ratings.ratings[1]),
        characteristics_thickness=float(ratings.ratings[12]),
        characteristics_value=float(ratings.ratings[14]),
        characteristics_warmth=float(ratings.ratings[15])
    )

    if material_data.store_in_db:
        db.add(material)
        db.commit()
        db.refresh(material)  # reloads data from DB = material now has ID assigned from DB and so on

        specular_filename = app.core.config.get_specular_image_name(material.id)
        non_specular_filename = app.core.config.get_non_specular_image_name(material.id)

        save_image(specular_image, specular_filename)
        save_image(non_specular_image, non_specular_filename)

    else:
        material.id = -1

    return material

def material_name_validation(name: str) -> tuple[bool, str]:
    if not name:
        return False, "Name cannot be empty"
    if len(name) < 3:
        return False, "Name must be at least 3 characters long"
    if len(name) > 20:
        return False, "Name length cannot exceed 20 characters"
    if " " in name:
        return False, "Spaces are not allowed, use underscores"
    if not all(c.isalnum() or c == '_' for c in name):
        return False, "Only letters, numbers and underscores allowed"
    return True, ""