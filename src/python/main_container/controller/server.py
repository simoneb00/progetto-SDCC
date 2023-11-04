import threading

from flask import Flask, request

from model import container
from model.city import City
from . import container_launcher
from . import utils
from . import container_manager
from .utils import checker


app = Flask(__name__)


def check_new_containers(country, containers):
    for container in containers.values():
        if container.id == "container_" + str.lower(country.country[1:]):
            print(container.id + " already running!")
            container.reset_time()
            return True
    return False


@app.route('/end-round/', methods=['POST'])
def receive_msg():

    json_data = request.get_json()
    round_index = json_data.get('round_index')
    active_countries = json_data.get('list')

    print("Thread to manage container: starting to check...")
    print("\n\n ***************** ROUND INDEX ************************")
    print(" *                        " + str(round_index) + "                           *")
    print(" ******************************************************")

    for cnt in container_manager.all_containers.copy().values():
        if cnt.id[10:] in active_countries:
            container_manager.all_containers[cnt.id].reset_time()

    print("Country       Age")
    for cnt in container_manager.all_containers.copy().values():
        container_manager.all_containers[cnt.id].pass_time()
        print(cnt.id + "    " + str(cnt.alive_round))

    for cnt in container_manager.all_containers.copy().values():
        if cnt.alive_round >= 3:
            container_launcher.shutdown_container(cnt)
            container_manager.all_containers.pop(cnt.id)

    return 'End of Round message correctly received', 200


def thread_receive_data(received_data):
    name = received_data['name']
    country = received_data['country']
    lat = received_data['lat']
    lon = received_data['lon']
    country_number = received_data['country_number']
    data = received_data['data']

    city = City(name, country, lat, lon, country_number)
    city.set_data(data)

    print(f'[INFO] Thread received data for the city {city.name}')

    is_running = utils.checker.check_new_containers(city, container_manager.all_containers)

    if not is_running:
        container_launcher.launch_container(str.lower(city.country[1:]), city.country_number)
        container_manager.all_containers[f"container_{str.lower(city.country[1:])}"] = container.Container(
            f"container_{str.lower(city.country[1:])}")
    else:
        container_manager.all_containers[f"container_{str.lower(city.country[1:])}"].reset()

    print('[INFO] Sending data to the destination container')
    utils.checker.send_packet_to_container(city)


@app.route('/send-data', methods=['POST'])
def receive_data():
    received_data = request.get_json()

    print('[INFO] Launching thread to handle the request')
    thread = threading.Thread(target=thread_receive_data(received_data))
    thread.start()
    thread.join()

    return 'Data correctly received', 200


def start_flask_server():
    round_index = 0

    print('[INFO] Container manager listening on port 9001...')
    print("Thread to manage container: starting to check...")
    print(" ***************** ROUND INDEX ************************")
    print(" *                        " + str(round_index) + "                           *")
    print(" ******************************************************")
    app.run(host='0.0.0.0', port=9001)
