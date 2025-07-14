import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import os
import json
from datetime import datetime

# Load known faces
known_face_encodings = []
known_face_names = []
print("[INFO] Loading known faces...")
for filename in os.listdir("known_faces"):
    if filename.lower().endswith((".jpg", ".png")):
        image = face_recognition.load_image_file(os.path.join("known_faces", filename))
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            name = os.path.splitext(filename)[0].upper()
            known_face_names.append(name)
print(f"[✓] Loaded known faces: {known_face_names}")

# Load or initialize engagement log
log_path = "engagement_log.json"
if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
    with open(log_path, "r") as f:
        engagement_log = json.load(f)
else:
    engagement_log = []

last_logged = {}  # For throttling log entries

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# Start webcam
cap = cv2.VideoCapture(0)
print("[INFO] Webcam started")

frame_count = 0
recognized_name = "UNKNOWN"
RECOGNITION_INTERVAL = 10

def is_hand_raised(landmarks):
    try:
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        return right_wrist.y < right_shoulder.y
    except:
        return False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    flipped = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)

    # Face Recognition every N frames
    if frame_count % RECOGNITION_INTERVAL == 0:
        small = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(small)
        face_encodings = face_recognition.face_encodings(small, face_locations)
        recognized_name = "UNKNOWN"
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if matches and any(matches):
                best_match = np.argmin(distances)
                if matches[best_match]:
                    recognized_name = known_face_names[best_match]
                    print(f"[MATCH] Face: {recognized_name}")

    # Pose detection for hand raise
    pose_result = pose.process(rgb_frame)
    if recognized_name != "UNKNOWN" and pose_result.pose_landmarks:
        if is_hand_raised(pose_result.pose_landmarks):
            now = datetime.now()
            current_minute = now.strftime("%Y-%m-%d %H:%M")
            if last_logged.get(recognized_name) != current_minute:
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                engagement_log.append({
                    "timestamp": timestamp,
                    "event": "hand_raise",
                    "student": recognized_name
                })
                last_logged[recognized_name] = current_minute
                print(f"[LOGGED] {recognized_name} raised hand at {timestamp}")
            else:
                print(f"[SKIP] Already logged this minute")
        else:
            print("[INFO] Hand not raised")

    # Draw landmarks
    if pose_result.pose_landmarks:
        mp_drawing.draw_landmarks(flipped, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Display name
    if recognized_name != "UNKNOWN":
        cv2.putText(flipped, f"Detected: {recognized_name}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    cv2.imshow("Live Face + Hand Raise Detection", flipped)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

# Save engagement log
with open(log_path, "w") as f:
    json.dump(engagement_log, f, indent=4)
print("[INFO] Engagement log saved.")
