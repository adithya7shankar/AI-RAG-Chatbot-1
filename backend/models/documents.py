# filepath: AI-RAG-Chatbot/backend/models/documents.py

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True)  # Store embeddings as text or JSON
    created_at = Column(Integer, nullable=False)  # Timestamp for creation

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title})>"