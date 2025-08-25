import os
from dotenv import load_dotenv

# Build the absolute path to the .env file and load it.
# This makes the config loading independent of the current working directory.
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(basedir, '.env'))

# --- Binance API Credentials ---
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# --- Telegram Bot Credentials ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# --- Telegram Personal Account Credentials (for Telethon) ---
TELETHON_API_ID = os.getenv('TELETHON_API_ID')
TELETHON_API_HASH = os.getenv('TELETHON_API_HASH')
TELETHON_PHONE = os.getenv('TELETHON_PHONE')
TELETHON_SESSION_NAME = os.getenv('TELETHON_SESSION_NAME')

# --- Validation ---
def validate_config():
    """Checks if all essential configuration variables are set."""
    essential_vars = [
        BINANCE_API_KEY,
        BINANCE_API_SECRET,
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHANNEL_ID,
    ]
    if not all(essential_vars):
        raise ValueError("One or more essential environment variables are missing. Please check your .env file.")
    print("Configuration loaded and validated successfully.")

# You can call validate_config() on import if you want to fail early,
# or call it from the main script.
# validate_config()
