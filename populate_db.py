from random import uniform, choice
from sqlalchemy.orm import Session
from app.db.database import engine
from app.models.material import Material, MaterialCategory

def populate_data(material_count = 496):
    session = Session(bind=engine)

    # some random words for random names generator
    adjectives = ["Bright", "Dull", "Smooth", "Rough", "Shiny", "Matte", "Light", "Heavy"]
    nouns = ["Wonder", "Gem", "Wave", "Aura", "Spark", "Luster"]

    def random_name():
        return f"{choice(adjectives)} {choice(nouns)}" # todo ted obsahuje mezeru, povolime ji v apce?

    # for testing just some random values, later add real materials
    def random_characteristics():
        return {
            "characteristics_brightness": uniform(-2.75, 2.75),
            "characteristics_color_vibrancy": uniform(-2.75, 2.75),
            "characteristics_hardness": uniform(-2.75, 2.75),
            "characteristics_checkered_pattern": uniform(-2.75, 2.75),
            "characteristics_movement_effect": uniform(-2.75, 2.75),
            "characteristics_multicolored": uniform(-2.75, 2.75),
            "characteristics_naturalness": uniform(-2.75, 2.75),
            "characteristics_pattern_complexity": uniform(-2.75, 2.75),
            "characteristics_scale_of_pattern": uniform(-2.75, 2.75),
            "characteristics_shininess": uniform(-2.75, 2.75),
            "characteristics_sparkle": uniform(-2.75, 2.75),
            "characteristics_striped_pattern": uniform(-2.75, 2.75),
            "characteristics_surface_roughness": uniform(-2.75, 2.75),
            "characteristics_thickness": uniform(-2.75, 2.75),
            "characteristics_value": uniform(-2.75, 2.75),
            "characteristics_warmth": uniform(-2.75, 2.75),
        }

    default_materials = [
        Material(
            name = random_name(),
            category = choice(list(MaterialCategory)),
            **random_characteristics() # operator "**" unpacks the dictionary returned by random_characteristics() function so key-value pairs are passed as named arguments
        )
        for _ in range(material_count)
    ]

    session.add_all(default_materials)
    session.commit()
    session.close()

if __name__ == "__main__":
    populate_data()
    print("Default data populated.")