from typing import Any, Dict, Optional, Union
import json
from langchain_community.chat_models import ChatOllama
from openai import OpenAI
from langchain_openai import ChatOpenAI
import os 
from dotenv import load_dotenv
from categorization.llm_helper import SexLevel, AgeFormat, get_assessment_label,Diagnosis_Level,list_terms

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
llm = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

def Diagnosis(
    key: str, value: str, code_system: str
) -> Optional[Union[Dict[str, str], Dict[str, Any]]]:
    prompt_template = """Given the column data header:{key}:, content: {value},
    Based on the sample data provided, please evaluate whether each
    column should be categorized as a "Diagnosis".
    by considering the following characteristics
    Is the column intended to indicate or identify
    a medical diagnosis (purpose)?
    Is the data {value} structured in a way that suggests
    medical diagnoses, such as ICD codes,
    disease names, their common abbreviations, or conditions (format)?
    Is there a consistent format or terminology for
    diagnoses used throughout the data?
    including disease names, diagnostic codes, and
    ecurring abbreviations (consistency)?
    Does the content suggest medical diagnoses, including
    names of diseases, conditions, or symptoms (content)?
    Are there labels, descriptions, or metadata that
    indicate the purpose of the column?
    related to medical diagnoses (Metadata)?
    In addition, if the column content consists of numbers,
    check to see if it is dichotomous,
    which indicates that it may be a diagnosis column.
    If the content is strings, check if it is a list of strings,
    which also indicates that it may be a diagnosis column.
    If the content resembles scores or ratings, it is not a
    diagnostic column.
    The sample data may contain assessment tools;
    These are not diagnostic columns. Output only a single "yes" or "no".
    Do not include any explanation in the output.
    """
    prompt= prompt_template.format(key=key, value=value)
    llm_response_Diagnosis = llm.chat.completions.create(
    model="openai/chatgpt-4o-latest",
    messages=[
        {"role": "user", 
         "content": prompt}
    ]
)
    reply = str(llm_response_Diagnosis)
    print(reply)
    if "yes" in reply.lower():
        output = {"TermURL": "nb:Diagnosis", "Levels": {}}
        unique_entries=list_terms(key,value)
        level = Diagnosis_Level(unique_entries, code_system)        
        output["Levels"] = level
        print(json.dumps(output))
        return output

    else:
        return AssessmentTool(key, value, code_system)



def AssessmentTool(
    key: str, value: str, code_system: str
) -> Optional[Dict[str, Any]]:

    prompt_template = """Given the column data header:{key}, content: {value},
    Instructions: Based on the provided information,
    please evaluate if this column is an assessment tool.
    Consider the following characteristics of assessment tools
    in your evaluation:
    In context of medical studies return yes or no for is the {key}:{value} an assessment tool?
    if properties of Assessment tool is as follows:
    The {value} structured in a way that suggests a test,
    survey, or questionnaire or evaluation metric(e.g.,IQ,scores,
    Likert scale, multiple-choice, ratings) and consistent format or
    scale used throughout the {value} with numerical entries
    (e.g., scores out of powers of 10, ratings in a range of numbers)?
    The {key} aim to measure or evaluate something specific?

    Give answer No if {key}:{value} indicate a "group"
    or result of a collection

    If not describing a diagnosis in context of medical research answer Yes

    provide yes if assessment tool or no if not.
    Do not give any explanation in the output.
    """
    prompt = prompt_template.format(key=key, value=value)
    llm_response_Assessment = llm.chat.completions.create(
    model="openai/chatgpt-4o-latest",
    messages=[
        {"role": "user", 
         "content": prompt}
    ]
)

    reply = str(llm_response_Assessment)
    print(reply)
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
    #llm = ChatOllama(model="gemma")
    #chainGeneral = GeneralPrompt | llm
    key, value = list(result_dict.items())[0]
    # llm_response = chainGeneral.invoke({"column": key, "content": value})
    print(key, value)
    
    prompt_template ="""Given the column data - header: {key}, content: {value},
    determine the category and give only the category name as output. 
    Check if it fits the category of Participant_IDs, Session ID, Sex or Age.

    Do Not Give any explanation in the output.
    Input: "{key}: {value}"
    Output= <category>
    """ 
    prompt = prompt_template.format(key=key, value=value)

    llm_response= llm.chat.completions.create(
    model="openai/chatgpt-4o-latest",
    messages=[
        {"role": "user", 
         "content": prompt}
    ]
)
    #r = str(llm_response)
    r = str(llm_response.choices[0].message.content)
    print(r)
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
