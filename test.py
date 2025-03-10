import logging

from fingeprint_analyzer import FingerPrintAnalyzer
from image_validation import ImageValidator
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():

    image = Image.open('images/slot2.png')
    image = image.resize((500, 500))
    image = np.array(image)

    validator = ImageValidator(image)
    print(validator.validate().valid)


    analyzer = FingerPrintAnalyzer()
    ratings = analyzer.get_material_ratings(image, image)



    print(f"Ratings: {ratings.ratings}")

    # returns plots as np.ndarray images
    # they can be later used for saving to file,
    # sending across the server or anything else that is needed
    line_plot = ratings.get_line_plot()
    polar_plot = ratings.get_polar_plot()


    # saving to file for example
    line_plot_image = Image.fromarray(line_plot)
    polar_plot_image = Image.fromarray(polar_plot)

    line_plot_image.save('line_plot.png')
    polar_plot_image.save('polar_plot.png')

if __name__ == "__main__":

    main()
