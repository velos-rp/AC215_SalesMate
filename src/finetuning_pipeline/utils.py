import ast
import random

import pandas as pd


def generate_train_test(df):
    data = []
    for _, row in df.iterrows():
        # Parse the string as a list of dictionaries
        if type(row) == str:
            conversation = ast.literal_eval(row["transcription_translated"])
        else:
            conversation = row["transcription_translated"]

        for i in range(0, len(conversation), 2):
            if i + 1 < len(conversation):
                user_part = (
                    conversation[i + 1].get("message", "").replace("user:", "").strip()
                )
                bot_part = (
                    conversation[i]
                    .get("message", "")
                    .replace("bot:", "")
                    .replace("bot", "model")
                    .strip()
                )

                data.append(
                    {
                        "contents": [
                            {"role": "user", "parts": [{"text": user_part}]},
                            {"role": "model", "parts": [{"text": bot_part}]},
                        ]
                    }
                )

    n_size = 1000
    if n_size > len(data):
        n_size = int(len(data) / 2)
    data_train = random.sample(data, n_size)
    data_test = random.sample(data, n_size)
    return data_train, data_test
