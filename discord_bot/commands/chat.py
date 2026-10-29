import discord
from discord.ext import commands
import requests
import importlib.util
from pathlib import Path
import asyncio

# Load configuration relative to file location
config_path = Path(__file__).resolve().parents[1] / "config.py"
spec = importlib.util.spec_from_file_location("rag_command_config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

ALLOWED_MENTIONS = discord.AllowedMentions.none()

async def _post_json(url: str, payload: dict):
    """Shared helper to POST JSON and return parsed dict or None on error."""
    def _sync_post():
        return requests.post(url, json=payload, timeout=(3, 30))

    try:
        resp = await asyncio.to_thread(_sync_post)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, dict):
            return None
        return data
    except (requests.RequestException, ValueError):
        return None

def _split_message(text: str, limit: int = 1900):
    """Split text into chunks of at most `limit` characters."""
    if not text:
        return []
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Try to split at last newline within limit
        cut = text.rfind('\n', 0, limit)
        if cut == -1:
            cut = limit
        else:
            cut += 1
        chunks.append(text[:cut])
        text = text[cut:]
    return chunks

class ChatCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ask')
    async def ask(self, ctx, *, question: str):
        """Handles the /ask command to interact with the AI chatbot."""
        await ctx.send("Thinking...", allowed_mentions=ALLOWED_MENTIONS)

        data = await _post_json(f"{config.BACKEND_API_URL}/rag", {"query": question})

        if data is None:
            await ctx.send("Sorry, I couldn't process your request.", allowed_mentions=ALLOWED_MENTIONS)
            return

        response = data.get("response")
        if not isinstance(response, str) or not response.strip():
            await ctx.send("Sorry, I couldn't process your request.", allowed_mentions=ALLOWED_MENTIONS)
            return

        for chunk in _split_message(response):
            await ctx.send(chunk, allowed_mentions=ALLOWED_MENTIONS)

    @commands.command(name='book-search')
    async def book_search(self, ctx, *, query: str):
        """Handles the /book-search command to search for books."""
        await ctx.send("Searching for books...", allowed_mentions=ALLOWED_MENTIONS)

        data = await _post_json(f"{config.BACKEND_API_URL}/chat/book-search", {"query": query})

        if data is None:
            await ctx.send("Sorry, I couldn't process your request.", allowed_mentions=ALLOWED_MENTIONS)
            return

        results = data.get("results")
        if not isinstance(results, list):
            await ctx.send("Sorry, I couldn't process your request.", allowed_mentions=ALLOWED_MENTIONS)
            return

        if any(not isinstance(item, str) for item in results):
            await ctx.send("Sorry, I couldn't process your request.", allowed_mentions=ALLOWED_MENTIONS)
            return
        valid_results = [item for item in results if item.strip()]

        if not valid_results:
            await ctx.send("No books found.", allowed_mentions=ALLOWED_MENTIONS)
            return

        for chunk in _split_message("\n".join(valid_results)):
            await ctx.send(chunk, allowed_mentions=ALLOWED_MENTIONS)

async def setup(bot):
    await bot.add_cog(ChatCommand(bot))
