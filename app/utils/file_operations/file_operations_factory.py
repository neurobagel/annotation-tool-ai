from typing import Type, Dict
from app.utils.file_operations.convert_tsv_to_dict import ConvertTSVToDict
from app.utils.file_operations.tsv_to_json import TSVToJSON
from app.utils.file_operations.update_json_file import UpdateJSONFile
from app.utils.file_operations.file_operations_interface import FileOperations


class FileOperationsFactory:
    @staticmethod
    def get_file_operation(operation_type: str) -> Type[FileOperations]:
        operations: Dict[str, Type[FileOperations]] = {
            "convert_tsv_to_dict": ConvertTSVToDict,
            "tsv_to_json": TSVToJSON,
            "update_json_file": UpdateJSONFile,
        }
        if operation_type in operations:
            return operations[operation_type]
        raise ValueError(f"Unknown operation type: {operation_type}")
