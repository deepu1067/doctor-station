from gpiozero import Button
from signal import pause
import requests
import time
import serial
from roboflow import Roboflow

ROBOFLOW_API = "API KEY"
YELLOW_START = 26
PROCEED_BLACK = 19
MIC_BROWN = 13
RESET_RED = 6

start_button = Button(YELLOW_START, pull_up=True)
mic_button = Button(MIC_BROWN, pull_up=True)
proceed_button = Button(PROCEED_BLACK, pull_up=True)
reset_button = Button(RESET_RED, pull_up=True)

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)
esp32_url = "http://10.15.14.127/capture"
BASE_API = "http://10.10.201.213:5000"

def start():
    try:
        res = requests.get(f"{BASE_API}/checking") #turning the chekcing status on
        print("coin checking")

        response = requests.get(esp32_url)
        if response.status_code == 200:
            with open("capture.jpg", "wb") as f:
                f.write(response.content)
            print("Image saved as capture.jpg")

            # Initialize Roboflow
            rf = Roboflow(api_key=ROBOFLOW_API)
            project = rf.workspace().project("coin-iajma")
            model = project.version("1").model

            # Predict using the image
            prediction = model.predict("capture.jpg").json()
            print("Prediction:", prediction)

            # Access the top prediction class
            top_prediction = prediction['predictions'][0]['top']
            print("Top Prediction Class:", top_prediction)

            try:
                if top_prediction == "five":
                    print("Correct coin")
                    requests.get(f"{BASE_API}/valid-coins")
                    requests.get(f"{BASE_API}/start")
                    arduino.write("collect".encode())
                else:
                    print("Performing right sweep (return coin).")
                    arduino.write("return".encode())
            except Exception as servo_error:
                print(f"Error controlling servo: {servo_error}")
        else:
            print(f"Failed to capture image. Status code: {response.status_code}")

        res = requests.get(f"{BASE_API}/checking") #turning the chekcing status off

    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from ESP32-CAM: {e}")

def demo_checking():
    print("start button pressed")
    res = requests.get(f"{BASE_API}/checking") #turning the chekcing status on
    print(res)
    
    requests.get(f"{BASE_API}/valid-coins")
    requests.get(f"{BASE_API}/start")
    
    requests.get(f"{BASE_API}/checking") #turning the chekcing status off

def reset_btn():
    print("pressed reset")
#    requests.get("http://192.168.0.79:8000/pieapi/rejectcoin")
    arduino.write("return".encode())
    requests.get(f"{BASE_API}/reset")
    
    
    
def mic():
    print("Mic button pressed")
    requests.get(f"{BASE_API}/mic")
    
def proceed():
    print("Proceed button pressed")
    requests.get(f"{BASE_API}/proceed")
    
def pr():
    try:
        print("Button pressed. Calling API...")
    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")

def res():
    pass


start_button.when_pressed = start
start_button.when_released = res

reset_button.when_pressed = reset_btn
reset_button.when_released = res

mic_button.when_pressed = mic
mic_button.when_released = res

proceed_button.when_pressed = proceed
proceed_button.when_released = res

print("Waiting for button press...")
pause()
