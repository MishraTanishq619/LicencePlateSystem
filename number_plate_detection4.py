import cv2
import time
import os
import pytesseract
from picamera2 import Picamera2
import numpy as np
import RPi.GPIO as GPIO
from fuzzywuzzy import fuzz

# Function to initialize and capture from Picamera2
def get_video_device():
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration())
    picam2.start()
    return picam2

# Function to release and reinitialize the camera if needed
def release_and_reinitialize_camera(picam2):
    picam2.stop()
    time.sleep(1)  # Wait for a brief moment before reinitializing
    return get_video_device()

# Servo control (if needed in your application)
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
    time.sleep(3)
    set_servo_angle(0)
    time.sleep(0.5)

    pwm.stop()
    GPIO.cleanup()

# Plate detection and text matching
def match_text_with_list(extracted_text, word_list, threshold=70):
    for word in word_list:
        score = fuzz.ratio(extracted_text, word)
        print(f"Comparing '{extracted_text}' with '{word}': {score}% match")  # Debugging line
        if score >= threshold:
            return True
    return False

# Initialize camera using Picamera2
picam2 = get_video_device()

# Plate cascade for number plate detection
plate_cascade = cv2.CascadeClassifier('haarcascades_indian_plate_number.xml')

# Log script start
with open('log.txt', 'a') as f:
    f.write('Script has started!\n')

while True:
    try:
        # Capture image using Picamera2
        frame = picam2.capture_array()

        if frame is None:
            print("Error: Could not read frame. Reattempting...")
            picam2 = release_and_reinitialize_camera(picam2)  # Reinitialize the camera if frame cannot be read
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in plates:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            plate = frame[y:y + h, x:x + w]

            gray_plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
            gray_plate = cv2.GaussianBlur(gray_plate, (5, 5), 0)
            _, binary_plate = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            plate_resized = cv2.resize(binary_plate, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            # Extract text from the plate
            text = pytesseract.image_to_string(plate_resized, config='--psm 8 --oem 3')
            text = text.strip()
            print("Extracted Text:", text)

            # Match text with predefined list
            isMatch = match_text_with_list(text, ["KL07AH9981","22BH6517A"])
            print("isMatch : ", isMatch)
            if isMatch:
                servoFunc()

        # Display the frame
        cv2.imshow('Indian Number Plate Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(1)

    except Exception as e:
        print(f"Error occurred: {e}")
        picam2 = release_and_reinitialize_camera(picam2)  # Reinitialize the camera if an error occurs
        continue

# Release resources when the script ends
picam2.stop()
cv2.destroyAllWindows()
