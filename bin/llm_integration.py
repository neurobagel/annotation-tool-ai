import pandas as pd
from typing import Dict


def convert_tsv_to_dict(tsv_file: str) -> Dict[str, str]:
    # read tsv
    df = pd.read_csv(tsv_file, delimiter="\t")

    # convert each column to a string
    column_strings = {
        col: f"{col} {' '.join(df[col].astype(str).str.strip())}"
        for col in df.columns
    }

    return column_strings


if __name__ == "__main__":

    file_path = "participants.tsv"

    columns_dict = convert_tsv_to_dict(file_path)
    print(columns_dict)

    headers = list(columns_dict.keys())
    print(headers)
