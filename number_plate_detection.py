import cv2
from PIL import Image
import pytesseract

# Load Haar Cascade model
plate_cascade = cv2.CascadeClassifier('haarcascades_indian_plate_number.xml')

# Initialize the camera
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

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
    cv2.imshow('Indian Number Plate Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()
