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

echo -e "AKHQ UI will be available on \e]8;;http://localhost:8080;\a"

}

function start_pipeline(){
echo "starting ASI pipeline"
docker compose -f "./pipeline/docker-compose.yaml" build 
    docker compose -f "./pipeline/docker-compose.yaml" up -d
}

function start_api_service(){
  echo "spinning up api service..."
  docker compose -f "./api-service/docker-compose.yaml" build
  docker compose -f "./api-service/docker-compose-yaml" up -d
}

function wait_with_progress(){
  echo -n "Waiting 20 seconds for services to start: ["
  for i in {1..20}; do
    sleep 1
    echo -n "#"
  done
  echo "] Done."
}

function compose_services(){
  compose_db
  compose_kafka
}
function start_all_services(){
  compose_services
  wait_with_progress
  start_pipeline

}
function main() {
  if [[ "$1" == "--function" && -n "$2" ]]; then
    FUNC_NAME="$2"
    if declare -F "$FUNC_NAME" > /dev/null; then
      shift 2
      "$FUNC_NAME" "$@"
    else
      echo "❌ Function '$FUNC_NAME' not found."
      show_help
    fi
  else
    show_help
  fi
}


main "$@"


