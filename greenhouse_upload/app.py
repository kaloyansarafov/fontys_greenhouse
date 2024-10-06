import json

import requests
import serial

ser = serial.Serial('COM6', 9600)

while True:
    data = ser.readline().strip().decode()
    print(data)

    deserialized_data = json.loads(data)

    requests.post("http://localhost:5000/sensor_data", json=deserialized_data)


