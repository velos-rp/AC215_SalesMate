#!/bin/bash

set -e

export IMAGE_NAME="sales-mate-frontend-react"
export DEV="0"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile.dev .

# Run the container
docker run --rm --name $IMAGE_NAME -ti -v "$(pwd)/:/app/" -e DEV=$DEV -p 3000:3000 $IMAGE_NAME
