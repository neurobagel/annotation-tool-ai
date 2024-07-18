from typing import Dict, Optional
from app.factories.llm_factories.llm_factory_interface import LLMFactory
from langchain_community.chat_models import ChatOllama

from app.factories.llm_factories.promptTemplate import GeneralPrompt
from app.utils.data_transformers import AgeFormat, SexLevel


class FactoryGeneral(LLMFactory):
    def create(self, key: str, value: str) -> Optional[Dict[str, str]]:
        llm = ChatOllama(model="gemma")
        chainGeneral = GeneralPrompt | llm
        llm_response = chainGeneral.invoke({"column": key, "content": value})
        r = str(llm_response)
        if "Participant_IDs" in r:
            output = {"TermURL": "nb:ParticipantID"}
        elif "Session_IDs" in r:
            output = {"TermURL": "nb:Session"}
        elif "Sex" in r:
            output = SexLevel({key: value}, r, key)
        elif "Age" in r:
            output = AgeFormat({key: value}, r, key)
        else:
            output = None
        return output
