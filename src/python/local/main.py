""" Entry-point """

import os
import subprocess

if __name__ == "__main__":
    root_dir = os.getcwd()
    try:
        subprocess.call(["bash", root_dir + "/src/bash/create_main_container.sh"])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")