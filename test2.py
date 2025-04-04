from picamera2 import Picamera2
import cv2
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Load Haar Cascade model
plate_cascade = cv2.CascadeClassifier('/home/abhishek/project/haarcascade_russian_plate_number.xml')

# Check if the Haar Cascade file is loaded correctly
if plate_cascade.empty():
    print("Error: Could not load Haar Cascade file.")
    exit()

# Initialize the camera
picam2 = Picamera2()
picam2.start_preview()
picam2.start()

while True:
    # Capture a frame
    frame = picam2.capture_array()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect number plates
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in plates:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        plate = frame[y:y+h, x:x+w]
        # Save the detected plate
        cv2.imwrite('plate.png', plate)
        # Preprocess the plate image
        gray_plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
        _, binary_plate = cv2.threshold(gray_plate, 128, 255, cv2.THRESH_BINARY)
        # Extract text
        text = pytesseract.image_to_string(binary_plate, config='--psm 8')
        print("Extracted Text:", text)

    # Display the frame
    cv2.imshow('Number Plate Detection', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the camera
picam2.stop()
picam2.stop_preview()
cv2.destroyAllWindows()
