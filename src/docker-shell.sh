#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Set vairables
# export BASE_DIR=$(pwd)
# export PERSISTENT_DIR=$(pwd)/../persistent-folder/
# export SECRETS_DIR=$(pwd)/secrets/
export GCP_PROJECT="ac-215-436117" # CHANGE TO YOUR PROJECT ID
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/gcp-key.json"
export IMAGE_NAME="rag-copilot-pipeline"


# Create the network if we don't have it yet
docker network inspect llm-rag-network >/dev/null 2>&1 || docker network create llm-rag-network

# Build the image based on the Dockerfile
docker build -t rag-copilot-pipeline -f ./rag-copilot-pipeline/Dockerfile ./rag-copilot-pipeline/

# Run docker compose targeting one container
docker compose run --rm --service-ports $IMAGE_NAME

# Run all containers
# docker compose up --build