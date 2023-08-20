""" Entry-point """

import os
import subprocess


if __name__ == "__main__":
    # Run main container to start all the other ones
    ROOT_DIR = os.path.dirname(os.path.abspath(os.curdir))

    try:
        subprocess.run(["bash", ROOT_DIR + "/progetto-SDCC/coordinator.sh"])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")
    # container_manager.start()
