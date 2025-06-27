
import os
import sys
import pandas as pd
import numpy as np
import sys
import logging
import streamlit as st
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources.loading import load_qa_with_sources_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.globals import set_debug
from langchain.globals import set_verbose
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import json
import hashlib
import requests

# os.environ['GOOGLE_API_KEY'] = 'AIzaSyDG8Hh3JEAwWKdXz5j6yjJL2GKOlUy_7es'
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")
sys.path.append('../..')
_ = load_dotenv(find_dotenv()) # read local .env file

class EmbeddingModels:
    def __init__(self, model):
        self.model = model
    
    def embeddingmodel(self, model):
        self.model = model
        if model == "gemini-1.5-pro":
            return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        elif self.model == "deepseek-r1:8b":
            from langchain.embeddings import OllamaEmbeddings
            return OllamaEmbeddings(model="deepseek-r1:8b")
        else:
            raise ValueError(f"Model {model} not supported.")


class LoadDocs:
    # def __init__(self, chroma_dir, query):
    # We could use this if we did not load the llmsynthesizer in the __init__.py file
    # but then we will have to pass these parameters to even run load docs.
    #     self.chroma_dir = chroma_dir
    #     self.query = query
    #     self.LlmSynthesis = LlmSynthesis(self.chroma_dir, self.query)

    def process_and_store_pdfs(self,directory_path, chroma_dir, model):
        self.directory_path = directory_path
        self.chroma_dir = chroma_dir
        self.model = model
        # Initialize your embeddings object
        # embedding = self.embeddingmodel(model)  
        embedding = EmbeddingModels.embeddingmodel(self, model)
        
        # Assuming vectordb should be initialized once and reused
        vectordb = None
        # print('1')
        # Loop through all the files in the specified directory
        for filename in os.listdir(directory_path):
            # print('2')
            # print(filename)
            if filename.endswith('.pdf'):
                # Construct the full file path
                file_path = os.path.join(directory_path, filename)
                # print(file_path)
                try:
                    # Open the PDF file
                    unique_id = self.generate_unique_id(file_path)
                    # print(f'Processing {filename}...')
                    if self.check_book_processed(unique_id):
                        print(f'Book {file_path} has already been processed.')
                        # return
                    else:
                        loader = PyPDFLoader(file_path) 
                        pages = loader.load()
                        print(f'Processing {filename}...')

                        # Extract text from each page and store in a list
                        #splits = [page.extract_text() for page in pdf_reader.pages if page.extract_text() is not None]
                        r_splitter = RecursiveCharacterTextSplitter(
                        separators = ["\n\n", "\n", ".",","],  # List of separators based on requirement (defaults to ["\n\n", "\n", " "])
                        chunk_size = 500,  # size of each chunk created
                        chunk_overlap  = 75,  # size of  overlap between chunks in order to maintain the context
                        length_function = len  # Function to calculate size, currently we are using "len" which denotes length of string however you can pass any token counter)
                        )
                        docs = r_splitter.split_documents(pages)
                        splits=docs

                        # If this is the first PDF, initialize vectordb with its content
                        if vectordb is None:
                            vectordb = Chroma.from_documents(documents=splits, embedding=embedding, persist_directory=chroma_dir)
                        else:
                            # For subsequent PDFs, add their content to the existing vectordb
                            vectordb.add_documents(documents=splits, embedding=embedding)

                        # Optional: Persist after each PDF if desired, or do it once after all PDFs are processed
                        vectordb.persist()
                        # After successful loading
                        self.update_processed_books(unique_id)
                        print(f'Book {file_path} successfully loaded and recorded.')
                    
                except Exception as e:
                    print(f'Failed to process {filename}: {e}')
        
        # Persist the database after all PDFs have been processed
        if vectordb is not None:
            vectordb.persist()
            print('All PDFs have been processed and stored in Chroma.')

    def generate_unique_id(self,book_path):
        # print('generate_unique_id')
        self.book_path = book_path
        # Example using the file path to generate a unique ID
        return hashlib.sha256(book_path.encode('utf-8')).hexdigest()

    def check_book_processed(self,unique_id, record_file='processed_books.json'):
        # print('check_book_processed')
        self.unique_id = unique_id
        self.record_file = record_file
        try:
            with open(record_file, 'r') as file:
                processed_books = json.load(file)
        except FileNotFoundError:
            processed_books = []

        return unique_id in processed_books

    def update_processed_books(self,unique_id, record_file='processed_books.json'):
        # print('update_processed_books')
        self.unique_id = unique_id
        self.record_file = record_file
        try:
            with open(record_file, 'r') as file:
                processed_books = json.load(file)
        except FileNotFoundError:
            processed_books = []

        processed_books.append(unique_id)

        with open(record_file, 'w') as file:
            json.dump(processed_books, file)

    ### method to load all pdf and convert them to embedding and store in the chroma db on disk


class LlmSynthesis:
    def __init__(self,chroma_dir, query,model):
        self.chroma_dir = chroma_dir
        self.query = query
        self.model = model
        # embedding = embeddings
        
    def generate_synthesis(self,chroma_dir, query, model):
        self.chroma_dir = chroma_dir
        self.query = query
        self.model = model
       
        set_verbose(False)
        set_debug(False)
        embedding = EmbeddingModels.embeddingmodel(self, model)
       
        loadchroma = Chroma(persist_directory=chroma_dir, embedding_function=embedding)

        llm = self.llm_in_use(model)
        llm.temperature = 0.9

        prompt_template = self.prompt_template()
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain_type_kwargs = {"prompt": PROMPT}

        chain = RetrievalQA.from_chain_type(llm=llm,
                                    chain_type="stuff",
                                    retriever=loadchroma.as_retriever(),
                                    input_key="query",
                                    return_source_documents=True,
                                    chain_type_kwargs=chain_type_kwargs)

        
        result = chain (query)
        return result['result']
        
    def llm_in_use(self, model):
        self.model = model
        if model == "gemini-1.5-pro":
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2 #,     # other params...
                )
        elif self.model == "deepseek-r1:8b":
            from langchain.chains import RetrievalQA
            from langchain.llms import Ollama
            return Ollama(model="deepseek-r1:8b")
        else:
            raise ValueError(f"Model {model} not supported.")
    
    def prompt_template(self):
        return """Given the following context and a question, generate an answer based on this context only.
        In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
        If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

        CONTEXT: {context}

        QUESTION: {question}"""
        

