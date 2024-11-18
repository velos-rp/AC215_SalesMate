#!/bin/bash

# Exit immediately if any command fails
set -e


# Skip pre-commit hook if --no-verify used
for arg in "$@"; do
    if [ "$arg" = "--no-verify" ]; then
        echo "Pre-commit hook skipped (--no-verify used)."
        exit 0
    fi
done

# Check if the SKIP_HOOKS environment variable is set
if [ "$SKIP_CONTAINER_TESTS" = "True" ]; then
    echo "Pre-commit hook skipped."
    exit 0
fi


echo "Starting Docker containers and running tests..."

# Start the containers in detached mode
cd src
source docker-shell.sh -d

# Wait for the containers to start
sleep 10

# Define the services to test
services=("rag-copilot-pipeline")

# Run pytest in each container
for service in "${services[@]}"; do
  echo "Running tests in $service..."
  docker compose exec "$service" pipenv run pytest || {
    echo "Tests failed in $service. Aborting."
    docker compose down
    exit 1
  }
done

# Stop the containers after tests
docker compose down

echo "All tests passed!"

cd ..
