import cv2 as cv

# Load the Haar cascade classifier for face detection
face_cascade = cv.CascadeClassifier('haarcascade_frontalface_default.xml')

# --- Color Definitions (BGR format) ---
GREEN = (0, 238, 0)
BLUE = (255, 0, 0)
RED = (0, 0, 255)

def draw_center_crosshair(frame, center):
    """ Draws a crosshair in the center of the frame for alignment purposes """
    circle_rad = 25
    line_length = 15
    cv.circle(frame, center, circle_rad, GREEN, 1)
    cv.line(frame, (center[0], center[1] - line_length), (center[0], center[1] + line_length), GREEN, 1)
    cv.line(frame, (center[0] - line_length, center[1]), (center[0] + line_length, center[1]), GREEN, 1)

def detect_face(frame):
    """
    Detects faces in a given frame.

    - If faces are detected, it tracks the one with the largest area.
    - Draws a central crosshair, the face bounding box, and a connection line on the frame.
    - Returns (diff_x, diff_y, width) or None if no face is detected.
    """
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # detectMultiScale(image, scaleFactor, minNeighbors)
    # scaleFactor: Specifies how much the image size is reduced at each image scale. 1.2 means 20%.
    # minNeighbors: Specifies how many neighbors each candidate rectangle should have to retain it.
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    frame_height, frame_width, _ = frame.shape
    center = (frame_width // 2, frame_height // 2)

    # Draw the central crosshair on the frame
    draw_center_crosshair(frame, center)

    # If no faces are detected
    if len(faces) == 0:
        return None

    # --- If faces are detected, find the one with the largest area ---
    # Sort detected faces by area (w*h) in descending order
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    
    # Select the largest face
    x, y, w, h = faces[0]

    # Calculate the center point of the face
    center_face = (x + w // 2, y + h // 2)

    # Calculate the offset between the face center and the frame center
    diff_x = center_face[0] - center[0]
    diff_y = center_face[1] - center[1]

    # --- Draw information on the frame for debugging ---
    # Draw the face bounding box
    cv.rectangle(frame, (x, y), (x + w, y + h), BLUE, 2)
    # Draw a line from the frame center to the face center
    cv.line(frame, center, center_face, RED, 2)

    # Return the offsets and the face width
    return diff_x, diff_y, w

# --- Code below is for testing this file independently ---
def main():
    cap = cv.VideoCapture(0)
    while True:
        ret, frame_now = cap.read()
        if not ret:
            break

        face_info = detect_face(frame_now)

        if face_info is not None:
            _, _, width = face_info
            print(f"Face detected, width: {width}")
        else:
            print("No face detected.")

        cv.imshow('Face Detection Test', frame_now)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()