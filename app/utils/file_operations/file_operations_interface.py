from abc import ABC, abstractmethod
from typing import Any


class FileOperations(ABC):
    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> None:
        pass
