# Real-Time AI Monitoring during Online Exams 🛡️

<img width="806" height="973" alt="Screenshot 2026-02-26 103046" src="https://github.com/user-attachments/assets/1b0d19ca-5144-4f53-b674-7398e5a8d4d5" />


An automated, multi-modal proctoring and security system built with Python. This lightweight application ensures exam integrity by combining computer vision, acoustic speech isolation, and OS-level environment lockdown without requiring cloud-compute or heavy GPUs.

### 🚀 Key Features

* **Visual Gaze & Face Tracking:** Uses MediaPipe Face Mesh to dynamically map screen boundaries and track student eye movements, while continuously checking for multiple faces in the frame.
* **Acoustic Speech Isolation:** Implements WebRTC Voice Activity Detection (VAD) via PyAudio to specifically isolate human speech and filter out background room noise.
* **System-Level Lockdown:** Utilizes OS-hooks to detect unauthorized tab-switching or loss of active window focus.
* **Live Command Dashboard:** A Flask-based web server using Tailwind CSS that provides human evaluators with a real-time, color-coded log of timestamped cheating violations.

### 🛠️ Tech Stack

**Core Language:**<br>
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

**Computer Vision & Audio Processing:**<br>
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white)
![WebRTC](https://img.shields.io/badge/WebRTC-333333?style=for-the-badge&logo=webrtc&logoColor=white)
* **Libraries:** MediaPipe, PyAudio, PyGetWindow

**Web Server & UI:**<br>
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FontAwesome](https://img.shields.io/badge/FontAwesome-339AF0?style=for-the-badge&logo=fontawesome&logoColor=white)

### ⚙️ How to Run

1. Clone this repository to your local machine.
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the proctoring dashboard: `python dashboard.py` (Open the provided localhost link).
4. In a separate terminal, start the monitoring script: `python monitor.py`
5. Perform the 4-corner visual calibration when prompted on the webcam feed.

### 🔒 Privacy First

Unlike commercial proctoring software, this system is designed to run entirely on the "edge" (the student's local machine). No video or audio data is ever recorded or uploaded to a cloud server.
