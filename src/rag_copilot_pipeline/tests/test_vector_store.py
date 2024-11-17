import vector_store


def test_vector_store_manual():
    collection_name = "test_collection"
    chroma_db = vector_store.ChromaDB(collection_name)

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
    vector_store.ChromaDB.delete_collection(collection_name)
    print(f"Collection '{collection_name}' deleted.")
