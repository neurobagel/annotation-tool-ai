import json
from typing import Dict, Optional
from app.factories.llm_factories.llm_factory_interface import LLMFactory
from langchain_community.chat_models import ChatOllama

from app.factories.llm_factories.promptTemplate import AssessmentToolPrompt


class FactoryAssessmentTool(LLMFactory):
    def create(self, key: str, value: str) -> Optional[Dict[str, str]]:
        llm = ChatOllama(model="gemma")
        questionAssessmentTool = f"Is the {key}:{value} an assessment tool?"
        chainAssessmentTool = AssessmentToolPrompt | llm
        llm_response_Assessment = chainAssessmentTool.invoke(
            {
                "column": key,
                "content": value,
                "question": questionAssessmentTool,
            }
        )
        reply = str(llm_response_Assessment)
        print(reply)
        if "yes" in reply.lower():
            output = {"TermURL": "nb:Assessment"}
            print(json.dumps(output))
            return output
        else:
            print(f"{key}: {value} not in data model as an assessment tool")
            return None
