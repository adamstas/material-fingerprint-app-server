from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile
from fastapi import Response
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import FileResponse

from app.db.database import get_db
from app.schemas.material import MaterialCreate, MaterialResponse, MaterialCategory
from app.models.material import Material
from app.schemas.material_characteristics import MaterialCharacteristics
from app.services.image import get_material_response, image_validation, load_image
from app.services.material import calculate_similarity_using_id, calculate_similarity_using_characteristics, \
    filter_materials, calculate_material_characteristics_and_process_all
router = APIRouter()

@router.get("/materials", response_model=List[MaterialResponse])
def get_all_materials(db: Session = Depends(get_db)):
    materials = db.query(Material).all()
    return [get_material_response(material = material) for material in materials]

@router.get("/materials/search", response_model=List[MaterialResponse])
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

   # return query.all()
    return [get_material_response(material) for material in query.all()]

@router.post("/materials", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(
    # material_data: MaterialCreate,
    name: str,
    category: MaterialCategory,
    store_in_db: bool,
    specular_image: UploadFile, # files are not part of Pydantic models (they are not JSONs), and therefore they have to be placed here
    non_specular_image: UploadFile,
    response: Response,
    db: Session = Depends(get_db)
):
    if not image_validation(image=specular_image):
        raise HTTPException(status_code=400, detail=f"Specular image is not a valid image.")

    if not image_validation(image=non_specular_image):
        raise HTTPException(status_code=400, detail=f"Non specular image is not a valid image.")

    material_data = MaterialCreate(name=name, category=category, store_in_db=store_in_db)
    material = calculate_material_characteristics_and_process_all(material_data, specular_image, non_specular_image, db)

    if not store_in_db:
        response.status_code = status.HTTP_200_OK

    return get_material_response(material)

@router.get("/materials/{material_id}/image")
def get_material_image(
        material_id: int
):
    image_path = f"images/{material_id}_specular.jpg" # todo add from config
    file_path = load_image(image_path)

    if file_path is None:
        raise HTTPException(status_code=404, detail=f"Image for material with ID {material_id} not found")

    return FileResponse(file_path, media_type="image/jpeg")

@router.get("/materials/{material_id}/similar", response_model=List[MaterialResponse])
def get_similar_materials(
        material_id: int,
        db: Session = Depends(get_db)
):
    materials = calculate_similarity_using_id(material_id, db)

    if not materials:
        raise HTTPException(status_code=404, detail=f"Material with ID {material_id} not found")

    return [get_material_response(material) for material in materials]

@router.post("/materials/similarity", response_model=List[MaterialResponse])
def find_similar_materials_by_characteristics(
    characteristics: MaterialCharacteristics,
    db: Session = Depends(get_db)
):
    materials = calculate_similarity_using_characteristics(characteristics, db)
    return [get_material_response(material) for material in materials]

# todo zajistit aby jak tady na serveru, tak i v android apce, byly ty materialy vraceny defaultne ordered by name - i kdyz similar materials budou ordered by similarity, takze tam to upravit i v kodu v apce..

@router.get("/materials/{material_id}/similar/search", response_model=List[MaterialResponse])
def search_similar_materials(
    material_id: int,
    name: Optional[str] = None,
    categories: Optional[List[MaterialCategory]] = Query(None),
    db: Session = Depends(get_db)
):
    materials = calculate_similarity_using_id(material_id, db)
    if not materials:
        raise HTTPException(status_code=404, detail=f"Material with ID {material_id} not found")

    materials = filter_materials(materials, name, categories)
    return [get_material_response(material) for material in materials]

@router.post("/materials/similarity/search", response_model=List[MaterialResponse])
def search_similar_materials_by_characteristics(
    characteristics: MaterialCharacteristics,
    name: Optional[str] = None,
    categories: Optional[List[MaterialCategory]] = Query(None),
    db: Session = Depends(get_db)
):
    materials = calculate_similarity_using_characteristics(characteristics, db) # todo je to OK ze tady volam jednu servicu, pak se z ni vynorim a volam ji zase, ale jinou funkci?
    materials = filter_materials(materials, name, categories)
    return [get_material_response(material) for material in materials]