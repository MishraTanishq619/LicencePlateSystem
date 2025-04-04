from picamera2 import Picamera2
import cv2

# Initialize the camera
picam2 = Picamera2()
picam2.start_preview()
picam2.start()

while True:
    # Capture a frame
    frame = picam2.capture_array()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the frame
    cv2.imshow('Camera', gray)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the camera
picam2.stop()
picam2.stop_preview()
cv2.destroyAllWindows()
