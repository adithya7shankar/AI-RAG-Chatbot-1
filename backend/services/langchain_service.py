# filepath: AI-RAG-Chatbot/backend/services/langchain_service.py

import os
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Document, db
from flask import current_app
import logging

class LangChainService:
    def __init__(self, api_key=None):
        # Try to get API key from parameter, environment variable, or Flask config
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        
        # If still no API key, try to get from Flask config (only works in request context)
        if not self.api_key:
            try:
                self.api_key = current_app.config.get('OPENAI_API_KEY')
            except RuntimeError:
                # Not in Flask context, will need to set API key later
                pass
        
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None
        
        if self.api_key:
            self.initialize_services()
    
    def initialize_services(self):
        try:
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            self.vector_store = self.initialize_vector_store()
            
            # Use OpenAI LLM instead of embeddings for text generation
            llm = OpenAI(openai_api_key=self.api_key)
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever()
            )
        except Exception as e:
            self.log_error(f"Error initializing LangChain services: {e}")

    def initialize_vector_store(self):
        try:
            # Get database URL from environment or config
            db_url = os.environ.get('DATABASE_URL')
            if not db_url:
                try:
                    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
                except RuntimeError:
                    # Not in Flask context
                    db_url = 'sqlite:///default.db'  # Fallback
            
            # Create engine and session
            engine = create_engine(db_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Query documents
            documents = session.query(Document).all()
            document_texts = [doc.content for doc in documents]  # Using 'content' instead of 'text'
            session.close()
            
            # Create a FAISS vector store if we have documents
            if document_texts:
                vector_store = FAISS.from_texts(document_texts, self.embeddings)
                return vector_store
            else:
                # Create an empty vector store with a dummy document if no documents exist
                vector_store = FAISS.from_texts(["No documents available"], self.embeddings)
                return vector_store
                
        except Exception as e:
            self.log_error(f"Error initializing vector store: {e}")
            # Return a minimal vector store with a dummy document
            return FAISS.from_texts(["Error loading documents"], self.embeddings)

    def get_response(self, query):
        """Get a response using the QA chain"""
        try:
            if not self.qa_chain:
                self.initialize_services()
                
            if self.qa_chain:
                response = self.qa_chain.run(query)
                return response
            else:
                return "Sorry, the QA service is not available at this time."
        except Exception as e:
            self.log_error(f"Error getting response: {e}")
            return "Sorry, I couldn't process your query at this time."
    
    def retrieve_documents(self, query):
        """Retrieve relevant documents for a query"""
        try:
            if not self.vector_store:
                self.initialize_services()
                
            if self.vector_store:
                docs = self.vector_store.similarity_search(query, k=5)
                return [doc.page_content for doc in docs]
            else:
                return ["Sorry, the document retrieval service is not available at this time."]
        except Exception as e:
            self.log_error(f"Error retrieving documents: {e}")
            return ["Sorry, I couldn't retrieve documents at this time."]
    
    def log_error(self, message):
        """Log errors, handling both Flask and non-Flask contexts"""
        try:
            current_app.logger.error(message)
        except RuntimeError:
            # Not in Flask context
            print(f"ERROR: {message}")
