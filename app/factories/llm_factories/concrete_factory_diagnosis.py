import json
from typing import Dict, Optional
from app.factories.llm_factories.llm_factory_interface import LLMFactory
from langchain_community.chat_models import ChatOllama

from app.factories.llm_factories.promptTemplate import DiagnosisPrompt


class FactoryDiagnosis(LLMFactory):
    def create(self, key: str, value: str) -> Optional[Dict[str, str]]:
        llm = ChatOllama(model="gemma")
        chainDiagnosis = DiagnosisPrompt | llm
        llm_response_Diagnosis = chainDiagnosis.invoke(
            {"column": key, "content": value}
        )
        reply = str(llm_response_Diagnosis)
        if "yes" in reply.lower():
            output = {"TermURL": "nb:Diagnosis"}
            print(json.dumps(output))
            return output
        else:
            print("next")
            return None
