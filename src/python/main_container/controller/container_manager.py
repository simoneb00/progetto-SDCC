import threading
from . import container_launcher
from . import server

# Generate exclusive lock to maintain coherent container time lived
lock = threading.Lock()
all_containers = {}  # Dict of containers running to manage round exits {container_it:container}


def launch_main_container():
    container_launcher.launch_main_container()


# The manager retrieves data every 60 seconds, and sends packets to containers
def start():

    # Create a thread to execute the Flask server
    flask_server_thread = threading.Thread(target=server.start_flask_server)

    flask_server_thread.start()
    flask_server_thread.join()

    print("[INFO] The main thread stopped.")
