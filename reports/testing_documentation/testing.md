## CI/CD Pipeline

Our testing pipeline enables us to test the quality, integration, and functionality of our different applications/containers both locally and on the server. Since each of our applications functions are decomposed into containers we use Docker to deploy our containers and then run `pytest` on a set of tests local to each container.
The tests for each individual container are found in the `<container>/tests` directory for each `<container>`. Currently, we have tests for the following containers: rag_copilot_pipeline and finetuning_pipeline.

To run these tests, we use the action workflows with configurations located in the `.github/workflows/` directory. Therefore, after each push to github, all the required containers are started in Github and each of the tests are run inside the container. 


### Test Descriptions

#### API Service
- `src/api_service/tests/test_direct_chat.py` We have one test that tests the direct chat endpoint to create a chat session. This is a simple test that demands the server returns a success code.
- `src/api_service/tests/test_rag_endpoint.py` We have one test that tests the sales copilot endpoint. This is a simple test that demands the server returns a success code using a basic query. There is a second test that queries the information from the vector database as well. 

#### RAG Copilot Pipeline
- `src/rag_copilot_pipeline/tests/test_preprocessing.py` We have one test that on the preprocessing workflow tha tests the chunking functionality of the pipeline.
- `src/rag_copilot_pipeline/tests/test_vector_store.py` Another test tests the main functionalities of the vector database class by creating a toy collection, writing data to it, and querying it.

#### Finetuning Pipeline
- `src/rag_copilot_pipeline/tests/test_vector_store.py: test_processing_pipeline` Runs the end-to-end data processing pipeline for preparing the data for the fine-tuning model. It uses a sample of only 4 rows of the original dataset to speed-up test
- `src/finetuning_pipeline/tests/test_finetuning.py: test_generate_train_test` Tests specifically the generate_train_test step with all the data that was used to train the model.


### Local Testing Workflow
- We have two testing protocols. First, we have a pre-commit hook that runs the basic hooks found in the tutorials, including black, isort, flake8 (linting), etc. This ensures the qualit of our code before we make commits locally before pushing to remote.
- Next, we have a bash script (`.hooks/run_docker_tests.sh`) that spins up docker containers for the api_service and rag_copilot_pipeline using our Dockerfiles and docker-compose.yml fils in the `src` directory. This script ensures that the docker compose function works and executes a pytest command from the project directory in each service.

### Server Side: CI Workflow 1: `.github/workflows/CI_docker.yml`

This workflow configuration spins up a set of containers using the Github Actions runner. This workflow uses the ubuntu image to load our repo, test basic linting/formatting, securely load our API keys, spin up our main application containers [frontend, api_service, rag_copilot_pipeline], and finally run our pytest tests. This test happens whenever there is a push/merge to main.