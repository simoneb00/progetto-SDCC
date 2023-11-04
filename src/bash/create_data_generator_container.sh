#!/bin/bash

if [ "$(docker ps -aq -f name="data_generator_container")" ]; then
  echo "The data_generator container already exist, so its creation is skipped"
  docker start $(docker inspect -f '{{.Id}}' "data_generator_container")
else
  docker volume create "volume_data_generator"
  docker build -t "data_generator_image" -f src/docker_files/Dockerfile_data_generator .
  docker run -v "volume_data_generator":/volume -d --network containers_network -p "9001:9001" -e CONTAINER_NAME="data_generator_container" -e PYTHONUNBUFFERED=1 --name "data_generator_container" "data_generator_image"
  echo "The data_generator container has been created and it is running"
fi