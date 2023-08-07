"""
This file contains the containers' basic operations.
Every container is relative to a specific country, and gets data from sensors located in that country.
It must perform the following operations:
* Receive messages sent on a socket
* Collect significant data from raw measurement (json file)
* Convert data to common units of measure (e.g. temperature -> Celsius)
* Send data (relative to every city) to the cloud
(This file should be loaded into every container)
"""

import datetime
import sys

from flask import Flask, request, json
import os


class Packet:
    def __init__(self, name, country, temp, feels_like, temp_min, temp_max, pressure, humidity, date_time):
        self.name = name
        self.country = country
        self.temp = temp
        self.feels_like = feels_like
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.pressure = pressure
        self.humidity = humidity
        self.date_time = date_time


app = Flask(__name__)


def decode_json(data):
    print("Decoding data...", flush=True)
    print(data["name"], flush=True)
    print(data["main"]["temp"], flush=True)



def pack_city_data(city):
    name = city.name
    country = city.code
    data = city.data

    kelvin_temp = data["main"]["temp"]
    kelvin_feels_like = data["main"]["feels_like"]
    kelvin_min = data["main"]["temp_min"]
    kelvin_max = data["main"]["temp_max"]
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    unix_timestamp = data["dt"]

    celsius_temp = kelvin_temp - 273.15
    celsius_feels_like = kelvin_feels_like - 273.15
    celsius_min = kelvin_min - 273.15
    celsius_max = kelvin_max - 273.15
    date_time = datetime.datetime.fromtimestamp(unix_timestamp)

    return Packet(name,
                  country,
                  celsius_temp,
                  celsius_feels_like,
                  celsius_min,
                  celsius_max,
                  pressure,
                  humidity,
                  date_time)


def pack_data(cities):
    data = []
    for city in cities:
        data.append(pack_city_data(city))

    return data



# def send_data: todo


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No files in the request", 400

    file = request.files['file']

    if file:
        file_contents = file.read()
        deserialized_data = json.loads(file_contents)
        decode_json(deserialized_data)
        return "Data correctly received", 200

@app.route('/')
def hello_geek():
    return '<h1>Hello from Flask & Docker</h2>'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)