import json
from typing import Dict, Any
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate


def llm_invocation(result_dict: Dict[str, str]) -> Dict[str, Any]:

    # Initialize model
    llm = ChatOllama(model="gemma")

    # Create prompt template
    prompt = PromptTemplate(
        template="""Given the column data {column}: {content}, determine the \
category and give only the category name as output

Examples:
1. Input: "participant_id: sub-01 sub-02 sub-03"
Output: Subject_IDs

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
    elif "Age" in r:
        output = {"TermURL": "nb:Age"}
        print(f"{json.dumps(output)}")
    elif "Sex" in r:
        output = {"TermURL": "nb:Sex"}
        print(f"{json.dumps(output)}")
    else:
        output = llm_response

    return output
