import cv2
import time
import os
import pytesseract
from picamera2 import Picamera2
import numpy as np
import RPi.GPIO as GPIO
from fuzzywuzzy import fuzz
import smbus  # For I2C communication with LCD

# GPIO Pin Setup
GPIO.setmode(GPIO.BCM)
BUZZER_PIN = 23
RED_LED_PIN = 24
GREEN_LED_PIN = 25
TRIG_PIN = 27
ECHO_PIN = 22

GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Initialize I2C LCD
I2C_ADDR = 0x27  # Change this based on your LCD's I2C address
bus = smbus.SMBus(1)

def lcd_init():
    lcd_write(0x33)  # Initialize
    lcd_write(0x32)  # Set to 4-bit mode
    lcd_write(0x06)  # Cursor move direction
    lcd_write(0x0C)  # Turn cursor off
    lcd_write(0x28)  # 2 line display
    lcd_write(0x01)  # Clear display
    time.sleep(0.0005)

def lcd_write(cmd, mode=0):
    bus.write_byte_data(I2C_ADDR, mode, cmd)
    time.sleep(0.0005)

def lcd_display(message):
    lcd_write(0x01)  # Clear display
    for char in message:
        lcd_write(ord(char), 1)

# Ultrasonic Sensor Function
def get_distance():
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Distance in cm
    return distance

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

lcd_init()
lcd_display("System Ready")
GPIO.output(RED_LED_PIN, True)  # Red LED is ON initially
GPIO.output(GREEN_LED_PIN, False)

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
            isMatch = match_text_with_list(text, ["KL07AH9981", "22BH6517A"])
            print("isMatch : ", isMatch)

            # Inside the main loop where isMatch is checked
            if isMatch:
                lcd_display("License: True")
                GPIO.output(GREEN_LED_PIN, True)
                GPIO.output(RED_LED_PIN, False)
                servoFunc()

                # Start the loop to monitor distance after servoFunc()
                while True:
                    distance = get_distance()
                    print(f"Distance: {distance} cm")

                    if distance < 10:  # Threshold distance in cm
                        GPIO.output(RED_LED_PIN, True)
                        GPIO.output(GREEN_LED_PIN, False)
                        print("Object detected within range. Reverting LEDs.")
                    else:
                        GPIO.output(RED_LED_PIN, False)
                        GPIO.output(GREEN_LED_PIN, True)
                        print("Object out of range. Exiting loop.")
                        break  # Exit the loop when the object is out of range
            else:
                lcd_display("License: False")
                GPIO.output(GREEN_LED_PIN, False)
                GPIO.output(RED_LED_PIN, True)
                GPIO.output(BUZZER_PIN, True)
                time.sleep(0.5)
                GPIO.output(BUZZER_PIN, False)

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
GPIO.cleanup()