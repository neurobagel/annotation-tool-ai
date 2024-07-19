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
from langchain.chains import RetrievalQA

base='/home/atharv-vedant/NB/annotation-tool-ai/app/categorization/Docfolder'
file= 'Docfolder/demo.txt'
def embeddings(name: str, file: str, base: str) -> None:
    """
    Create or load a Chroma database based on the given name.

    Parameters:
    name (str): The name of the database to be created or loaded.
    """
    # The directory path is the local directory I was working on once dockerized this will have to be figured out
    persist_base_directory: str = base

    # Override the base directory for persisted databases
    persist_base_directory = "persisted_databases"
    os.makedirs(persist_base_directory, exist_ok=True)

    # Full path to the persistence directory for the given database name
    persist_directory: str = os.path.join(persist_base_directory, name)

    # Check if the persist directory exists
    if os.path.exists(persist_directory):
        # Reload the existing Chroma database
        db= Chroma(embedding_function=OllamaEmbeddings(model="gemma"), persist_directory=persist_directory)
        print("Existing Chroma database reloaded.")
    else:
        # Load the documents
        raw_documents: list = TextLoader(file).load()

        # Split the documents
        text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        documents: list = text_splitter.split_documents(raw_documents)

        # Initialize the Chroma database with persistence
        db: Chroma = Chroma.from_documents(documents[:8], OllamaEmbeddings(model="nomic-embed-text"), persist_directory=persist_directory)

        # Save the database
        db.persist()
        print("New Chroma database created and persisted.")