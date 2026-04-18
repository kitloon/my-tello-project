# handmain.py

import cv2 as cv
import time
from DroneController import Tello
from FaceDetection import detect_face
from HandDetection import HandDetector

# --- Control Parameters ---
kpX, kpY, kpPitch = 0.4, 0.4, 0.4
TARGET_WIDTH = 175
FLIP_COOLDOWN = 5  # seconds

# --- Object Initialization ---
# print("🚀 Initializing Tello and HandDetector...")
tello = Tello()
hand_detector = HandDetector()
last_flip_time = 0

try:
    # print("🔗 Connecting to Tello...")
    tello.connect()
    # print("✅ Tello connected")

    # print("🔋 Fetching battery status...")
    time.sleep(1.0)
    print(f"🔋 Current Battery Level: {tello.get_battery()} %")

    # print("📺 Enabling video stream...")
    tello.streamon()
    time.sleep(2)
    # print("✅ Video stream is ON")

    # print("🛫 Taking off...")
    tello.takeoff()
    time.sleep(3)

    # print("📈 Initial ascent...")
    tello.send_rc_control(0, 0, 20, 0)
    time.sleep(1)
    tello.send_rc_control(0, 0, 0, 0)

    # print("✅ Entering main loop")

    while True:
        reader = tello.get_frame_read()
        frame = reader.frame

        if frame is None or frame.size == 0:
            # print("⚠️ Unable to retrieve video frame. Check if streamon is active.")
            continue

        # --- Face Tracking Logic ---
        face_info = detect_face(frame)
        if face_info:
            diff_x, diff_y, width = face_info
            controlX = diff_x * kpX
            controlY = diff_y * kpY
            controlPitch = (TARGET_WIDTH - width) * kpPitch
            tello.send_rc_control(0, int(controlPitch), int(-controlY), int(controlX))
        else:
            # Hover if no face is detected
            tello.send_rc_control(0, 0, 0, 0)

        # --- Hand Detection (No trigger zone) ---
        frame, _, lmList = hand_detector.detect_hands(frame)

        if hand_detector.is_flip_gesture(lmList):
            if time.time() - last_flip_time > FLIP_COOLDOWN:
                print("🌀 Flip gesture detected. Executing BACK flip!")
                tello.flip("b")
                last_flip_time = time.time()

        # Display the result window
        cv.imshow("Drone Face + Hand Control", frame)

        # Exit condition
        if cv.waitKey(1) & 0xFF == ord('q'):
            # print("🧯 User requested exit.")
            break

except Exception as e:
    print(f"❌ Exception occurred: {e}")

finally:
    # --- Shutdown sequence ---
    # print("🔻 Initiating landing...")
    if tello.is_flying:
        tello.land()
    tello.streamoff()
    cv.destroyAllWindows()
    print("✅ System shut down safely.")