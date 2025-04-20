import tempfile
import pytest
import io
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.db.repository.repository_factory import get_material_repository
from app.db.repository.sqlite_material_repository import SQLiteMaterialRepository
from app.main import app as application
from app.db.database import get_db
from app.models.material import Base
import app.models
import app.core.config as config


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",  # in-memory database
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="repository")
def repository_fixture(session):
    return SQLiteMaterialRepository(session)

@pytest.fixture(name="client")
def client_fixture(repository, session):
    def override_get_db():
        try:
            yield session
        finally:
            pass  # closing is handled in the session fixture

    application.dependency_overrides[get_db] = override_get_db

    def override_get_repository():
        return repository

    application.dependency_overrides[get_material_repository] = override_get_repository

    with TestClient(application) as test_client:
        yield test_client

    application.dependency_overrides = {}

def create_test_image():
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))  # red square
    image.save(file, format="PNG")
    file.name = "test.png"
    file.seek(0)
    return file

@pytest.fixture
def test_images():
    specular_image = create_test_image()
    non_specular_image = create_test_image()
    return specular_image, non_specular_image

@pytest.fixture(autouse=True)
def temp_image_dir(): # temporary directory for images during tests
    original_images_dir = config.IMAGES_DIR

    with tempfile.TemporaryDirectory() as temp_dir:
        app.core.config.IMAGES_DIR = temp_dir

        yield temp_dir

        # reset to original after test
        app.core.config.IMAGES_DIR = original_images_dir
        # when this code block finishes
        # the temp directory is automatically deleted

def create_colored_test_image(color):
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), color=color)
    image.save(file, format="PNG")
    file.name = f"test_{color[0]}_{color[1]}_{color[2]}.png"
    file.seek(0)
    return file

# ----------------------------- Test cases -----------------------------

def test_get_materials_empty_db(client: TestClient):
    response = client.get("/materials")
    assert response.status_code == 200
    assert response.json() == []

def test_create_material_missing_fields(client: TestClient, test_images):
    specular_image, non_specular_image = test_images
    response = client.post(
        "/materials",
        files={
            "specular_image": ("specular.png", specular_image, "image/png"),
            "non_specular_image": ("non_specular.png", non_specular_image, "image/png"),
        },
        data={
            # missing 'name' field
            "category": "METAL",
            "store_in_db": "true",
        },
    )
    assert response.status_code == 422
    assert "name" in response.text

def test_create_material_invalid_image(client: TestClient):
    specular_image = io.BytesIO(b"This is not an image") # invalid image
    specular_image.name = "specular.png"
    non_specular_image = create_test_image()

    response = client.post(
        "/materials",
        files={
            "specular_image": ("specular.png", specular_image, "image/png"),
            "non_specular_image": ("non_specular.png", non_specular_image, "image/png"),
        },
        data={
            "name": "Test_material",
            "category": "METAL",
            "store_in_db": "true",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Specular image is not a valid image."

def test_create_material_successful(test_images, client: TestClient):
    specular_image, non_specular_image = test_images

    response = client.post(
        "/materials",
        files={
            "specular_image": ("specular.png", specular_image, "image/png"),
            "non_specular_image": ("non_specular.png", non_specular_image, "image/png"),
        },
        data={
            "name": "Test_material",
            "category": "METAL",
            "store_in_db": "true",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test_material"
    assert data["category"] == "METAL"
    assert "id" in data

def test_get_materials_with_filter(client: TestClient):
    response = client.post(
        "/materials",
        files={
            "specular_image": ("specular.png", create_test_image(), "image/png"),
            "non_specular_image": ("non_specular.png", create_test_image(), "image/png"),
        },
        data={
            "name": "Filter_test_material",
            "category": "WOOD",
            "store_in_db": "true",
        },
    )
    assert response.status_code == 201

    # filter materials by name
    response = client.get("/materials", params={"name": "Filter"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    for material in data:
        assert "Filter" in material["name"]

def test_get_material_image_not_found(client: TestClient):
    response = client.get("/materials/123456/image/specular")
    assert response.status_code == 404
    assert response.json()["detail"] == "Image for material with ID 123456 not found"

def test_get_material_image_successful(test_images, client: TestClient):
    specular_image, non_specular_image = test_images

    response = client.post(
        "/materials",
        files={
            "specular_image": ("specular.png", specular_image, "image/png"),
            "non_specular_image": ("non_specular.png", non_specular_image, "image/png"),
        },
        data={
            "name": "Material_for_test",
            "category": "METAL",
            "store_in_db": "true",
        },
    )
    assert response.status_code == 201
    material_id = response.json()["id"]

    response = client.get(f"/materials/{material_id}/image/specular")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

def test_get_similar_materials_not_found(client: TestClient):
    response = client.get("/materials/9999/similar")
    assert response.status_code == 404  # Not Found
    assert response.json()["detail"] == "Material with ID 9999 not found"

def test_get_similar_materials_successful(client: TestClient):
    red_specular = create_colored_test_image((255, 0, 0))
    red_non_specular = create_colored_test_image((255, 0, 0))

    blue_specular = create_colored_test_image((0, 0, 255))
    blue_non_specular = create_colored_test_image((0, 0, 255))

    response1 = client.post(
        "/materials",
        files={
            "specular_image": ("specular_red.png", red_specular, "image/png"),
            "non_specular_image": ("non_specular_red.png", red_non_specular, "image/png"),
        },
        data={
            "name": "Red_test",
            "category": "PLASTIC",
            "store_in_db": "true",
        },
    )
    assert response1.status_code == 201
    material1_id = response1.json()["id"]

    response2 = client.post(
        "/materials",
        files={
            "specular_image": ("specular_blue.png", blue_specular, "image/png"),
            "non_specular_image": ("non_specular_blue.png", blue_non_specular, "image/png"),
        },
        data={
            "name": "Blue_test",
            "category": "WOOD",
            "store_in_db": "true",
        },
    )

    assert response2.status_code == 201
    material2_id = response2.json()["id"]

    response = client.get(f"/materials/{material1_id}/similar")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2

    assert data[0]["id"] == material1_id # material red is more similar to material red than material blue is to material red
    assert data[1]["id"] == material2_id

def test_get_similar_materials_by_characteristics(client: TestClient):
    red_specular = create_colored_test_image((255, 0, 0))
    red_non_specular = create_colored_test_image((255, 0, 0))

    blue_specular = create_colored_test_image((0, 0, 255))
    blue_non_specular = create_colored_test_image((0, 0, 255))

    response1 = client.post(
        "/materials",
        files={
            "specular_image": ("specular_red.png", red_specular, "image/png"),
            "non_specular_image": ("non_specular_red.png", red_non_specular, "image/png"),
        },
        data={
            "name": "Red_material_test",
            "category": "PLASTIC",
            "store_in_db": "true",
        },
    )
    assert response1.status_code == 201

    response2 = client.post(
        "/materials",
        files={
            "specular_image": ("specular_blue.png", blue_specular, "image/png"),
            "non_specular_image": ("non_specular_blue.png", blue_non_specular, "image/png"),
        },
        data={
            "name": "Blue_material_test",
            "category": "WOOD",
            "store_in_db": "true",
        },
    )

    assert response2.status_code == 201
    material2_id = response2.json()["id"]

    characteristics_data = {
        "brightness": 0.5,
        "color_vibrancy": -1.2,
        "hardness": 1.0,
        "checkered_pattern": -2.5,
        "movement_effect": 2.0,
        "multicolored": 0.0,
        "naturalness": 1.7,
        "pattern_complexity": -0.7,
        "scale_of_pattern": 2.75,
        "shininess": -2.0,
        "sparkle": 1.5,
        "striped_pattern": -1.3,
        "surface_roughness": 0.9,
        "thickness": -2.75,
        "value": 0.0,
        "warmth": 2.1
    }

    request_data = {
        "characteristics": characteristics_data,
        "name": "Blue",
        "categories": ["WOOD"]
    }

    response = client.post(
        "/materials/similar",
        json=request_data,
    )
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == material2_id  # filter should return only material 2

def test_get_similar_materials_by_characteristics_missing_characteristics(client: TestClient):
    request_data = {
        # "characteristics" is missing
        "name": "Test",
        "categories": ["METAL", "WOOD"],
    }

    response = client.post(
        "/materials/similar",
        json=request_data,
    )
    assert response.status_code == 422
    assert "characteristics" in response.text

def test_material_images_are_stored_correctly(client: TestClient, temp_image_dir):
    specular_image = create_test_image()
    non_specular_image = create_test_image()

    response = client.post(
        "/materials",
        files={
            "specular_image": ("specular.png", specular_image, "image/png"),
            "non_specular_image": ("non_specular.png", non_specular_image, "image/png"),
        },
        data={
            "name": "Image_storage_test",
            "category": "METAL",
            "store_in_db": "true",
        },
    )

    assert response.status_code == 201
    material_id = response.json()["id"]

    specular_path = os.path.join(temp_image_dir, app.core.config.get_specular_image_name(material_id))
    non_specular_path = os.path.join(temp_image_dir, app.core.config.get_non_specular_image_name(material_id))

    assert os.path.exists(specular_path)
    assert os.path.exists(non_specular_path)

    from PIL import Image
    try:
        Image.open(specular_path)
        Image.open(non_specular_path)
    except Exception as e:
        pytest.fail(f"Failed to open stored images: {e}")