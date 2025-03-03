from flask import Blueprint, request, jsonify
from services.langchain_service import LangChainService
from services.gpt_service import GPTService

rag_bp = Blueprint('rag', __name__)
langchain_service = LangChainService()
gpt_service = GPTService()

@rag_bp.route('', methods=['POST'])
def rag_interaction():
    data = request.json
    user_query = data.get('query')
    
    if not user_query:
        return jsonify({'error': 'Query is required'}), 400

    # Retrieve relevant documents using LangChain
    documents = langchain_service.get_response(user_query)

    # Generate a response using GPT with context from documents
    response = gpt_service.generate_response(user_query, context=documents)

    return jsonify({'response': response, 'results': documents}), 200
