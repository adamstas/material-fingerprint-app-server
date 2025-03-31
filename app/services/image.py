import base64
from io import BytesIO
from PIL import Image
import numpy as np
from app.models.material import Material
from app.schemas.material import MaterialResponse

def save_image(image: np.array, path: str):
    img = Image.fromarray(image)
    img.save(path, "JPEG")

def encode_image_step_two(image: Image) -> str:
    image = image.resize((150, 150))  # todo resize to 150x150 or differently?
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def encode_image_to_base64_from_image(image: Image) -> str:
    return encode_image_step_two(image)

def encode_image_to_base64_from_path(image_path: str) -> str:
    with Image.open(image_path) as image:
        return encode_image_to_base64_from_image(image)

def get_material_response_with_base64_image(material: Material, base64: str = None) -> MaterialResponse:
    # todo dat cestu nekam do configu
    if base64 is None:
        specular_base64 = encode_image_to_base64_from_path(f"images/{material.id}_specular.jpg")
        #specular_base64 = encode_image_to_base64("images/1_specular.jpg")
    else:
        specular_base64 = base64

    return MaterialResponse(
        id = material.id,
        name = material.name,
        category = material.category,
        specular_image_base64 = specular_base64,
        characteristics_brightness = material.characteristics_brightness,
        characteristics_color_vibrancy = material.characteristics_color_vibrancy,
        characteristics_hardness = material.characteristics_hardness,
        characteristics_checkered_pattern = material.characteristics_checkered_pattern,
        characteristics_movement_effect = material.characteristics_movement_effect,
        characteristics_multicolored = material.characteristics_multicolored,
        characteristics_naturalness = material.characteristics_naturalness,
        characteristics_pattern_complexity = material.characteristics_pattern_complexity,
        characteristics_scale_of_pattern = material.characteristics_scale_of_pattern,
        characteristics_shininess = material.characteristics_shininess,
        characteristics_sparkle = material.characteristics_sparkle,
        characteristics_striped_pattern = material.characteristics_striped_pattern,
        characteristics_surface_roughness = material.characteristics_surface_roughness,
        characteristics_thickness = material.characteristics_thickness,
        characteristics_value = material.characteristics_value,
        characteristics_warmth = material.characteristics_warmth
    )