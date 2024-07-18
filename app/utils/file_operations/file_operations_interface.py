from abc import ABC, abstractmethod
from typing import Any, Dict

# src/utils/file_operations_interface.py


class FileOperations(ABC):
    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def get_column_strings(self) -> Dict[str, str]:
        pass
