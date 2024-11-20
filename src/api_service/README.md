## AC215_SalesMate: API Service

The api_service container is the FastAPI server that is meant to communicate with the rag-copilot-pipeline container and make calls to the LLM model (in this case, a finetuned Gemini endpoint). It is the main entry point for the front end React application to both start chat sessions and make requests to the LLM model while also pinging the rag-copilot-pipeline container to get insights for customer queries. Most of this backend code was adapted from the class cheese-app tutorial. 

Important files:
- `src/api_service/api/routers/direct_chat.py`: Contains the chat endpoints that allows the front end to create chat sessions with the gemini model and get previous chat data that is persisted in the local filesystem through the `ChatHistoryManager` class. Again, this is mainly adapted from the class tutorial.
- `src/api_service/api/routers/rag_copilot.py`: Contains the rag endpoint that makes requests to the rag-copilot-pipeline FastAPI server to get insights for customer queries. This module is quite simple and exposes just one get endpoint that a user can call to make a query, these queries can either be questions from the customer sales rep or directly from the user's conversation. 
- `src/api_service/api/utils`: This folder contains helper functions and classes that are used in the `direct_chat` endpoints. The `ChatHistoryManager` class is used to store the chat history in the local filesystem and the `llm_utils_gemini` module contains helper functions for sending messages to the Gemini model. We have also created a lengthy system prompt to set the context for the Gemini model for properly "simulating" a prospective customer.

### Instructions for Individually Running This Container

1. Start a new terminal from the `src/api_service` directory.
2. `sh docker-shell.sh`: This shell script will run the container and give you the shell as an entrypoint.
3. Run `uvicorn api.service:app --host 0.0.0.0 --port 9000 --log-level debug --reload --reload-dir api/ "$@"` to start the FastAPI server. This will allow you to make requests to the API endpoints from within the docker-network or from local host. If you want the container to start the server in step 2, change the DEV env variable in the docker script to 0.  

### Testing

We have added two tests for this container, located in the `tests` folder for this container. The `test_chat.py` file contains tests for the chat endpoint and the `test_rag_endpoint.py` file contains tests for the rag endpoint that communicates with the rag-copilot-pipeline FastAPI server. 