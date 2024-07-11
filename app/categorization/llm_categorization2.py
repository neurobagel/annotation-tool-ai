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
    AgeFormat

)
pass2={}

def llm_invocation2(pass2: Dict[str, str]):
    key, value = list(pass2.items())[0]
    print(key)
       
    llm = ChatOllama(model="gemma")
    Aprompt = PromptTemplate(
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
        input_variables=["column", "content","question"],
    )

    question1=f"Is the {key}:{value} a assesment tool"
        # question2=f"Is the {key}:{value} a diagnosis"
    chain =Aprompt | llm
    llm_response2 = chain.invoke({"column": key, "content": value,"question":question1})
    reply = str(llm_response2)
        # print(reply)
    if "yes" in reply.lower():
            # print("Processing column:", key)
            output = {"TermURL": "nb:A"}
            print(f"{json.dumps(output)}")
         
    elif "no" in reply.lower():
            print("Processing column:", key)
            output = {"TermURL": "nb:D"}
            print(f"{json.dumps(output)}")
    else:
            out = "nah"
    del pass2[key]

def llm_invocation1(result_dict: Dict[str, str]) -> Dict[str, Any]:

    # Initialize model
    llm = ChatOllama(model="gemma")

    # Create prompt template
    prompt = PromptTemplate(
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
        pass2[key]=value
        llm_invocation2(pass2)

    return output
