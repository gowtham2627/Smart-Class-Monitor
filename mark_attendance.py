import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from PIL import Image

# Load known faces from folder
def load_image_rgb_force(path):
    img = Image.open(path).convert("RGB")         # Ensure RGB format
    arr = np.array(img).astype(np.uint8)          # Ensure uint8 dtype
    return arr

def find_encodings(images):
    encode_list = []
    for img, name in images:
        try:
            img_rgb = img.astype(np.uint8)
            encodings = face_recognition.face_encodings(img_rgb)
            if encodings:
                encode_list.append((encodings[0], name))
                print(f"[✓] Encoded: {name}")
            else:
                print(f"[!] No face found in: {name}")
        except Exception as e:
            print(f"[ERROR] Failed to encode {name}: {e}")
    return encode_list

def mark_attendance(name):
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    dt_string = now.strftime('%Y-%m-%d %H:%M:%S')

    already_marked_today = False

    # Read existing entries
    if os.path.exists('attendance.csv'):
        with open('attendance.csv', 'r') as f:
            for line in f:
                entry_name, timestamp = line.strip().split(',')
                entry_date = timestamp.split(' ')[0]
                if entry_name == name and entry_date == current_date:
                    already_marked_today = True
                    break

    # Write if not marked today
    if not already_marked_today:
        with open('attendance.csv', 'a') as f:
            f.write(f'{name},{dt_string}\n')
        print(f"[✓] Marked attendance for: {name}")
    else:
        print(f"[⏳] Already marked today: {name}")


# Load all images from known_faces
path = 'known_faces'
images = []
class_names = []

print("[INFO] Loading known faces...")
for file in os.listdir(path):
    full_path = os.path.join(path, file)
    try:
        image = load_image_rgb_force(full_path)
        images.append((image, os.path.splitext(file)[0]))
        print(f"[✓] Loaded {file}, dtype={image.dtype}, shape={image.shape}")
    except Exception as e:
        print(f"[ERROR] Could not load {file}: {e}")

# Encode known faces
encode_list_known = find_encodings(images)
print("[INFO] Encoding complete")

# Start webcam
print("[INFO] Starting webcam...")
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        print("[ERROR] Failed to capture frame from webcam")
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB).astype(np.uint8)

    try:
        faces_current_frame = face_recognition.face_locations(rgb_small_frame)
        encodes_current_frame = face_recognition.face_encodings(rgb_small_frame, faces_current_frame)

        for encode_face, face_loc in zip(encodes_current_frame, faces_current_frame):
            matches = face_recognition.compare_faces([enc[0] for enc in encode_list_known], encode_face)
            face_dist = face_recognition.face_distance([enc[0] for enc in encode_list_known], encode_face)
            match_index = np.argmin(face_dist)

            if matches[match_index]:
                name = encode_list_known[match_index][1].upper()
                print(f"[INFO] Match found: {name}")
                mark_attendance(name)

                # ✅ Write to current_person.txt
                with open("current_person.txt", "w") as f:
                    f.write(name)

                y1, x2, y2, x1 = face_loc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    except Exception as e:
        print(f"[ERROR] Face processing failed: {e}")

    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
