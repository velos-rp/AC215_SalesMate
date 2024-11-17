#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Set vairables
# export BASE_DIR=$(pwd)
# export PERSISTENT_DIR=$(pwd)/../persistent-folder/
# export SECRETS_DIR=$(pwd)/secrets/
export GCP_PROJECT="ac-215-436117" # CHANGE TO YOUR PROJECT ID
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/gcp-key.json"
export TARGET_IMAGE="sales-mate-api-service"


# Create the network if we don't have it yet
docker network inspect sales-mate-network >/dev/null 2>&1 || docker network create sales-mate-network

# Build the image based on the Dockerfile
docker build -t rag-copilot-pipeline -f ./rag_copilot_pipeline/Dockerfile ./rag_copilot_pipeline/
docker build -t sales-mate-api-service -f ./api_service/Dockerfile ./api_service/

# Run docker compose targeting one container
# docker compose run --rm --service-ports $TARGET_IMAGE

# Run all containers
docker compose up --build
