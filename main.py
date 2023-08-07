""" Entry-point """
import threading

import container
import data_retriever
import container_manager
import subprocess
import time

# sending packets to container (TODO remove)



if __name__ == "__main__":

    # container_manager.create_containers()

    print("containers created")

    # cities = data_retriever.entry_point()  # tuples (name, country, lat, lon, data)
    # packets = container.pack_data(cities)

    # for packet in packets:
    #     print(f"[{packet.name}, {packet.country}, {packet.temp}, {packet.feels_like},{packet.temp_min}, {packet.temp_max}, {packet.humidity}, {packet.pressure}, {packet.date_time}]")

    try:
        subprocess.run(["bash", "./create_containers.sh"])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")

    cities = data_retriever.retrieve()
    for city in cities:
        container_manager.send_packet_to_container(city)
