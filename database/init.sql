-- SQL script to initialize the database for the AI-RAG-Chatbot project

-- Create a table for storing user messages
CREATE TABLE user_messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for storing document embeddings
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    embedding FLOAT8[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for storing documents
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on the user_messages table for faster retrieval
CREATE INDEX idx_user_messages_user_id ON user_messages (user_id);

-- Create an index on the document_embeddings table for faster retrieval
CREATE INDEX idx_document_embeddings_document_id ON document_embeddings (document_id);