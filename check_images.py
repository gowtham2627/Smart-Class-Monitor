import os
import cv2

path = 'known_faces'
for filename in os.listdir(path):
    img_path = os.path.join(path, filename)
    img = cv2.imread(img_path)
    print(f"{filename}: ", end="")
    if img is None:
        print("❌ Cannot read image.")
    elif img.dtype != 'uint8':
        print(f"❌ dtype is {img.dtype} (should be uint8)")
    elif len(img.shape) != 3 or img.shape[2] != 3:
        print(f"❌ shape is {img.shape} (should be H,W,3)")
    else:
        print("✅ Valid")
