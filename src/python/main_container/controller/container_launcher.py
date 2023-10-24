import subprocess


def launch_container(country, country_number):
    try:
        subprocess.call(["bash", "app/bash/create_containers.sh", country, str(8080 + country_number)])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")


def shutdown_container(container):
    try:
        subprocess.call(["bash", "app/bash/shutdown.sh", container.id])

    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")
        

def launch_main_container():
    try:
        subprocess.call(["bash", "app/bash/create_main_container.sh"])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")
