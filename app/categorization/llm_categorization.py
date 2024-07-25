from typing import Any, Dict, List, Optional, Union
import json
import re
from langchain_community.chat_models import ChatOllama
from categorization.promptTemplate import (
    AssessmentLevelPrompt,
    GeneralPrompt,
    AssessmentToolPrompt,
    DiagnosisPrompt,
)
from categorization.llm_helper import SexLevel, AgeFormat
from categorization.fetchlevels import get_assessment_label


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
        tool_term = get_assessment_label(key)
        if isinstance(tool_term, list) and len(tool_term) == 1:
            tool_term = tool_term[0]
        elif isinstance(tool_term, list) and len(tool_term) > 1:
            tool_term = assessment_level_decision(tool_term)
        else:
            tool_term = "Not found"
        output = {"TermURL": "nb:Assessment", "AssessmentTool": tool_term}
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


def assessment_level_decision(possible_tool_terms: List[str]) -> str:
    llm = ChatOllama(model="gemma")
    chain_assessment_level = AssessmentLevelPrompt | llm
    llm_response = chain_assessment_level.invoke(
        {"possible_tool_terms": possible_tool_terms}
    )
    response = re.sub(r"[^a-z0-9\s]", "", llm_response.content.lower())
    print(response)
    return response
