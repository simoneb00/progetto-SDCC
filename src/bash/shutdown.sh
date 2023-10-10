#!/bin/bash

container_name=$1

if [ "$(docker ps -aq -f name="${container_name}")" ]; then
  docker stop "${container_name}"
  echo "The container ${container_name} has been stopped correctly"
  docker rm "${container_name}"
  echo "The container ${container_name} has been removed correctly"
else
  echo "The container ${container_name} doesn't exists"
fi