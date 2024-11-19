#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export SECRETS_DIR_COPILOT="./rag_copilot_pipeline/secrets"
export SECRETS_DIR_API="./api_service/secrets"
export DEV="0"

# Create the network if we don't have it yet
docker network inspect sales-mate-network >/dev/null 2>&1 || docker network create sales-mate-network

# Build the backend images based on the Dockerfile
docker build -t rag-copilot-pipeline -f ./rag_copilot_pipeline/Dockerfile ./rag_copilot_pipeline/
docker build -t sales-mate-api-service -f ./api_service/Dockerfile ./api_service/

# Build the frontend based on the Dockerfile
docker build -t "sales-mate-frontend-react" -f ./frontend-react/Dockerfile.dev ./frontend-react/

# Run all containers
docker compose up --build -d

# docker compose logs -f
