import cv2
import numpy as np
import face_recognition
import os
from PIL import Image

# Load known faces
def load_image_rgb_force(path):
    img = Image.open(path).convert("RGB")
    return np.array(img).astype(np.uint8)

def find_encodings(images):
    encodings = []
    for img, name in images:
        try:
            img_rgb = img.astype(np.uint8)
            encode = face_recognition.face_encodings(img_rgb)
            if encode:
                encodings.append((encode[0], name))
                print(f"[✓] Encoded: {name}")
            else:
                print(f"[!] No face found in: {name}")
        except Exception as e:
            print(f"[ERROR] Encoding failed for {name}: {e}")
    return encodings

# Load all images
known_path = 'known_faces'
images = []
for file in os.listdir(known_path):
    try:
        img = load_image_rgb_force(os.path.join(known_path, file))
        name = os.path.splitext(file)[0]
        images.append((img, name))
    except Exception as e:
        print(f"[ERROR] Could not load {file}: {e}")

known_encodings = find_encodings(images)

# Webcam capture
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB).astype(np.uint8)

    face_locations = face_recognition.face_locations(rgb_small)
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    for encode_face, face_loc in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces([e[0] for e in known_encodings], encode_face)
        face_distances = face_recognition.face_distance([e[0] for e in known_encodings], encode_face)
        match_index = np.argmin(face_distances)

        name = "Unknown"
        if matches[match_index]:
            name = known_encodings[match_index][1].upper()

        # Draw box and name
        y1, x2, y2, x1 = [val * 4 for val in face_loc]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        # Save name to file
        with open("current_person.txt", "w") as f:
            f.write(name)

    cv2.imshow("Live Face Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
