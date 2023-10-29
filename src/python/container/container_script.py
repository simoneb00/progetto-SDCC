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
import csv
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

    f = request.files['file']

    if f:
        file_contents = f.read()
        deserialized_data = json.loads(file_contents)
        p = pack_city_data(deserialized_data)

        source = request.headers.get('X-Source-Container')
        print(f'[INFO] Data received from {source}')

        print(f"[INFO] Received data for city {p.name}")
        print('[INFO] Sending data to cloud')
        code, message = cloud_interface.send_packet(p, config)
        print(f'[INFO] Results: {code}: {message}')

        now = datetime.datetime.now()
        print(f'[INFO] Results got at time {now}')

        # save time for statistics
        cold_start = source != 'data_generator_container'

        filename = '/volume/statistics.csv'
        file_exists = os.path.isfile(filename)

        with open(filename, 'a') as f:
            csv_writer = csv.writer(f)
            if not file_exists:
                csv_writer.writerow(['city', 'time', 'cold_start'])
            csv_writer.writerow([p.name, now, cold_start])

        date = '2023-10-26'

        print('[INFO] Sending queries to cloud')
        query_code, query_result = cloud_interface.query(p.name, p.country, date, 0, 0, config)
        if query_code != 200:
            print(f'[INFO] Results: {query_code} - {query_result}')
        else:
            stats = json.loads(query_result)
            # print avg statistics
            print(stats)

        query_code, query_result = cloud_interface.query(p.name, p.country, date, 1, 0, config)
        if query_code != 200:
            print(f'[INFO] Results: {query_code} - {query_result}')
        else:
            stats = json.loads(query_result)
            # print avg statistics
            print(stats)

        query_code, query_result = cloud_interface.query(None, p.country, date, 0, 1, config)
        if query_code != 200:
            print(f'[INFO] Results: {query_code} - {query_result}')
        else:
            stats = json.loads(query_result)
            # print avg statistics
            print(stats)

        print('\n\n')

        return message, code


if __name__ == "__main__":
    print(f"[INFO] Hello from {container_name}, representing the country {container_country}")

    with open('config.json', 'r') as file:
        config = json.load(file)

    params = {'country': container_country}
    response = requests.get(config.get('service_registry_endpoint'), params=params)
    if response.status_code != 200:
        raise Exception('An error occurred in calling the service registry.')

    return_data = json.loads(response.text)
    port_number = return_data.get('port_number')

    app.run(host='0.0.0.0', port=port_number)
