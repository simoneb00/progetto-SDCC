#!/bin/bash

sudo bash ./src/bash/create_service_registry.sh
sudo bash ./src/bash/create_main_container.sh
sudo bash ./src/bash/create_data_generator_container.sh

for id in $(docker ps --quiet); do
	# gnome-terminal --window -- bash -c "set-title $(docker ps --filter "id=$id" --format "{{.Names}}"); docker logs -f $id"
	gnome-terminal --window -- bash -c "set-title Prova; docker logs -f $id"
done


