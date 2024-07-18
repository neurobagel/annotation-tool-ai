from abc import ABC, abstractmethod
from typing import Any

# src/utils/file_operations_interface.py


class FileOperations(ABC):
    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> None:
        pass
