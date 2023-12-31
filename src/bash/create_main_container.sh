#!/bin/bash



if [ "$(docker ps -aq -f name="main_container")" ]; then
  echo "The main container already exist, so its creation is skipped"
  docker start $(docker inspect -f '{{.Id}}' "main_container")
else
  docker build --no-cache --pull -t "main_image" -f src/docker_files/Dockerfile_main_container .
  docker run -d --privileged=true  -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket -v /var/run/docker.sock:/var/run/docker.sock --network containers_network -e CONTAINER_NAME="main_container" -e PYTHONUNBUFFERED=1 --name "main_container" "main_image"
  docker logs "main_container"
  echo "The main container has been created and it is running"
fi