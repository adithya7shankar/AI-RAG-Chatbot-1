import sys
import types
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask

# External LLM services are mocked; this test must never call a paid API.
gpt_module = types.ModuleType('services.gpt_service')
gpt_module.GPTService = MagicMock()
gpt_module.GPTService.return_value.generate_response.return_value = 'answer'
lc_module = types.ModuleType('services.langchain_service')
lc_module.LangChainService = MagicMock()
lc_module.LangChainService.return_value.retrieve_documents.return_value = ['source text']
with patch.dict(sys.modules, {'services.gpt_service':gpt_module, 'services.langchain_service':lc_module}):
    from routes.chat import chat_bp
    from routes.rag import rag_bp

class RouteTests(unittest.TestCase):
    def setUp(self):
        # Reset mocks to ensure clean state for each test
        lc_module.LangChainService.return_value.retrieve_documents.reset_mock()
        lc_module.LangChainService.return_value.retrieve_documents.return_value = ['source text']
        gpt_module.GPTService.return_value.generate_response.reset_mock()
        gpt_module.GPTService.return_value.generate_response.return_value = 'answer'

        app=Flask(__name__);app.register_blueprint(chat_bp,url_prefix='/chat');app.register_blueprint(rag_bp,url_prefix='/rag');self.client=app.test_client()

    def test_invalid_bodies_are_client_errors(self):
        for route,field in [('/chat','message'),('/chat/book-search','query'),('/rag','query')]:
            for body in [None, [], 'text', {}, {field:123}, {field:'  '}]:
                with self.subTest(route=route,body=body):
                    response=self.client.post(route,data=__import__('json').dumps(body),content_type='application/json')
                    self.assertEqual(response.status_code,400)
            self.assertEqual(self.client.post(route,data='{',content_type='application/json').status_code,400)

    def test_rag_returns_retrieved_sources(self):
        response=self.client.post('/rag',json={'query':' hello '})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['results'],['source text'])
        lc_module.LangChainService.return_value.retrieve_documents.assert_called_with('hello')
        gpt_module.GPTService.return_value.generate_response.assert_called_once_with('hello', context=['source text'])

    def test_rag_empty_documents_returns_503(self):
        lc_module.LangChainService.return_value.retrieve_documents.return_value = []
        response=self.client.post('/rag',json={'query':' hello '})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json['results'],[])
        self.assertIn('error', response.json)
        gpt_module.GPTService.return_value.generate_response.assert_not_called()
