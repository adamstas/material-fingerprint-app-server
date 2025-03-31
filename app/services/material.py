from typing import Optional, List
from PIL import Image
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.fingeprint_analyzer import FingerPrintAnalyzer
from app.models.material import Material
import numpy as np
from app.material_similarity import calculate_similarity
from app.schemas.material import MaterialCreate, MaterialResponse
from app.schemas.material_category import MaterialCategory
from app.schemas.material_characteristics import MaterialCharacteristics
from app.services.image import save_image, encode_image_to_base64_from_image

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
    return calculate_similarity_for_vector(target_vector, db) #todo pozdeji lze vracet i tu similaritu a vypisovat ji v apce

def calculate_similarity_using_characteristics(characteristics: MaterialCharacteristics, db: Session): # todo kontrolovat zda jsou hodnoty -2,75 do +2,75? asi neni potreba, proste uzivatel si muze najit podobny material k nejakemu fiktivnimu, ktery ma nerealne hodnoty v charakteristikach
    target_vector = get_material_vector_from_characteristics(characteristics)
    return calculate_similarity_for_vector(target_vector, db) #todo pozdeji lze vracet i tu similaritu a vypisovat ji v apce

def filter_materials(materials: List[Material], name: Optional[str], categories: Optional[List[MaterialCategory]]):
    if name:
        materials = [material for material in materials if name.lower() in material.name.lower()]

    if categories:
        materials = [material for material in materials if material.category in categories]

    return materials

def process_image_upload(image_file: UploadFile) -> np.array:
    image = Image.open(image_file.file)
    image = image.convert("RGB") # remove alpha channel that comes with Java Bitmap from Android app
    image = image.resize((500, 500))
    return np.array(image)

def calculate_material_characteristics_and_process_all(
        material_data: MaterialCreate,
        specular_image_file: UploadFile,
        non_specular_image_file: UploadFile,
        db: Session
) -> (Material, str):

    specular_image = process_image_upload(specular_image_file)
    non_specular_image = process_image_upload(non_specular_image_file)

    analyzer = FingerPrintAnalyzer()
    ratings = analyzer.get_material_ratings(non_specular_image, specular_image) # todo ktery je ktery?

# todo ratings maji jine poradi nez moje statistiky,takze to projit a tady to spravne ulozit!
    material = Material(
        name = material_data.name,
        category = material_data.category,
        characteristics_brightness = float(ratings.ratings[0]),
        characteristics_color_vibrancy = float(ratings.ratings[1]),
        characteristics_hardness = float(ratings.ratings[2]),
        characteristics_checkered_pattern = float(ratings.ratings[3]),
        characteristics_movement_effect = float(ratings.ratings[4]),
        characteristics_multicolored = float(ratings.ratings[5]),
        characteristics_naturalness = float(ratings.ratings[6]),
        characteristics_pattern_complexity = float(ratings.ratings[7]),
        characteristics_scale_of_pattern = float(ratings.ratings[8]),
        characteristics_shininess = float(ratings.ratings[9]),
        characteristics_sparkle = float(ratings.ratings[10]),
        characteristics_striped_pattern = float(ratings.ratings[11]),
        characteristics_surface_roughness = float(ratings.ratings[12]),
        characteristics_thickness = float(ratings.ratings[13]),
        characteristics_value = float(ratings.ratings[14]),
        characteristics_warmth = float(ratings.ratings[15])
    )

    if material_data.store_in_db:
        db.add(material)
        db.commit()
        db.refresh(material)  # reloads data from DB = material now has ID assigned from DB and so on

        specular_path = f"images/{material.id}_specular.jpg"
        non_specular_path = f"images/{material.id}_non_specular.jpg"

        save_image(specular_image, specular_path)
        save_image(non_specular_image, non_specular_path)

    else:
        material.id = -1

    image_base64 = encode_image_to_base64_from_image(Image.fromarray(specular_image)) # todo tady pozor ze kdyz to delam primo pro origo obrazek, tak je to 500x500 a neni to zkompriovany JPEG (Ale na to se vykaslat, stejne to pak bude pres endpoint a pro materialy, ktere neukladame, to proste nevratim)
    return material, image_base64

     # todo resit nejak kdyby image byly rozbity a analyza by nesla, tak aby se pak neulozilo neco nejak do DB ale image ne apod.?