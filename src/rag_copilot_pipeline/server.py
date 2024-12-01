import sales_copilot
from fastapi import FastAPI
import chromadb
import vector_store

app = FastAPI()

INPUT_FOLDER = "sample-data"
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Copilot API"}


# define route for sales copilot, /{collection_name}/query
# takes in collection name and input in payload
@app.get("/{collection_name}/insights")
async def get_query(collection_name: str, input: str):
    return {"copilot_response": sales_copilot.process_queries(input, collection_name)}

# load data from input folder into the vector database
@app.post("/{collection_name}/")
async def load_data(collection_name: str):
    db = vector_store.LlamaIndexDB(collection_name)
    db.load_from_dir(INPUT_FOLDER)
    return {"message": "Data loaded into vector database"}

# delete collection from vector database
@app.delete("/{collection_name}/")
async def delete_collection(collection_name: str):
    vector_store.LlamaIndexDB.delete_collection(collection_name)
    return {"message": "Collection deleted from vector database"}

# reset vector database
@app.delete("/reset")
async def reset():
    vector_store.LlamaIndexDB.delete_all_data()
    return {"message": "Vector database reset"}


# get general info on db collections and counts
@app.get("/info")
async def get_info():
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    # list collections and their metadata
    collections = client.list_collections()

    metadata = {}
    for collection in collections:
        metadata[collection.name] = collection.count()

    return {"metadata": metadata}