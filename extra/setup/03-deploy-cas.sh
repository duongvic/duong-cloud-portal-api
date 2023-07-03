#!/bin/bash
source utils/color.sh
source utils/alias.sh

if [ ! "$(docker network ls | grep casnetwork)" ]; then
  echo "Creating new cas network ..."
  docker network create -d bridge casnetwork
fi
docker-compose down --volumes
docker-compose up -d
#docker stack deploy --compose-file prod_docker-compose.yml casstack
#docker stack services casstack
#docker stack rm casstack
#docker swarm leave --force
#docker-compose up -d --scale cas-portal=2 --scale cas-redis-master=1 --scale cas-redis-replica=2