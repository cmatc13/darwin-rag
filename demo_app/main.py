import sys
import os
sys.path.append(os.path.abspath('.'))

from chainlit import user_session


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service

import time
import chainlit as cl
import tiktoken 
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate,  ChatPromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_community.vectorstores import FAISS, Chroma
import csv
from typing import Dict, List, Optional
from langchain.document_loaders.base import BaseLoader
from langchain.docstore.document import Document
import lark
from langchain.chains.llm import LLMChain
from google.cloud import storage
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from selenium import webdriver

import json
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()



theme_files = {
    "EMPCONTRACT1": "Fixed_Term_Contracts_FTCs.csv",
    "EMPCONTRACT2": "Probationary_Trial_Period.csv",
    "SOURCESCOPE1": "Legal_Coverage_General.csv",
    "SOURCESCOPE2": "Legal_Coverage_Reference.csv", 
    "DISMISSREQT1": "Valid_and_prohibited_grounds_for_dismissal.csv", 
    "DISMISSREQT2": "Workers_enjoying_special_protection_against_dismissal.csv", 
    "PROCREQTINDIV1": "Procedures_for_individual_dismissals_general.csv", 
    "PROCREQTINDIV2": "Procedures_for_individual_dismissals_notice_period.csv",
    "PROCREQTCOLLECT": "Procedures_for_collective_dismissals.csv",
    "SEVERANCEPAY": "Redundancy_and_severance_pay.csv",
    "REDRESS": "Redress.csv"
}


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client.from_service_account_json('llm-app-project-26a82e769088.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

# Iterate through the dictionary items
for theme, filename in theme_files.items():
    download_blob("ilo_storage", "download/" + filename, "download/" + filename)





def download_folder(bucket_name, prefix, destination_dir):
    
    storage_client = storage.Client.from_service_account_json('llm-app-project-26a82e769088.json')
    bucket = storage_client.get_bucket(bucket_name)
    
    blobs = bucket.list_blobs(prefix=prefix)  # List all objects that start with the folder prefix
    for blob in blobs:
        if not blob.name.endswith("/"):  # Ignore directories
            destination_file_name = f"{destination_dir}/{blob.name.split('/')[-1]}"
            blob.download_to_filename(destination_file_name)
            print(f"Downloaded {blob.name} to {destination_file_name}")



from langchain_openai import OpenAIEmbeddings
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate,  ChatPromptTemplate



metadata_field_info=[
AttributeInfo(
    name="Region",
    description="Region of the country",
    type="string",
),
AttributeInfo(
    name="Country",
    description="Country",
    type="string",
),
AttributeInfo(
    name="Year",
    description="Year of the latest legislation",
    type="string",
),
]
document_content_description = """Most recent legal information on the regulation of temporary 
contracts and employment termination at the initiative of the employer. It covers over fifty elements 
of employment protection, grouped under nine themes. The information is based on regulation at the 
national level. """


bucket_name = "ilo_storage"
local_persistence_dir = 'chroma'  # Your local directory
gcs_persistence_dir = 'chroma_persistence/'  # Path in your GCS bucket

download_folder(bucket_name, gcs_persistence_dir, local_persistence_dir)
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = Chroma(embedding_function=embeddings, persist_directory='chroma')

llm= ChatOpenAI( model_name="gpt-4-turbo",temperature=0, api_key=os.getenv("OPENAI_API_KEY"))


retriever = SelfQueryRetriever.from_llm(
llm, vectorstore, document_content_description, metadata_field_info, search_kwargs={"k": 20},verbose=True
)

# Define the system message template
system_template = """The provided data are tabular datasets containing the most
recent legal information on the regulation of temporary contracts and employment
termination at the initiative of the employer.
It covers over fifty elements of employment protection, grouped under nine themes.
The information is based on regulation at the national level. If a country is provided
in the query, always filter by that country first and then find the relevant document(s).
You are an expert on International Labour Law however please use only the documents
provided in formulating your answer.

----------------
{context}"""



@cl.on_message
async def main(message: cl.Message):

    
    # Create the chat prompt templates
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, 
    return_source_documents=False,combine_docs_chain_kwargs={"prompt": qa_prompt},memory=memory,verbose=True)
    
  
    res = await qa.acall(message.content, callbacks=[cl.LangchainCallbackHandler()])

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="""Welcome to the Lano ILO LLM app! I'm here to assist you with any questions you have about the EPLex database. This comprehensive resource provides detailed legal information on employment termination and the regulation of temporary contracts, focusing on key aspects of employment protection across various national contexts. Whether you're interested in specific regulations or comparative legal provisions, I'm here to help you navigate and understand the intricacies of International Labour Law.""").send()