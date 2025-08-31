📸 Smart Class Monitor
An AI-powered classroom monitoring system that automates:

🎯 Face Recognition-Based Attendance
😊 Emotion Detection
🙋 Hand Raise Engagement Tracking
📋 Daily Class Summary Generation
Built using Python, Streamlit, Face Recognition, OpenCV, and a pretrained FER model.

📂 Project Structure
📁 known_faces/              → Store registered user face images (name.jpg)
📁 Summaries/                → Daily auto-generated session summaries
📄 attendance.csv            → Records attendance logs
📄 emotion_log.json          → Logs emotion events
📄 engagement_log.json       → Logs hand raise events
📄 current_person.txt        → Stores latest recognized face
📄 fer.h5, fer.json          → Pretrained Facial Emotion Recognition model
📄 streamlit_app.py          → Launches the web interface
📄 mark_attendance.py        → Handles face-based attendance
📄 emotion_hand_combined.py    → Emotion detection + hand raise detection using webcam
📄 generate_summary.py       → Creates daily summary report
📄 requirements.txt          → All required packages
📄 dlib-19.22.99-cp310-cp310-win_amd64.whl          → dlib file
🔧 Installation Instructions
Follow this step-by-step 🪜:

✅ Step 1: Clone the Repo
git clone https://github.com/yourusername/smart-attendance-ai.git
cd smart-attendance-ai
✅ Step 2: Create Virtual Environment
python -m venv .venv
✅ Step 3: Activate the Environment
On Windows:
.venv\Scripts\activate
On Linux/Mac:
source .venv/bin/activate
✅ Step 4: Install Dependencies
pip install -r requirements.txt
🛠 Dlib Installation Troubleshooting
dlib is required for face recognition. It might fail if build tools are missing.

🧱 Install CMake & Build Tools (Only Once)
🔹 Windows:
Install CMake: https://cmake.org/download/
Install Visual Studio Build Tools:
Go to https://visualstudio.microsoft.com/visual-cpp-build-tools/
During installation, select:
C++ build tools
Windows SDK
MSVC Compiler
Then install dlib manually:

pip install cmake
pip install dlib
If still not working, use the prebuilt .whl file from the uploaded files.

Download the one matching your Python version (e.g., dlib‑19.22.99‑cp311‑cp311‑win_amd64.whl), then:

pip install path_to_downloaded_whl
🧠 How It Works
✅ Face Attendance (mark_attendance.py)
Loads face encodings from known_faces/
Recognizes users through webcam
Saves detected names with timestamp to attendance.csv
😊 Emotion Detection (emotion_folder_scan.py)
Detects faces via webcam in real time
Predicts emotions using pretrained FER model (fer.h5, fer.json)
Logs only non-neutral emotions to emotion_log.json every 10 minutes
🙋 Hand Raise Detection (hand_raise_detect.py)
Uses MediaPipe to detect hand raise gestures
Logs engagement to engagement_log.json
📋 Summary Generator (generate_summary.py)
Combines attendance, emotion, and hand raise logs
Generates daily summary in Summaries/YYYY-MM-DD.txt
🖥 Launch the Streamlit UI
streamlit run streamlit_app.py
You’ll get UI buttons to:

✅ Start/Stop Attendance
📡 Start/Stop Session (Emotion + Hand Raise)
🔁 Show/Close Live Face Detection
📅 View Today’s Summary
📂 View Past Summaries
🛑 End Class
📸 Adding Users
Just add images to the known_faces/ folder like:

known_faces/
├── USER6.jpg
├── USER7.jpg
User names are extracted from the image file names.

📦 Requirements
All packages are listed in requirements.txt. Some major ones:

face_recognition
opencv-python
streamlit
keras
tensorflow
mediapipe
numpy
pandas
🧪 Sample Testing
To test individual modules, run them like this:

python mark_attendance.py
python emotion_folder_scan.py
python hand_raise_detect.py
python generate_summary.py
📬 Credits
Project Title: Smart Class Monitor
Duration: May 25 – July 10
Developer: Abhinay Reddy, Edimudi Gowtham
Tools Used: Python, Streamlit, OpenCV, MediaPipe, TensorFlow, Keras, Face Recognition

🙌 Feedback / Issues
Feel free to create an issue if you face any problem or want to suggest improvements.
