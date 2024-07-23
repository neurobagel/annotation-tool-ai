from typing import Any, Dict, Optional, Union
import json
from langchain_community.chat_models import ChatOllama
from categorization.promptTemplate import (
    GeneralPrompt,
    AssessmentToolPrompt,
    DiagnosisPrompt,
)
from categorization.llm_helper import SexLevel, AgeFormat


def Diagnosis(
    key: str, value: str
) -> Optional[Union[Dict[str, str], Dict[str, Any]]]:
    llm = ChatOllama(model="gemma")
    chainDiagnosis = DiagnosisPrompt | llm
    llm_response_Diagnosis = chainDiagnosis.invoke(
        {"column": key, "content": value}
    )
    reply = str(llm_response_Diagnosis)
    print(reply)

    if "yes" in reply.lower():
        values = value.split()
        unique_values = list(set(values[1:]))

        # Create dictionary for Levels
        levels_dict = {val: "" for val in unique_values}

        # Create the output dictionary
        output = {"TermURL": "nb:Diagnosis", "Levels": levels_dict}

        print(json.dumps(output))
        return output
    else:
        return AssessmentTool(key, value)


def AssessmentTool(key: str, value: str) -> Optional[Dict[str, str]]:
    llm = ChatOllama(model="gemma")
    questionAssessmentTool = f"Is the {key}:{value} an assessment tool"
    chainAssessmentTool = AssessmentToolPrompt | llm
    llm_response_Assessment = chainAssessmentTool.invoke(
        {"column": key, "content": value, "question": questionAssessmentTool}
    )
    reply = str(llm_response_Assessment)
    if "yes" in reply.lower():
        output = {"TermURL": "nb:Assessment"}
        print(json.dumps(output))
        return output
    else:
        print(
            "The column does not fit any entity in the current Neurobagel data model. "  # noqa: E501
            "Please be patient as we are working on expanding the data model for more entities :)"  # noqa: E501
        )
        return None


def llm_diagnosis_assessment(key: str, value: str) -> Optional[Dict[str, str]]:
    resultDiagnosis = Diagnosis(key, value)
    if resultDiagnosis:
        return resultDiagnosis
    else:
        return AssessmentTool(key, value)


def llm_invocation(result_dict: Dict[str, str]) -> Optional[Dict[str, str]]:
    output: Union[Dict[str, str], None]
    llm = ChatOllama(model="gemma")
    chainGeneral = GeneralPrompt | llm
    key, value = list(result_dict.items())[0]
    llm_response = chainGeneral.invoke({"column": key, "content": value})
    r = str(llm_response)
    if "Participant_IDs" in r:
        output = {"TermURL": "nb:ParticipantID"}
    elif "Session_IDs" in r:
        output = {"TermURL": "nb:Session"}
    elif "Sex" in r:
        output = SexLevel(result_dict, key)
    elif "Age" in r:
        output = AgeFormat(result_dict, key)
    else:
        output = llm_diagnosis_assessment(key, value)

    return output
