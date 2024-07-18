# src/utils/update_json_file.py
import json
from typing import Any, Dict, Union, List

from app.utils.file_operations.file_operations_interface import FileOperations


class UpdateJSONFile(FileOperations):
    def execute(
        self, annotations_instance: Any, file_path: str, target_key: str
    ) -> None:
        annotations_json: str = annotations_instance.model_dump_json()

        try:
            with open(file_path, "r") as file:
                file_data: Dict[str, Any] = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            file_data = {}

        annotations_data: Union[Dict[str, Any], List[Any], Any] = json.loads(
            annotations_json
        )
        annotations_data = self.remove_none_values(annotations_data)

        if isinstance(annotations_data, dict):
            file_data[target_key] = annotations_data
        else:
            raise TypeError(
                f"Unexpected annotations_data type: {type(annotations_data)}"
            )

        with open(file_path, "w") as file:
            json.dump(file_data, file, indent=2)

    def remove_none_values(
        self, data: Union[Dict[str, Any], List[Any], Any]
    ) -> Union[Dict[str, Any], List[Any], Any]:
        if isinstance(data, dict):
            return {
                k: self.remove_none_values(v)
                for k, v in data.items()
                if v is not None
            }
        elif isinstance(data, list):
            return [
                self.remove_none_values(item)
                for item in data
                if item is not None
            ]
        else:
            return data
