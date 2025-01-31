from max30102 import max30102, hrcalc
from smbus2 import SMBus
from mlx90614 import MLX90614
import time

"""
    GPIO2 (SDA), GPIO3 (SCL)
    common for both sensor
"""
def get_average_heart_rate(m, num_readings=5):
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
        return None

def measure_heart_rate():
    """
    Measure the user's heart rate using the MAX30102 sensor.
    """
    print("\nMeasuring heart rate... Please place your finger on the sensor.")
    time.sleep(2)

    m = max30102.MAX30102()
    avg_hr, avg_spo2 = get_average_heart_rate(m)

    if avg_hr:
        print(f"\nAverage Heart Rate: {avg_hr} BPM and Average SPO2: {avg_spo2}\n")
    else:
        print("\nUnable to detect a valid heart rate. Please try again.\n")

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

# def main_menu():
#     """
#     Display the main menu for user interaction.
#     """
#     while True:
#         print("Welcome to the Health Monitor!")
#         print("1. Measure Heart Rate")
#         print("2. Measure Body Temperature")
#         print("3. Exit")
#         choice = input("Please enter your choice (1/2/3): ")

#         if choice == "1":
#             measure_heart_rate()
#         elif choice == "2":
#             measure_temperature()
#         elif choice == "3":
#             print("\nThank you for using the Health Monitor. Goodbye!")
#             break
#         else:
#             print("\nInvalid choice. Please try again.\n")

if __name__ == "__main__":
    main_menu()
