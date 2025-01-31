from flask import Flask, jsonify
from max30102 import max30102, hrcalc
from smbus2 import SMBus
from mlx90614 import MLX90614
from flask_cors import CORS
import time
import requests
import time
from AudioPlayer import AudioRecorder
import speech_recognition as sr
import logging
import serial

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/pieapi/*": {"origins": "*"}})
recorder = AudioRecorder()

"""
    GPIO2 (SDA), GPIO3 (SCL)
    common for both sensors
"""

def get_average_heart_rate(m, num_readings=1):
    """
    Calculate the average heart rate based on multiple readings,
    skipping the first two readings for accuracy.
    """
    heart_rates = []
    sp02_all = []
    for i in range(num_readings + 2):  # +2 to account for skipped readings
        red, ir = m.read_sequential()
        hr, hr_valid, spo2, spo2_valid = hrcalc.calc_hr_and_spo2(ir, red)
        
        if i >= 2 and hr_valid:  # Skip the first two readings
            print(f"heart rate: {hr} ---- spo2: {spo2}")
            heart_rates.append(hr)
            sp02_all.append(spo2)
        time.sleep(0.5)

    if heart_rates:
        avg_hr = sum(heart_rates) / len(heart_rates)
        avg_spo2 = sum(sp02_all) / len(sp02_all)
        return round(avg_hr, 2), round(avg_spo2, 2)
    else:
        return None, None

def measure_temperature():
    """
    Measure the user's body and ambient temperature using the MLX90614 sensor.
    """
    print("\nMeasuring temperature...")
    time.sleep(1)  # Delay for sensor stability

    bus = SMBus(1)  # GPIO2 (SDA), GPIO3 (SCL)
    sensor = MLX90614(bus, address=0x5A)



    body_temp_c = sensor.get_obj_temp()  # Object temperature
    body_temp_f = (body_temp_c * 1.8) + 32
    ambient_temp_c = sensor.get_amb_temp()

    print(f"\nBody Temperature: {round(body_temp_f, 2)} °F")
    print(f"Ambient Temperature: {round(ambient_temp_c-6, 2)} °C\n")

    bus.close()
    return {
        "body_temperature_f": round(body_temp_f, 2),
        "ambient_temperature_c": round(ambient_temp_c - 6, 2)
    }


# API endpoint for measuring heart rate
@app.route('/pieapi/heart_rate', methods=['GET'])
def heart_rate():
    try:
        m = max30102.MAX30102()
        avg_hr, avg_spo2 = get_average_heart_rate(m)
        if avg_hr:
            return jsonify({
                "success": True,
                "average_heart_rate_bpm": avg_hr,
                "average_spo2": avg_spo2
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Unable to detect a valid heart rate. Please try again."
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# API endpoint for measuring temperature
@app.route('/pieapi/temperature', methods=['GET'])
def temperature():
    try:
        temp_data = measure_temperature()
        return jsonify({
            "success": True,
            **temp_data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        

@app.route("/pieapi/takecoin", methods=['GET'])
def takecoin():
    print("take coin called")
#    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
#   arduino.write("collect".encode())
    with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as arduino:
        arduino.write(b"collect\n") 
    
    return jsonify({"success": True, "message": "Coin stored"})


@app.route("/pieapi/rejectcoin" ,methods=['GET'])
def rejectcoin():
    #arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    #arduino.write("return".encode())
    with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as arduino:
        arduino.write(b"return\n")

    return jsonify({"success":True, "message":"Coin returned"})


@app.route('/pieapi/start', methods=['GET'])
def start_recording():
    if recorder.st == 1:
        return jsonify({"message": "Recording is already in progress."}), 400
    recorder.start_record()
    return jsonify({"status": "recording started"}), 200


@app.route('/pieapi/stop', methods=['GET'])
def stop_recording():
    if recorder.st == 0:
        return jsonify({"message": "No recording is in progress."}), 400
    file_path = "output.wav"
    recorder.stop_record(file_path)
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as audio:
        audio_data = recognizer.record(audio)
        text = recognizer.recognize_google(audio_data)
    print(text)
    
    return jsonify({"status": text}), 200


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8000, debug=True)
    finally:
        pass
