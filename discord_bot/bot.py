import discord
from discord.ext import commands
import requests
import importlib.util
import sys
import os

# Load configuration
spec = importlib.util.spec_from_file_location("config", "discord_bot/config.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

TOKEN = config.DISCORD_TOKEN
API_URL = config.BACKEND_API_URL

# Set up the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required for message content access
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

# Load command extensions
def load_extensions():
    for filename in os.listdir('./discord_bot/commands'):
        if filename.endswith('.py') and not filename.startswith('__'):
            bot.load_extension(f'discord_bot.commands.{filename[:-3]}')
            print(f'Loaded extension: {filename[:-3]}')

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Type `/help` for a list of commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param}")
    else:
        await ctx.send(f"An error occurred: {error}")
        print(f"Error: {error}")

# Load extensions and run the bot
if __name__ == "__main__":
    load_extensions()
    bot.run(TOKEN)
