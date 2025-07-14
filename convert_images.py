# convert_images.py
from PIL import Image
import os

folder = 'known_faces'

for filename in os.listdir(folder):
    if filename.lower().endswith(".png"):
        img_path = os.path.join(folder, filename)
        img = Image.open(img_path).convert('RGB')
        new_name = filename.rsplit('.', 1)[0] + '.jpg'
        img.save(os.path.join(folder, new_name), "JPEG")
        print(f"[✓] Converted: {filename} → {new_name}")
