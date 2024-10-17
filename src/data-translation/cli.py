import pandas as pd
import json
from pprint import pprint
import ast
from google.cloud import translate
from google.cloud import translate_v2
import os
from tqdm import tqdm
import argparse
from pathlib import Path

tqdm.pandas()

GCP_PROJECT = os.environ["GCP_PROJECT"]
PARENT = f"projects/{GCP_PROJECT}"
OUTPUT_FOLDER = "output"
KEYS_TO_TRANSLATE = ["message", "summary", "title", "type"]


translate_client = translate_v2.Client()

def translate_textV2(text: str, target, source = None) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target, source_language=source)

    return result["translatedText"]


translation_cache = {}

def translate_keys_in_structure(data, keys_to_translate, src_lang = 'pt', target_lang='en'):
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
                translate_keys_in_structure(value, keys_to_translate, src_lang, target_lang)

    # If the data is a list
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, (dict, list)):
                # Recurse into nested structures
                translate_keys_in_structure(item, keys_to_translate, src_lang, target_lang)

def col_translation(data_str, keys_to_translate):
    data = ast.literal_eval(data_str)

    # functions will apply the translation to the corresponding keys in place
    translate_keys_in_structure(data, keys_to_translate)

    return data


def translate_df(df):
    df['feedbacks_translated'] = df['feedbacks'].progress_apply(col_translation, keys_to_translate = KEYS_TO_TRANSLATE)
    df['transcription_translated'] = df['transcription'].progress_apply(col_translation, keys_to_translate = KEYS_TO_TRANSLATE)
    df['overview_translated'] = df['overview'].progress_apply(col_translation, keys_to_translate = KEYS_TO_TRANSLATE)
    df['positive_translated'] = df['positive'].progress_apply(col_translation, keys_to_translate = KEYS_TO_TRANSLATE)
    df['negative_translated'] = df['negative'].progress_apply(col_translation, keys_to_translate = KEYS_TO_TRANSLATE)


    return df


def main(args):
    df = pd.read_csv(args.input)

    df_translated = translate_df(df)

    file_name = args.input.name.split(".")[0]

    df_translated.to_csv(f"{OUTPUT_FOLDER}/{file_name}_translated.csv", index=False)


if __name__ == "__main__":
    # Generate the inputs arguments parser
    parser = argparse.ArgumentParser(description="CLI for dataset translation")

    parser.add_argument(
        "input",
        type=Path,
        help="Input file path",
    )

    args = parser.parse_args()

    main(args)