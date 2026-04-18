# app.py

import cv2 as cv
import numpy as np
import time
import threading
from flask import Flask, render_template, Response, jsonify

# Import from your project files
from DroneController import Tello
from FaceDetection import detect_face

# --- Control Parameters ---
KP_X = 0.4
KP_Y = 0.4
KP_PITCH = 0.45
TARGET_WIDTH = 175
FACE_LOST_YAW_VELOCITY = 15 # If face is lost, drone rotates slowly to search

# --- Global Variables and Locks ---
# Encapsulating drone state and operations in a class for better clarity and safety
class DroneManager:
    def __init__(self):
        self.tello = Tello()
        self.is_connected = False
        self.is_tracking = False
        self.stop_event = threading.Event()
        self.video_thread = None
        self.last_frame = None
        self.frame_lock = threading.Lock()

    def connect(self):
        if not self.is_connected:
            try:
                self.tello.connect()
                self.is_connected = True
                print("Drone connected.")
                # Start video stream and processing loop
                self.stop_event.clear()
                self.video_thread = threading.Thread(target=self._video_loop, daemon=True)
                self.video_thread.start()
                return True
            except Exception as e:
                print(f"Connection failed: {e}")
                return False
        return True

    def disconnect(self):
        if self.is_connected:
            self.stop_event.set() # Send stop signal
            if self.tello.is_flying:
                print("Landing before disconnect...")
                self.tello.land()
            self.tello.streamoff()
            self.is_connected = False
            # self.tello.end() # Use if your Tello library has an end() method
            print("Drone disconnected.")

    def get_status(self):
        if not self.is_connected:
            return {"battery": "N/A", "is_flying": False, "is_tracking": self.is_tracking}
        return {
            "battery": self.tello.get_battery(),
            "is_flying": self.tello.is_flying,
            "is_tracking": self.is_tracking
        }

    def takeoff(self):
        if self.is_connected and not self.tello.is_flying:
            self.tello.takeoff()
            time.sleep(2) # Wait for stabilization
            # Ascend slightly
            self.tello.send_rc_control(0, 0, 20, 0)
            time.sleep(1.5)
            self.tello.send_rc_control(0, 0, 0, 0)
            return True
        return False
        
    def land(self):
        if self.is_connected and self.tello.is_flying:
            self.is_tracking = False # Stop tracking before landing
            self.tello.land()
            return True
        return False

    def start_tracking(self):
        if self.is_connected and self.tello.is_flying:
            self.is_tracking = True
            return True
        return False

    def stop_tracking(self):
        self.is_tracking = False
        # Hover
        if self.is_connected:
            self.tello.send_rc_control(0, 0, 0, 0)
        return True

    def get_video_frame(self):
        with self.frame_lock:
            if self.last_frame is not None:
                ret, jpeg = cv.imencode('.jpg', self.last_frame)
                if ret:
                    return jpeg.tobytes()
        return None

    def _video_loop(self):
        """Background thread function to handle video stream and control logic"""
        self.tello.streamon()
        frame_read = self.tello.get_frame_read()
        
        while not self.stop_event.is_set():
            frame = frame_read.frame
            
            # If tracking is active, execute tracking logic
            if self.is_tracking:
                # detect_face should return the processed frame and coordinates info
                face_info = detect_face(frame) 
                
                if face_info is not None:
                    # We assume detect_face returns (diff_x, diff_y, width)
                    # If not, modify FaceDetection.py or draw the bounding box here
                    
                    # --- Calculate Control Signals ---
                    diff_x, diff_y, width = face_info
                    controlX = int(np.clip(diff_x * KP_X, -70, 70))
                    controlY = int(np.clip(diff_y * KP_Y, -70, 70))
                    error_pitch = TARGET_WIDTH - width
                    controlPitch = int(np.clip(error_pitch * KP_PITCH, -70, 70))
                    
                    self.tello.send_rc_control(0, controlPitch, -controlY, controlX)
                else:
                    # Face lost: hover and rotate slowly to search
                    self.tello.send_rc_control(0, 0, 0, FACE_LOST_YAW_VELOCITY)
            
            # Update frame for Web stream regardless of tracking status
            with self.frame_lock:
                self.last_frame = frame.copy()

            time.sleep(1/30) # Limit loop frequency

        print("Video loop stopped.")


# --- Flask Application ---
app = Flask(__name__)
drone_manager = DroneManager()

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

def gen_video():
    """Video stream generator function"""
    while True:
        frame_bytes = drone_manager.get_video_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(1/30) # Wait briefly

@app.route('/video_feed')
def video_feed():
    """Video stream route returning a multipart response"""
    return Response(gen_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- API Endpoints ---
@app.route('/api/drone/<command>', methods=['POST'])
def drone_command(command):
    success = False
    if command == 'connect':
        success = drone_manager.connect()
    elif command == 'disconnect':
        drone_manager.disconnect()
        success = True
    elif command == 'takeoff':
        success = drone_manager.takeoff()
    elif command == 'land':
        success = drone_manager.land()
    elif command == 'start_tracking':
        success = drone_manager.start_tracking()
    elif command == 'stop_tracking':
        success = drone_manager.stop_tracking()
    
    return jsonify({"success": success, "command": command})

@app.route('/api/drone/status')
def drone_status():
    return jsonify(drone_manager.get_status())

# Ensure safe landing and cleanup when shutting down
@app.route('/shutdown', methods=['POST'])
def shutdown():
    drone_manager.disconnect()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)