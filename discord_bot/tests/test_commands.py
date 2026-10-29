import importlib.util
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import requests

BOT_DIR = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rag_commands_under_test', BOT_DIR / 'commands/chat.py')
chat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chat)


class CommandTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.cog = chat.ChatCommand(None)
        self.ctx = MagicMock(send=AsyncMock())

    async def ask(self):
        await self.cog.ask.callback(self.cog, self.ctx, question='a question')

    def assert_neutral_error(self):
        message = self.ctx.send.call_args.args[0]
        self.assertEqual(message, "Sorry, I couldn't process your request.")

    async def test_ask_uses_rag_off_event_loop_with_timeout(self):
        main_thread = threading.get_ident()
        threads = []
        response = MagicMock(status_code=200)
        response.json.return_value = {'response': 'a grounded answer'}
        def post(*args, **kwargs):
            threads.append(threading.get_ident())
            return response
        with patch.object(chat.requests, 'post', side_effect=post) as request:
            await self.ask()
        request.assert_called_once_with(chat.config.BACKEND_API_URL + '/rag', json={'query': 'a question'}, timeout=(3, 30))
        self.assertNotEqual(threads[0], main_thread)
        self.assertEqual(self.ctx.send.call_args.args[0], 'a grounded answer')

    async def test_search_retrieves_without_calling_generation_route(self):
        response = MagicMock(status_code=200)
        response.json.return_value = {'results': ['first passage', 'second passage']}
        with patch.object(chat.requests, 'post', return_value=response) as request:
            await self.cog.book_search.callback(self.cog, self.ctx, query='a book')
        request.assert_called_once_with(chat.config.BACKEND_API_URL + '/chat/book-search', json={'query': 'a book'}, timeout=(3, 30))
        self.assertEqual(self.ctx.send.call_args.args[0], 'first passage\nsecond passage')

    async def test_long_output_is_complete_and_mentions_are_disabled(self):
        text = '@everyone ' + 'x' * 5000
        response = MagicMock(status_code=200)
        response.json.return_value = {'response': text}
        with patch.object(chat.requests, 'post', return_value=response):
            await self.ask()
        chunks = [call.args[0] for call in self.ctx.send.call_args_list[1:]]
        self.assertEqual(''.join(chunks), text)
        self.assertTrue(all(0 < len(chunk) <= 1900 for chunk in chunks))
        for call in self.ctx.send.call_args_list:
            mentions = call.kwargs['allowed_mentions']
            self.assertFalse(mentions.everyone or mentions.users or mentions.roles or mentions.replied_user)

    async def test_timeout_does_not_expose_diagnostics(self):
        with patch.object(chat.requests, 'post', side_effect=requests.Timeout('sensitive detail')):
            await self.ask()
        self.assert_neutral_error()

    async def test_unavailable_or_malformed_answers_fail_neutrally(self):
        for body in [None, [], {}, {'response': 5}, {'response': '   '}]:
            with self.subTest(body=body):
                response = MagicMock(status_code=200)
                response.json.return_value = body
                with patch.object(chat.requests, 'post', return_value=response):
                    await self.ask()
                self.assert_neutral_error()
        response = MagicMock(status_code=503)
        with patch.object(chat.requests, 'post', return_value=response):
            await self.ask()
        response.json.assert_not_called()
        self.assert_neutral_error()
        response = MagicMock(status_code=200)
        response.json.side_effect = ValueError('bad JSON')
        with patch.object(chat.requests, 'post', return_value=response):
            await self.ask()
        self.assert_neutral_error()

    async def test_search_distinguishes_empty_from_malformed_results(self):
        for results in [None, 'text', [7], ['passage', 7]]:
            response = MagicMock(status_code=200)
            response.json.return_value = {'results': results}
            with patch.object(chat.requests, 'post', return_value=response):
                await self.cog.book_search.callback(self.cog, self.ctx, query='book')
            self.assert_neutral_error()
        response.json.return_value = {'results': []}
        with patch.object(chat.requests, 'post', return_value=response):
            await self.cog.book_search.callback(self.cog, self.ctx, query='book')
        self.assertEqual(self.ctx.send.call_args.args[0], 'No books found.')

    async def test_real_extensions_load_from_another_working_directory(self):
        spec = importlib.util.spec_from_file_location('rag_bot_under_test', BOT_DIR / 'bot.py')
        module = importlib.util.module_from_spec(spec)
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp:
            try:
                os.chdir(tmp)
                spec.loader.exec_module(module)
                async with module.bot:
                    await module.bot.setup_hook()
                    self.assertTrue({'ask', 'book-search', 'help'} <= {command.name for command in module.bot.commands})
            finally:
                os.chdir(previous)


if __name__ == '__main__':
    unittest.main()
