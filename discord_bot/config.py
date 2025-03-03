# filepath: /AI-RAG-Chatbot/discord_bot/config.py

import os

# Discord bot configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "your_discord_bot_token_here")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "/")

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:5000")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Other configurations can be added as needed