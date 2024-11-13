import os
from fastapi import APIRouter, Header, Query, Body, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
import uuid
import time
from datetime import datetime
import mimetypes
from pathlib import Path
import requests


router = APIRouter()


RAG_COPILOT_HOST = "rag-copilot-pipeline"
RAG_COPILOT_PORT = 8081
COLLECTION_NAME = "llama-test"

@router.get("/")
async def get_insights(input: str):

    base_url = f"http://{RAG_COPILOT_HOST}:{RAG_COPILOT_PORT}"
    
    url = f"{base_url}/{COLLECTION_NAME}/query"
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
            detail=f"Failed to get Insights from Copilot: {response.text}"
        )