#!/bin/bash

ls

if [ "$(docker ps -aq -f name="main_container")" ]; then
  echo "The main container already exist, so its creation is skipped"
else
  docker build --no-cache --pull  -t "main_image" -f src/docker_files/Dockerfile_main_container .
  docker run -d -p "8080:8080" -e CONTAINER_NAME="main_container" -e PYTHONUNBUFFERED=1 --name "main_container" "main_image"
  docker logs "main_container"
  echo "The main container has been created and it is running"
fi