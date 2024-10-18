# AC215_SalesMate

The main purpose of the rag-copilot-pipeline is to provide the user (customer sales representative) with a autonomous agent that assists the sales rep in answering the questions or requests of a prospective clients. Hence, a vector database (ChromaDB) is utilized to store a knowledge base of the company's information of products, services, and/or procedures. Our initial application/proof-of-concept for the project is the investment management industry. Hence, our current knowledge base consists of information from several PDFs related to investment management law, securities, and procedures. This google drive [folder](https://drive.google.com/drive/folders/1ouqCW-i4Pifb7-HCtPnqunmH9EfS5ZbC?usp=sharing) holds our initial sample of relevant documents stored in the vector database. 

We have initially utilized the Vertex AI `text-embedding-004` embeddings for processing text chunks and provide the CLI user the option to chunk based on the three options discussed in class: character splitting, recursive splitting, and semantic chunking. 

There are three main components in this module:
1. `vector_store.py` - This module defines two classes that interact with the ChromaDB vector store: `ChromaDB` and `LlamaIndexDB`. Both classes provide methods for loading documents into the vector store, querying the vector store, and viewing the number of documents in each collection. The main purpose of each class is to abstract away the the implementations of the vector store and intricacies of loading documents into the vector store. First, I implemented the `ChromaDB` class to manually load and query documents using the `chromadb` module and a supplementary `preprocessing.py` module. The `preprocessing.py` file currently supports processing `.txt` and `.pdf` files. I also utilized the Llama-Index library and its plugins for ChromaDB and VertexAI for a secondary vector store class: this provides us flexibility since the Llama-Index library provides a simple directory reader that can process more file formats. Moreover, the Llama-Index library provides advanced functionality for making query engines and agentic RAG pipelines for further development.
2. `rag_cli.py` - This module defines a simple CLI interface to process and load documents into the ChromaDB vector store. It also contains utility functions to query the ChromaDB vector store and view the number of documents in each collection of the database.
3. `sales_copilot.py`- This module provides functions for running our first iteration of the sales-copilot. The `process_queries` function takes in a customer chat and returns a list of insights that can help the sales rep answer the customer's questions and/or facilitate the conversation. The underlying implementation utiliwa a Gemini LLM to formulate a list of read queries to the vector data base using few-shot prompting. These reads are then pased through a LlamaIndex query engine to generate a list of insights that can be used to answer the customer's questions using relevant information from the vector store. 

Directions to run rag-copilot-pipeline:
1. Start a new terminal from the root project directory.
2. `cd src`
2. `sh docker-shell.sh`

Directions to load data into the vector database:
1. Start the rag-copilot-pipeline container with the above directions. This will launch a shell into the container and the container for the ChromaDB as well. 
2. Ensure that the files you'd like to load into the ChromaDB are in a local `data` directory. 
3. Execute `python rag_cli.py process-load --input-dir ./data --collection-name test-collection --output ./outputs`. This command will both save processed chunks and their embeddins to the `./outputs` folder and load these embeddings into the ChromaDB vector store in the collection `test-collection`. There are extra arguments for chunking params that can also be provided.

Directions to run the sales-copilot agent:
1. Start the rag-copilot-pipeline container with the above directions. This will launch a shell into the container and the container for the ChromaDB as well.
2. Ensure that the relevant files and documents are loaded into the vector store as per the above directions. 
3. Run the following code block in a jupyter notebook opened in the container shell with QUERY set to the customer chat/request:
<pre>QUERY = "SAMPLE CUSTOMER QUERY"
insights = process_queries(QUERY, "test-collection")
print(insights)</pre>

## Next Steps and Stretch Goals
- Transition embedding model to the Amazon Titan embedding models and the LLMs used as we're aiming to utilize AWS as our cloud and main services provider.
- Refine the files in the knowledge base, we found it easy to procure documents relating to investment management for instutional investors but not as much for retail investors.
- Integrate the sales copilot with the customer simulator: utilize a Python FAST API in the rag-copilot-pipeline container to facilitate HTTP requests from the customer simulator to the sales copilot.
- Create a script that can scrape HTML pages and generate texts to be loaded into the vector database.
- Look into more advanced Agentic RAG workflows to improve the sales copilot.