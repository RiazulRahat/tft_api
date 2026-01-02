import json
from pathlib import Path
import cv2
from data_extraction import ImageProcessor


PARENT_DIR = Path(__file__).resolve().parents[1]
SAVE_PATH = PARENT_DIR / "data" / "game_data.json"
IMAGE_DIR = PARENT_DIR / "data" / "screenshots"
IMAGE_EXTS = {".png"}

# Save new data to JSON file
with open(SAVE_PATH, 'r') as f:
    existing = json.load(f)

for image_path in sorted(
    path for path in IMAGE_DIR.iterdir()
    if path.is_file() and path.suffix.lower() in IMAGE_EXTS
):
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Skipping unreadable image: {image_path}")
        continue

    print(f"\n=== {image_path.name} ===")
    processor = ImageProcessor(image)

    processor.extract_texts()
    for name, texts in processor.text_dict.items():
        print(f"{name}: {texts}\n")

    processor.data_clean()
    for name, texts in processor.data.items():
        print(f"{name}: {texts}\n")
    
    try:
        existing['info'].append(processor.data)
    except KeyError:
        existing['info'] = [processor.data]

with open(SAVE_PATH, 'w') as f:
    json.dump(existing, f, indent=4)

