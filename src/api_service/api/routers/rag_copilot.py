import requests
from fastapi import APIRouter, HTTPException
import os

router = APIRouter()


RAG_COPILOT_HOST = "rag-copilot-pipeline"
RAG_COPILOT_PORT = 8081
COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", default="investment-management")
BASE_URL = f"http://{RAG_COPILOT_HOST}:{RAG_COPILOT_PORT}"


@router.get("/insights")
async def get_insights(input: str):
    url = f"{BASE_URL}/{COLLECTION_NAME}/insights"
    params = {"input": input}

    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()
        return {"message": result}
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to get Insights from Copilot: {response.text}",
        )

# load data from input folder into the vector database
@router.post("/")
async def load_data():
    url = f"{BASE_URL}/{COLLECTION_NAME}/"
    response = requests.post(url)

    # Check if the request was successful
    if response.status_code == 200:
        return {"message": "Data loaded into vector database"}
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to load data into vector database: {response.text}",
        )

# delete the collection from the vector database
@router.delete("/")
async def delete_collection():
    url = f"{BASE_URL}/{COLLECTION_NAME}/"
    response = requests.delete(url)

    # Check if the request was successful
    if response.status_code == 200:
        return {"message": "Collection deleted from vector database"}
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to delete collection from vector database: {response.text}",
        )

# reset the vector database
@router.delete("/reset")
async def reset():
    url = f"{BASE_URL}/reset"
    response = requests.delete(url)

    # Check if the request was successful
    if response.status_code == 200:
        return {"message": "Vector database reset"}
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to reset vector database: {response.text}",
        )

# get info on the vector database
@router.get("/info")
async def get_info():
    url = f"{BASE_URL}/info"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to get info from vector database: {response.text}",
        )