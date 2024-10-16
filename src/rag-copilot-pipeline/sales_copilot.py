import os
import argparse
import pandas as pd
import json
import time
import glob
import hashlib
import chromadb
# from chromadb.config import Settings
import uuid
from pathlib import Path
import logging
import re

import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.generative_models import GenerativeModel, GenerationConfig, Content, Part, ToolConfig

# llama index
from llama_index.llms.vertex import Vertex
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    Settings,
    StorageContext,
    Document,
    get_response_synthesizer
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor


import preprocessing
import vector_store

from google.oauth2 import service_account
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 768
GENERATIVE_MODEL = "gemini-1.5-flash-001"
INPUT_FOLDER = "sample-data"
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000
creds = service_account.Credentials.from_service_account_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)



generation_config = {
    "max_output_tokens": 8192,  # Maximum number of tokens for output
    "temperature": 0.01,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

Settings.llm = Vertex(model="gemini-1.5-flash-001", project=creds.project_id, credentials=creds, temperature=0.01)

SYSTEM_INSTRUCTION = """
You are an AI assistant that is is helping a customer sales representative respond to client questions in regards 
to investment management. You will process customer chats and have access to a memory API that stores
relevant information about investment and portfolio management, investemnt management law, different securities products,
and customer sales training material. Your goal is to output a list of up to 3 helpful read queries that can be answered
using the information in the memory API in the following format:

Read[query1]

Read[query2]

Read[query3]


When answering a query from a prospective or current client:
1. Carefully read the question, be sure to note references to any specific products or services that the company may offer.
2. Maintain a professional and knowledgable tone in your answer.
3. Sometimes, the best read query is to repeat the client's question, but other times it might be better to create more detailed queries from the client chat.
4. Keep in mind that the customer chat may refer to the name of the customer sales representative.
5. If you don't think making a Read operation is useful, then simply return "No Read operations necessary."
6. Format the read queries as questions.

Here are some examples of a customer chat and possible outputs:

Client Chat: Good morning.I've been looking into some real estate investment opportunities for the past few years. I have some left over money from
a savings account and inheritance. I usually prefer to invest directly in real estate since I like tangible things more. Is there anything you can do
for me. One reason I don't like other investemnts is because I lost a lot of money with a bad stock market investment in Boeing
last year.

Ouptut:
Read[What are important aspects about real estate investment law?]
Read[Is there anything notable about rules for investemnts resulting from inheritance money?]
Read[What are some low-risk investment opportunities in public equities?]


Client Chat: Good afternoon Daniel. How did you get my number?

Output:
No Read operations necessary.

Now it's your turn. Be sure to use the memory API effectively by creating detailed and relevant Read queries.
"""

generative_model = GenerativeModel(
	GENERATIVE_MODEL,
	system_instruction=[SYSTEM_INSTRUCTION]
)


def simple_copilot_get_read_queries(input):
    INPUT_PROMPT = f"Client Chat: {input}"
    print(f"INPUT PROMPT: {INPUT_PROMPT}")
    response = generative_model.generate_content(
        [INPUT_PROMPT], # Input prompt
        generation_config=generation_config,
        stream=False,
    )

    generated_text = response.text
     
    print(f"LLM Response: {generated_text}")

    # filter for the queries
    return re.findall(r"Read\[(.*?)\]", generated_text)

def process_queries(input, collection_name, custom_settings = False):
    queries = simple_copilot_get_read_queries(input)

    if len(queries) == 0:
        return ["No Read operations necessary."]
    
    db = vector_store.LlamaIndexDB(collection_name)

    if db.get_count() == 0:
        return ["No information from the memory API was found."]

    llm = Vertex(model="gemini-1.5-flash-001", project=creds.project_id, credentials=creds, temperature=0.01)

    index = VectorStoreIndex.from_vector_store(db.vector_store, embed_model=db.embed_model, llm=llm)

    query_engine = index.as_query_engine(llm=llm)

    if custom_settings:
        # configure retriever
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=10,
        )

        # configure response synthesizer
        response_synthesizer = get_response_synthesizer()

        # assemble query engine
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
            llm=llm
        )

    insights = []
    
    for query in queries:
        response = query_engine.query(query)
        insights.append(response)
        print("-"*80)
        print(f"Query: {query}")
        print(f"Response: {response}")

    return insights
    