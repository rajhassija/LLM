import openai
import os
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class RAGFramework:
    def __init__(self):
        # Set API key globally
        # self.api_key = os.getenv("GOOGLE_API_KEY")
        self.api_key = "AIzaSyDG8Hh3JEAwWKdXz5j6yjJL2GKOlUy_7es" 
        if not self.api_key:
            raise ValueError("Missing API key for gemini-1.5-pro-001 Please set GOOGLE_API_KEY.")
        os.environ['GOOGLE_API_KEY'] = self.api_key
        
        self.input_component = InputComponent()
        self.input_guardrail = InputGuardrail()
        self.embedding_component = EmbeddingComponent()
        self.vector_db = VectorDatabase()
        self.vector_search = VectorSearch(self.vector_db)
        self.knowledge_graph = KnowledgeGraph()
        self.retriever = Retriever(self.vector_search)
        self.re_ranker = ReRanker()
        
        self.llms = {
            "gemini-1.5-pro-001": LLMComponent(model="gemini-1.5-pro-001", api_key=self.api_key),
            "deepseek-r1:8b": LLMComponent(model="deepseek-r1:8b")
        }
        self.response_generator = ResponseGenerator(self.llms)
        self.output_guardrail = OutputGuardrail()

    def run(self, query: str, llm_name="gemini-1.5-pro-001"):
        query = self.input_component.process(query)
        query = self.input_guardrail.validate(query)
        query_vector = self.embedding_component.embed_query(query)
        print("Query Embedding:", query_vector)  # Debugging step
        retrieved_docs = self.retriever.retrieve(query_vector)
        
        if not retrieved_docs or len(retrieved_docs) == 0:
            print("No relevant documents found. Proceeding with direct LLM response.")
            ranked_docs = []  # No context provided to LLM
        else:
            enriched_docs = self.knowledge_graph.enrich(retrieved_docs)
            ranked_docs = self.re_ranker.rerank(enriched_docs)
        
        response = self.response_generator.generate(query, ranked_docs, llm_name)
        response = self.output_guardrail.validate(response)
        print("Final response:", response)
        return response
    
    # def ingest_document(self, doc_id: str, text: str):
    #     """Embed and store a document in the vector database."""
    #     print(f"Ingesting document: {doc_id}")
    #     vector = self.embedding_component.embed_query(text)  # Generate embedding
    #     metadata = {"text": text}  # Store document text as metadata
    #     self.vector_db.store(doc_id, vector, metadata)  # Store in ChromaDB
    #     print(f"Document {doc_id} stored successfully.")

    # def ingest_document(self, doc_id: str, text: str):
    #     """Embed and store a document in the vector database."""
    #     print(f"Ingesting document: {doc_id}")
    #     vector = self.embedding_component.embed_query(text)  # Generate embedding
    #     print(f"Generated Embedding for {doc_id}:", vector)  # Debugging step
    #     metadata = {"text": text}  # Store document text as metadata
    #     self.vector_db.store(doc_id, vector, metadata)  # Store in ChromaDB
    #     print(f"Document {doc_id} stored successfully.")

    def ingest_document(self, doc_id: str, text: str):
        """Embed and store a document in the vector database."""
        print(f"Ingesting document: {doc_id}")
        
        vector = self.embedding_component.embed_query(text)  # Generate embedding
        if not vector or len(vector) == 0:
            print(f"Error: No embedding generated for {doc_id}.")
            return
        
        print(f"Generated Embedding for {doc_id}:", vector)  # Debugging step
        metadata = {"text": text}  # Store document text as metadata
        self.vector_db.store(doc_id, vector, metadata)  # Store in ChromaDB
        print(f"Document {doc_id} stored successfully.")


class InputComponent:
    def process(self, query: str):
        print("Processing input query")
        return query

class InputGuardrail:
    def validate(self, query: str):
        print("Validating query")
        return query

# class EmbeddingComponent:
#     def __init__(self, model="models/embedding-001"):
#         self.model = model
#         self.embedder = GoogleGenerativeAIEmbeddings(model=self.model)
    
#     def embed_query(self, query: str):
#         print("Generating embedding for query")
#         return self.embedder.embed_query(query)

class EmbeddingComponent:
    def __init__(self, model="models/embedding-001"):
        self.model = model
        self.embedder = GoogleGenerativeAIEmbeddings(model=self.model)

    def embed_query(self, query: str):
        print(f"Generating embedding for query: {query}")
        vector = self.embedder.embed_query(query)
        if not vector or len(vector) == 0:
            print("Error: No embedding generated!")
        return vector


class VectorDatabase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="documents")
    
    def store(self, doc_id: str, vector, metadata: dict):
        print(f"Storing document {doc_id} in vector database")
        self.collection.add(ids=[doc_id], embeddings=[vector], metadatas=[metadata])
    
    def retrieve(self, query_vector, top_k=3):
        print("Retrieving relevant vectors")
        results = self.collection.query(query_embeddings=[query_vector], n_results=top_k)
        return results.get("documents", [])

class VectorSearch:
    def __init__(self, vector_db):
        self.vector_db = vector_db
    
    def search(self, query_vector):
        print("Searching vector database")
        return self.vector_db.retrieve(query_vector)

class KnowledgeGraph:
    def enrich(self, retrieved_data):
        print("Enriching data with knowledge graph")
        return retrieved_data

# class Retriever:
#     def __init__(self, vector_search):
#         self.vector_search = vector_search

#     def retrieve(self, query_vector):
#         print("Retrieving documents")
#         retrieved_docs = self.vector_search.search(query_vector)
        
#         if not retrieved_docs or len(retrieved_docs) == 0:
#             print("No relevant documents found in vector DB.")
#             return []  # Return empty list when no relevant data is found

#         return retrieved_docs

class Retriever:
    def __init__(self, vector_search):
        self.vector_search = vector_search

    def retrieve(self, query_vector):
        print("Retrieving documents")
        result = self.vector_search.search(query_vector)
        print("Result:", result)  # Debugging step

        # Ensure result is a list and has at least two elements
        if not isinstance(result, list) or len(result) < 2 or not isinstance(result[0], list):
            print("No valid documents found in vector DB.")
            return [], []

        retrieved_docs = result[0] if isinstance(result[0], list) else []
        retrieved_metadata = result[1] if len(result) > 1 and isinstance(result[1], list) else []

        return retrieved_docs, retrieved_metadata


    
class ReRanker:
    def rerank(self, documents):
        print("Re-ranking documents")
        return documents

class LLMComponent:
    def __init__(self, model="gemini-1.5-pro-001", api_key=None):
        self.model = model
        self.api_key = api_key

    def generate_response(self, query: str, context: str):
        full_prompt = f"User Query: {query}\n\nContext:\n{context}\n\nProvide a concise response based on the above context."
        print("Full Prompt:", full_prompt)
        if self.model == "gemini-1.5-pro-001":
            print(f"Generating response using LLM: {self.model}")
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model=self.model)
            ai_msg = llm.invoke(full_prompt)
            print("AI Message:", ai_msg)
            return ai_msg.content
        elif self.model == "deepseek-r1:8b":
            print(f"Generating response using LLM: {self.model}")
            import requests
            url = os.getenv("DEESEEK_API_URL", "http://localhost:11434/api/generate")
            headers = {"Content-Type": "application/json"}
            data = {"model": self.model, "prompt": full_prompt, "stream": False}
            response = requests.post(url, json=data, headers=headers)
            return response.json().get("response", "Error: Invalid response from API")
        
    
        
class ResponseGenerator:
    def __init__(self, llms):
        self.llms = llms  # Dictionary of LLMs
    
    def generate(self, query, ranked_documents, llm_name="gemini-1.5-pro-001"):
        print(f"Generating response using LLM: {llm_name}")
        
        # Flatten ranked_documents to ensure all elements are strings
        flattened_documents = []
        for doc in ranked_documents:
            if isinstance(doc, list):  
                flattened_documents.extend(doc)  # Expand nested lists
            else:
                flattened_documents.append(doc)
        
        context = "\n".join(flattened_documents) if flattened_documents else ""
        
        llm = self.llms.get(llm_name)
        if not llm:
            raise ValueError(f"LLM '{llm_name}' not available.")
        
        return llm.generate_response(query, context)


class OutputGuardrail:
    def validate(self, response):
        print("Validating response")
        return response

# # setx GOOGLE_API_KEY "AIzaSyDG8Hh3JEAwWKdXz5j6yjJL2GKOlUy_7es"
# # setx DEESEEK_API_URL "http://localhost:11434/api/generate"
