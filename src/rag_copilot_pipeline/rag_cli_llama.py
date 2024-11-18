import argparse
import logging
from pathlib import Path
from pprint import pprint

import chromadb
import vector_store

logger = logging.getLogger(__name__)

# Setup
INPUT_FOLDER = "sample-data"
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000

CHUNK_CHOICES = ["char-split", "recursive-split", "semantic-split"]


def main(args):

    if args.command == "load":
        chunk_params = {
            "method": args.method,
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
        }
        db = vector_store.LlamaIndexDB(args.collection_name)
        db.load_from_dir(args.input_dir, chunk_params)
        pprint(f"Loaded {args.input_dir} into vector store {args.collection_name}")

    elif args.command == "query":
        db = vector_store.LlamaIndexDB(args.collection_name)
        res = db.read(args.query, top_k=args.top_k)
        pprint(res)
    elif args.command == "delete-collection":
        vector_store.LlamaIndexDB.delete_collection(args.collection_name)
    elif args.command == "reset":
        vector_store.LlamaIndexDB.delete_all_data()
    elif args.command == "info":
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        # list collections and their metadata
        collections = client.list_collections()
        print(f"There are {len(collections)} collection(s) in the database")
        for idx, collection in enumerate(collections):
            print(f"{idx} - Name: {collection.name}, Count: {collection.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # add subparser
    subparsers = parser.add_subparsers(help="subcommand help", dest="command")

    # subparser for the 'load' command

    load_parser = subparsers.add_parser(
        "load", help="Process raw text/pdf files and save them to a json file"
    )

    load_parser.add_argument(
        "--collection-name", type=str, help="Collection name", required=True
    )

    load_parser.add_argument(
        "--input-dir", type=Path, help="Input directory", default=Path(INPUT_FOLDER)
    )

    load_parser.add_argument(
        "--method",
        type=str,
        choices=CHUNK_CHOICES,
        default="recursive-split",
        help="Chunking method",
    )
    load_parser.add_argument("--chunk-size", type=int, default=350, help="Chunk size")
    load_parser.add_argument(
        "--chunk-overlap", type=int, default=20, help="Chunk overlap"
    )

    # subparser for the 'query' command
    query_parser = subparsers.add_parser("query", help="Query vector store")
    query_parser.add_argument("query", type=str, help="Query")
    query_parser.add_argument(
        "--collection-name", type=str, help="Collection name", required=True
    )
    query_parser.add_argument("--top-k", type=int, default=5, help="Top k results")

    # subparser for the 'delete collection' command
    delete_collection_parser = subparsers.add_parser(
        "delete-collection", help="Delete collection"
    )
    delete_collection_parser.add_argument(
        "collection_name", type=str, help="Collection name"
    )

    # subparser for the 'reset' command
    reset_parser = subparsers.add_parser("reset", help="Reset vector store")

    # subparser for the 'info' command
    info_parser = subparsers.add_parser(
        "info", help="Get information about the vector store"
    )

    # detect which subcommand is used
    args = parser.parse_args()

    main(args)
