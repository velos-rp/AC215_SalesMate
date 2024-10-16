#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Set vairables
# export BASE_DIR=$(pwd)
# export PERSISTENT_DIR=$(pwd)/../persistent-folder/
# export SECRETS_DIR=$(pwd)/secrets/
export GCP_PROJECT="ac-215-436117" # CHANGE TO YOUR PROJECT ID
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/ac-215-436117-6c53e25e170d.json"
export IMAGE_NAME="rag-copilot-pipeline"


# Create the network if we don't have it yet
docker network inspect llm-rag-network >/dev/null 2>&1 || docker network create llm-rag-network

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f ./rag-copilot-pipeline/Dockerfile ./rag-copilot-pipeline/

# Run All Containers
docker compose run --rm --service-ports $IMAGE_NAME






# # Build the image based on the Dockerfile
# docker build -t $IMAGE_NAME -f Dockerfile .

# # Run Container
# docker run --rm --name $IMAGE_NAME -ti \
# -v "$BASE_DIR":/app \
# -v "$SECRETS_DIR":/secrets \
# -v "$PERSISTENT_DIR":/persistent \
# -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
# -e GCP_PROJECT=$GCP_PROJECT \
# $IMAGE_NAME