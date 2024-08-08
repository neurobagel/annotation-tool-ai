from typing import Any, Dict, Optional, Union
import json
from langchain_community.chat_models import ChatOllama
from app.categorization.promptTemplate import (
    GeneralPrompt,
    AssessmentToolPrompt,
    DiagnosisPrompt,
)
from app.categorization.llm_helper import SexLevel, AgeFormat, get_assessment_label,Diagnosis_Level,list_terms


def Diagnosis(
    key: str, value: str, code_system: str
) -> Optional[Union[Dict[str, str], Dict[str, Any]]]:
    # llm = ChatOllama(model="gemma")
    # chainDiagnosis = DiagnosisPrompt | llm
    # llm_response_Diagnosis = chainDiagnosis.invoke(
    #     {"column": key, "content": value}
    # )
    # reply = str(llm_response_Diagnosis)
    # print(reply)
    reply='yes'
    if "yes" in reply.lower():
        output = {"TermURL": "nb:Diagnosis", "Levels": {}}
        unique_entries=list_terms(value)
        levels={}
        level={}
        level = Diagnosis_Level(unique_entries, code_system,levels)
        print(''' 

llm_file

''')
        
        output["Levels"] = level
        print(json.dumps(output))
        return output

    else:
        return AssessmentTool(key, value, code_system)


def AssessmentTool(
    key: str, value: str, code_system: str
) -> Optional[Dict[str, Any]]:
    llm = ChatOllama(model="gemma")
    questionAssessmentTool = f"Is the {key}:{value} an assessment tool"
    chainAssessmentTool = AssessmentToolPrompt | llm
    llm_response_Assessment = chainAssessmentTool.invoke(
        {"column": key, "content": value, "question": questionAssessmentTool}
    )
    reply = str(llm_response_Assessment)
    if "yes" in reply.lower():
        tool_term = get_assessment_label(key, code_system)
        if isinstance(tool_term, list) and len(tool_term) == 1:
            tool_term = tool_term[0]
        elif isinstance(tool_term, list) and len(tool_term) > 1:
            print(
                "Multiple terms found for the assessment tool. Please select one:"  # noqa: E501
            )
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


def llm_diagnosis_assessment(
    key: str, value: str, code_system: str
) -> Optional[Dict[str, str]]:
    resultDiagnosis = Diagnosis(key, value, code_system)
    if resultDiagnosis:
        return resultDiagnosis
    else:
        print(
            "Currently no entity in the Neurobagel data model fits the column."
        )
        return None


def llm_invocation(
    result_dict: Dict[str, str], code_system: str
) -> Optional[Dict[str, str]]:
    output: Union[Dict[str, str], None]
    # llm = ChatOllama(model="gemma")
    # chainGeneral = GeneralPrompt | llm
    key, value = list(result_dict.items())[0]
    # llm_response = chainGeneral.invoke({"column": key, "content": value})
    # r = str(llm_response)
    r="Diagnosis"
    if "Participant_IDs" in r:
        output = {"TermURL": "nb:ParticipantID"}
    elif "Session_IDs" in r:
        output = {"TermURL": "nb:Session"}
    elif "Sex" in r:
        output = SexLevel(result_dict, key)
    elif "Age" in r:
        output = AgeFormat(result_dict, key)
    else:
        output = llm_diagnosis_assessment(key, value, code_system)

    return output