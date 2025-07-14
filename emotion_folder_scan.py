import os
import json
import cv2
import numpy as np
import face_recognition
from datetime import datetime, timedelta
import time
from keras.models import model_from_json

# --- Load Keras emotion model ---
with open("fer.json", "r") as json_file:
    loaded_model_json = json_file.read()
model = model_from_json(loaded_model_json)
model.load_weights("fer.h5")

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
print("[INFO] Emotion model loaded (Keras).")

# --- Load known faces ---
print("[INFO] Encoding known faces...")
known_encodings = []
known_names = []

for filename in os.listdir("known_faces"):
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp")):
        path = os.path.join("known_faces", filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0].upper())
            print(f"[✓] Encoded: {filename}")

# --- Emotion logging setup ---
log_file = "emotion_log.json"
emotion_logs = []

if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
    with open(log_file, "r") as f:
        emotion_logs = json.load(f)

last_logged = {}

def should_log(name):
    now = datetime.now()
    if name not in last_logged:
        last_logged[name] = now
        return True
    if now - last_logged[name] >= timedelta(minutes=10):
        last_logged[name] = now
        return True
    return False

def log_emotion(name, emotion, img_file):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "name": name,
        "emotion": emotion,
        "image": img_file,
        "timestamp": now
    }
    emotion_logs.append(entry)
    with open(log_file, "w") as f:
        json.dump(emotion_logs, f, indent=4)
    print(f"[LOGGED] {name}: {emotion} ({img_file}) at {now}")

# --- Main scanning loop ---
print("[INFO] Starting 10-minute emotion scanning loop...")
try:
    while True:
        for img_file in os.listdir("emotion_images"):
            if img_file.lower().endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp")):
                path = os.path.join("emotion_images", img_file)
                img = cv2.imread(path)
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb)
                face_encodings = face_recognition.face_encodings(rgb, face_locations)

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    matches = face_recognition.compare_faces(known_encodings, face_encoding)
                    name = "UNKNOWN"
                    if True in matches:
                        best_match_index = np.argmin(face_recognition.face_distance(known_encodings, face_encoding))
                        name = known_names[best_match_index]

                    # --- Emotion detection using Keras model ---
                    face_img = rgb[top:bottom, left:right]
                    face_img = cv2.resize(face_img, (48, 48))
                    gray_face = cv2.cvtColor(face_img, cv2.COLOR_RGB2GRAY)
                    gray_face = gray_face.astype("float32") / 255.0
                    gray_face = np.expand_dims(gray_face, axis=(0, -1))  # shape: (1, 48, 48, 1)

                    preds = model.predict(gray_face, verbose=0)
                    emotion = emotion_labels[np.argmax(preds)]

                    if emotion != "Neutral" and should_log(name):
                        log_emotion(name, emotion, img_file)

        print("[INFO] Waiting 10 minutes before next scan...\n")
        time.sleep(600)

except KeyboardInterrupt:
    print("[INFO] Scanning stopped.")
