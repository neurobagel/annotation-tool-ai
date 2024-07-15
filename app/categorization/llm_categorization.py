from typing import Dict, Optional, Union
import json
from langchain_community.chat_models import ChatOllama
from promptTemplate import(
prompt,
Aprompt,
Dprompt)
from llm_helper import (
SexLevel, 
AgeFormat)


def Diagnosis(key: str, value: str) -> Optional[Dict[str, str]]:
    llm = ChatOllama(model="gemma")
    chainDiagnosis = DiagnosisPrompt | llm
    llm_response2 = chainDiagnosis.invoke({"column": key, "content": value})
    reply = str(llm_response2)
    if "yes" in reply.lower():
        output = {"TermURL": "nb:Diagnosis"}
        print(json.dumps(output))
        return output
    else:
        print("next")
        return None


def AssessmentTool(key: str, value: str) -> Optional[Dict[str, str]]:
    llm = ChatOllama(model="gemma")
    questionAssessmentTool = f"Is the {key}:{value} an assessment tool"
    chain = Aprompt | llm
    llm_response2 = chain.invoke(
        {"column": key, "content": value, "question": questionA}
    )
    reply = str(llm_response2)
    if "yes" in reply.lower():
        output = {"TermURL": "nb:Assessment"}
        print(json.dumps(output))
        return output
    else:
        print(key)
        print("not in data model")
        return None


def llm_invocation2(key: str, value: str) -> Optional[Dict[str, str]]:
    result_d = D(key, value)
    if result_d:
        return result_d
    else:
        return A(key, value)


def llm_invocation1(result_dict: Dict[str, str]) -> Optional[Dict[str, str]]:
    output: Union[Dict[str, str], None]
    llm = ChatOllama(model="gemma")
    chain = prompt | llm
    key, value = list(result_dict.items())[0]
    llm_response = chain.invoke({"column": key, "content": value})
    r = str(llm_response)
    if "Participant_IDs" in r:
        output = {"TermURL": "nb:ParticipantID"}
    elif "Session_IDs" in r:
        output = {"TermURL": "nb:Session"}
    elif "Sex" in r:
        output = SexLevel(result_dict, r, key)
    elif "Age" in r:
        output = AgeFormat(result_dict, r, key)
    else:
        output = llm_invocation2(key, value)

    return output
