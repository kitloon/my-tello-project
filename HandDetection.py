# HandDetection.py
import cv2
import mediapipe as mp

# Initialize Mediapipe hand detection module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Create Hand Detection class
class HandDetector:
    def __init__(self, maxHands=1, detectionCon=0.7, trackCon=0.5):
        self.hands = mp_hands.Hands(
            max_num_hands=maxHands,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon
        )

    def detect_hands(self, frame):
        """Detect hand landmarks and return the hand bounding box and landmark coordinates"""
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)
        hand_bbox = None
        lmList = []

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                # Calculate bounding box
                xList = [lm.x for lm in handLms.landmark]
                yList = [lm.y for lm in handLms.landmark]
                h, w, _ = frame.shape
                xMin, xMax = int(min(xList) * w), int(max(xList) * w)
                yMin, yMax = int(min(yList) * h), int(max(yList) * h)
                hand_bbox = (xMin, yMin, xMax - xMin, yMax - yMin)

                # Get landmark coordinates
                for lm in handLms.landmark:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append((cx, cy))

                # Draw hand skeleton/landmarks
                mp_drawing.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
                break  # Process only the first hand detected

        return frame, hand_bbox, lmList

    def is_in_zone(self, bbox, zone_rect):
        """Determine if the hand center is within the specified cyan trigger zone"""
        if bbox is None:
            return False

        x, y, w, h = bbox
        zx, zy, zw, zh = zone_rect
        hand_cx = x + w // 2
        hand_cy = y + h // 2

        return zx <= hand_cx <= zx + zw and zy <= hand_cy <= zy + zh

    def is_flip_gesture(self, lmList):
        """
        Identify if the hand is in a 'flip' gesture.
        - thumb(4), index(8), and pinky(20) are stretched out
        - middle(12) and ring(16) are folded
        """
        if len(lmList) < 21:
            return False

        def is_finger_up(tip_id, pip_id):
            # Returns True if the tip is above the PIP joint (lower y-coordinate value)
            return lmList[tip_id][1] < lmList[pip_id][1]

        thumb = is_finger_up(4, 3)
        index = is_finger_up(8, 6)
        pinky = is_finger_up(20, 18)
        
        # Checking if middle and ring fingers are folded (tip below joint)
        middle = lmList[12][1] > lmList[10][1]
        ring = lmList[16][1] > lmList[14][1]

        return thumb and index and pinky and middle and ring