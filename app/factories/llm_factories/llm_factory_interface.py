# Factory Interface
from typing import Dict, Optional


class LLMFactory:
    @abstractmethod
    def create(self, key: str, value: str) -> Optional[Dict[str, str]]:
        raise NotImplementedError("Subclasses must implement create method")
