#!/bin/bash

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
source docker-shell.sh

# Wait for the containers to start
sleep 10

docker compose exec sales-mate-api-service curl -f http://sales-mate-api-service:9876/
curl -f http://localhost:9876/

docker compose exec rag-copilot-pipeline curl -f http://rag-copilot-pipeline:8081/
curl -f http://localhost:8081/

# Define the services to test
# add 'sales-mate-api-service'
services=("rag-copilot-pipeline" "sales-mate-api-service")

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
