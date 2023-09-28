"""
This file contains the logic to manage containers.
For every country, a container must be created (named "container-XX", where XX is the country code).
Then, every container must receive data relative to cities in that country.
The countries are retrieved from the file cities.csv.
"""
import json
import time
import os
import requests

from src.python.local.controller import container_launcher
from src.python.local.controller.utils import data_retriever
from src.python.local.model import container

def send_packet_to_container(packet):
    if os.name == 'posix':
        root_dir = os.path.dirname(os.path.abspath(os.curdir)+"/../")  # todo improve
    else:
        root_dir = os.path.dirname(os.path.abspath(os.curdir))
    dest_country = packet.country.lower()[1:]

    with open(root_dir + "/progetto-SDCC/data/routing.json", 'r') as file:
        data = json.load(file)

    port_number = data[f"{dest_country}"]

    url = f"http://localhost:{port_number}/{dest_country}"

    with open(root_dir + "/progetto-SDCC/data/data.json", 'w') as file:
        json.dump(packet.data, file)

    with open(root_dir + "/progetto-SDCC/data/data.json", 'r') as file:
        files = {'file': file}
        headers = requests.utils.default_headers()
        time_count = 0
        server_running = False

        while (time_count < 30) and (not server_running):  # Needed to wait flask app to be running
            try:
                time.sleep(1)
                time_count = time_count + 1
                requests.post(url, files=files, headers=headers)
                server_running = True
            except Exception as e:
                server_running = False

    if os.path.exists(root_dir + "/progetto-SDCC/data/data.json"):
        os.remove(root_dir + "/progetto-SDCC/data/data.json")


def check_new_containers(city, containers):
    for container in containers.values():
        if container.id == "container_" + str.lower(city.country[1:]):
            print(container.id + " already running!")
            container.reset_time()
            return True
    return False


def uncheck_all(containers):
    for container in containers.values():
        container.reset()


# The manager retrieves data every 60 seconds, and sends packets to containers
def start():
    keep_running = True
    all_containers = {}  # Dict of containers running to manage round exits {container_it:container}

    while keep_running:
        uncheck_all(all_containers)
        print("Container manager: starting to retrieve data...")
        cities = data_retriever.retrieve()

        for city in cities:
            print(city.name + " " + city.country)
            is_running = check_new_containers(city, all_containers)
            if not is_running:
                container_launcher.launch_container(str.lower(city.country[1:]), city.country_number)
                all_containers["container_" + str.lower(city.country[1:])] = container.Container(
                    "container_" + str.lower(city.country[1:]))
            else:
                all_containers["container_" + str.lower(city.country[1:])].reset()
                all_containers["container_" + str.lower(city.country[1:])].check()
            send_packet_to_container(city)
            print(all_containers)

        print("Country    Keep_Alive    Checked")
        for cnt in all_containers.copy().values():
            if not cnt.checked:
                cnt.pass_time()
                if cnt.alive_round > 1:
                    container_launcher.shutdown_container(cnt)
                    all_containers.pop(cnt.id)
            print(cnt.id + "    " + str(cnt.alive_round) + "    " + str(cnt.checked))

        print("Container manager: sleeping for 60 seconds")
        time.sleep(60)
