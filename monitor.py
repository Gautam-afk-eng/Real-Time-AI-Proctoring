import cv2
import numpy as np
import mediapipe as mp
import pyaudio
import webrtcvad
import threading
import pygetwindow as gw
import csv
from datetime import datetime

# ==========================================
# 1. SETUP & INITIALIZATION
# ==========================================

# --- A. Logger Setup ---
# Create/clear the log file when the script starts and write the header
with open("exam_log.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Violation Type", "Details"])


def log_event(violation_type, details):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open("exam_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, violation_type, details])
    print(f"[{timestamp}] {violation_type} FLAG: {details}")


# --- B. Audio Setup (WebRTC VAD & PyAudio) ---
vad = webrtcvad.Vad(3)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE * 30 / 1000)

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)


def audio_monitoring_thread():
    print("Started Background Audio Monitoring...")
    while True:
        try:
            audio_frame = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(audio_frame, dtype=np.int16)
            volume = np.linalg.norm(audio_data)

            if vad.is_speech(audio_frame, RATE) and volume > 500:
                # Throttle audio logging so it doesn't spam the CSV instantly
                if np.random.rand() < 0.1:
                    log_event("Audio", f"Human Speech Detected (Vol: {volume:.0f})")
        except Exception:
            pass


audio_thread = threading.Thread(target=audio_monitoring_thread, daemon=True)
audio_thread.start()

# --- C. Multiple Face Setup (MediaPipe Face Detection) ---
mp_face_detection = mp.solutions.face_detection
face_detector = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# --- D. Gaze Tracking Setup (MediaPipe Face Mesh) ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- E. Calibration Storage ---
calibrated = False
calib_data = {"TL": None, "TR": None, "BL": None, "BR": None}
bounds = {"x_min": 0.0, "x_max": 0.0, "y_min": 0.0, "y_max": 0.0}


def get_gaze_point(landmarks):
    """Calculates relative gaze point (gx, gy)"""

    def get_pt(idx):
        return np.array([landmarks[idx].x, landmarks[idx].y])

    L_inner, L_outer = get_pt(33), get_pt(133)
    L_iris = get_pt(468)
    L_width = np.linalg.norm(L_outer - L_inner)

    R_inner, R_outer = get_pt(362), get_pt(263)
    R_iris = get_pt(473)
    R_width = np.linalg.norm(R_outer - R_inner)

    rx_L = np.linalg.norm(L_iris - L_inner) / L_width
    rx_R = np.linalg.norm(R_iris - R_inner) / R_width
    gx = (rx_L + rx_R) / 2

    L_center = (L_inner + L_outer) / 2
    R_center = (R_inner + R_outer) / 2
    ry_L = (L_iris[1] - L_center[1]) / L_width
    ry_R = (R_iris[1] - R_center[1]) / R_width
    gy = (ry_L + ry_R) / 2

    return gx, gy


# ==========================================
# 2. MAIN WEBCAM LOOP
# ==========================================

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Flip image for a mirror effect and convert color space
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape

    # --- 1. Environment Lockdown (Active Window Check) ---
    if calibrated:  # Only enforce lockdown after the exam starts
        try:
            active_window = gw.getActiveWindow()
            if active_window is not None:
                win_title = active_window.title
                # Check if they clicked away from our specific OpenCV window
                if "Proctoring Monitor" not in win_title and win_title.strip() != "":
                    cv2.putText(frame, "FLAG: TAB SWITCH DETECTED!", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 0, 255), 3)
                    if np.random.rand() < 0.05:  # Throttle CSV logging
                        log_event("Environment", f"Switched to: {win_title}")
        except Exception:
            pass

    # --- 2. Multiple Face Detection Logic ---
    results_faces = face_detector.process(rgb_frame)
    num_faces = len(results_faces.detections) if results_faces.detections else 0

    # --- 3. Gaze Tracking Logic ---
    results_mesh = face_mesh.process(rgb_frame)
    gx, gy = 0, 0

    if results_mesh.multi_face_landmarks:
        for face_landmarks in results_mesh.multi_face_landmarks:
            landmarks = face_landmarks.landmark
            gx, gy = get_gaze_point(landmarks)

            # PHASE 1: 4-CORNER CALIBRATION
            if not calibrated:
                cv2.putText(frame, "CALIBRATION: Look at corner & Press Key", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 255), 2)


                def draw_status(text, key, val, y_pos):
                    color = (0, 255, 0) if val else (0, 0, 255)
                    status = "DONE" if val else "TODO"
                    cv2.putText(frame, f"[{key}] {text}: {status}", (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color,
                                2)


                draw_status("Top-Left", "Q", calib_data["TL"], 80)
                draw_status("Top-Right", "W", calib_data["TR"], 110)
                draw_status("Bottom-Left", "A", calib_data["BL"], 140)
                draw_status("Bottom-Right", "S", calib_data["BR"], 170)

                if all(calib_data.values()):
                    cv2.putText(frame, "Press 'SPACE' to Start Exam", (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (0, 255, 255), 2)

            # PHASE 2: PROCTORING
            else:
                msg = "SAFE: On Screen"
                color = (0, 255, 0)
                BUFFER = 0.02
                gaze_flag_type = None

                # Check Boundaries
                if gx < (bounds["x_min"] - BUFFER):
                    msg, color, gaze_flag_type = "ALERT: Looking LEFT", (0, 0, 255), "Looking LEFT"
                elif gx > (bounds["x_max"] + BUFFER):
                    msg, color, gaze_flag_type = "ALERT: Looking RIGHT", (0, 0, 255), "Looking RIGHT"
                elif gy < (bounds["y_min"] - BUFFER):
                    msg, color, gaze_flag_type = "ALERT: Looking UP", (0, 0, 255), "Looking UP"
                elif gy > (bounds["y_max"] + BUFFER):
                    msg, color, gaze_flag_type = "ALERT: Looking DOWN", (0, 0, 255), "Looking DOWN"

                cv2.putText(frame, msg, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

                if gaze_flag_type and np.random.rand() < 0.05:
                    log_event("Gaze Tracking", gaze_flag_type)

                # Draw Iris tracking dots
                L_iris, R_iris = landmarks[468], landmarks[473]
                cv2.circle(frame, (int(L_iris.x * w), int(L_iris.y * h)), 2, (0, 255, 0), -1)
                cv2.circle(frame, (int(R_iris.x * w), int(R_iris.y * h)), 2, (0, 255, 0), -1)

    # --- 4. Display Face Count Text & Logging ---
    if calibrated:
        if num_faces > 1:
            cv2.putText(frame, "FLAG: Multiple Faces!", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if np.random.rand() < 0.05: log_event("Face Detection", "Multiple Faces Detected")
        elif num_faces == 0:
            cv2.putText(frame, "FLAG: No Face!", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if np.random.rand() < 0.05: log_event("Face Detection", "No Face Detected")
        else:
            cv2.putText(frame, "SAFE: 1 Face", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Proctoring Monitor', frame)

    # --- 5. Keybinds ---
    key = cv2.waitKey(1) & 0xFF
    if key == 27: break

    if not calibrated:
        if key == ord('q'): calib_data["TL"] = (gx, gy)
        if key == ord('w'): calib_data["TR"] = (gx, gy)
        if key == ord('a'): calib_data["BL"] = (gx, gy)
        if key == ord('s'): calib_data["BR"] = (gx, gy)

        if key == 32 and all(calib_data.values()):
            all_x, all_y = [v[0] for v in calib_data.values()], [v[1] for v in calib_data.values()]
            bounds["x_min"], bounds["x_max"] = min(all_x), max(all_x)
            bounds["y_min"], bounds["y_max"] = min(all_y), max(all_y)
            calibrated = True

            print(f"Calibration Complete: {bounds}")
            log_event("System", "Exam Started - Calibration Finished")

# ==========================================
# 3. CLEANUP
# ==========================================
log_event("System", "Exam Ended - Proctoring Terminated")
cap.release()
cv2.destroyAllWindows()
stream.stop_stream()
stream.close()
audio.terminate()