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
import threading

from . import container_launcher
from .utils import data_retriever
from model import container

def send_packet_to_container(packet):
    root_dir = os.path.dirname(os.path.abspath(os.curdir))
    print(root_dir)
    dest_country = packet.country.lower()[1:]

    with open(root_dir + "app/data/routing.json", 'r') as file:
        data = json.load(file)

    """
    params = {'country' : dest_country}
    response = requests.get('http://localhost:9000/service-registry', params=params)
    if response.status_code != 200:
        raise Exception('An error occurred in calling the service registry.')

    return_data = json.loads(response.text)
    port_number = return_data.get('port_number')
"""

    port_number = data[f'{dest_country}']

    print(f'Invoking destination container on port number {port_number}')

    url = f"http://localhost:{port_number}/{dest_country}"

    with open(root_dir + "app/data/data.json", 'w') as file:
        json.dump(packet.data, file)

    print('Preparing data')

    with open(root_dir + "app/data/data.json", 'r') as file:
        files = {'file': file}
        headers = requests.utils.default_headers()
        time_count = 0
        server_running = False

        print('Starting to send data')

        while (time_count < 30) and (not server_running):  # Needed to wait flask app to be running
            try:
                time.sleep(1)
                time_count = time_count + 1
                response = requests.post(url, files=files, headers=headers)
                if response.status_code == 200:
                    print('Request correctly received and processed')

                server_running = True
            except Exception as e:
                server_running = False

    if os.path.exists(root_dir + "app/data/data.json"):
        os.remove(root_dir + "app/data/data.json")


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

# The manager starts a thread to retrieve data every 60 seconds, and sends
# Be careful that the daemon doesn't take trace of the already present containers at the first iteration, or until some request for all containers is generated
def thread_daemon_data_generator(all_containers,lock):
    keep_running = True


    while keep_running:
        
        print("Thread for data generation: starting to retrieve data...")
        cities = data_retriever.retrieve()

        for city in cities:
            print(city.name + " " + city.country)
            
            # Go into critical section to check container status
            with lock:
                is_running = check_new_containers(city, all_containers)
                
                
            if not is_running:
                container_launcher.launch_container(str.lower(city.country[1:]), city.country_number)
                with lock:
                    all_containers["container_" + str.lower(city.country[1:])] = container.Container(
                        "container_" + str.lower(city.country[1:]))
            else:
                with lock:
                    all_containers["container_" + str.lower(city.country[1:])].reset()                

            send_packet_to_container(city)

        print("Thread for data generation: sleeping for 60 seconds")
        time.sleep(60)


def thread_daemon_container_manager(all_containers,lock):
    keep_running = True
    round_index = 0

    # This loop has the responsability to stop all containers which are alive for more than 2 rounds
    while keep_running:
        print("Thread to manage container: starting to check...")        
        print(" ***************** ROUND INDEX IS ************************")
        print(" *                        " + str(round_index) + "                              *")   
        print(" *********************************************************")
        round_index = round_index + 1
        with lock:
            # Set all containers to false (unchecked)
            uncheck_all(all_containers)

        print("Country    Keep_Alive    Checked")
        for cnt in all_containers.copy().values():
            with lock:
                all_containers[cnt.id].pass_time()
            print(cnt.id + "    " + str(cnt.alive_round) + "    " + str(cnt.checked))


        for cnt in all_containers.copy().values():
            if not all_containers[cnt.id].checked:
                with lock:
                    all_containers[cnt.id].checked = True
                if all_containers[cnt.id].alive_round > 1:
                    container_launcher.shutdown_container(cnt)
                    with lock:
                        all_containers.pop(cnt.id)

        print("Thread to manage container: sleeping for 60 seconds")
        time.sleep(60)



def launch_main_container():
    container_launcher.launch_main_container()
    


# The manager retrieves data every 60 seconds, and sends packets to containers
def start():
    all_containers = {}  # Dict of containers running to manage round exits {container_it:container} sahred nei due thread
    
    # Generate exclusive lock to maintain coherent container time lived
    lock = threading.Lock()
    
    # Crea il thread principale per la gestione dei container
    main_thread = threading.Thread(target=thread_daemon_container_manager, args=(all_containers,lock))
    # Crea il thread secondario per la generazione dei dati
    data_thread = threading.Thread(target=thread_daemon_data_generator, args=(all_containers,lock))

    # Avvia il thread
    data_thread.start()
    main_thread.start()

    # Attendere che il data_thread abbia terminato l'esecuzione 
    main_thread.join()
    data_thread.join()

    print("Il thread principale ha terminato.")
