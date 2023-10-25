from flask import Flask, request

from model import container
from model.city import City
from . import container_launcher
from . import utils
from . import container_manager
import time
from .utils import checker


app = Flask(__name__)

all_containers = {}  # Dict of containers running to manage round exits {container_it:container}


def check_new_containers(city, containers):
    for container in containers.values():
        if container.id == "container_" + str.lower(city.country[1:]):
            print(container.id + " already running!")
            container.reset_time()
            return True
    return False


def uncheck_all(containers):
    for container in containers:
        city = checker.parse_id(container)

        print(city.name + " " + city.country)

        is_running = check_new_containers(city, all_containers)

        if not is_running:
            container_launcher.launch_container(str.lower(city.country[1:]), city.country_number)
            all_containers["container_" + str.lower(city.country[1:])] = container.Container(
                    "container_" + str.lower(city.country[1:]))
        else:
            all_containers["container_" + str.lower(city.country[1:])].reset()

        checker.send_packet_to_container(city)

    print("[INFO] Thread for data generation: sleeping for 60 seconds")
    time.sleep(60)

@app.route('/end-round/<int:round_index>', methods=['GET'])
def receive_msg(round_index):

    print('[INFO] Container manager listening on port 9002...')
    print("Thread to manage container: starting to check...")
    print(" ***************** ROUND INDEX IS ************************")
    print(" *                        " + str(round_index) + "                              *")
    print(" *********************************************************")

    # Set all containers to false (unchecked)
    uncheck_all(all_containers)

    print("Country    Keep_Alive    Checked")
    for cnt in all_containers.copy().values():
        all_containers[cnt.id].pass_time()
        print(cnt.id + "    " + str(cnt.alive_round) + "    " + str(cnt.checked))

    for cnt in all_containers.copy().values():
        if not all_containers[cnt.id].checked:
            all_containers[cnt.id].checked = True
            if all_containers[cnt.id].alive_round > 1:
                container_launcher.shutdown_container(cnt)
                all_containers.pop(cnt.id)

    print("[INFO] Thread to manage container: sleeping for 60 seconds")
    time.sleep(60)

    return 'End of Round message correctly received', 200

@app.route('/send-data', methods=['POST'])
def receive_data():

    received_data = request.get_json()

    name = received_data['name']
    country = received_data['country']
    lat = received_data['lat']
    lon = received_data['lon']
    country_number = received_data['country_number']
    data = received_data['data']

    city = City(name, country, lat, lon, country_number)
    city.set_data(data)

    print(f'[INFO] Main container received data for the city {city.name}')

    # Go into critical section to check container status
    with container_manager.lock:
        is_running = utils.checker.check_new_containers(city, container_manager.all_containers)

    if not is_running:
        container_launcher.launch_container(str.lower(city.country[1:]), city.country_number)
        with container_manager.lock:
            container_manager.all_containers["container_" + str.lower(city.country[1:])] = container.Container(
                "container_" + str.lower(city.country[1:]))
    else:
        with container_manager.lock:
            container_manager.all_containers["container_" + str.lower(city.country[1:])].reset()

    print('[INFO] Main container sending data to the destination container')
    utils.checker.send_packet_to_container(city)

    return 'Data correctly received', 200





def start_flask_server():
    print('[INFO] listening on port 9001...')
    round_index = 0

    print('[INFO] Container manager listening on port 9002...')
    print("Thread to manage container: starting to check...")
    print(" ***************** ROUND INDEX IS ************************")
    print(" *                        " + str(round_index) + "                              *")
    print(" *********************************************************")
    app.run(host='0.0.0.0', port=9001)