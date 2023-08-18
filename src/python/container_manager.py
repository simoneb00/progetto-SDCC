"""
This file contains the logic to manage containers.
For every country, a container must be created (named "container-XX", where XX is the country code).
Then, every container must receive data relative to cities in that country.
The countries are retrieved from the file cities.csv.
"""
import json
import time
import docker
import os
import requests
import data_retriever


# def send_stop_messages():
#     ROOT_DIR = os.path.dirname(os.path.abspath(os.curdir))
#     countries = data_retriever.retrieve_countries()
#
#     with open(ROOT_DIR + "/progetto-SDCC/data/routing.json", 'r') as file:
#         data = json.load(file)
#
#     for country in countries:
#         dest_country = country.lower()[1:]
#         port_number = data[f"{dest_country}"]
#         url = f"http://localhost:{port_number}/{dest_country}/stop"
#         response = requests.get(url)
#         if response.status_code == 200:
#             print("Container manager: stop message successfully delivered")


def send_packet_to_container(packet):
    ROOT_DIR = os.path.dirname(os.path.abspath(os.curdir))
    dest_country = packet.country.lower()[1:]

    with open(ROOT_DIR + "/progetto-SDCC/data/routing.json", 'r') as file:
        data = json.load(file)

    port_number = data[f"{dest_country}"]

    url = f"http://localhost:{port_number}/{dest_country}"

    with open(ROOT_DIR + "/progetto-SDCC/data/data.json", 'w') as file:
        json.dump(packet.data, file)

    with open(ROOT_DIR + "/progetto-SDCC/data/data.json", 'r') as file:
        files = {'file': file}
        response = requests.post(url, files=files)

    if os.path.exists(ROOT_DIR + "/progetto-SDCC/data/data.json"):
        os.remove(ROOT_DIR + "/progetto-SDCC/data/data.json")


# The manager retrieves data every 60 seconds, and sends packets to containers
def start():
    keep_running = True
    while keep_running:
        print("Container manager: starting to retrieve data...")
        cities = data_retriever.retrieve()
        print("Container manager: data retrieved, sending packets to containers")
        for city in cities:
            send_packet_to_container(city)
        print("Container manager: packets successfully delivered, now sending stop messages")

        # send_stop_messages()

        user_input = input("Do you want to continue? (y/n)")
        if user_input.lower() == "n":
            keep_running = False
        else:
            print("Container manager: sleeping for 60 seconds")
            time.sleep(60)
