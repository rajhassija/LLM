import os
import pandas as pd
import numpy as np
import logging
from dotenv import load_dotenv, find_dotenv

import streamlit as st
from sentence_transformers import SentenceTransformer

# langchain 
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.document_loaders import UnstructuredURLLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.globals import set_debug
from langchain.globals import set_verbose

### openai apis
import openai
from langchain_openai import ChatOpenAI
#from langchain.embeddings import OpenAIEmbeddings
from langchain import OpenAI

## google apis 
import google.generativeai as palm
from langchain.embeddings import GooglePalmEmbeddings
from langchain.llms import GooglePalm
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

## custom code for verbose and debug

# Define your custom logging handler to capture generated queries
class CaptureGeneratedQueriesHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.generated_queries = []

    def emit(self, record):
        message = record.getMessage()
        if "Generated queries:" in message:
            self.generated_queries.append(message)

# Initialize and add your custom handler to the specific logger
capture_handler = CaptureGeneratedQueriesHandler()
logger = logging.getLogger("langchain.retrievers.multi_query")
logger.addHandler(capture_handler)
logger.setLevel(logging.INFO)

class StreamlitHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []  # Store log messages

    def emit(self, record):
        msg = self.format(record)
        self.logs.append(msg)
    
    def get_logs(self):
        return self.logs

# Create an instance of your handler and add it to the root logger
streamlit_handler = StreamlitHandler()
logging.basicConfig(handlers=[streamlit_handler], level=logging.DEBUG)

# Example function to simulate logging from another part of your application
def do_something_that_logs():
    logger = logging.getLogger(__name__)
    logger.info("This is an info log.")
    logger.debug("This is a debug log.")

# Load environment variables
_ = load_dotenv(find_dotenv())

##google palm api keys
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDG8Hh3JEAwWKdXz5j6yjJL2GKOlUy_7es'
google_api_key=os.getenv('GOOGLE_API_KEY')
llmg = GooglePalm(google_api_key=google_api_key)
llmg.temperature = 0.1
google_palm_embeddings = GooglePalmEmbeddings(google_api_key=google_api_key)

# openai  api keys
openai.api_key  = os.environ.get("OPENAI_API_KEY")
os.environ['OPENAI_API_KEY'] = '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'
llmo = OpenAI(temperature=0.1, max_tokens=500)

# prompts = ['Explain the difference between effective and affective with examples']
# llm_result = llm._generate(prompts)

# Encoder initialization (choose one)
# encoder = SentenceTransformer("all-mpnet-base-v2")
# encoder = SentenceTransformer("all-MiniLM-L6-v2")

# Specify the directory path for Chroma's persistent storage
chroma_dir = '/Users/rajes/LLM/lbg/chroma_google_db'
pdf_directory_path = '/Users/rajes/LLM/lbg/pdf/'

def print_files_in_directory(directory_path):
    # List all files and directories in the specified path
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            st.sidebar.text(filename)

def get_similar_queries(user_question):
           # Replace the hardcoded question with the user-provided one
    question = user_question
    google_palm_embeddings = GooglePalmEmbeddings(google_api_key=google_api_key)
    loadchroma = Chroma(persist_directory=chroma_dir, embedding_function=google_palm_embeddings)
    set_verbose(False)
    set_debug(False)
    #llm = GooglePalm(google_api_key=google_api_key)
    llmg.temperature = 0
    retriever_from_llm = MultiQueryRetriever.from_llm(
        retriever=loadchroma.as_retriever(), llm=llmg
    )

    # Generate the queries
    unique_docs = retriever_from_llm.get_relevant_documents(query=question)
    st.subheader("Generated Similar Queries")
    queries_markdown = "\n\n".join(f"- {query}" for query in capture_handler.generated_queries)
    st.markdown(queries_markdown)
    # Optionally clear the captured queries to prepare for the next operation
    capture_handler.generated_queries.clear()

def get_google_results(user_question, temperature):
    try:
        google_palm_embeddings = GooglePalmEmbeddings(google_api_key=google_api_key)
        loadchroma = Chroma(persist_directory=chroma_dir, embedding_function=google_palm_embeddings)
        set_verbose(False)
        set_debug(False)
        #llm = GooglePalm(google_api_key=google_api_key)
        llmg.temperature = temperature

        prompt_template = """Given the following context and a question, generate an answer based on this context only.
        In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
        If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

        CONTEXT: {context}

        QUESTION: {question}"""


        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": PROMPT}

        chain = RetrievalQA.from_chain_type(llm=llmg,
                                    chain_type="stuff",
                                    retriever=loadchroma.as_retriever(),
                                    input_key="query",
                                    return_source_documents=True,
                                    chain_type_kwargs=chain_type_kwargs)        

        result =chain(user_question)
        st.subheader("Google Response:")
        if 'result' in result:
            st.write(result['result'])
            
            if result['result'].strip() != "I don't know.":
                # Display sources, only if LLM response available
                unique_sources = set()
                if 'source_documents' in result:
                    for i in  result['source_documents']:
                        unique_sources.add(i.metadata['source'])

                    for source in unique_sources:
                        #print(source)
                        st.write(source)
        else:
            st.write("No result found.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        
def get_openai_results(user_question, temperature, max_tokens):
    try:
        google_palm_embeddings = GooglePalmEmbeddings(google_api_key=google_api_key)
        loadchroma = Chroma(persist_directory=chroma_dir, embedding_function=google_palm_embeddings)
        set_verbose(False)
        set_debug(False)
        # Initialise LLM with required params
        llmo = OpenAI(temperature=temperature, max_tokens=max_tokens) 
        chain = RetrievalQAWithSourcesChain.from_llm(llm=llmo, retriever=loadchroma.as_retriever())
        #chain
        result = chain({"question": user_question}, return_only_outputs=True)
        st.subheader("OpenAI Response:")
        st.write(result["answer"])
#         if 'result' in result:
#             st.write(result["answer"])
#         else:
#             st.write("No result found.")
            
        # Display sources, if available
        sources = result.get("sources", "")
        if sources:
            #st.subheader("Sources:")
            sources_list = sources.split("\n")
            for source in sources_list:
                st.write(source)
    except Exception as e:
        st.error(f"An error occurred: {e}")
            
#pdflist = print_files_in_directory(pdf_directory_path)

# Streamlit interface setup
st.title("Krishna GPT")
st.sidebar.title("Krishna Books Loaded")
print_files_in_directory(pdf_directory_path)

#st.write(pdflist)
#st.text("new text")
output_placeholder = st.empty()
user_question = st.text_input("Ask your question:")

# New temperature input field
temperature_input = st.sidebar.text_input("Enter temperature value (between 0.0 and 1.0):", "0.1")
try:
    temperature = float(temperature_input)
    if not 0.0 <= temperature <= 1.0:
        st.error("Temperature must be between 0.0 and 1.0")
        raise ValueError("Temperature out of bounds")
except ValueError:
    st.error("Invalid temperature value. Please enter a number between 0.0 and 1.0.")

# New token input field   
token_input = st.sidebar.text_input("Enter token value (between 100 and 2000):", "500")
try:
    max_tokens = int(token_input) 
    if not 100 <= max_tokens <= 2000:
        st.error("Token must be between 100 and 2000")
        raise ValueError("Token out of bounds")
except ValueError:
    st.error("Invalid token value. Please enter a number between100 and 2000.")

# User-selectable options for verbose and debug logging
# enable_verbose = st.sidebar.checkbox("Enable verbose logging")
# enable_debug = st.sidebar.checkbox("Enable debug logging")


if st.button("Generate similar queries"):
    if user_question:  # Ensure there is a question to process
        # Replace the hardcoded question with the user-provided one
        get_similar_queries(user_question)
    else:
        st.error("Please enter a question to generate similar queries.")

submit_button = st.button("Submit")
if submit_button and user_question:
    # Ensure the temperature is within the valid range before proceeding
    if 0.0 <= temperature <= 1.0:
        get_openai_results(user_question, temperature, max_tokens)
        get_google_results(user_question, temperature)

        # Place this after the code that generates logs
        
#         if enable_verbose or enable_debug:
#             st.subheader("Logs:")
#             for log_msg in streamlit_handler.get_logs():
#                 st.text(log_msg)

