from datetime import datetime
import json
from typing import Dict, Any, Union
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate

from llm_helper import (
    is_european_decimal,
    is_float,
    is_integer,
    is_iso8601,
    SexLevel,
    AgeFormat,
)

from promptTemplate import prompt, Aprompt, Dprompt

pass2 = {}
pass3 = {}


def D(pass2: Dict[str, str]) -> None:
    key, value = list(pass2.items())[0]
    print(key)

    llm = ChatOllama(model="gemma")

    chainD = Dprompt | llm

    llm_response2 = chainD.invoke({"column": key, "content": value})
    reply = str(llm_response2)
    # print(reply)
    if "yes" in reply.lower():
        # print("Processing column:", key)
        output = {"TermURL": "nb:Diagnosis"}
        print(f"{json.dumps(output)}")
    else:
        pass3[key] = value
    del pass2[key]


def A(pass3: Dict[str, str]) -> None:
    key, value = list(pass3.items())[0]
    print(key)

    llm = ChatOllama(model="gemma")

    questionA = f"Is the {key}:{value} a assesment tool"

    chain = Aprompt | llm
    llm_response2 = chain.invoke(
        {"column": key, "content": value, "question": questionA}
    )
    reply = str(llm_response2)
    # print(reply)
    if "yes" in reply.lower():
        # print("Processing column:", key)
        output = {"TermURL": "nb:Assessment"}
        print(f"{json.dumps(output)}")
    else:
        print("not in data model")

    del pass3[key]


def llm_invocation2(pass2: Dict[str, str]) -> None:
    D(pass2)
    if bool(not pass3):
        A(pass3)


def llm_invocation1(result_dict: Dict[str, str]) -> Dict[str, Any]:
    llm = ChatOllama(model="gemma")

    chain = prompt | llm

    key, value = list(result_dict.items())[0]

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
        pass2[key] = value
        llm_invocation2(pass2)

    return output
