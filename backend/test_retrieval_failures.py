"""Exercise the real service logic without embedding or LLM API calls."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


class RetrievalFailureTests(unittest.TestCase):
    def setUp(self):
        exports = {
            'langchain.llms': ['OpenAI'],
            'langchain.document_loaders': ['TextLoader'],
            'langchain.embeddings': ['OpenAIEmbeddings'],
            'langchain.vectorstores': ['FAISS'],
            'langchain.chains': ['RetrievalQA'],
            'sqlalchemy': ['create_engine'],
            'sqlalchemy.orm': ['sessionmaker'],
            'models.database': ['Document', 'db'],
        }
        modules = {}
        for name, names in exports.items():
            module = types.ModuleType(name)
            for export in names:
                setattr(module, export, MagicMock())
            modules[name] = module
        source = Path(__file__).parent / 'services/langchain_service.py'
        spec = importlib.util.spec_from_file_location('retrieval_under_test', source)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(self.module)
        self.service = self.module.LangChainService.__new__(self.module.LangChainService)
        self.service.embeddings = MagicMock()
        self.service.vector_store = None
        self.service.qa_chain = None
        self.service.log_error = MagicMock()
        self.module.os = types.SimpleNamespace(environ={'DATABASE_URL': 'sqlite://'})

    def test_empty_corpus_does_not_embed_placeholder_text(self):
        session = self.module.sessionmaker.return_value.return_value
        session.query.return_value.all.return_value = []
        self.assertIsNone(self.service.initialize_vector_store())
        self.module.FAISS.from_texts.assert_not_called()
        session.close.assert_called_once()

    def test_database_failure_does_not_embed_an_error_message(self):
        self.module.create_engine.side_effect = RuntimeError('private diagnostic')
        self.assertIsNone(self.service.initialize_vector_store())
        self.module.FAISS.from_texts.assert_not_called()

    def test_empty_corpus_does_not_construct_a_qa_chain(self):
        self.service.api_key = 'not-a-real-key'
        self.service.initialize_vector_store = MagicMock(return_value=None)
        self.service.initialize_services()
        self.assertIsNone(self.service.qa_chain)
        self.module.RetrievalQA.from_chain_type.assert_not_called()

    def test_retrieval_failure_returns_no_evidence(self):
        self.service.vector_store = MagicMock()
        self.service.vector_store.similarity_search.side_effect = RuntimeError('private diagnostic')
        self.assertEqual(self.service.retrieve_documents('question'), [])

    def test_retrieval_success_keeps_source_content(self):
        self.service.vector_store = MagicMock()
        self.service.vector_store.similarity_search.return_value = [types.SimpleNamespace(page_content='real source')]
        self.assertEqual(self.service.retrieve_documents('question'), ['real source'])


if __name__ == '__main__':
    unittest.main()
