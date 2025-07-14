import json
import os
from collections import defaultdict
from datetime import datetime

# Load today's date
today = datetime.now().date()
today_str = today.strftime("%Y-%m-%d")

# Load Attendance
attendance = []
if os.path.exists("attendance.csv"):
    with open("attendance.csv", "r") as f:
        for line in f:
            name, timestamp = line.strip().split(",")
            timestamp_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").date()
            if timestamp_date == today:
                attendance.append(name.upper())

# Load Emotion Logs
emotion_data = defaultdict(list)
if os.path.exists("emotion_log.json"):
    with open("emotion_log.json", "r") as f:
        emotions = json.load(f)
        for entry in emotions:
            entry_date = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S").date()
            if entry_date == today and entry["emotion"] != "Neutral":
                emotion_data[entry["name"]].append(entry["emotion"])

# Load Engagement Logs (Hand Raises)
hand_raises = defaultdict(int)
if os.path.exists("engagement_log.json"):
    with open("engagement_log.json", "r") as f:
        engagements = json.load(f)
        for entry in engagements:
            entry_date = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S").date()
            if entry["event"] == "hand_raise" and entry_date == today:
                name = entry["student"].upper()
                hand_raises[name] += 1

# ✅ Generate Summary
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
summary = f"📋 **Class Session Summary**\n🕒 Date: {now_str}\n\n"

# Attendance Section
summary += "✅ Attendance:\n"
if attendance:
    for name in attendance:
        summary += f"- {name}\n"
else:
    summary += "- No attendance recorded today.\n"

# Emotions Section
summary += "\n😊 Emotions Detected:\n"
if emotion_data:
    for name, emotions in emotion_data.items():
        counts = defaultdict(int)
        for emotion in emotions:
            counts[emotion] += 1
        emotion_summary = ', '.join([f"{emo} ({count})" for emo, count in counts.items()])
        summary += f"- {name}: {emotion_summary}\n"
else:
    summary += "- No emotional events logged today.\n"

# Hand Raises Section
summary += "\n🙋 Engagement (Hand Raises):\n"
if hand_raises:
    for name, count in hand_raises.items():
        summary += f"- {name}: {count} time(s)\n"
else:
    summary += "- No hand raises logged today.\n"

# ✅ Save summary in Summaries folder
os.makedirs("Summaries", exist_ok=True)
summary_filename = f"Summaries/{today_str}.txt"

if not os.path.exists(summary_filename):
    with open(summary_filename, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"[✓] Summary saved to {summary_filename}")
else:
    print(f"[!] Summary for today already exists: {summary_filename}")

# ✅ Optional: Print summary to console
print("\n" + summary)
