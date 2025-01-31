import serial
import time

# Set up the serial connection (adjust the port as needed)
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Allow some time for the connection to establish

# Function to send a message to Arduino
def send_message(message):
    arduino.write(message.encode())  # Send the message
    print(f"Sent: {message}")


send_message("LED_OFF")
