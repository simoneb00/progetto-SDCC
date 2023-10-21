""" Entry-point """

import subprocess

if __name__ == "__main__":
    try:
        subprocess.call(["bash", "src/bash/create_service_registry.sh"])
        subprocess.call(["bash", "src/bash/create_main_container.sh"])
        subprocess.call(["bash", "src/bash/create_data_generator_container.sh"])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")
