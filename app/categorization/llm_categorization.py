from datetime import datetime
import json
from typing import Dict, Any, Union, Optional
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.chains import SequentialChain


def SexLevel(result_dict: Dict[str, str], r: str, key: str) -> Dict[str, Any]:
    value = result_dict[key]
    value = value.casefold()
    var1: str = ""
    var2: str = ""
    var3: str = ""

    if "1" in value or "2" in value or "3" in value:
        var1 = "1"
        var2 = "2"
        var3 = "3"
    elif "0" in value or "1" in value or "2" in value:
        var1 = "0"
        var2 = "1"
        var3 = "2"
    elif "m" in value or "f" in value or "o" in value:
        var1 = "m"
        var2 = "f"
        var3 = "o"
    elif "male" in value or "female" in value or "other" in value:
        var1 = "male"
        var2 = "female"
        var3 = "other"
    else:
        output: Dict[str, Union[str, Dict[str, str]]] = (
            {}
        )  # Or any default output as per your requirement
        print(json.dumps(output))

    output = {
        "TermURL": "nb:Sex",
        "Levels": {str(var1): "male", str(var2): "female"},
    }
    return output


def is_integer(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_iso8601(s: str) -> bool:
    try:
        datetime.fromisoformat(s)
        return True
    except ValueError:
        return False


def is_european_decimal(s: str) -> bool:
    s = s.strip()  # Remove leading and trailing whitespace

    if s.count(",") == 1:
        if s.index(",") > 0 and s.index(",") < len(s) - 1:
            return True

    return False


def is_bounded(s: str) -> bool:
    if "+" in s:
        return True
    else:
        return False


def is_years(s: str) -> bool:
    s.casefold()
    if "y" in s:
        return True
    else:
        return False


def AgeFormat(result_dict: Dict[str, str], r: str, key: str) -> Dict[str, Any]:
    value = result_dict[key].strip()  # Ensure no leading/trailing whitespace
    numbers_list_str = value.split()
    Age_l = [num_str.strip() for num_str in numbers_list_str]
    Fvar: str = "Unknown"

    for num_str in Age_l:
        if is_integer(num_str):
            Fvar = "integervalue"
            break
        elif is_float(num_str):
            Fvar = "floatvalue"
            break
        elif is_iso8601(num_str):
            Fvar = "iso8601"
            break
        elif is_european_decimal(num_str):
            Fvar = "europeandecimalvalue"
            break
        elif is_bounded(num_str):
            Fvar = "boundedvalue"
            break
        elif is_years(num_str):
            Fvar = "yearunit"
            break

    output: Dict[str, str] = {
        "TermURL": "nb:Age",
        "Format": Fvar,
    }
    return output


def Diagnosis(key: str, value: str) -> Optional[Dict[str, str]]:
    llm = ChatOllama(model="gemma")

    DiagnosisPrompt = PromptTemplate(
        template="""Given the column data {column}: {content},
    Based on the sample data provided, please evaluate whether each column should be categorized as a "Diagnosis". 
    by considering the following characteristics 
    Is the column intended to indicate or identify a medical diagnosis (purpose)? 
    Is the data {content} structured in a way that suggests medical diagnoses, such as ICD codes, 
    disease names, their common abbreviations, or conditions (format)? 
    Is there a consistent format or terminology for diagnoses used throughout the data? 
    including disease names, diagnostic codes, and recurring abbreviations (consistency)? 
    Does the content suggest medical diagnoses, including names of diseases, conditions, or symptoms (content)? 
    Are there labels, descriptions, or metadata that indicate the purpose of the column? 
    related to medical diagnoses (Metadata)? 
    In addition, if the column content consists of numbers, check to see if it is dichotomous, 
    which indicates that it may be a diagnosis column. 
    If the content is strings, check if it is a list of strings, 
    which also indicates that it may be a diagnosis column. 
    If the content resembles scores or ratings, it is not a diagnostic column. 
    The sample data may contain assessment tools; 
    These are not diagnostic columns. Output only a single "yes" or "no".
    Do not include any explanation in the output.
    """,
        input_variables=["column", "content"],
    )
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
        # print("next")
        return None


def AssessmentTool(key: str, value: str) -> Optional[Dict[str, str]]:
    llm = ChatOllama(model="gemma")
    questionAssessmentTool = f"Is the {key}:{value} an assessment tool"

    AssessmentToolPrompt = PromptTemplate(
        template="""
        Given the column data {column}: {content},
    Instructions: Based on the provided information, please evaluate if this column is an assessment tool  . Consider the following characteristics of assessment tools in your evaluation:
    In context of medical studies return yes or no for {question} if properties of Assessment tool is as follows:
    The {content} structured in a way that suggests a test, survey, or questionnaire or evaluation metric(e.g.,IQ,scores, Likert scale, multiple-choice, ratings) and  consistent format or scale used throughout the {content} with numerical entries  (e.g., scores out of powers of 10, ratings in a range of numbers )?
    The {column} aim to measure or evaluate something specific?


    Give answer No if  {column}:{content}  indicate a "group" or result of a collection

If not describing a  diagnosis in context of medical research answer Yes


    provide yes if assessment tool  or no if not.
    Do not give any explanation in the output.
    """,
        input_variables=["column", "content", "question"],
    )
    chainAssessmentTool = AssessmentToolPrompt | llm
    llm_response_Assessment = chainAssessmentTool.invoke(
        {"column": key, "content": value, "question": questionAssessmentTool}
    )
    reply = str(llm_response_Assessment)
    if "yes" in reply.lower():
        output = {"TermURL": " nb:Assessment"}
        print(json.dumps(output))
        return output
    else:
        print(key)
        print("not in data model")
        return None


def llm_diagnosis_assessment(key: str, value: str) -> Optional[Dict[str, str]]:
    resultDiagnosis = Diagnosis(key, value)
    if resultDiagnosis:
        return resultDiagnosis
    else:
        return AssessmentTool(key, value)


def llm_invocation(result_dict) -> Optional[Dict[str, str]]:
    output: Union[Dict[str, str], None]
    llm = ChatOllama(model="gemma")
    key, value = list(result_dict.items())[0]

    GeneralPrompt = PromptTemplate(
        template="""Given the column data {column}: {content}, determine the category and give only the category name as output

Examples:
1. Input: "participant_id: sub-01 sub-02 sub-03"
Output: Participant_IDs

2. Input: 'pheno_age: ["34,1", "35,3", "NA", "39,0", "22,1",
"23,2", "21,1", "22,3", "42,5", "43,2"]'
Output: Age

3. Input: "session_id: ses-01 ses-02"
Output: Session_IDs

4. Input: "pheno_sex : ["F", "F", "M", "M", "missing",
"missing", "F", "F", "M", "M"]"
Output: Sex

5. Input: "pheno_sex : ["1", "2", "1", "2", "missing", "missing"]"
Output: Sex

Do Not Give any explanation in the output.
Input: "{column}: {content}"
Output= <category>
""",
        input_variables=["column", "content"],
    )

    chainGeneral = GeneralPrompt | llm

    llm_response = chainGeneral.invoke({"column": key, "content": value})
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
        output = llm_diagnosis_assessment(key, value)

    return output
