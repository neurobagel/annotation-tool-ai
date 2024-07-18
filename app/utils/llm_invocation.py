from typing import Dict, Optional

from app.factories.llm_factories.factory_context import FactoryContext
from app.factories.llm_factories.llm_factory_manager import FactoryLLM


def llm_invocation(result_dict: Dict[str, str]) -> Optional[Dict[str, str]]:
    key, value = list(result_dict.items())[0]
    factories = FactoryLLM.get_factories()
    context = FactoryContext(factories)
    return context.create(key, value)
