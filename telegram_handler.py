import json
import os
import asyncio
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

async def main():
    """
    The main async function to initialize and run the bot.
    """
    # Load config
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found. Cannot start bot.")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)

    telegram_config = config.get('telegram')
    if not telegram_config or not telegram_config.get('bot_token') or "YOUR_BOT_TOKEN" in telegram_config.get('bot_token'):
        print("Error: Telegram bot token not found or is a placeholder in config.json.")
        return

    bot_token = telegram_config['bot_token']

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))

    print("Telegram bot is starting...")

    # Run the bot until the process is shut down
    try:
        await application.initialize()
        await application.updater.start_polling()
        # Keep the bot running
        while True:
            await asyncio.sleep(3600) # Sleep for a long time
    except (KeyboardInterrupt, SystemExit):
        print("Received shutdown signal for bot.")
    finally:
        # The stop() and shutdown() methods are idempotent, so we can call them safely.
        if application.updater:
            await application.updater.stop()
        await application.shutdown()
        print("Telegram bot has stopped.")

def run_bot():
    """
    Entry point to run the bot's async main function.
    This function can be called from a standard thread.
    """
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred while running the bot: {e}")

if __name__ == '__main__':
    # This allows running the bot directly for testing.
    run_bot()
