import os
import subprocess
import time

if __name__ == "__main__":
    print(f"Running...")
    try:
        subprocess.run(["bash", "create_containers.sh", "it", "8081"])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")

    while True:
        time.sleep(100)

    print("Stopped")
