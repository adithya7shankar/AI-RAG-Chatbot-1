from flask import Blueprint, request, jsonify
from routes.validation import required_text
from services.langchain_service import LangChainService
from services.gpt_service import GPTService

rag_bp = Blueprint('rag', __name__)
langchain_service = LangChainService()
gpt_service = GPTService()

@rag_bp.route('', methods=['POST'])
def rag_interaction():
    user_query = required_text('query')
    
    if not user_query:
        return jsonify({'error': 'Query is required'}), 400

    # Retrieve relevant documents using LangChain
    documents = langchain_service.retrieve_documents(user_query)

    # If no documents are retrieved, return 503 without generating a response
    if not documents:
        return jsonify({'error': 'No source documents are available to answer this query', 'results': []}), 503

    # Generate a response using GPT with context from documents
    response = gpt_service.generate_response(user_query, context=documents)

    return jsonify({'response': response, 'results': documents}), 200
