
import os
import json
import cv2
import numpy as np
import face_recognition
import mediapipe as mp
from datetime import datetime
from keras.models import model_from_json

# Load FER emotion model
with open("fer.json", "r") as json_file:
    loaded_model_json = json_file.read()
emotion_model = model_from_json(loaded_model_json)
emotion_model.load_weights("fer.h5")
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
print("[INFO] Emotion model loaded.")

# Load known faces
known_encodings = []
known_names = []
print("[INFO] Encoding known faces...")
for filename in os.listdir("known_faces"):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join("known_faces", filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0].upper())
print(f"[✓] Loaded known faces: {known_names}")

# Emotion and engagement log setup
emotion_log_path = "emotion_log.json"
engagement_log_path = "engagement_log.json"

emotion_logs = []
if os.path.exists(emotion_log_path) and os.path.getsize(emotion_log_path) > 0:
    with open(emotion_log_path, "r") as f:
        emotion_logs = json.load(f)

engagement_logs = []
if os.path.exists(engagement_log_path) and os.path.getsize(engagement_log_path) > 0:
    with open(engagement_log_path, "r") as f:
        engagement_logs = json.load(f)

last_emotion_logged = {}
last_hand_logged = {}

# Mediapipe pose setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)
frame_count = 0
RECOGNITION_INTERVAL = 10
recognized_name = "UNKNOWN"

def should_log_emotion(name):
    now = datetime.now()
    if name not in last_emotion_logged or (now - last_emotion_logged[name]).seconds >= 600:
        last_emotion_logged[name] = now
        return True
    return False

def should_log_hand(name):
    now = datetime.now()
    current_minute = now.strftime("%Y-%m-%d %H:%M")
    if last_hand_logged.get(name) != current_minute:
        last_hand_logged[name] = current_minute
        return True
    return False

def is_hand_raised(landmarks):
    try:
        return landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y < landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
    except:
        return False

print("[INFO] Starting combined detection...")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_count += 1

    # Face recognition every N frames
    if frame_count % RECOGNITION_INTERVAL == 0:
        small = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small)
        face_encodings = face_recognition.face_encodings(small, face_locations)
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            if True in matches:
                best_match = np.argmin(distances)
                recognized_name = known_names[best_match]
                print(f"[MATCH] Face: {recognized_name}")

    # Emotion detection
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        face_img = rgb_frame[top:bottom, left:right]
        try:
            face_img = cv2.resize(face_img, (48, 48))
            gray_face = cv2.cvtColor(face_img, cv2.COLOR_RGB2GRAY)
            gray_face = gray_face.astype("float32") / 255.0
            gray_face = np.expand_dims(gray_face, axis=(0, -1))
            preds = emotion_model.predict(gray_face, verbose=0)
            emotion = emotion_labels[np.argmax(preds)]
            if emotion != "Neutral" and recognized_name != "UNKNOWN" and should_log_emotion(recognized_name):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                emotion_logs.append({"timestamp": timestamp, "name": recognized_name, "emotion": emotion})
                print(f"[EMOTION] {recognized_name}: {emotion} at {timestamp}")
        except:
            pass

    # Hand raise detection
    pose_result = pose.process(rgb_frame)
    if pose_result.pose_landmarks and recognized_name != "UNKNOWN":
        if is_hand_raised(pose_result.pose_landmarks) and should_log_hand(recognized_name):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            engagement_logs.append({"timestamp": timestamp, "event": "hand_raise", "student": recognized_name})
            print(f"[HAND RAISE] {recognized_name} at {timestamp}")

    # Draw landmarks
    if pose_result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display name
    if recognized_name != "UNKNOWN":
        cv2.putText(frame, f"{recognized_name}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv2.imshow("Emotion + Hand Raise Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Save logs
with open(emotion_log_path, "w") as f:
    json.dump(emotion_logs, f, indent=4)
with open(engagement_log_path, "w") as f:
    json.dump(engagement_logs, f, indent=4)
print("[INFO] Logs saved.")
cap.release()
cv2.destroyAllWindows()
