# FILE: /AI-RAG-Chatbot/AI-RAG-Chatbot/discord_bot/commands/chat.py

import discord
from discord.ext import commands
import requests
import importlib.util
import sys

# Load configuration
spec = importlib.util.spec_from_file_location("config", "discord_bot/config.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

class ChatCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ask')
    async def ask(self, ctx, *, question: str):
        """Handles the /ask command to interact with the AI chatbot."""
        await ctx.send("Thinking...")

        # Send the question to the backend API
        response = requests.post(f'{config.BACKEND_API_URL}/chat', json={'message': question})

        if response.status_code == 200:
            answer = response.json().get('response', 'No response received.')
            await ctx.send(answer)
        else:
            await ctx.send("Sorry, I couldn't process your request.")

    @commands.command(name='book-search')
    async def book_search(self, ctx, *, query: str):
        """Handles the /book-search command to search for books."""
        await ctx.send("Searching for books...")

        # Send the book search query to the backend API
        response = requests.post(f'{config.BACKEND_API_URL}/rag', json={'query': query})

        if response.status_code == 200:
            results = response.json().get('results', [])
            documents = response.json().get('documents', [])
            
            if results:
                await ctx.send("\n".join(results))
            elif documents:
                await ctx.send("\n".join(documents))
            else:
                await ctx.send("No books found.")
        else:
            await ctx.send("Sorry, I couldn't process your request.")

def setup(bot):
    bot.add_cog(ChatCommand(bot))
