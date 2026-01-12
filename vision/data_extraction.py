import json, ijson
import cv2, easyocr
import pathlib
import re

PARENT_DIR = pathlib.Path('/users/riazulislamrahat/documents/tft')
JSON_PATH = pathlib.Path(PARENT_DIR / 'data/rectangles.json')
DRAGON_PATH = pathlib.Path(PARENT_DIR / 'data/tft_data.json')
RECTANGLES = json.load(open(JSON_PATH, 'r'))

reader = easyocr.Reader(['en'], gpu=True, quantize=False)
scale = 2.0
TFT_SET = "TFT16"

class ImageProcessor:

    def __init__(self, img):
        # Original image
        self.img = img
        # 'sharpen' variant for better OCR
        self.sharpen = self._unsharp_mask(self._upscale_gray(img), amount=1.2, sigma=1.0)
        
        # Dictionary to hold extracted texts
        self.text_dict = {}

        # Cleaned data to be stored
        self.data = {}

    def print_texts(self):
        for key, texts in self.text_dict.items():
            print(f"{key}: {texts}")

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
        # Extract texts from predefined ROI and store in dictionary
        for name, box in RECTANGLES.items():
            x, y, w, h = box
            x2, y2, w2, h2 = int(x*scale), int(y*scale), int(w*scale), int(h*scale)
            crop = self.sharpen[y2:y2+h2, x2:x2+w2]
            results = self._ocr_boxes(crop)
            texts = [res[1] for res in results if res[2] > 0.3]
            self.text_dict[name] = texts

    def _clean_round(self, round, prev_round):
        for text in round:
            pass
        
        return prev_round

    # Cleaning and organizing extracted data
    def data_clean(self):
        for key, texts in self.text_dict.items():
            if key == 'round':
                prev_round = self.data.get('round', None)
                self.data['round'] = self._clean_round(texts, prev_round)
            elif key == 'exp':
                cur_exp, max_exp = self._clean_exp(texts[0], self.data.get('level', 1))
                self.data['cur_exp'] = cur_exp
                self.data['max_exp'] = max_exp
            elif 'shop' in key:
                champs = []
                for item in texts:
                    try:
                        float(item)
                    except:
                        champs.append([item])
                for c in champs:
                    name = c[0]
                    cost, traits = self._get_cost_trait(name)
                    c.append(cost)
                    c.append(traits)
                self.data["shop"] = champs
            elif key == 'gold':
                s = texts
                if isinstance(s, list):
                    s = ''.join(s)
                s = str(s).replace(' ', '')
                self.data[key] = int(s) if s else 0
            elif key == 'streak':
                s = texts
                if isinstance(s, list):
                    s = ''.join(s)
                s = str(s).replace(' ', '')
                self.data[key] = int(s) if s else 0
            elif 'trait' in key:
                # to be fixed later for incorrect OCR
                trait_list = [item for item in texts if not any(char.isdigit() for char in item)]
                self.data.setdefault('active_traits', []).extend(trait_list)
            else:
                # template matching
                pass


    def dump_to_json(self, path):
        with open(path, 'w') as f:
            json.dump(self.data, f, indent=4)
