# create json file from images in a folder

import json
from pathlib import Path
import cv2
from data_extraction import ImageProcessor


PARENT_DIR = Path(__file__).resolve().parents[1]
SAVE_PATH = PARENT_DIR / "data" / "game_data.json"
IMAGE_DIR = PARENT_DIR / "data" / "shadow_0"
IMAGE_EXTS = {".png"}

# create new json file
if not SAVE_PATH.exists():
    SAVE_PATH.write_text('{"info": []}', encoding="utf-8")

# open file
with open(SAVE_PATH, 'r') as f:
    existing = json.load(f)

#go through each image in the folder
for image_path in sorted(
    path for path in IMAGE_DIR.iterdir()
    if path.is_file() and path.suffix.lower() in IMAGE_EXTS
):
    image = cv2.imread(str(image_path))

    # error check
    if image is None:
        print(f"Skipping unreadable image: {image_path}")
        continue
    
    # process image
    processor = ImageProcessor(image)
    # extract texts
    processor.extract_texts()
    # clean data
    processor.data_clean()
    
    # append cleaned data to json
    try:
        existing['info'].append(processor.data)
    except KeyError:
        existing['info'] = [processor.data]

# save updated json
with open(SAVE_PATH, 'w') as f:
    json.dump(existing, f, indent=4)
