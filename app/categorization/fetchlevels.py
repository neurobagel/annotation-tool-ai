from datetime import datetime
import json
from typing import Dict, Any, Union
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate

import os
from langchain_community.document_loaders import TextLoader

from langchain_community.llms import Ollama


pass2={}


from llm_helper import (
    is_years,
    is_bounded,
    is_european_decimal,
    is_float,
    is_integer,
    is_iso8601,
   
    SexLevel,
    AgeFormat

)
from promptTemplate import(
    prompt,
    Aprompt,
    Dprompt
)
def D(key: str, value: str) -> Union[None, Dict[str, str]]:
    # print(key)
    # print("D entry")
    llm = ChatOllama(model="gemma")

    chainD = Dprompt | llm

    llm_response2 = chainD.invoke({"column": key, "content": value})
    reply = str(llm_response2)
    
    if "yes" in reply.lower():
        print(key)
        output = {"TermURL": "nb:Diagnosis"}
        print(f" {json.dumps(output)}")
        unique_entries=list_terms(value)
        Diagnosis_Levels(key)
        for i in range (0,len(unique_entries)):
            Diagnosis_Levels(unique_entries[i])

        return output
    else:
        print("next")
        
    return None

def A(key: str, value: str) -> Union[None, Dict[str, str]]:
    print(key)
    # print("A entry")

    llm = ChatOllama(model="gemma")

    questionA = f"Is the {key}:{value} an assessment tool"

    chain = Aprompt | llm
    llm_response2 = chain.invoke(
        {"column": key, "content": value, "question": questionA}
    )
    reply = str(llm_response2)
    
    if "yes" in reply.lower():
        output = {"TermURL": "nb:Assessment"}
        print(f" {json.dumps(output)}")
        return output
    else:
        print(key)
        print("not in data model")
    return None


def llm_invocation2(key: str, value: str) -> Union[None, Dict[str, str]]:
    # print(f"llm_invocation2 called with key: {key}, value: {value}")
    result = D(key, value)
    if result:
        return result
    else:
        return A(key, value)
    return None


def list_terms (value):
    words = value.split()
    unique_entries = list(set(words))
    print(unique_entries)
    return unique_entries

# from langchain.chains import load_qa_chain
def Diagnosis_Levels(entry):
    print("entry")
    

    def load_dictionary(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def get_label_for_abbreviation(abbreviation, abbreviation_to_label):
        if abbreviation in abbreviation_to_label:
            return abbreviation_to_label[abbreviation]
        elif abbreviation.isdigit():
            return "some score"
        else:
            return "LLMcheck"
# Path to your JSON file
    file_path = 'Docfolder/abbreviation_to_labels.json'

# Load the JSON data
    data = load_dictionary(file_path)

# Abbreviation to check in the mappings
    abbreviation_to_check = entry

# Get the label for the abbreviation
    result = get_label_for_abbreviation(abbreviation_to_check, data)

    print(result)
    
  



def llm_invocation(result_dict: Dict[str, str]) -> Dict[str, Any]:

    # Initialize model
    llm = ChatOllama(model="gemma")

    # Create prompt template
    
    # Create chain
    chain = prompt |llm
    
    # chain = SequentialChain(
#     chains=[chain1,chain2],
#     input_variables=["column","content"]
# )
    

    

    age = { "pheno_age","age","Age"}
    #key, value = list(result_dict.items())[0]
    for key, value in result_dict.items():

    # Invoke LLM
        llm_response = chain.invoke({"column": key, "content": value,"age":age})

        r = str(llm_response)
    # check mapping of categorization
        #print(llm_response)
        if "Participant_IDs" in r:
            output = {"TermURL": "nb:ParticipantID"}
            print(f"{json.dumps(output)}")
        elif "Session_IDs" in r or "session" in r.lower():
            output = {"TermURL": "nb:Session"}
            print(f"{json.dumps(output)}")
        elif "sex" in r.lower():
            output = SexLevel(result_dict, r, key)
            print(f"{json.dumps(output)}")
        elif "Age" in r:
            output = AgeFormat(result_dict, r, key)
            print(f"{json.dumps(output)}")
        # elif "Diagnosis" in r:
        #   print("Processing column:", key)
        #   output = {"TermURL": "nb:diagnosis"}
        #   print(f"{json.dumps(output)}")
        else:
            # pass2[key]=value
            # pass2[key] = value
            output = llm_invocation2(key, value)


    # print(pass2.keys())
    return output


if __name__ == "__main__":
  result_dict = { 'group_dx': ' MDD MDD PDD PDD PDD PDD HC HC HC HC HC HC MDD MDD MDD PDD MDD PDD MDD PDD MDD MDD MDD PDD MDD HC HC HCconvertedMDD HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC MDD MDD MDD MDD PDD MDD MDD MDD PDD MDD MDD PDD MDD MDD PDD PDD HC HC HC HC HC HC HC HC MDD MDD MDD MDD', 'number_comorbid_dx': ' 0 0 1 3 1 4 0 0 0 0 0 0 1 1 1 3 3 5 1 0 3 2 4 1 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 2 1 2 0 0 1 0 0 0 2 0 0 2 3 0 0 0 0 0 0 0 0 0 2 1 1', 'medload': ' 0 0 2 0 6 0 0 0 0 0 0 0 0 1 1 0 0 1 4 2 3 3 1 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 2 3 2 0 0 1 0 3 0 0 0 0 1 3 4 0 0 0 0 0 0 0 0 1 1 4 0', 'iq': ' 117.66 109.08 112.98 114.54 107.52 99.72 104.4 98.16 111.42 108.3 109.86 111.42 108.3 105.96 121.56 110.64 113.76 111.42 114.54 119.22 109.86 109.08 121.56 117.66 110.64 104.4 100.5 111.42 107.52 111.42 109.08 107.52 108.3 113.76 112.98 93.48 101.28 96.6 115.32 103.62 102.84 95.82 105.18 102.06 98.16 102.06 105.96 91.92 114.54 105.96 109.86 103.62 107.52 102.84 105.96 111.42 108.3 108.3 113.76 109.08 120.78 118.44 119.22 100.5 108.3 115.32 102.84 116.88 109.86 118.44 102.06 107.52 88.8 110.64 99.72 114.54 122.34 112.98 106.74 102.06 110.64 105.96 115.32 102.84 109.86 105.18 95.82', 'session': ' 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1'}


  llm_invocation(result_dict)
