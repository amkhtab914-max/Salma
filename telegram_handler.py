import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text('Hello! I am the Khtab Recommendation Bot. I am currently online.')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a status message when the /status command is issued."""
    # In the future, this could be expanded to check MT5 connection, etc.
    await update.message.reply_text('Bot status: Online')

def run_bot():
    """
    Runs the Telegram bot.
    """
    # Load config
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found. Cannot start bot.")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)

    telegram_config = config.get('telegram')
    if not telegram_config or not telegram_config.get('bot_token'):
        print("Error: 'telegram' configuration or 'bot_token' not found in config.json")
        return

    bot_token = telegram_config['bot_token']
    if "YOUR_BOT_TOKEN" in bot_token:
        print("Warning: Bot token is a placeholder. The bot will not be able to start.")
        print("Please fill in your actual bot token in config.json.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))

    print("Telegram bot is starting...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    print("Telegram bot has stopped.")

if __name__ == '__main__':
    run_bot()
