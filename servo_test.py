import RPi.GPIO as GPIO
import time

# Set up the GPIO mode and pin
GPIO.setmode(GPIO.BCM)  # GPIO.BCM or GPIO.BOARD, depending on your setup
servo_pin = 18  # GPIO pin where the servo is connected (GPIO18 in this case)

# Set the GPIO pin as an output
GPIO.setup(servo_pin, GPIO.OUT)

# Set up PWM on the pin
pwm = GPIO.PWM(servo_pin, 50)  # PWM at 50Hz (standard frequency for servos)
pwm.start(0)  # Initialize the PWM with 0% duty cycle

# Function to move servo to a given angle
def set_servo_angle(angle):
    duty_cycle = (angle / 18) + 2  # Convert angle to duty cycle (2-12)
    pwm.ChangeDutyCycle(duty_cycle)  # Set the servo position
    time.sleep(1)  # Give time for the servo to reach the position
    pwm.ChangeDutyCycle(0)  # Stop PWM to avoid jittering

# Example: Move the servo to different angles
try:
    while True:
        print("Loop starts")
        set_servo_angle(0)  # Move to 0 degrees
        time.sleep(0.1)
        set_servo_angle(90)  # Move to 90 degrees
        time.sleep(0.1)
        # set_servo_angle(180)  # Move to 180 degrees
        # time.sleep(0.1)

except KeyboardInterrupt:
    print("Program interrupted")

# Clean up GPIO settings
pwm.stop()
GPIO.cleanup()
