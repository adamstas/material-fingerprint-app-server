from pathlib import Path
from PIL import Image
import numpy as np
from fastapi import UploadFile, HTTPException

from app.models.material import Material
from app.schemas.material import MaterialResponse
from app.schemas.material_characteristics import MaterialCharacteristics


def process_image_upload(image_file: UploadFile) -> np.array:
    image = Image.open(image_file.file)
    image = image.convert("RGB") # remove alpha channel that comes with Java Bitmap from Android app
    image = image.resize((500, 500))
    return np.array(image)

def image_validation(image: UploadFile) -> bool:
    if not image.content_type.startswith("image/"):
        return False

    try:
        Image.open(image.file)
    except Exception:
        return False

    image.file.seek(0)  # reset file pointer after checking because UploadFile is passed as reference
    return True


def save_image(image: np.array, path: str):
    img = Image.fromarray(image)
    img.save(path, "JPEG")

def load_image(path: str):
    image_path = Path(path)
    if not image_path.is_file():
        return None
    return image_path

def get_material_response(material: Material) -> MaterialResponse:
    return MaterialResponse(
        id = material.id,
        name = material.name,
        category = material.category,
        characteristics=MaterialCharacteristics(
            brightness=material.characteristics_brightness,
            color_vibrancy=material.characteristics_color_vibrancy,
            hardness=material.characteristics_hardness,
            checkered_pattern=material.characteristics_checkered_pattern,
            movement_effect=material.characteristics_movement_effect,
            multicolored=material.characteristics_multicolored,
            naturalness=material.characteristics_naturalness,
            pattern_complexity=material.characteristics_pattern_complexity,
            scale_of_pattern=material.characteristics_scale_of_pattern,
            shininess=material.characteristics_shininess,
            sparkle=material.characteristics_sparkle,
            striped_pattern=material.characteristics_striped_pattern,
            surface_roughness=material.characteristics_surface_roughness,
            thickness=material.characteristics_thickness,
            value=material.characteristics_value,
            warmth=material.characteristics_warmth
        )
    )