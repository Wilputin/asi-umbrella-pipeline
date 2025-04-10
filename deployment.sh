#!/usr/bin/env bash

function compose_db(){
  docker network create asi_network
  echo "building asi database service"
docker compose -f "./asi-db/docker-compose.yaml" build
  docker compose -f "./asi-db/docker-compose.yaml" up -d
}

function compose_kafka(){
echo "building kafka service"
docker compose -f "./kafka_build/docker-compose.yaml" build --no-cache
docker compose -f "./kafka_build/docker-compose.yaml" up -d

echo -e "AKHQ UI will be available on \e]8;;http://localhost:8080\ahttp://localhost:8080\e]8;;\a"

}

function start_pipeline(){
echo "starting ASI pipeline"
docker compose -f "./pipeline/docker-compose.yaml" build 
    docker compose -f "./pipeline/docker-compose.yaml" up -d
}

function wait_with_progress(){
  echo -n "Waiting 20 seconds for services to start: ["
  for i in {1..20}; do
    sleep 1
    echo -n "#"
  done
  echo "] Done."
}


compose_db
compose_kafka
wait_with_progress
start_pipeline

