import pandas as pd
from typing import Dict, Any
from app.utils.file_operations.file_operations_interface import FileOperations


class ConvertTSVToDict(FileOperations):
    def __init__(self):  # type: ignore
        super().__init__()
        self.column_strings: Dict[str, str] = {}

    def execute(self, *args: Any, **kwargs: Any) -> None:
        if len(args) != 1:
            raise ValueError(
                "execute method requires exactly one argument (tsv_file)"
            )

        tsv_file: str = args[0]

        try:
            df = pd.read_csv(tsv_file, delimiter="\t")
            self.column_strings = {
                col: f"{col} {' '.join(df[col].astype(str).str.strip())}"
                for col in df.columns
            }
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{tsv_file}' not found")

    def get_column_strings(self) -> Dict[str, str]:
        return self.column_strings
