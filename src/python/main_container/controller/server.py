from flask import Flask, request

from model import container
from model.city import City
from . import container_launcher
from . import utils
from . import container_manager

app = Flask(__name__)


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
    print('[INFO] Data getter: listening on port 9001...')
    app.run(host='0.0.0.0', port=9001)