#!/bin/bash

# Define some environment variables
export IMAGE_NAME="sales-mate-deployment"
export BASE_DIR=$(pwd)
export AWS_REGION="us-east-1" 
export AWS_ECR_REPO="396608784103.dkr.ecr.us-east-1.amazonaws.com/sales-mate"

# Authenticate Docker to ECR
# aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ECR_REPO

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

# Push the image to ECR
# docker tag $IMAGE_NAME $AWS_ECR_REPO:$IMAGE_NAME
# docker push $AWS_ECR_REPO:$IMAGE_NAME

# Load AWS config keys from the .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found! Make sure it exists in the current directory."
    exit 1
fi

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v /var/run/docker.sock:/var/run/docker.sock \
-v "$BASE_DIR":/app \
-v "$HOME/.ssh":/home/app/.ssh \
-v "$BASE_DIR/../api_service":/api_service \
-v "$BASE_DIR/../frontend-react":/frontend-react \
-v "$BASE_DIR/../rag_copilot_pipeline":/rag_copilot_pipeline \
-e AWS_REGION=$AWS_REGION \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
$IMAGE_NAME
