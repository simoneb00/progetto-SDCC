import os
import requests
import json
import time


def check_new_containers(city, containers):
    for container in containers.values():
        if container.id == "container_" + str.lower(city.country[1:]):
            print(container.id + " already running!")
            container.reset_time()
            return True
    return False


def send_packet_to_container(packet):
    root_dir = os.path.dirname(os.path.abspath(os.curdir))
    dest_country = packet.country.lower()[1:]

    config_file_path = '/app/data/config.json'

    with open(config_file_path, 'r') as file:
        config = json.load(file)

    params = {'country': dest_country}
    response = requests.get(config.get('service_registry_endpoint'), params=params)
    if response.status_code != 200:
        raise Exception('An error occurred in calling the service registry.')

    return_data = json.loads(response.text)
    port_number = return_data.get('port_number')

    print(f'[INFO] Invoking destination container on port number {port_number}')

    dest_container_name = f'container_{dest_country}'

    url = f"http://{dest_container_name}:{port_number}/{dest_country}"

    with open(root_dir + "app/data/data.json", 'w') as file:
        json.dump(packet.data, file)

    with open(root_dir + "app/data/data.json", 'r') as file:
        files = {'file': file}
        headers = {"X-Source-Container": 'main_container'}
        time_count = 0
        server_running = False

        while (time_count < 30) and (not server_running):  # Needed to wait flask app to be running
            try:
                time.sleep(1)
                time_count = time_count + 1
                response = requests.post(url, files=files, headers=headers)
                if response.status_code == 200:
                    print('[INFO] Request correctly received and processed')
                server_running = True
            except Exception as e:
                print(e)
                server_running = False

    if os.path.exists(root_dir + "app/data/data.json"):
        os.remove(root_dir + "app/data/data.json")


def parse_id(container_id):
    country = ""
    
    print(container_id)
    country = container_id.split("_")[1]
    
    return country
