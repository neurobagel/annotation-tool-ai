from datetime import datetime
import json
from typing import Dict, Any, Union
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate

import os
from langchain_community.document_loaders import TextLoader

from langchain_community.llms import Ollama
from langchain_community import embeddings
from langchain_community.embeddings import OllamaEmbeddings 
from langchain.chains import RetrievalQA
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_community.vectorstores import Chroma


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
# from llm_categorization import(
    
#     D,
#     A
# )


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
        VS(key)
        for i in range (0,len(unique_entries)):
            VS(unique_entries[i])

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
def VS(entry):
    


    persist_directory = '/home/tvisha/gsoc/Annotation-tool-llm/Docfolder'

# Check if the persist directory exists
    if os.path.exists(persist_directory):
    # Reload the existing Chroma database
        db = Chroma(embedding_function=OllamaEmbeddings(model="gemma"), persist_directory=persist_directory)
        print("Existing Chroma database reloaded.")
    else:
    # Load the documents
        raw_documents = TextLoader('Docfolder/demo.txt').load()
        print("Documents loaded:", raw_documents)

    # Split the documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        documents = text_splitter.split_documents(raw_documents)
        print("Documents split into chunks:", documents)

    # Initialize the Chroma database with persistence
        
        db = Chroma.from_documents(documents, OllamaEmbeddings(model="gemma"),

        persist_directory=persist_directory)
    # Save the database
        db.persist()
        print("New Chroma database created and persisted.")

    prompt = ChatPromptTemplate.from_template("""
Give the full form for the Acronym based on the context given.
Use the information available in the db to give the output.
Return only the full form and not anything else.
The output should not have 'input' and 'context' 
and give only 'answer' as output.

Instruction: if a number or digit is present do not return anything.

<context>
{context}
</context>
Acronym: {input}
""")

    llm = ChatOllama(model="gemma")

# Create the document chain
    document_chain = create_stuff_documents_chain(llm, prompt)

# Set up the retriever
    retriever = db.as_retriever()

# Create the retrieval chain
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

# Example input for testing
    # entry = "example acronym"  # Replace with actual input

# Invoke the retrieval chain
    response = retrieval_chain.invoke({"input": entry})
    print("Response:", response)


    # query = "What is full form of HC according to the text"
    # retireved_results=db.similarity_search(query)
    # print(retireved_results)




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
  result_dict = {'participant_id': 'participant_id sub-718211 sub-718213 sub-718216 sub-718217 sub-718220 sub-718221 sub-718315 sub-718318 sub-718320 sub-718321 sub-718322 sub-718323 sub-718518 sub-719211 sub-719215 sub-719222 sub-719224 sub-719225 sub-719226 sub-719231 sub-719232 sub-719238 sub-719241 sub-719245 sub-719247 sub-719311 sub-719312 sub-719313 sub-719315 sub-719316 sub-719318 sub-719319 sub-719322 sub-719326 sub-719327 sub-719329 sub-719330 sub-719331 sub-719332 sub-719334 sub-719335 sub-719337 sub-719339 sub-719341 sub-719345 sub-719348 sub-719349 sub-719350 sub-719351 sub-719354 sub-719355 sub-719356 sub-719358 sub-719360 sub-719362 sub-719364 sub-719369 sub-719370 sub-719371 sub-719511 sub-719515 sub-719518 sub-719522 sub-719523 sub-719524 sub-719525 sub-719526 sub-719527 sub-719528 sub-719530 sub-719531 sub-719535 sub-719536 sub-720219 sub-720220 sub-720311 sub-720312 sub-720314 sub-720316 sub-720317 sub-720318 sub-720319 sub-720320 sub-720511 sub-720515 sub-720516 sub-720517',  'age': 'age 28.4 24.6 43.6 19.1 38.9 32.5 19.7 23.0 25.9 31.2 38.2 36.3 33.8 28.3 29.1 25.6 43.2 24.4 36.1 21.8 26.5 20.1 32.2 44.0 24.1 26.0 36.4 25.5 26.9 36.8 23.4 30.4 22.2 27.6 29.3 19.3 41.2 21.4 26.7 22.9 39.5 21.3 22.4 34.1 27.5 33.6 26.7 27.0 32.8 26.9 31.4 36.8 22.6 28.2 31.4 19.6 25.5 44.3 30.0 31.0 31.1 27.7 32.1 21.1 22.7 23.6 24.4 38.9 21.6 33.6 34.8 29.1 23.7 28.4 22.3 25.1 26.8 20.4 21.4 33.1 30.3 28.8 31.1 21.9 22.0 38.8 29.8','sex': 'sex M F M F F F F F M F F F F M F F F F F F F F F M F M F M F F F M M F F F F F M F F F F F F F M F M F M F F F M F F F F F F F F F M F F F M F F M M M F F M F M F F F F M F F F', 'group_dx': ' MDD MDD PDD PDD PDD PDD HC HC HC HC HC HC MDD MDD MDD PDD MDD PDD MDD PDD MDD MDD MDD PDD MDD HC HC HCconvertedMDD HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC HC MDD MDD MDD MDD PDD MDD MDD MDD PDD MDD MDD PDD MDD MDD PDD PDD HC HC HC HC HC HC HC HC MDD MDD MDD MDD', 'number_comorbid_dx': ' 0 0 1 3 1 4 0 0 0 0 0 0 1 1 1 3 3 5 1 0 3 2 4 1 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 2 1 2 0 0 1 0 0 0 2 0 0 2 3 0 0 0 0 0 0 0 0 0 2 1 1', 'medload': ' 0 0 2 0 6 0 0 0 0 0 0 0 0 1 1 0 0 1 4 2 3 3 1 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 2 3 2 0 0 1 0 3 0 0 0 0 1 3 4 0 0 0 0 0 0 0 0 1 1 4 0', 'iq': ' 117.66 109.08 112.98 114.54 107.52 99.72 104.4 98.16 111.42 108.3 109.86 111.42 108.3 105.96 121.56 110.64 113.76 111.42 114.54 119.22 109.86 109.08 121.56 117.66 110.64 104.4 100.5 111.42 107.52 111.42 109.08 107.52 108.3 113.76 112.98 93.48 101.28 96.6 115.32 103.62 102.84 95.82 105.18 102.06 98.16 102.06 105.96 91.92 114.54 105.96 109.86 103.62 107.52 102.84 105.96 111.42 108.3 108.3 113.76 109.08 120.78 118.44 119.22 100.5 108.3 115.32 102.84 116.88 109.86 118.44 102.06 107.52 88.8 110.64 99.72 114.54 122.34 112.98 106.74 102.06 110.64 105.96 115.32 102.84 109.86 105.18 95.82', 'session': ' 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1'}


  llm_invocation(result_dict)
