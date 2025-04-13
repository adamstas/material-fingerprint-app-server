from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, Form, File
from fastapi import Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import FileResponse

import app.core.config
from app.db.database import get_db
from app.schemas.material import MaterialRequest, MaterialResponse, MaterialCategory, SimilarMaterialsRequest
from app.models.material import Material
from app.services.image_service import get_material_response, image_validation, load_image
from app.services.material_service import calculate_similarity_using_id, calculate_similarity_using_characteristics, \
    filter_materials, calculate_material_characteristics_and_process_all, material_name_validation

router = APIRouter()

@router.get("/materials", response_model=List[MaterialResponse])
def get_materials(
    name: Optional[str] = None,
    categories: Optional[List[MaterialCategory]] = Query(None), # complex parameter, therefore must be Query(None) instead of just None
    db: Session = Depends(get_db)
):
    query = db.query(Material).order_by(func.lower(Material.name))

    if name:
        query = query.filter(Material.name.contains(name))

    if categories: # if categories are null then returned materials can have any category
        query = query.filter(Material.category.in_(categories))

    return [get_material_response(material) for material in query.all()]

@router.post("/materials", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(
    response: Response,
    specular_image: UploadFile = File(), # files are not part of Pydantic models (they are not JSONs), and therefore they have to be placed here
    non_specular_image: UploadFile = File(),
    name: str = Form(), # Form() specifies that name is expected to be in the body of the request
    category: MaterialCategory = Form(),
    store_in_db: bool = Form(),
    db: Session = Depends(get_db)
):
    name_validation_result = material_name_validation(name)
    if not name_validation_result[0]:
        raise HTTPException(status_code=400, detail="Invalid material name " + name + ": " + name_validation_result[1])

    if not image_validation(image=specular_image):
        raise HTTPException(status_code=400, detail="Specular image is not a valid image.")

    if not image_validation(image=non_specular_image):
        raise HTTPException(status_code=400, detail="Non specular image is not a valid image.")

    material_data = MaterialRequest(name=name, category=category, store_in_db=store_in_db)
    material = calculate_material_characteristics_and_process_all(material_data, specular_image, non_specular_image, db)

    if not store_in_db:
        response.status_code = status.HTTP_200_OK

    return get_material_response(material)

@router.get("/materials/{material_id}/image/specular")
def get_material_image(
        material_id: int
):
    image_name = app.core.config.get_specular_image_name(material_id)
    file_path = load_image(image_name)

    if file_path is None:
        raise HTTPException(status_code=404, detail=f"Image for material with ID {material_id} not found")

    return FileResponse(file_path, media_type="image/jpeg")

@router.get("/materials/{material_id}/similar", response_model=List[MaterialResponse])
def get_similar_materials(
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

@router.post("/materials/similar", response_model=List[MaterialResponse])
def get_similar_materials_by_characteristics(
    request: SimilarMaterialsRequest,
    db: Session = Depends(get_db)
):
    materials = calculate_similarity_using_characteristics(request.characteristics, db)
    materials = filter_materials(materials, request.name, request.categories)
    return [get_material_response(material) for material in materials]