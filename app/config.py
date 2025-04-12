import os
# we have to distinguish between directories where images are stored
# so during tests the real images are not replaced by test images
IMAGES_DIR = os.environ.get("IMAGES_DIR", "./images")

# returns full image path
def get_image_path(filename: str) -> str:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    return os.path.join(IMAGES_DIR, filename)

SPECULAR_IMAGE_NAME_SUFFIX =  "_specular.jpg"
NON_SPECULAR_IMAGE_NAME_SUFFIX =  "_non_specular.jpg"

def get_specular_image_name(id: int) -> str:
    return f"{id}{SPECULAR_IMAGE_NAME_SUFFIX}"

def get_non_specular_image_name(id: int) -> str:
    return f"{id}{NON_SPECULAR_IMAGE_NAME_SUFFIX}"