"""
This file contains the containers' basic operations.
Every container is relative to a specific country, and gets data from sensors located in that country.
It must perform the following operations:
* Receive messages sent on a socket
* Collect significant data from raw measurement (json file)
* Convert data to standard units of measure (e.g. temperature -> Celsius)
* Send data (relative to every city) to the cloud
(This file should be loaded into every container)
"""

import datetime
import sys
import time

import docker
import requests
from flask import Flask, request, json
import os
import packet
import cloud_interface


app = Flask(__name__)
container_name = os.environ.get("CONTAINER_NAME")
print(container_name)
container_country = container_name[len(container_name) - 2:]
print(container_country)


def pack_city_data(data):
    name = data["name"]
    country = container_country
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

    return packet.Packet(name,
                         country,
                         celsius_temp,
                         celsius_feels_like,
                         celsius_min,
                         celsius_max,
                         pressure,
                         humidity,
                         date_time)


@app.route(f'/{container_country}/stop')
def shutdown():
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        container.stop()
    except docker.errors.NotFound:
        print(f"Container {container_name} non trovato.")
    except docker.errors.APIError as e:
        print(f"Errore nell'interruzione del container {container_name}: {e}")
    return "shutting down", 200


@app.route(f'/{container_country}', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No files in the request", 400

    file = request.files['file']

    if file:
        file_contents = file.read()
        deserialized_data = json.loads(file_contents)
        packet = pack_city_data(deserialized_data)
        # todo remove below
        print(f"{packet.name}, {packet.country}, {packet.temp}, {packet.feels_like}, {packet.temp_min}, {packet.temp_max}, {packet.humidity}, {packet.pressure}, {packet.date_time}")
        print('Sending data to cloud')
        code, message = cloud_interface.send_packet(packet)
        print(f'{code}: {message}')

        print('Sending queries to cloud')
        query_code, query_result = cloud_interface.query(packet.name, packet.country, '2023-10-21', 0, 0)
        if query_code != 200:
            print(f'{query_code} - {query_result}')
        else:
            stats = json.loads(query_result)
            # print avg statistics
            print(stats)

        query_code, query_result = cloud_interface.query(packet.name, packet.country, '2023-10-21', 1, 0)
        if query_code != 200:
            print(f'{query_code} - {query_result}')
        else:
            stats = json.loads(query_result)
            # print avg statistics
            print(stats)

        query_code, query_result = cloud_interface.query(None, packet.country, '2023-10-21', 0, 1)
        if query_code != 200:
            print(f'{query_code} - {query_result}')
        else:
            stats = json.loads(query_result)
            # print avg statistics
            print(stats)


        return message, code


@app.route('/')
def hello():
    return f'<h1>Hello from the container for country {container_country} </h2>'


if __name__ == "__main__":
    print(f"{container_name}, representing the country {container_country}")

    with open("routing.json", 'r') as file:
        data = json.load(file)

    port_number = data[f"{container_country}"]
    app.run(host='0.0.0.0', port=port_number)
