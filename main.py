import cv2 as cv
import numpy as np
import time  # [Important Fix] Imported time module
from DroneController import Tello
from FaceDetection import detect_face

# --- Control Parameters (Adjustable based on testing) ---
# Proportional gains for rotation (yaw) and vertical movement (up/down)
# Previous test values for reference:
# 0.3 0.4 0.4
# 0.2 0.25 0.25

kpX = 0.4
kpY = 0.4
# Proportional gain for forward/backward (pitch) control
kpPitch = 0.45

# Target face width (pixels), used to maintain distance from the face
TARGET_WIDTH = 175

# Create Tello object
tello = Tello()

# --- Drone Initialization ---
# Using try...finally structure to ensure a safe landing regardless of errors
try:
    # Enter SDK mode and connect
    tello.connect()

    # [!!! --- Important Fix --- !!!]
    # Wait briefly before querying status to ensure drone state info 
    # has been received by the background thread.
    print("Waiting for drone state information...")
    time.sleep(1.0)
    # [!!! --- End of Fix --- !!!]

    print(f"The remaining battery: {tello.get_battery()} %")

    # Enable video stream
    tello.streamon()
    
    # Take off
    tello.takeoff()
    
    # Wait for flight to stabilize and ensure IMU is ready
    time.sleep(3)
    
    # Use a safer method to ascend slowly
    tello.send_rc_control(0, 0, 20, 0)
    time.sleep(1)
    
    # Stop movement
    tello.send_rc_control(0, 0, 0, 0)
    
    # Wait a moment for stabilization
    cv.waitKey(1000)

    # --- Main Control Loop ---
    while True:
        # 1. Retrieve video frame from the drone
        frame = tello.get_frame_read().frame

        # 2. Call face detection function
        face_info = detect_face(frame)

        # 3. Control logic based on detection results
        # If a face is detected (face_info is not None)
        if face_info is not None:
            diff_x, diff_y, width = face_info

            # --- Calculate control values for each channel ---
            # Rotation Control (Yaw)
            controlX = np.clip(diff_x * kpX, -70, 70)
            
            # Vertical movement control (Up/Down)
            controlY = np.clip(diff_y * kpY, -70, 70)
            
            # Forward / Backward control (Pitch)
            error_pitch = TARGET_WIDTH - width
            controlPitch = np.clip((TARGET_WIDTH - width) * kpPitch, -70, 70)

            # --- Send RC commands to the drone ---
            # Parameter order: (Roll/Left-Right, Pitch/Forward-Back, Throttle/Up-Down, Yaw/Rotate)
            # Note: The vertical control value (controlY) is inverted to match coordinate system
            tello.send_rc_control(0, int(controlPitch), int(-controlY), int(controlX))

        # If no face is detected
        else:
            # Send hover command/slow rotation to search
            tello.send_rc_control(0, 0, 0, 10)

        # 4. Display video frame in the window
        cv.imshow("Drone Face Tracking", frame)

        # 5. Check for exit signal
        if cv.waitKey(1) & 0xFF == ord('q'):
            break  # Exit loop

# Catch all possible exceptions, such as keyboard interrupts (Ctrl+C)
except Exception as e:
    print(f"An error occurred: {e}")

# Note: You may want to add a finally block here to ensure tello.land() 
# and tello.streamoff() are called when the program exits.