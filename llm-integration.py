from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd


def all_columns_to_strings(file_path):
    """
    Reads a TSV file and converts each column into a separate string.

    Parameters:
    - file_path: str, path to the TSV file.

    Returns:
    - dict: A dictionary where each key is the column header and the value is 
            the header followed by the contents of the column as a single string.
    """
    # Read the TSV file into a DataFrame
    df = pd.read_csv(file_path, delimiter='\t')

    # Convert each column to a string and store in a dictionary
    column_strings = {col: f"{col} {' '.join(df[col].astype(str))}" for col in df.columns}

    return column_strings

if __name__ == "__main__":
    
    # Prepare .tsv file
    file_path = 'participants.tsv'  # Replace with the path to your TSV file
    result_dict = all_columns_to_strings(file_path)

    #initialize model - llama3 run locally
    llm = ChatOllama(model="llama3")

    #create output structure
    class ColumnCategorization(BaseModel):
        originalColumn: str = Field(description="original name of the column assigned by researchers")
        predictedColumn: str = Field(description="column name predicted by the llm withing the nb datamodel entities")
    
    #set up parser
    parser = JsonOutputParser(pydantic_object=ColumnCategorization)

    #create prompt template
    prompt = PromptTemplate(
        template="Given the column data {column}:{content}. Process the content and determine which of the following labels fits best 'participant_id', 'sex', 'assessment_tool', 'diagnosis', or 'session_id'. Do not add any columns. Map the original {column} name to the determined label. Use only \n{format_instructions}\n to respond",
        input_variables=["column", "content"],
        partial_variables={"format_instructions": parser.get_format_instructions()})

    
    #create chain
    chain = prompt | llm |parser

    for key,value in result_dict.items():
        print(key,value)
        response = chain.invoke({"column": key, "content": value})
        print(response)



