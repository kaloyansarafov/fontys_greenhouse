import datetime
import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    sensor_data = {}
    data_folder = 'data'
    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            sensor_id = filename.split('.')[0]
            file_path = os.path.join(data_folder, filename)
            with open(file_path, 'r') as json_file:
                try:
                    if os.path.getsize(file_path) > 0:
                        data = json.load(json_file)
                        data.sort(key=lambda x: x['timestamp'], reverse=True)
                        sensor_data[sensor_id] = data
                    else:
                        sensor_data[sensor_id] = []
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from {file_path}: {e}")
                    sensor_data[sensor_id] = []

    settings_folder = 'settings'
    settings = {}
    for filename in os.listdir(settings_folder):
        if filename.endswith('.json'):
            sensor_id = filename.split('.')[0]
            file_path = os.path.join(settings_folder, filename)
            with open(file_path, 'r') as json_file:
                try:
                    if os.path.getsize(file_path) > 0:
                        data = json.load(json_file)
                        settings[sensor_id] = data[0]
                    else:
                        settings[sensor_id] = {}
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from {file_path}: {e}")
                    settings[sensor_id] = {}

    return render_template("index.html", sensor_data=sensor_data, settings=settings)


@app.route("/sensor_data", methods=["POST"])
def sensor_data():
    data = request.json
    sensor_id = data.get("sensor_id")
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    light = data.get("light")

    timestamp = datetime.datetime.now()
    data.update({"timestamp": timestamp.isoformat()})

    os.makedirs('data', exist_ok=True)

    file_path = os.path.join('data', f"{sensor_id}.json")

    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            try:
                if os.path.getsize(file_path) > 0:
                    existing_data = json.load(json_file)
                else:
                    existing_data = []
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {file_path}: {e}")
                existing_data = []
    else:
        existing_data = []

    existing_data.append(data)

    with open(file_path, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

    return f"Received data from sensor {sensor_id} at {timestamp}: Temperature={temperature}, Humidity={humidity}, Light={light}"

@app.route("/sensor_data/<sensor_id>", methods=["GET"])
def get_sensor_data(sensor_id):
    file_path = os.path.join('data', f"{sensor_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
                data.sort(key=lambda x: x['timestamp'], reverse=True)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    settings_folder = 'settings'
    settings = {}
    for filename in os.listdir(settings_folder):
        if filename.endswith('.json'):
            settings_sensor_id = filename.split('.')[0]
            file_path = os.path.join(settings_folder, filename)
            with open(file_path, 'r') as json_file:
                try:
                    if os.path.getsize(file_path) > 0:
                        settings_data = json.load(json_file)
                        settings[settings_sensor_id] = settings_data[0]
                    else:
                        settings[settings_sensor_id] = {}
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from {file_path}: {e}")
                    settings[sensor_id] = {}

    return render_template("sensor_data.html", sensor_id=sensor_id, data=data, settings=settings)

@app.route("/settings", methods=["GET", "POST"])
@app.route("/settings/<sensor_id>", methods=["GET", "POST"])
def settings(sensor_id=None):
    settings_folder = 'settings'
    settings_file = os.path.join(settings_folder, f"{sensor_id}.json" if sensor_id else "global.json")

    if request.method == "POST":
        new_settings = request.form.to_dict()
        with open(settings_file, 'w') as json_file:
            json.dump([new_settings], json_file, indent=4)
        return redirect(url_for('settings', sensor_id=sensor_id))

    if os.path.exists(settings_file):
        with open(settings_file, 'r') as json_file:
            settings_data = json.load(json_file)[0]
    else:
        settings_data = {}

    return render_template("settings.html", sensor_id=sensor_id, settings=settings_data)


if __name__ == '__main__':
    app.run(debug=True)