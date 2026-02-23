# Real-Time AI Monitoring during Online Exams 🛡️

An automated, multi-modal proctoring and security system built with Python. This lightweight application ensures exam integrity by combining computer vision, acoustic speech isolation, and OS-level environment lockdown without requiring cloud-compute or heavy GPUs.

## 🚀 Key Features
* **Visual Gaze & Face Tracking:** Uses MediaPipe Face Mesh to dynamically map screen boundaries and track student eye movements, while continuously checking for multiple faces in the frame.
* **Acoustic Speech Isolation:** Implements WebRTC Voice Activity Detection (VAD) via PyAudio to specifically isolate human speech and filter out background room noise.
* **System-Level Lockdown:** Utilizes OS-hooks to detect unauthorized tab-switching or loss of active window focus.
* **Live Command Dashboard:** A Flask-based web server using Tailwind CSS that provides human evaluators with a real-time, color-coded log of timestamped cheating violations.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Computer Vision:** OpenCV, MediaPipe
* **Audio Processing:** WebRTC VAD, PyAudio, Numpy
* **Environment Security:** PyGetWindow
* **Web Server & UI:** Flask, Tailwind CSS, FontAwesome

## ⚙️ How to Run
1. Clone this repository to your local machine.
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the proctoring dashboard: `python dashboard.py` (Open the provided localhost link).
4. In a separate terminal, start the monitoring script: `python monitor.py`
5. Perform the 4-corner visual calibration when prompted on the webcam feed.

## 🔒 Privacy First
Unlike commercial proctoring software, this system is designed to run entirely on the "edge" (the student's local machine). No video or audio data is ever recorded or uploaded to a cloud server.