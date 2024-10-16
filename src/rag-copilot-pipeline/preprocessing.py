import os
import pandas as pd
import json
import time
import glob
import pdfplumber
from pathlib import Path
from typing import List
import datetime
import logging

# Langchain
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from semantic_splitter import SemanticChunker

# Vertex AI
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
INPUT_FOLDER = "input-datasets"
OUTPUT_FOLDER = "outputs"
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000

vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
logger = logging.getLogger(__name__)

embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

def chunk_text(input_text: str, chunk_params: dict = {"method": "char-split", "chunk_size": 350, "chunk_overlap": 20}) -> List[str]:
    method = chunk_params["method"]
    chunk_size = chunk_params["chunk_size"]
    chunk_overlap = chunk_params["chunk_overlap"]

    if method == "char-split":
        # Init the splitter
        text_splitter = CharacterTextSplitter(chunk_size = chunk_size, chunk_overlap=chunk_overlap, separator='', strip_whitespace=False)
        # Perform the splitting
        text_chunks = text_splitter.create_documents([input_text])
        text_chunks = [doc.page_content for doc in text_chunks]

    elif method == "recursive-split":
        # Init the splitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size)

        # Perform the splitting
        text_chunks = text_splitter.create_documents([input_text])
        text_chunks = [doc.page_content for doc in text_chunks]

    elif method == "semantic-split":
        # Init the splitter
        text_splitter = SemanticChunker(embedding_function=generate_text_embeddings)
        # Perform the splitting
        text_chunks = text_splitter.create_documents([input_text])
        
        text_chunks = [doc.page_content for doc in text_chunks]
        print("Number of chunks:", len(text_chunks))

    return text_chunks



def process_folder(folder_path: Path, save: str = None, chunk_params: dict = {"method": "char-split", "chunk_size": 350, "chunk_overlap": 20}) -> pd.DataFrame:
    """
    Process a folder of text and pdf files.

    The function takes a folder path and will extract text from all text and pdf files in the folder. 
    It will then chunk the text according to the chunk_params and store the text and metadata in a pandas DataFrame.

    The metadata includes the file name and the number of chunks and the folder path.

    If save is set to True, the function will save the DataFrame to a single json file in the output folder.
    The output file name will include the datetime and the folder name.

    :param folder_path: The path to the folder to be processed
    :param save: Whether to save the DataFrame to a file
    :param chunk_params: A dictionary of parameters for chunking, including the method and chunk size
    :return: A pandas DataFrame with the text and metadata
    """
    files = list(folder_path.glob("*.txt")) + list(folder_path.glob("*.pdf"))
    # iniitalize dataframe
    df = pd.DataFrame(columns=["text", "metadata", "embeddings"])

    # loop through files
    for file in files:
        print(f"Processing file: {file.name}")
        # filter for pdf, if the file is a pdf then extract text from it using the helper method
        if file.suffix == ".pdf":
            input_text = extract_text_from_pdf(file)
        else:
            # read file
            with open(file, "r") as f:
                input_text = f.read()
    
        # chunk text
        text_chunks = chunk_text(input_text, chunk_params=chunk_params)
        print("\nNumber of chunks:", len(text_chunks),"\n")
        # print length of each of the first ten chunks
        # embed chunks
        embeddings = generate_text_embeddings(text_chunks, dimensionality=EMBEDDING_DIMENSION)

        # metadata for file, include file name and number of chunks
        # add base of folder path to metadata
        metadata = {"file_name": file.name, "number_of_chunks": len(text_chunks), "folder_path": folder_path.name}
        
        # add to dataframe
        df = pd.concat([df, pd.DataFrame({"text": text_chunks, "metadata": [metadata] * len(text_chunks), "embeddings": embeddings})], ignore_index=True)
    
    if save:
        # make sure output folder exists
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        # save dataframe with chunk params to single json file
        # include datetime and folder name in output file name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        df.to_json(os.path.join(OUTPUT_FOLDER, f"{save}{timestamp}.json"), orient="records")
        # also write the chunk params to a json file
        with open(os.path.join(OUTPUT_FOLDER, f"{save}{timestamp}_chunk_params.json"), "w") as f:
            json.dump(chunk_params, f)
    
    return df


def generate_text_embeddings(chunks, dimensionality: int = 256, batch_size=50):
	# Max batch size is 250 for Vertex AI
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in batch]
        kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
        embeddings = embedding_model.get_embeddings(inputs, **kwargs)
        all_embeddings.extend([embedding.values for embedding in embeddings])

    return all_embeddings

def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract the text from a pdf file using pdfplumber
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text






