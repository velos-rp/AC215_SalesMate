from fastapi import FastAPI
import sales_copilot

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# define route for sales copilot, /{collection_name}/query
# takes in collection name and input in payload
@app.get("/{collection_name}/query")
async def get_query(collection_name: str, input: str):
    return {"copilot_response": sales_copilot.process_queries(input, collection_name)}