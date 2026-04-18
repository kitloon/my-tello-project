This project explores high-level autonomous control for the [DJI Tello Drone](https://store.dji.com/shop/tello-series). It streams live video from the drone to a laptop via UDP, processes the frames off-board using advanced computer vision techniques, and sends flight commands back to the drone in real-time.

## ✨ Key Features

*   👤 **Autonomous Face Tracking:** Utilizes OpenCV's Haar Cascade and a custom **PID controller** to constantly adjust the drone's Yaw, Pitch, and Altitude to keep the user's face centered at a fixed distance.
*   🖐️ **Hand Gesture Control:** Integrates Google's **Mediapipe** to detect hand landmarks. Showing a specific gesture (e.g., "Rock" / Spider-Man gesture: Thumb, Index, and Pinky extended) triggers the drone to perform a **Backflip**!
*   🌐 **Web-Based Dashboard:** A sleek **Flask** web interface that allows users to view the live video stream and control the drone (Connect, Takeoff, Land, Start/Stop Tracking) directly from a browser.
*   🛡️ **Thread-Safe Architecture:** Implements a robust `DroneManager` with threading locks to ensure smooth video streaming and zero-conflict command execution.

## 🛠️ Dependencies

Ensure you have Python 3.8+ installed. The main libraries used are:
*   `opencv-python` (Image processing and Face detection)
*   `mediapipe` (Hand landmark detection)
*   `numpy` (Matrix calculations for PID control)
*   `flask` (Web server for GUI)

## 🚀 Installation & Setup

**Clone the repository:**
```
git clone ...
cd your-repo-name
```

1. **Create a virtual environment (Recommended):**
```
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. **Install the required packages:**
```
pip install -r requirement.txt
```

4. **Connect to the Drone:**
Power on your DJI Tello and connect your laptop to the drone's Wi-Fi network (usually named TELLO-XXXXXX).

## 🎮 How to Use
This project offers three different ways to interact with the drone. Run one of the following commands based on what you want to test:

*Option 1: Web UI Dashboard (Recommended)*
Launch the Flask server to control the drone via a web browser.
```
python app.py
```
Open your browser and navigate to: http://localhost:5000


**Option 2: Face Tracking + Hand Gesture Control**
Run the standalone OpenCV window. The drone will track your face, and if you show the specific hand gesture, it will do a backflip (with a 5-second cooldown)
```
python handmain.py
```
(Press q to quit and land safely)


**Option 3: Pure Face Tracking**
The classic version. It will take off, find your face, and follow you around.
```
python main.py
```
(Press q to quit and land safely)

## 📂 Project Structure
app.py: Flask web server and API endpoints.

* handmain.py / main.py: Standalone execution scripts for OpenCV-based display.
* DroneController.py: The core wrapper class handling UDP sockets, video decoding, and drone state parsing.
* FaceDetection.py: Handles bounding box creation and deviation calculations using Haar Cascades.
* HandDetection.py: Mediapipe logic for hand landmarks and gesture identification.
* templates/index.html: The frontend layout for the Flask application.
* haarcascade_frontalface_default.xml: Pre-trained face detection model.

