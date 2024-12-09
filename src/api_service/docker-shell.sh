#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Define some environment variables
export IMAGE_NAME="sales-mate-api-service"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/secrets/
export PERSISTENT_DIR=$(pwd)/

# Build the image based on the Dockerfile
#docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$PERSISTENT_DIR":/persistent \
-p 9876:9876 \
-e DEV=0 \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json \
-e GCP_PROJECT=project-id-3187519002330642642 \
-e FINETUNED_MODEL=1 \
$IMAGE_NAME
