import os
import re
import sqlite3
from typing import List, Tuple
from PIL import Image

from app.schemas.material_category import MaterialCategory

# Paths configuration
SPECULAR_FOLDER = "original_images/specular"
NON_SPECULAR_FOLDER = "original_images/non-specular"
SERVER_IMAGE_DIR = "app/images"
DB_PATH = "materials.db"
TARGET_SIZE = (500, 500)  # Target image size

# Load characteristics data
with open("original_images/ratings.txt", "r") as f:
    characteristics_data = f.readlines()
characteristics_list = []
for line in characteristics_data:
    if line.strip():  # Skip empty lines
        characteristics_list.append([float(val) for val in line.strip().split()])


def determine_category(material_name: str) -> MaterialCategory:
    """Determine material category based on the specific material names in the dataset."""
    name_lower = material_name.lower()

    # FABRIC category
    if (name_lower.startswith("fabric") or
            name_lower.startswith("carpet")):
        return MaterialCategory.FABRIC

    # WOOD category
    if name_lower.startswith("wood"):
        return MaterialCategory.WOOD

    # LEATHER category
    if name_lower.startswith("leather"):
        return MaterialCategory.LEATHER

    # METAL category
    if (name_lower.startswith("metal") or
            name_lower.startswith("aluminium") or
            "silver" in name_lower or
            "merkur_toy" in name_lower.replace(" ", "_")):
        return MaterialCategory.METAL

    # PAPER category
    if (name_lower.startswith("paper") or
            name_lower.startswith("paperboard") or
            name_lower.startswith("wallpaper")):
        return MaterialCategory.PAPER

    # PLASTIC category
    if (name_lower.startswith("plastic") or
            name_lower.startswith("print3d") or
            name_lower.startswith("mmpp") or
            name_lower.startswith("ppg") or
            name_lower == "rubber01"):
        return MaterialCategory.PLASTIC

    # COATING category
    if (name_lower.startswith("colorlak") or
            name_lower.startswith("car_paint") or
            name_lower.startswith("coating") or
            name_lower.startswith("schlenk")):
        return MaterialCategory.COATING

    # Special cases
    special_cases = {
        "baked_clay": MaterialCategory.UNCATEGORIZED,
        "beads": MaterialCategory.UNCATEGORIZED,
        "glass": MaterialCategory.UNCATEGORIZED,
        "graphite": MaterialCategory.UNCATEGORIZED,
        "sand": MaterialCategory.UNCATEGORIZED,
        "soil": MaterialCategory.UNCATEGORIZED,
        "stone": MaterialCategory.UNCATEGORIZED,
        "tile": MaterialCategory.UNCATEGORIZED,
        "leaf": MaterialCategory.UNCATEGORIZED,
        "merck": MaterialCategory.UNCATEGORIZED,
        "mam": MaterialCategory.UNCATEGORIZED,
        "3m_467mp_silver": MaterialCategory.METAL
    }

    for prefix, category in special_cases.items():
        if name_lower.startswith(prefix):
            return category

    return MaterialCategory.UNCATEGORIZED


def extract_material_name(filename: str) -> str:
    """Extract material name from filename (format: number_name.jpg)."""
    # Remove file extension
    base_name = os.path.splitext(filename)[0]

    # Extract material name (everything after the first underscore)
    match = re.match(r'\d+_(.*)', base_name)
    if match:
        return match.group(1).replace('_', ' ')

    return "unknown_material"


def sanitize_name(name: str) -> str:
    """Replace spaces with underscores in the material name."""
    return name.replace(' ', '_')


def resize_image(image_path: str, target_size: tuple = TARGET_SIZE) -> Image.Image:
    """
    Resize an image to target size while maintaining aspect ratio by center cropping.
    Returns a PIL Image object.
    """
    with Image.open(image_path) as img:
        # Convert to RGB if needed (in case the image is RGBA or another mode)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Calculate dimensions for center crop to maintain aspect ratio
        width, height = img.size

        # First, resize to ensure the smallest dimension matches the target
        if width < height:
            # Width is the smaller dimension
            ratio = target_size[0] / width
            new_width = target_size[0]
            new_height = int(height * ratio)
        else:
            # Height is the smaller dimension (or they're equal)
            ratio = target_size[1] / height
            new_height = target_size[1]
            new_width = int(width * ratio)

        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Then center crop to get exactly target_size
        width, height = img.size
        left = (width - target_size[0]) // 2
        top = (height - target_size[1]) // 2
        right = left + target_size[0]
        bottom = top + target_size[1]

        # Crop and return
        return img.crop((left, top, right, bottom))


def init_database() -> sqlite3.Connection:
    """Initialize SQLite database with proper schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create materials table with is_original field
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        characteristics_brightness REAL NOT NULL,
        characteristics_color_vibrancy REAL NOT NULL,
        characteristics_hardness REAL NOT NULL,
        characteristics_checkered_pattern REAL NOT NULL,
        characteristics_movement_effect REAL NOT NULL,
        characteristics_multicolored REAL NOT NULL,
        characteristics_naturalness REAL NOT NULL,
        characteristics_pattern_complexity REAL NOT NULL,
        characteristics_scale_of_pattern REAL NOT NULL,
        characteristics_shininess REAL NOT NULL,
        characteristics_sparkle REAL NOT NULL,
        characteristics_striped_pattern REAL NOT NULL,
        characteristics_surface_roughness REAL NOT NULL,
        characteristics_thickness REAL NOT NULL,
        characteristics_value REAL NOT NULL,
        characteristics_warmth REAL NOT NULL,
        is_original BOOLEAN NOT NULL
    )
    ''')

    # Create index on name
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_material_name ON materials(name)')

    # Create index on category
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_material_category ON materials(category)')

    conn.commit()
    return conn


def get_material_files() -> List[Tuple[str, str]]:
    """Get paired specular and non-specular image filenames."""
    specular_files = os.listdir(SPECULAR_FOLDER)
    non_specular_files = os.listdir(NON_SPECULAR_FOLDER)

    # Extract number prefixes to match files
    specular_dict = {}
    for filename in specular_files:
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            match = re.match(r'(\d+)_', filename)
            if match:
                number = match.group(1)
                specular_dict[number] = filename

    # Match with non-specular files
    matched_pairs = []
    for filename in non_specular_files:
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            match = re.match(r'(\d+)_', filename)
            if match:
                number = match.group(1)
                if number in specular_dict:
                    matched_pairs.append((specular_dict[number], filename))

    return matched_pairs


def process_materials():
    """Main function to process all materials."""
    conn = init_database()
    cursor = conn.cursor()

    # Get paired image files
    material_pairs = get_material_files()

    # Process each material
    for material_id, (specular_file, non_specular_file) in enumerate(material_pairs, start=1):
        if material_id > 347:  # Only process 347 materials as specified
            break

        # Extract material name from specular file
        material_name = extract_material_name(specular_file)

        # Sanitize the material name (replace spaces with underscores)
        sanitized_name = sanitize_name(material_name)

        # Determine category
        category = determine_category(material_name)

        # Define paths for new files
        new_specular_path = os.path.join(SERVER_IMAGE_DIR, f"{material_id}_specular.jpg")
        new_non_specular_path = os.path.join(SERVER_IMAGE_DIR, f"{material_id}_non_specular.jpg")

        # Create directory if it doesn't exist
        os.makedirs(SERVER_IMAGE_DIR, exist_ok=True)

        # Resize and save specular image
        specular_img = resize_image(os.path.join(SPECULAR_FOLDER, specular_file))
        specular_img.save(new_specular_path, "JPEG", quality=95)

        # Resize and save non-specular image
        non_specular_img = resize_image(os.path.join(NON_SPECULAR_FOLDER, non_specular_file))
        non_specular_img.save(new_non_specular_path, "JPEG", quality=95)

        # Get characteristics data for this material
        if material_id <= len(characteristics_list):
            char_data = characteristics_list[material_id - 1]

            # Insert into database - using the specified order of properties
            cursor.execute('''
            INSERT INTO materials (
                id, name, category,
                characteristics_color_vibrancy,
                characteristics_surface_roughness,
                characteristics_pattern_complexity,
                characteristics_striped_pattern,
                characteristics_checkered_pattern,
                characteristics_brightness,
                characteristics_shininess,
                characteristics_sparkle,
                characteristics_hardness,
                characteristics_movement_effect,
                characteristics_scale_of_pattern,
                characteristics_naturalness,
                characteristics_thickness,
                characteristics_multicolored,
                characteristics_value,
                characteristics_warmth,
                is_original
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                material_id,
                sanitized_name,  # Use the sanitized name here
                category,
                char_data[0],  # color_vibrancy
                char_data[1],  # surface_roughness
                char_data[2],  # pattern_complexity
                char_data[3],  # striped_pattern
                char_data[4],  # checkered_pattern
                char_data[5],  # brightness
                char_data[6],  # shininess
                char_data[7],  # sparkle
                char_data[8],  # hardness
                char_data[9],  # movement_effect
                char_data[10],  # scale_of_pattern
                char_data[11],  # naturalness
                char_data[12],  # thickness
                char_data[13],  # multicolored
                char_data[14],  # value
                char_data[15],  # warmth
                1  # Set is_original to True (1 in SQLite boolean)
            ))

        print(f"Processed material {material_id}: {sanitized_name} ({category})")

    conn.commit()
    conn.close()
    print(f"Successfully imported {min(len(material_pairs), 347)} materials into the database.")


if __name__ == "__main__":
    process_materials()