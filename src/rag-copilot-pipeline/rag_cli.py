import argparse
import logging
from pathlib import Path
from pprint import pprint

import chromadb
import preprocessing
import vector_store

logger = logging.getLogger(__name__)

# Setup
INPUT_FOLDER = "sample-data"
OUTPUT_FOLDER = "outputs"
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000

CHUNK_CHOICES = ["char-split", "recursive-split", "semantic-split"]


def main(args):

    if args.command == "process":
        chunk_params = {
            "method": args.method,
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
        }
        preprocessing.process_folder(args.input_dir, args.output, chunk_params)
        logger.info(f"Processed {args.input_dir} and saved to output folder")
    elif args.command == "load":
        db = vector_store.ChromaDB(args.collection_name)
        db.batch_write_from_df_records(args.input_file)
    elif args.command == "process-load":
        chunk_params = {
            "method": args.method,
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
        }
        db = vector_store.ChromaDB(args.collection_name)
        db.batch_process_write(args.input_dir, args.output, chunk_params)
    elif args.command == "query":
        db = vector_store.ChromaDB(args.collection_name)
        res = db.read(args.query, top_k=args.top_k)
        pprint(res)
    elif args.command == "delete-collection":
        vector_store.ChromaDB.delete_collection(args.collection_name)
    elif args.command == "reset":
        vector_store.ChromaDB.delete_all_data()
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

    # subparser for the 'process' command
    process_parser = subparsers.add_parser(
        "process", help="Process raw text/pdf files and save them to a json file"
    )
    process_parser.add_argument(
        "--input-dir", type=Path, help="Input directory", default=Path(INPUT_FOLDER)
    )
    process_parser.add_argument(
        "--output", type=str, default="base", help="Output file"
    )
    process_parser.add_argument(
        "--method",
        type=str,
        choices=CHUNK_CHOICES,
        default="char-split",
        help="Chunking method",
    )
    process_parser.add_argument(
        "--chunk-size", type=int, default=350, help="Chunk size"
    )
    process_parser.add_argument(
        "--chunk-overlap", type=int, default=20, help="Chunk overlap"
    )

    # subparser for the 'load' command
    load_parser = subparsers.add_parser(
        "load", help="Load text into vector store from a json file"
    )
    load_parser.add_argument(
        "--input-file", type=Path, help="Input file", required=True
    )
    load_parser.add_argument(
        "--collection-name", type=str, help="Collection name", required=True
    )

    # subparser for the 'process-load' command
    process_load_parser = subparsers.add_parser(
        "process-load",
        help="Process and load text into vector store all in one operation",
    )
    process_load_parser.add_argument(
        "--input-dir", type=Path, help="Input directory", default=Path(INPUT_FOLDER)
    )
    process_load_parser.add_argument(
        "--collection-name", type=str, help="Collection name", required=True
    )
    process_load_parser.add_argument(
        "--output", type=str, default="base", help="Output file"
    )
    process_load_parser.add_argument(
        "--method",
        type=str,
        choices=CHUNK_CHOICES,
        default="char-split",
        help="Chunking method",
    )
    process_load_parser.add_argument(
        "--chunk-size", type=int, default=350, help="Chunk size"
    )
    process_load_parser.add_argument(
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
