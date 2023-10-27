import threading
from . import container_launcher
from . import server

# Generate exclusive lock to maintain coherent container time lived
lock = threading.Lock()
all_containers = {}  # Dict of containers running to manage round exits {container_it:container}


"""
def check_new_containers(city, containers):
    for container in containers.values():
        if container.id == "container_" + str.lower(city.country[1:]):
            print(container.id + " already running!")
            container.reset_time()
            return True
    return False

def uncheck_all(containers):
    for container in containers:
        city = checker.parse_id(container)
        
        print(city.name + " " + city.country)
            
        # Go into critical section to check container status
        with lock:
            is_running = check_new_containers(city, all_containers)
                
                
        if not is_running:
            container_launcher.launch_container(str.lower(city.country[1:]), city.country_number)
            with lock:
                all_containers["container_" + str.lower(city.country[1:])] = container.Container(
                        "container_" + str.lower(city.country[1:]))
        else:
            with lock:
                all_containers["container_" + str.lower(city.country[1:])].reset()                

        checker.send_packet_to_container(city)

    print("[INFO] Thread for data generation: sleeping for 60 seconds")
    time.sleep(60)





def thread_daemon_container_manager(all_containers, lock):
    keep_running = True
    round_index = 0
    print("[INFO] Main container thread for containers managing correctly started")

    # This loop has the responsibility to stop all containers which are alive for more than 2 rounds
    while keep_running:
        print("Thread to manage container: starting to check...")        
        print(" ***************** ROUND INDEX IS ************************")
        print(" *                        " + str(round_index) + "                              *")   
        print(" *********************************************************")
        round_index = round_index + 1
        with lock:
            # Set all containers to false (unchecked)
            uncheck_all(all_containers)

        print("Country    Keep_Alive    Checked")
        for cnt in all_containers.copy().values():
            with lock:
                all_containers[cnt.id].pass_time()
            print(cnt.id + "    " + str(cnt.alive_round) + "    " + str(cnt.checked))


        for cnt in all_containers.copy().values():
            if not all_containers[cnt.id].checked:
                with lock:
                    all_containers[cnt.id].checked = True
                if all_containers[cnt.id].alive_round > 1:
                    container_launcher.shutdown_container(cnt)
                    with lock:
                        all_containers.pop(cnt.id)

        print("[INFO] Thread to manage container: sleeping for 60 seconds")
        time.sleep(60)
"""

def launch_main_container():
    container_launcher.launch_main_container()


# The manager retrieves data every 60 seconds, and sends packets to containers
def start():

    # Crea il thread principale per la gestione dei container
    flask_server_thread = threading.Thread(target= server.start_flask_server)

    # Start thread
    flask_server_thread.start()

    # Attendere che il data_thread abbia terminato l'esecuzione 
    flask_server_thread.join()

    print("[INFO] The main thread stopped.")
