from flask import Blueprint, request, jsonify
from services.gpt_service import GPTService
from services.langchain_service import LangChainService

chat_bp = Blueprint('chat', __name__)

gpt_service = GPTService()
langchain_service = LangChainService()

@chat_bp.route('', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    # Get response from GPT
    gpt_response = gpt_service.generate_response(user_message)

    return jsonify({'response': gpt_response})

@chat_bp.route('/book-search', methods=['POST'])
def book_search():
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    # Retrieve documents using LangChain
    documents = langchain_service.retrieve_documents(query)

    return jsonify({'results': documents})
