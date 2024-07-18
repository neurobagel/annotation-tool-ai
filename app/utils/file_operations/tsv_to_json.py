# src/utils/tsv_to_json.py
import pandas as pd
import json
from typing import List, Dict

from app.utils.file_operations.file_operations_interface import FileOperations


class TSVToJSON(FileOperations):
    def execute(self, tsv_file: str, json_file: str) -> None:
        df = pd.read_csv(tsv_file, delimiter="\t")
        columns: List[str] = df.columns.tolist()
        data: Dict[str, str] = {column: "" for column in columns}
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)
