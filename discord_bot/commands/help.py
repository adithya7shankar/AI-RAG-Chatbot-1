# FILE: /AI-RAG-Chatbot/AI-RAG-Chatbot/discord_bot/commands/help.py

import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx):
        help_message = (
            "Here are the commands you can use:\n"
            "`/ask <question>` - Ask the chatbot a question.\n"
            "`/book-search <title>` - Retrieve matching document passages.\n"
            "For more information, visit our documentation."
        )
        await ctx.send(help_message)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))