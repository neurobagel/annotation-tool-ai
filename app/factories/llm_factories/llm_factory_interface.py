# Factory Interface
from typing import Dict, Optional


class LLMFactory:
    def create(self, key: str, value: str) -> Optional[Dict[str, str]]:
        raise NotImplementedError
