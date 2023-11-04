#!/bin/bash

mkdir -p "time_data"
for volume in $(docker volume ls -q); do
  echo "copying $volume to directory time_data"

  volume_name=$(docker volume inspect --format '{{.Name}}' $volume)
  filename="statistics_$volume_name"

  mkdir -p "time_data/$volume_name"
  docker run --rm -v "$volume:/$volume_name" -v "$(pwd)/time_data/":/dest alpine cp -r "/$volume_name" /dest

  docker
done