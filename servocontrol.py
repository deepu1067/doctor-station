# from roboflow import Roboflow
# from time import sleep
# import json
# import numpy as np
# import requests
# import cv2

# rf = Roboflow(api_key="qLojUGTXF602vpyJrGT3")
# project = rf.workspace().project("coin-iajma")
# model = project.version("1").model

# # Predict using the image
# prediction = model.predict("capture.jpg").json()
# print("Prediction:", prediction)



import RPi.GPIO as GPIO
import time

# GPIO pin connected to the servo signal pin
SERVO_PIN = 18

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Set the PWM frequency to 50Hz (typical for servo motors)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(7.5)  # 7.5% duty cycle sets the servo to 90 degrees

def right_sweep():
    # Move from 90° to 135° (Right sweep) //return coin
    for angle in range(90, 136, 1):
        set_angle(angle)
        time.sleep(0.015)
    
    # Move back from 135° to 90° (Return sweep)
    for angle in range(135, 89, -1):
        set_angle(angle)
        time.sleep(0.015)

def left_sweep():
    # Move from 90° to 45° (Left sweep) ///store coin
    for angle in range(90, 44, -1):
        set_angle(angle)
        time.sleep(0.015)

    # Move back from 45° to 90° (Return sweep)
    for angle in range(45, 91, 1):
        set_angle(angle)
        time.sleep(0.015)


def set_angle(angle):
    """
    Convert the angle (0-180 degrees) to a duty cycle (2-12% range)
    and send the signal to the servo.
    """
    duty_cycle = 2 + (angle / 18)  # Map angle to duty cycle
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.015)  # Allow the servo to reach the position



# if __name__ == "__main__":
#     try:
#         while True:
#             time.sleep(3)

#             right_sweep()

#             # Short delay before moving to the left
#             time.sleep(3)

#             left_sweep()

#     except KeyboardInterrupt:
#         print("Program stopped by user.")
#     finally:
#         pwm.stop()  # Stop the PWM signal
#         GPIO.cleanup()  # Clean up GPIO settings
