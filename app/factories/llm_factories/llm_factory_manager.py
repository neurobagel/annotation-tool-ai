from typing import List
from app.factories.llm_factories.concrete_factory_assessmentTool import (
    FactoryAssessmentTool,
)
from app.factories.llm_factories.concrete_factory_diagnosis import (
    FactoryDiagnosis,
)
from app.factories.llm_factories.concrete_factory_general import FactoryGeneral
from app.factories.llm_factories.llm_factory_interface import LLMFactory


class FactoryLLM:
    @staticmethod
    def get_factories() -> List[LLMFactory]:
        # Return the sequence of factories to be used
        return [FactoryGeneral(), FactoryDiagnosis(), FactoryAssessmentTool()]
