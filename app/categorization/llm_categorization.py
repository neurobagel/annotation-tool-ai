from datetime import datetime
import json
from typing import Dict, Any, Union
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate


def SexLevel(result_dict: Dict[str, str], r: str, key: str) -> Dict[str, Any]:
    value = result_dict[key]
    value = value.lower()
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
        "Levels": {str(var1): "male", str(var2): "female", str(var3): "other"},
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


# def is_bounded(s:str)->bool: yet to be added
# def is_years yet to be added


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
        # 2 more conditions yet to be added

    output: Dict[str, str] = {
        "TermURL": "nb:Age",
        "Format": Fvar,
    }
    return output


def llm_invocation(result_dict: Dict[str, str]) -> Dict[str, Any]:

    # Initialize model
    llm = ChatOllama(model="gemma")

    # Create prompt template
    prompt = PromptTemplate(
        template="""Given the column data {column}: {content},
    determine the category and give only the category name as output

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

    # Create chain
    chain = prompt | llm

    key, value = list(result_dict.items())[0]

    # Invoke LLM
    llm_response = chain.invoke({"column": key, "content": value})

    r = str(llm_response)
    # check mapping of categorization
    print(llm_response)
    if "Participant_IDs" in r:
        output = {"TermURL": "nb:ParticipantID"}
        print(f"{json.dumps(output)}")
    elif "Session_IDs" in r:
        output = {"TermURL": "nb:Session"}
        print(f"{json.dumps(output)}")
    elif "Sex" in r:
        output = SexLevel(result_dict, r, key)
    elif "Age" in r:
        output = AgeFormat(result_dict, r, key)
    else:
        output = llm_response

    return output
