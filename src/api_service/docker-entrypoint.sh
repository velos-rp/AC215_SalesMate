#!/bin/bash

echo "Container is running!!!"

# this will run the api/service.py file with the instantiated app FastAPI
uvicorn_server() {
    pipenv run uvicorn api.service:app --host 0.0.0.0 --port 9876 --log-level debug --reload --reload-dir api/ "$@"
}

uvicorn_server_production() {
    pipenv run uvicorn api.service:app --host 0.0.0.0 --port 9876 --lifespan on
}

export -f uvicorn_server
export -f uvicorn_server_production

echo -en "\033[92m
The following commands are available:
    uvicorn_server
        Run the Uvicorn Server
\033[0m
"

if [ "${DEV}" = "1" ]; then
  pipenv shell
elif [ "${DEV}" = "2" ]; then
  uvicorn_server_production
else
  uvicorn_server
fi