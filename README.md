# AI-RAG-Chatbot

## Overview
The AI RAG - Discord Chatbot is a real-time AI-powered chatbot for Discord that integrates Retrieval-Augmented Generation (RAG) for book-based assistance and conversational AI. It leverages Flask microservices and GPT-based LLMs, optimizing efficiency with PostgreSQL and Docker.

## Project Structure
```
AI-RAG-Chatbot/
├── backend/
│   ├── app.py
│   ├── routes/
│   │   ├── chat.py
│   │   ├── rag.py
│   ├── models/
│   │   ├── database.py
│   │   ├── documents.py
│   ├── services/
│   │   ├── langchain_service.py
│   │   ├── gpt_service.py
│   ├── config.py
│   ├── Dockerfile
│   ├── requirements.txt
├── discord_bot/
│   ├── bot.py
│   ├── commands/
│   │   ├── chat.py
│   │   ├── help.py
│   ├── config.py
├── database/
│   ├── init.sql
├── deployment/
│   ├── docker-compose.yml
└── README.md
```

## 1. Backend - Flask Microservices
- **Framework**: Flask
- **APIs**: REST API for LLM interactions
- **Integration**: LangChain for RAG, OpenAI GPT-3.5-turbo for conversation
- **Storage**: PostgreSQL for document management

### Setup Flask Backend
- **app.py**: Entry point for the Flask application, defining routes for chat and RAG interactions.

### GPT Service
- **gpt_service.py**: Handles communication with OpenAI's GPT model for generating responses.

### RAG with LangChain
- **langchain_service.py**: Implements RAG functionality using LangChain for document retrieval.

## 2. Database - PostgreSQL Integration
- **ORM**: SQLAlchemy
- **Tables**: User messages, document embeddings

### Database Configuration
- **database.py**: Configures the database connection and defines the Document model for storing documents.

## 3. Discord Bot - AI-Powered Interactions
- **Framework**: discord.py
- **Commands**: /ask, /book-search

### Bot Setup
- **bot.py**: Main file for the Discord bot, defining commands for interacting with the backend.

## 4. Deployment - Docker & AWS
### Dockerfile (Backend)
- **Dockerfile**: Defines the Docker image for the Flask backend.

### Docker Compose
- **docker-compose.yml**: Configures services for the backend and PostgreSQL database.

### AWS Deployment
- **EC2**: Deploy Flask app & PostgreSQL
- **Docker Compose**: Used for container orchestration
- **Cloud Storage**: Use S3 for logs, files

## Evaluation status

This repository does not include a reproducible benchmark supporting its former
latency, concurrency, retrieval-accuracy or database-speedup numbers. Those numbers
have been removed. Offline regression tests establish specific behavior; they do
not establish deployment capacity or answer quality.

### Discord command behavior

`/ask <question>` requests a document-backed answer from `POST /rag`.
`/book-search <query>` retrieves matching passages from `POST /chat/book-search`
without generating an answer. These are prefix commands, not registered Discord
application slash commands. Enable Message Content Intent for the bot.

Backend requests run outside the Discord event loop, with connection/read timeouts
of 3/30 seconds. Long output is split for Discord, mentions are suppressed, and
unavailable or malformed backend responses get a neutral error. Extensions load
through Discord.py 2's asynchronous setup hook; the custom help command replaces
the default one.

From the repository root, run `python discord_bot/bot.py` with `DISCORD_TOKEN`
and `BACKEND_API_URL` set. The bot's configuration and extensions are resolved
relative to its files. Inside Compose, `BACKEND_API_URL` must point to the backend
service, for example `http://backend:5000`, rather than the bot container itself.

Run bot tests from the repository root:

```sh
python -m unittest discover -s discord_bot/tests -v
```

These tests load the real Discord command extensions and mock HTTP requests.
They do not log in to Discord or contact an LLM provider.

### Retrieval failure behavior

`POST /rag` generates an answer only when retrieval returns source documents.
An empty corpus, unavailable vector store, or retrieval failure returns HTTP 503
with an error and `results: []`, without calling the generation service. Error
messages and empty-corpus placeholders are not indexed as source evidence.
A successful response keeps the existing `response` and `results` shape.
This guard prevents generation without retrieved context; it does not establish
that every retrieved passage is relevant or that the generated answer is correct.

Run the offline regression checks from `backend/`:

```sh
python -m unittest test_routes test_retrieval_failures -v
```

These tests use fake service dependencies and never contact embedding or LLM
providers. They do not validate the repository's legacy provider integrations.
