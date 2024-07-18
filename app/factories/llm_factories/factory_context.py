from typing import Dict, List, Optional
from app.factories.llm_factories.llm_factory_interface import LLMFactory


class FactoryContext:
    def __init__(self, factories: List[LLMFactory]):
        self.factories = factories

    def create(self, key: str, value: str) -> Optional[Dict[str, str]]:
        for factory in self.factories:
            result = factory.create(key, value)
            if result:
                return result
        print(
            f"{key} does not match any entity in the current Neurobagel data model."  # noqa: E501
        )
        return None
