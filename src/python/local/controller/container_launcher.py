import os
import subprocess


def launch_container(country, country_number):
    if os.path.split(os.getcwd())[1] != 'progetto-SDCC':
        os.chdir(os.getcwd()+"/../../../")

    root_dir = os.getcwd()
    try:
        subprocess.call(["bash", root_dir + "/bash/create_containers.sh", country, str(8080 + country_number)])
    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")


def shutdown_container(container):
    root_dir = os.path.dirname(os.path.abspath(os.curdir))

    try:
        subprocess.call(["bash", root_dir + "/bash/progetto-SDCC/shutdown.sh", container.id])

    except subprocess.CalledProcessError as e:
        print("Error in calling the containers' creation script")
