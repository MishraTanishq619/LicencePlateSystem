import cv2
from PIL import Image
import pytesseract
import time

# Servo control
import RPi.GPIO as GPIO

def servoFunc():
    GPIO.setmode(GPIO.BCM)
    servo_pin = 18
    GPIO.setup(servo_pin, GPIO.OUT)
    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(0)

    def set_servo_angle(angle):
        duty_cycle = (angle / 18) + 2
        pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(1)
        pwm.ChangeDutyCycle(0)

    set_servo_angle(90)
    time.sleep(0.5)
    set_servo_angle(0)
    time.sleep(0.5)

    pwm.stop()
    GPIO.cleanup()


# Text matching
from fuzzywuzzy import fuzz
def match_text_with_list(extracted_text, word_list, threshold=70):
    for word in word_list:
        score = fuzz.ratio(extracted_text, word)
        print(f"Comparing '{extracted_text}' with '{word}': {score}% match")  # Debugging line
        if score >= threshold:
            return True
    return False


# Plate cascade
plate_cascade = cv2.CascadeClassifier('haarcascades_indian_plate_number.xml')

# Initialize camera
cap = cv2.VideoCapture(0)

# Check if camera is opened
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Log script start
with open('log.txt', 'a') as f:
    f.write('Script has started!\n')

while True:
    if not cap.isOpened():
        print("Error: Camera not detected. Please check the connection.")
        cap.release()
        break

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame. Reattempting...")
        cap.release()  # Release the current capture object
        time.sleep(1)  # Sleep for a while before retrying
        cap = cv2.VideoCapture(0)  # Reinitialize the camera capture
        continue  # Skip the rest of the loop and try reading the frame again

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in plates:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        plate = frame[y:y + h, x:x + w]

        gray_plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
        gray_plate = cv2.GaussianBlur(gray_plate, (5, 5), 0)
        _, binary_plate = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        plate_resized = cv2.resize(binary_plate, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Extract text
        text = pytesseract.image_to_string(plate_resized, config='--psm 8 --oem 3')
        text = text.strip()
        print("Extracted Text:", text)

        # Match text
        isMatch = match_text_with_list(text, ["KL07AH9981"])
        print("isMatch : ", isMatch)
        #if isMatch:
        servoFunc()

    # Display the frame
    cv2.imshow('Indian Number Plate Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1)

# Release resources when the script ends
cap.release()
cv2.destroyAllWindows()
