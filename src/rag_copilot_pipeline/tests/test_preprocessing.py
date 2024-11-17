import preprocessing


def test_chunk_text():
    text = "This is a test sentence."
    chunks = preprocessing.chunk_text(text)
    assert len(chunks) == 1


def test_chunk_test():
    # load text from file tests/test_files/jungle.txt
    f = open("tests/test_files/jungle.txt", "r")
    text = f.read()
    chunks = preprocessing.chunk_text(text)

    assert len(chunks) > 0

    for chunk in chunks:
        # assert type to string
        assert isinstance(chunk, str)
