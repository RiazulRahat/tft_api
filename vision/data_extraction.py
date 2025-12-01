import json
import cv2, easyocr
import matplotlib.pyplot as plt
import pathlib
import torch


PARENT_DIR = pathlib.Path('/users/riazulislamrahat/documents/tft')
JSON_PATH = pathlib.Path(PARENT_DIR / 'data/rectangles.json')
RECTANGLES = json.load(open(JSON_PATH, 'r'))

reader = easyocr.Reader(['en'], gpu=True, quantize=False)
scale = 2.0

class ImageProcessor:
    
    def __init__(self, img):
        # Original image
        self.img = img
        # 'sharpen' variant for better OCR
        self.sharpen = self._unsharp_mask(self._upscale_gray(img), amount=1.2, sigma=1.0)
        # Dictionary to hold extracted texts
        self.text_dict = {}

    # Conversion to sharpen - required methods
    def _upscale_gray(self, img, scale=scale):
        color = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if scale != 1.0:
            color = cv2.resize(color, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        return color
    

    def _unsharp_mask(self, color, amount=1.0, sigma=1.0):
        blur = cv2.GaussianBlur(color, (0,0), sigma)
        sharp = cv2.addWeighted(color, 1 + amount, blur, -amount, 0)
        return sharp
    
    # OCR methods
    def _ocr_boxes(self, box):
        args = dict(
            detail = 1,
            paragraph = False,
            text_threshold = 0.7,
            low_text = 0.3,
            link_threshold = 0.4,
            contrast_ths = 0.1,
            adjust_contrast = 0.7
        )
        return reader.readtext(box, **args)
    
    def extract_texts(self):
        # Extract texts from predefined rectangles and store in dictionary
        for name, box in RECTANGLES.items():
            x, y, w, h = box
            x2, y2, w2, h2 = int(x*scale), int(y*scale), int(w*scale), int(h*scale)
            crop = self.sharpen[y2:y2+h2, x2:x2+w2]
            results = self._ocr_boxes(crop)
            texts = [res[1] for res in results if res[2] > 0.3]
            self.text_dict[name] = texts
    