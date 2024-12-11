import pandas as pd
from data_processing import process_pipeline
from utils import generate_train_test


def test_generate_train_test():
    df = pd.read_csv("tests/test_files/processed_calls_v1.csv")
    data_train, data_test = generate_train_test(df)
    assert len(data_train) == 1000
    assert "contents" in data_train[0]


def test_processing_pipeline():
    test_path = "data/data_extract_calls_pt_test.csv"
    output_path = "gs://test-llm-rp/sample-calls/test_"
    process_pipeline(test_path, output_path)
