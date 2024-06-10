import pandas as pd
import json
from typing import List


def tsv_to_json(tsv_file: str, json_file: str) -> None:
    # Read the TSV file into a DataFrame
    df = pd.read_csv(tsv_file, delimiter="\t")

    # Get the column names
    columns: List[str] = df.columns.tolist()


    # Create a dictionary with column names as keys and empty strings as values
    data = {column: "" for column in columns}

    # Write the dictionary to a JSON file

    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)


# Example usage
tsv_file = "input.tsv"
json_file = "output.json"

tsv_to_json(tsv_file, json_file)
