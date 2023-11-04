#!/bin/bash

country=$1
port=$2

container_name="container_$country"


if [ "$(docker ps -aq -f name="${container_name}")" ]; then
  echo "The container ${container_name} already exist, so its creation is skipped"
  docker start $(docker inspect -f '{{.Id}}' ${container_name})
else
  docker volume create "volume_${country}"
  docker build -t "image_${country}" -f app/docker_files/Dockerfile_container .
  docker run --privileged=true -v "volume_${country}":/volume -v /run/systemd/system:/run/systemd/system -v /bin/systemctl:/bin/systemctl -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket  -d --network containers_network -p "$port:$port" -e CONTAINER_NAME="container_${country}" -e PYTHONUNBUFFERED=1 --name "container_${country}" "image_${country}"
  docker logs "container_${country}"
  echo "The container container_${country} has been created and it is running"
fi