#!/bin/bash

set -e

export IMAGE_NAME="sales-mate-frontend-react-prod"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti -p 3000:3000 $IMAGE_NAME
