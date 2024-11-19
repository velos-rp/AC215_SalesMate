import argparse
import ast
import io
import json
import os
from pathlib import Path
from pprint import pprint

import pandas as pd

# from google.cloud import translate
from google.cloud import storage, translate_v2
from tqdm import tqdm
from utils import generate_train_test

tqdm.pandas()

GCP_PROJECT = os.environ["GCP_PROJECT"]
PARENT = f"projects/{GCP_PROJECT}"
OUTPUT_FOLDER = "output"
KEYS_TO_TRANSLATE = ["message", "summary", "title", "type"]

RAW_EXTRACT_BLOB_NAME = "data/extract_calls_pt.csv"
OUTPUT_ROOT = "gs://test-llm-rp/sample-calls/sample_1k_"  #
BUCKET_NAME = "ac215_salesmate"

translate_client = translate_v2.Client()


def translate_textV2(text: str, target, source=None) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(
        text, target_language=target, source_language=source
    )

    return result["translatedText"]


translation_cache = {}


def translate_keys_in_structure(
    data, keys_to_translate, src_lang="pt", target_lang="en"
):
    # If the data is a dictionary
    if isinstance(data, dict):
        for key, value in data.items():
            # If the key is one of the ones we want to translate
            if key in keys_to_translate and isinstance(value, str):
                cache_key = (key, value)

                if cache_key in translation_cache:
                    # Use the cached translation
                    data[key] = translation_cache[cache_key]
                else:
                    # Translate the text and replace the value
                    translated_txt = translate_textV2(value, target_lang, src_lang)
                    data[key] = translated_txt
                    translation_cache[cache_key] = translated_txt
            # Recurse into nested dictionaries/lists
            elif isinstance(value, (dict, list)):
                translate_keys_in_structure(
                    value, keys_to_translate, src_lang, target_lang
                )

    # If the data is a list
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, (dict, list)):
                # Recurse into nested structures
                translate_keys_in_structure(
                    item, keys_to_translate, src_lang, target_lang
                )


def col_translation(data_str, keys_to_translate):
    data = ast.literal_eval(data_str)

    # functions will apply the translation to the corresponding keys in place
    translate_keys_in_structure(data, keys_to_translate)

    return data


def translate_df(df):
    df["feedbacks_translated"] = df["feedbacks"].progress_apply(
        col_translation, keys_to_translate=KEYS_TO_TRANSLATE
    )
    df["transcription_translated"] = df["transcription"].progress_apply(
        col_translation, keys_to_translate=KEYS_TO_TRANSLATE
    )
    df["overview_translated"] = df["overview"].progress_apply(
        col_translation, keys_to_translate=KEYS_TO_TRANSLATE
    )
    df["positive_translated"] = df["positive"].progress_apply(
        col_translation, keys_to_translate=KEYS_TO_TRANSLATE
    )
    df["negative_translated"] = df["negative"].progress_apply(
        col_translation, keys_to_translate=KEYS_TO_TRANSLATE
    )

    return df


def save_jsonl_to_gcs(data, bucket_name, destination_blob_name):
    """Saves a list of dictionaries as JSONL format to GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Convert data to JSONL format
    jsonl_data = "\n".join(json.dumps(entry) for entry in data)

    # Upload JSONL to GCS
    blob.upload_from_string(jsonl_data, content_type="application/jsonl")
    print(f"Data saved to {destination_blob_name} in bucket {bucket_name}.")


def process_pipeline(data_path=RAW_EXTRACT_BLOB_NAME, output_path=OUTPUT_ROOT):

    storage_client = storage.Client()
    # Get the bucket
    bucket = storage_client.bucket(BUCKET_NAME)
    # Define the blob (object in the bucket)
    blob = bucket.blob(data_path)
    # Download the file
    data = blob.download_as_text()
    df = pd.read_csv(io.StringIO(data))
    df_translated = translate_df(df)

    df_translated_transcription = df_translated[["transcription_translated"]]

    data_train, data_test = generate_train_test(df_translated_transcription)
    # Save the data as JSONL

    output_train_blob_name = output_path + "train.jsonl"
    output_test_blob_name = output_path + "test.jsonl"

    # Save train and test data to GCS
    save_jsonl_to_gcs(data_train, BUCKET_NAME, output_train_blob_name)
    save_jsonl_to_gcs(data_test, BUCKET_NAME, output_test_blob_name)
