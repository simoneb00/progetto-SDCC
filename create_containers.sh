#!/bin/bash


if [ ! -f "countries.txt" ]; then
    echo "The file countries.txt does not exist."
    exit 1
fi

docker build -t image_main -f Dockerfile_main .

countries=($(cat countries.txt))

for country in "${countries[@]}"; do
    container_name="container-${country}"

    if [ "$(docker ps -aq -f name=${container_name})" ]; then
        echo "The container ${container_name} already exist, so its creation is skipped"
    else
        docker build -t "image_${country}" -f Dockerfile_container .
        docker run -d -p 8080:8080 -d --name "container_${country}" "image_${country}"   # the container will run on the local network
        docker logs "container_${country}"  # print container console output
        echo "The container container_${country} has been created and it is running"
    fi
done