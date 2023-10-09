""" Entry-point """

import os
import subprocess
from controller import container_manager

if __name__ == "__main__":
    root_dir = os.getcwd()
    try:
        subprocess.call(["bash", root_dir + "/bash/create_main_container.sh"])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")
    
    container_manager.start()
