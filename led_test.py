import RPi.GPIO as GPIO
import time

# Set up GPIO mode to use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# Set up GPIO18 as an output pin
GPIO.setup(18, GPIO.OUT)

# Blink the LED 5 times
try:
    while True:
        GPIO.output(18, GPIO.HIGH)  # Turn on LED
        print("LED is ON")
        time.sleep(1)  # Wait for 1 second

        GPIO.output(18, GPIO.LOW)  # Turn off LED
        print("LED is OFF")
        time.sleep(1)  # Wait for 1 second

except KeyboardInterrupt:
    print("Program interrupted by user")

finally:
    GPIO.cleanup()  # Clean up the GPIO settings (reset GPIO pins)
