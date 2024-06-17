from typing import Dict

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

def Categorize1(result_dict: Dict[str, str]) -> None:

     # Initialize model
    llm = ChatOllama(model="gemma")

    # # Create output structure
    # class ColumnCategorization(BaseModel):
    #     predictedColumn: str = Field(description="Column name predicted by the LLM within the NB data model entities")

    # # Set up parser
    # parser = JsonOutputParser(pydantic_object=ColumnCategorization)

    # Create prompt template
    prompt = PromptTemplate(
        template='''Given the column data {column}: {content}, determine the category and give only the category name as output

Examples:
1. Input: "participant_id: sub-01 sub-02 sub-03"
   Output: Subject_IDs

2. Input: 'pheno_age: ["34,1", "35,3", "NA", "39,0", "22,1", "23,2", "21,1", "22,3", "42,5", "43,2"]'
   Output: Age

3. Input: "session_id: ses-01 ses-02"
   Output: Session_IDs

4. Input: "pheno_sex : ["F", "F", "M", "M", "missing", "missing", "F", "F", "M", "M"]" 
   Output: Sex

5. Input: "pheno_sex : ["1", "2", "1", "2", "missing", "missing"]" 
   Output: Sex

Do Not Give any explanation in the output. 
Input: "{column}: {content}"
Output= <category> " "  "


''',
        input_variables=["column", "content"],
    )

    # Create chain
    chain = prompt | llm 

    # Process each column
    for key, value in result_dict.items():
        print("Processing column:", key)
        try:
            # Invoke the chain with the input data
            response = chain.invoke({"column": key, "content": value})
            print("Response:", response)

        except Exception as e:
            print("Error processing column:", key)
            print("Error message:", e)



if __name__ == "__main__":
    result_dict = {
        'participant_id': 'sub-01 sub-01 sub-02 sub-02 sub-03 sub-03 sub-04 sub-04 sub-05 sub-05',
        'session_id': 'ses-01 ses-02 ses-01 ses-02 ses-01 ses-02 ses-01 ses-02 ses-01 ses-02',
        'sex_column' : '[1, 2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 2]',
        'pheno_age': '34.1 35.3 nan 39.0 22.1 23.2 21.1 22.3 42.5 43.2',
    
    }

    Categorize1(result_dict)
   