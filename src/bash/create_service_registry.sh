#!/bin/bash

if [ "$(docker ps -aq -f name="service_registry")" ]; then
  echo "The service_registry container already exist, so its creation is skipped"
else
  docker network create containers_network
  docker build -t "service_registry_image" -f src/docker_files/Dockerfile_service_registry .
  docker run -d --network containers_network -p "9000:9000" -e CONTAINER_NAME="service_registry_container" -e PYTHONUNBUFFERED=1 --name "service_registry_container" "service_registry_image"
  docker logs "service_registry_container"
  echo "The service_registry container has been created and it is running"
fi