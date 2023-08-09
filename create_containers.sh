#!/bin/bash


if [ ! -f "countries.txt" ]; then
    echo "The file countries.txt does not exist."
    exit 1
fi

countries=($(cat countries.txt))

for i in "${!countries[@]}"; do
      country="${countries[i]}"
      container_name="container-$country"

    if [ "$(docker ps -aq -f name="${container_name}")" ]; then

        echo "The container ${container_name} already exist, so its creation is skipped"

    else
        docker build -t "image_${country}" -f Dockerfile_container .
        port=$((8080 + i))
        docker run -d -p "$port:$port" -e CONTAINER_NAME="container_${country}" -e PYTHONUNBUFFERED=1 --name "container_${country}" "image_${country}"
        # -p 8080:8080 : exposing the container port 8080 on tha actual port 8080
        # -e CONTAINER_NAME="container_${country}" : setting an env variable in the container, so the container can access to its own name
        # -e PYTHONUNBUFFERED=1 : env variable to see prints on the container

        docker logs "container_${country}"  # print container console output

        echo "The container container_${country} has been created and it is running"
    fi
done