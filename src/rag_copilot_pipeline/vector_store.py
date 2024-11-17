import logging
import os
import uuid
from pathlib import Path

import chromadb
import pandas as pd
import preprocessing

# Vertex AI
import vertexai

# Setup
from google.oauth2 import service_account

# Llama-Index
from llama_index.core import (
    Document,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.vertex import VertexTextEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 768
INPUT_FOLDER = "sample-data"
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000
creds = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
)


vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)

logger = logging.getLogger(__name__)


class ChromaDB:
    def __init__(self, collection_name):
        """
        Initialize a ChromaDB instance.

        Args:
            collection_name (str): Name of the ChromaDB collection to interact with.

        Raises:
            ValueError: If the collection does not exist and cannot be created.

        Returns:
            None
        """
        self.embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
        self.client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        self.collection_name = collection_name

        # check if collection exists
        self.collection = ChromaDB.get_collection_by_name(self.collection_name)

        # create a new collection if collection_name does not alr exist
        if self.collection is None:
            logger.info(
                f"Collection '{collection_name}' did not exist. Creating new instance."
            )
            self.collection = self.client.create_collection(
                name=collection_name, metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new empty collection '{collection_name}'")

        logger.info("Collection:", self.collection)

    def write(self, text, metadata):
        """
        Write a single text document to the ChromaDB collection.

        Args:
            text (str): Text of the document to add.
            metadata (dict): Metadata associated with the document.

        Returns:
            None
        """
        emb = generate_text_embedding(text, self.embedding_model)

        self.collection.add(
            ids=[str(uuid.uuid4())],
            documents=[text],
            metadatas=metadata,
            embeddings=[emb],
        )

    def batch_write(self, text_list, metadatas, embeddings=None, batch_size=250):
        """
        Write multiple text documents to the ChromaDB collection.

        Args:
            text_list (list[str]): List of text documents to add.
            metadatas (list[dict]): List of metadata associated with the documents.

        Returns:
            None
        """
        if embeddings is None:
            embeddings = batch_generate_text_embeddings(text_list, self.embedding_model)

        for i in range(0, len(text_list), batch_size):
            self.collection.add(
                ids=[str(uuid.uuid4()) for _ in text_list[i : i + batch_size]],
                documents=text_list[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
            )

    def batch_write_from_df(self, df):
        """
        Write a pandas DataFrame to the ChromaDB collection.

        The DataFrame should have two columns - 'text' and 'metadata'. The 'text'
        column should contain the text of the
        documents to be added, and the 'metadata' column should contain the metadata
        associated with the documents.

        Args:
            df (pd.DataFrame): DataFrame containing documents and metadata to be written
            to the ChromaDB collection.

        Returns:
            None
        """

        text_chunks = df["text"].tolist()
        metadatas = df["metadata"].tolist()
        embeddings = df["embeddings"].tolist()

        self.batch_write(text_chunks, metadatas, embeddings)

    def batch_process_write(
        self,
        folder_path: Path,
        save: str = None,
        chunk_params: dict = {
            "method": "char-split",
            "chunk_size": 350,
            "chunk_overlap": 20,
        },
    ):
        """
        Process a folder of text files and write the chunks to the ChromaDB collection.

        The documents will be processed using the preprocessing.process_folder function,
        which will split the documents into chunks according to the chunk_params.

        Args:
            folder_path (Path): The path to the folder of text files to be processed
            and written to the ChromaDB collection.
            save (bool, optional): Whether to save the processed DataFrame to a file.
            Defaults to False.
            chunk_params (dict, optional): The parameters to use for chunking the
            documents. Defaults to {"method": "char-split", "chunk_size": 350,
            "chunk_overlap": 20}.

        Returns:
            None
        """
        df = preprocessing.process_folder(
            folder_path, save=save, chunk_params=chunk_params
        )
        self.batch_write_from_df(df)

        logger.info(
            f"Added {len(df)} documents to the collection {self.collection_name}"
        )

    def batch_write_from_df_records(self, file_path: Path):
        """
        Write the records in a JSON file to the ChromaDB collection.

        The JSON file should contain a pandas DataFrame with columns 'text' and
        'metadata'. The 'text' column should contain
        the text of the documents to be added, and the 'metadata' column should
        contain the metadata associated with the
        documents.

        Args:
            file_path (Path): The path to the JSON file to be read and written to the
            ChromaDB collection.

        Returns:
            None
        """
        data_df = pd.read_json(file_path)
        self.batch_write_from_df(data_df)
        logger.info(
            f"Added {len(data_df)} documents to the collection {self.collection_name}"
        )

    def read(self, query_text, top_k=5, filter=None, return_raw=False):
        # TODO: implement filter
        """
        Retrieve the top k documents from the ChromaDB collection that are most
          similar to the given query_text.

        Args:
            query_text (str): The text to be used to query the collection.
            top_k (int, optional): The number of results to return. Defaults
            to 5.
            filter (dict, optional): A dictionary of metadata key-value pairs
            to filter the results by. Defaults to None.

        Returns:
            List[chromadb.Document]: A list of the top k documents that match
            the query.
        """
        query_emb = generate_text_embedding(query_text, self.embedding_model)

        response = self.collection.query(query_embeddings=[query_emb], n_results=top_k)

        if return_raw:
            return response

        # return info on texts and similarity scores
        results = []

        for i in range(len(response["documents"][0])):
            results.append((response["documents"][0][i], response["distances"][0][i]))

        return results

    # Only call if you want to delete everything in the index
    # Can't be reversed
    def reset_collection(self):
        """
        Resets the ChromaDB index by deleting the collection and recreating it.
          This is a destructive operation and
        cannot be reversed.

        This method is used to clear the index and start fresh. Note that this
        method will delete all documents that are
        currently in the index.

        Returns:
            None
        """
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )
        logger.info("Reset index for {self.collection_name}")

    def get_count(self):
        return self.collection.count()

    # Static helper method, cannot be reversed
    def delete_collection(collection_name):
        """
        Deletes the specified ChromaDB collection.

        This is a destructive operation and cannot be reversed.

        Args:
            collection_name (str): The name of the collection to be deleted.

        Returns:
            None
        """
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        client.delete_collection(name=collection_name)
        logger.info(f"Deleted collection {collection_name}")

    # Function to check if a collection exists
    def get_collection_by_name(collection_name):
        """
        Retrieves the ChromaDB collection by name. If the collection
        does not exist, this method will return None.

        Args:
            collection_name (str): The name of the collection to be retrieved.

        Returns:
            chromadb.Collection or None: The collection if it exists, or
            None if it does not.
        """
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        try:
            # Attempt to retrieve the collection by name
            collection = client.get_collection(name=collection_name)
            return collection
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def delete_all_data():
        """
        Resets the ChromaDB index by deleting all collections and recreating them.
        This is a destructive operation and
        cannot be reversed.

        This method is used to clear the index and start fresh. Note that this method
        will delete all documents that are
        currently in the index.

        Returns:
            None
        """
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        collections = client.list_collections()
        for idx, collection in enumerate(collections):
            client.delete_collection(name=collection.name)
        logger.info("Deleted all collections")


# TODO: develop similar implementation as ChromaDB but utilizes LlamaIndex
# as a vector store
class LlamaIndexDB:
    def __init__(self, collection_name):
        """
        Initialize a LlamaIndexDB instance.

        Args:
            collection_name (str): The name of the collection to interact with.

        Returns:
            None
        """
        self.chroma_client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            collection_name
        )
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)

        self.embed_model = VertexTextEmbedding(
            model_name=EMBEDDING_MODEL,
            project=GCP_PROJECT,
            location=GCP_LOCATION,
            credentials=creds,
        )

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

    def load_from_dir(self, dir_path, chunk_params=None):
        documents = SimpleDirectoryReader(dir_path).load_data()

        if chunk_params is None:
            VectorStoreIndex.from_documents(
                documents,
                embed_model=self.embed_model,
                storage_context=self.storage_context,
            )
        else:
            text_splitter = SentenceSplitter(
                chunk_size=chunk_params["chunk_size"],
                chunk_overlap=chunk_params["chunk_overlap"],
            )
            VectorStoreIndex.from_documents(
                documents,
                embed_model=self.embed_model,
                storage_context=self.storage_context,
                transformations=[text_splitter],
            )

    def write(self, text):
        """
        Write a single text document to the LlamaIndexDB.

        Args:
            text (str): Text of the document to add.

        Returns:
            None
        """
        docs = [Document(text=text)]
        VectorStoreIndex.from_documents(
            docs, embed_model=self.embed_model, storage_context=self.storage_context
        )

    def read(self, query_text, top_k=5, reutrn_raw=False):
        retriever = VectorIndexRetriever(
            index=VectorStoreIndex.from_vector_store(
                self.vector_store, embed_model=self.embed_model
            ),
            similarity_top_k=top_k,
        )

        results = retriever.retrieve(query_text)

        if reutrn_raw:
            return results

        # return info on texts and similarity scores
        return [(res.text, res.score) for res in results]

    def get_count(self):
        return self.chroma_collection.count()

    def delete_collection(collection_name):
        """
        Deletes the specified ChromaDB collection.

        This is a destructive operation and cannot be reversed.

        Args:
            collection_name (str): The name of the collection to be deleted.

        Returns:
            None
        """
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        client.delete_collection(name=collection_name)
        logger.info(f"Deleted collection {collection_name}")

    def delete_all_data():
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        collections = client.list_collections()
        for idx, collection in enumerate(collections):
            client.delete_collection(name=collection.name)
        logger.info("Deleted all collections")


def generate_text_embedding(query, embedding_model):
    query_embedding_inputs = [
        TextEmbeddingInput(task_type="RETRIEVAL_DOCUMENT", text=query)
    ]
    kwargs = (
        dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
    )
    embeddings = embedding_model.get_embeddings(query_embedding_inputs, **kwargs)
    return embeddings[0].values


def batch_generate_text_embeddings(
    chunks, embedding_model, dimensionality: int = 768, batch_size=250
):
    # Max batch size is 250 for Vertex AI
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in batch]
        kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
        embeddings = embedding_model.get_embeddings(inputs, **kwargs)
        all_embeddings.extend([embedding.values for embedding in embeddings])

    return all_embeddings


def main():
    # Create a new instance of ChromaDB
    collection_name = "test_collection"
    chroma_db = ChromaDB(collection_name)
    print("Created instance of vector store")
    chroma_db.reset_collection()

    sample_texts = [
        "The sky is blue.",
        "The sun is bright.",
        "The moon is full tonight.",
        "The stars are shining.",
        "The rain is pouring down.",
    ]

    sample_metadata = [
        {"source": "sentence1"},
        {"source": "sentence2"},
        {"source": "sentence3"},
        {"source": "sentence4"},
        {"source": "sentence5"},
    ]

    # Sample text and metadata for batch write
    batch_texts = [
        "This is batch text 1.",
        "This is batch text 2.",
        "This is batch text 3.",
        "This is batch text 4.",
        "This is batch text 5.",
        "This is batch text 6.",
        "This is batch text 7.",
        "This is batch text 8.",
        "This is batch text 9.",
        "This is batch text 10.",
        "This is batch text 11.",
        "This is batch text 12.",
        "This is batch text 13.",
        "This is batch text 14.",
        "This is batch text 15.",
    ]

    batch_metadata = [{"source": "batch_data"}] * len(batch_texts)

    # Perform five individual writes
    for i in range(5):
        text = sample_texts[i]
        metadata = sample_metadata[i]
        chroma_db.write(text, metadata)
        print(f"Added document {i+1}: {text}")

    # Perform batch write with 15 text strings
    chroma_db.batch_write(batch_texts, batch_metadata)
    print("Added batch of 15 documents.")

    # Perform one read query
    query_text = "The sky is blue."
    print(f"\nQuerying with: '{query_text}'")
    results = chroma_db.read(query_text, top_k=10)

    print("Query Results:")
    for result in results:
        print(result)

    # Delete the collection
    print(f"\nDeleting collection: {collection_name}")
    ChromaDB.delete_collection(collection_name)
    print(f"Collection '{collection_name}' deleted.")


if __name__ == "__main__":
    main()
