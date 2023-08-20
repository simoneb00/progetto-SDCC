#!/bin/bash

if [ "$(docker ps -aq -f name="coordinator")" ]; then
  echo "The container coordinator already exist, so its creation is skipped"
else
  docker build --no-cache -t "image_coordinator" -f Dockerfile_coordinator .
  docker run -d -p "7000:7000" -e CONTAINER_NAME="container_coordinator" -e PYTHONUNBUFFERED=1 --name "container_coordinator" "image_coordinator"
  docker logs "container_coordinator"
  echo "The container container_coordinator has been created and it is running"
fi