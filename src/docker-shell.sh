#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

DETACHED_MODE=""
# Parse arguments
while getopts "d" opt; do
  case $opt in
    d)
      DETACHED_MODE="-d"
      ;;
    *)
      echo "Usage: $0 [-d]"
      echo "  -d    Run containers in detached mode"
      exit 1
      ;;
  esac
done

export SECRETS_DIR_COPILOT="./rag_copilot_pipeline/secrets"
export SECRETS_DIR_API="./api_service/secrets"


# Create the network if we don't have it yet
docker network inspect sales-mate-network >/dev/null 2>&1 || docker network create sales-mate-network

# Build the image based on the Dockerfile
docker build -t rag-copilot-pipeline -f ./rag_copilot_pipeline/Dockerfile ./rag_copilot_pipeline/
docker build -t sales-mate-api-service -f ./api_service/Dockerfile ./api_service/

# Run docker compose targeting one container
# docker compose run --rm --service-ports $TARGET_IMAGE

# Run all containers
docker compose up --build -d

# Attach to logs if not running in detached mode
if [ -z "$DETACHED_MODE" ]; then
  echo "Attaching to logs..."
  docker compose logs -f
fi
