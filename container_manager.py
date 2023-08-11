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


def build_image(image_name):
    client = docker.from_env()
    try:
        with open(os.path.join("/", 'Dockerfile_container'), 'rb') as f:
            image = client.images.build(fileobj=f, tag=image_name, path="/Dockerfile_container")

        print(f"Image {image_name} successfully created")
    except docker.errors.BuildError as e:
        print(f"Error in creating the image {image_name}")
        print(e)
    finally:
        client.close()



def create_and_run_container(image_name, container_name):
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        container.remove()

        container = client.containers.create(image=image_name, name=container_name, detach=False, tty = True)
        container.start()

        print("Container successfully created and started")

    except docker.errors.APIError as e:
        print(f"Error during the creation and launch of the container {container_name}")
        print(e)
    finally:
        client.close()


def create_containers():
    countries = data_retriever.retrieve_countries()
    for country in countries:
        image_name = f"image_{country[1:]}".lower()
        container_name = f"container_{country[1:]}".lower()
        build_image(image_name)
        create_and_run_container(image_name, container_name)


def send_packet_to_container(packet):

    dest_country = packet.country.lower()[1:]

    with open("routing.json", 'r') as file:
        data = json.load(file)

    port_number = data[f"{dest_country}"]

    url = f"http://localhost:{port_number}/{dest_country}"

    with open("data.json", 'w') as file:
        json.dump(packet.data, file)

    with open("data.json", 'r') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
        print(response)


# The manager retrieves data every 60 seconds, and sends packets to containers
def start():

    keep_running = True
    while keep_running:

        print("Container manager: starting to retrieve data...")
        cities = data_retriever.retrieve()
        print("Container manager: data retrieved, sending packets to containers")
        for city in cities:
            send_packet_to_container(city)
        print("Container manager: packets successfully delivered, now sleeping for 60 seconds")
        user_input = input("Do you want to continue? (y/n)")
        if user_input.lower() == "n":
            keep_running = False
        else:
            time.sleep(60)
