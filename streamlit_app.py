import streamlit as st
import subprocess
import os
import time
import psutil
from datetime import datetime
import sys


st.set_page_config(page_title="Smart Class Monitor", layout="centered")
st.markdown("<h1 style='text-align: center;'>📸 Smart Class Monitor</h1>", unsafe_allow_html=True)

# --- Function to kill a process by PID ---
def kill_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=3)
        return True
    except Exception as e:
        print(f"[ERROR] Could not terminate PID {pid}: {e}")
        return False

# ---- Section: Attendance Controls ----
st.markdown("## 📍 Attendance Controls")
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Start Attendance", use_container_width=True):
        process = subprocess.Popen([sys.executable, "mark_attendance.py"])
        st.session_state.attendance_pid = process.pid
        st.success("🟢 Attendance started.")

with col2:
    if st.button("⛔ Stop Attendance", use_container_width=True):
        if "attendance_pid" in st.session_state and kill_process(st.session_state.attendance_pid):
            st.success("✅ Attendance process stopped.")
        else:
            st.warning("⚠️ Could not stop attendance process.")

# ---- Section: Session Controls ----
st.markdown("## 🎯 Engagement Session Controls")
col3, col4 = st.columns(2)

with col3:
    if st.button("📡 Start Session (Hand + Emotion)", use_container_width=True):
        venv_python = os.path.join(".venv", "Scripts", "python.exe")
        combined_proc = subprocess.Popen([venv_python, "emotion_hand_combined.py"])
        
        st.session_state.session_pid = combined_proc.pid
        st.success("🟢 Session started.")


with col4:
    if st.button("🛑 Stop Session", use_container_width=True):
        success = False
        if "hand_pid" in st.session_state:
            success |= kill_process(st.session_state.hand_pid)
        if "emotion_pid" in st.session_state:
            success |= kill_process(st.session_state.emotion_pid)
        if success:
            st.success("✅ Session processes stopped.")
        else:
            st.warning("⚠️ Could not stop session processes.")

# ---- Section: Live Face Detection ----
st.markdown("## 🧠 Live Face Detection")
col_live1, col_live2 = st.columns(2)

if "face_pid" not in st.session_state:
    st.session_state.face_pid = None

with col_live1:
    if st.button("🔁 Show Live Face Detection", use_container_width=True):
        process = subprocess.Popen([sys.executable, "face_detect_test.py"])
        st.session_state.face_pid = process.pid
        time.sleep(1)
        st.rerun()

with col_live2:
    if st.button("❌ Close Face Recognition", use_container_width=True):
        if st.session_state.face_pid:
            try:
                p = psutil.Process(st.session_state.face_pid)
                p.terminate()
                p.wait(timeout=3)
                st.success("✅ Face recognition stopped.")
                st.session_state.face_pid = None
            except Exception as e:
                st.warning(f"⚠️ Could not stop: {e}")
        else:
            st.warning("⚠️ No face recognition process running.")



# ---- Section: Summary Reports ----
st.markdown("## 📋 Summary Reports")

if st.button("🛠️ Generate Today's Summary", use_container_width=True):
    subprocess.run(["python", "generate_summary.py"])
    st.success("✅ Summary generated successfully.")

# View Today's Summary
if st.button("📅 View Today’s Summary", use_container_width=True):
    subprocess.run(["python", "generate_summary.py"])
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join("Summaries", f"{today}.txt")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        st.text_area("📝 Today's Summary", content, height=300, disabled=True)
        if st.button("❌ Close Today's Summary", use_container_width=True):
            st.experimental_rerun()
    else:
        st.error("⚠️ Summary file not found for today.")

# ---- View Past Summaries with Toggle Button ----
if "show_past_summary" not in st.session_state:
    st.session_state.show_past_summary = False
if "selected_summary_file" not in st.session_state:
    st.session_state.selected_summary_file = None

def toggle_summary_visibility():
    st.session_state.show_past_summary = not st.session_state.show_past_summary
    st.session_state.selected_summary_file = None

toggle_label = "❌ Close Past Summary" if st.session_state.show_past_summary else "📁 View Past Summaries"
st.button(toggle_label, on_click=toggle_summary_visibility, use_container_width=True)

if st.session_state.show_past_summary:
    summaries_dir = "Summaries"
    if os.path.exists(summaries_dir):
        summaries = sorted(
            [f for f in os.listdir(summaries_dir) if f.endswith(".txt")],
            reverse=True
        )
        if summaries:
            selected = st.selectbox(
                "🗂️ Select a past summary to view:",
                ["-- Select a summary --"] + summaries,
                index=0,
                key="summary_selector"
            )
            if selected != "-- Select a summary --":
                st.session_state.selected_summary_file = selected

        if st.session_state.selected_summary_file:
            filepath = os.path.join(summaries_dir, st.session_state.selected_summary_file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            st.text_area("📖 Summary Content", content, height=300, disabled=True)
    else:
        st.error("📁 'Summaries' folder does not exist.")

# ---- Isolated Styling for Only the "End Class" Button ----


import streamlit as st
import os

# Add CSS to style the button inside .end-class-btn
import streamlit as st
import os

# Inline CSS to target the button inside the wrapper div
st.markdown("""
    <style>
    .end-class-btn button {
        font-size: 24px !important;
        padding: 20px !important;
        height: auto;
        width: 100%;
        border-radius: 8px;
        background-color: #d9534f;
        color: white;
        font-weight: bold;
        border: none;
    }

    .end-class-btn button:hover {
        background-color: #c9302c;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Wrap st.button in a div with class
st.markdown('<div class="end-class-btn">', unsafe_allow_html=True)
if st.button("🛑 End Class", use_container_width=True):
    os.system("taskkill /f /im python.exe")
st.markdown('</div>', unsafe_allow_html=True)
