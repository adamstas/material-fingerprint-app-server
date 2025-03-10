import numpy as np
import cv2

WIDTH_PERCENTAGE = 0.10543979463156594
HEIGHT_PERCENTAGE = 0.10543978453272496
# acquired from the source svg file


def find_rects(segmented_img, min_contour_area=500, max_relative_area_diff=0.15):
    cnts, _ = cv2.findContours(segmented_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_filtered = []
    for cnt in cnts:

        contour_area = cv2.contourArea(cnt)
        center, dimensions, angle = cv2.minAreaRect(cnt)

        width, height = dimensions
        enclosing_rect_area = float(width) * height


        if enclosing_rect_area != 0 and contour_area > min_contour_area:
            if abs(1 - contour_area/enclosing_rect_area) <= max_relative_area_diff:
                cnts_filtered.append(cnt)
                
    return cnts_filtered

def is_straight(cnt, tolerance=5):
    
    _, _, angle = cv2.minAreaRect(cnt)
    
    angle = min(angle, 90 - angle)
    
    return abs(angle) <= tolerance

def is_rect(cnt, relative_tolerance=0.1):
    _, dimensions, _ = cv2.minAreaRect(cnt)
    
    width, height = dimensions
    
    print(width, height)
    
    return abs(1 - width / height ) <= relative_tolerance


def cut_outter_border(img, relative_width, relative_height):
    width = img.shape[1]
    height = img.shape[0]
    border_width = int(width * relative_width)
    border_height = int(height * relative_height)
    
    return img[border_height:height - border_height, border_width:width-border_width]

class ValidationResults:

    def __init__(self, valid, cropped_area):
        self.valid = valid
        self.cropped_area = cropped_area

class ImageValidator:

    def __init__(self, image: np.ndarray):
        self.image = image

    

    def validate(self) -> ValidationResults:

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)


        _, black_th = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        _, white_th = cv2.threshold(gray, 50, 155, cv2.THRESH_BINARY)

        rects_cnts = find_rects(black_th)


        if len(rects_cnts) < 1 or not (is_rect(rects_cnts[0]) and is_straight(rects_cnts)):
            return ValidationResults(False, None)
        
        image_points = cv2.approxPolyDP(rects_cnts[0], 50, True)

        dst_points = np.float32([[0, 0], [500, 0], [500, 500], [0, 500]])

        H, _ = cv2.findHomography(image_points, dst_points)

        dst = cv2.warpPerspective(self.image,H,(500,500))

        cropped_area = cut_outter_border(dst, WIDTH_PERCENTAGE*1.01, HEIGHT_PERCENTAGE*1.01)

        return ValidationResults(True, cropped_area)