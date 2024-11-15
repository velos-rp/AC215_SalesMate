from finetuning_pipeline.utils import generate_train_test
import pytest
import pandas as pd

def test_generate_train_test():
    df = pd.read_csv("tests/test_files/processed_calls_v1.csv")
    data_train, data_test = generate_train_test(df)
    assert len(data_train) == 1000
    assert 'contents' in data_train[0]

