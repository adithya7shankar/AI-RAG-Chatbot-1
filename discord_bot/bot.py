"""Discord entry point; run with `python discord_bot/bot.py`."""
from pathlib import Path
import importlib.util
import logging
import sys

import discord
from discord.ext import commands

BOT_DIR = Path(__file__).resolve().parent
# Extension imports work both from the repository and the flattened bot image.
sys.path.insert(0, str(BOT_DIR))
spec = importlib.util.spec_from_file_location("rag_bot_config", BOT_DIR / "config.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
logger = logging.getLogger(__name__)


class RAGBot(commands.Bot):
    async def setup_hook(self):
        for path in sorted((BOT_DIR / "commands").glob("*.py")):
            if not path.name.startswith("_"):
                await self.load_extension(f"commands.{path.stem}")


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = RAGBot(command_prefix=config.COMMAND_PREFIX, intents=intents, help_command=None,
             allowed_mentions=discord.AllowedMentions.none())


@bot.event
async def on_ready():
    logger.info("Logged in as %s", bot.user)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found. Type `{config.COMMAND_PREFIX}help` for commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
    else:
        logger.error("Command failed", exc_info=(type(error), error, error.__traceback__))
        await ctx.send("Sorry, that command could not be completed. Please try again.")


if __name__ == "__main__":
    logging.basicConfig(level=config.LOG_LEVEL)
    bot.run(config.DISCORD_TOKEN)
