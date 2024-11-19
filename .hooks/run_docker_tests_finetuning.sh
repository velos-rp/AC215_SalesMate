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
cd src/finetuning_pipeline
source docker-shell.sh "pipenv run pytest" || {
    echo "Tests failed. Aborting."
    # Stop all containers (assuming they were started earlier)
    docker ps -aq | xargs docker rm
    exit 1
  }

echo "Stopping all containers..."
docker ps -aq | xargs docker rm

echo "All tests passed!"

cd ..
