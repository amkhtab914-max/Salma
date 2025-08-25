"""
This module handles sending messages to Telegram.
"""
import telegram
import asyncio
import config

# --- Validation and Initialization ---
# Validate essential Telegram config on import
if not config.TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in config.py")
if not config.TELEGRAM_CHANNEL_ID:
    raise ValueError("TELEGRAM_CHANNEL_ID is not set in config.py")

bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)

async def send_telegram_message(message_text: str):
    """
    Sends a formatted message to the specified Telegram channel.

    :param message_text: The text of the message to send.
    :return: True if successful, False otherwise.
    """
    try:
        # Mask parts of the token for logging
        masked_token = f"{config.TELEGRAM_BOT_TOKEN[:15]}...{config.TELEGRAM_BOT_TOKEN[-4:]}"
        print("--- Attempting to send Telegram Message ---")
        print(f"Bot Token (Masked): {masked_token}")
        print(f"Target Channel ID: {config.TELEGRAM_CHANNEL_ID}")

        await bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=message_text,
            parse_mode='Markdown'
        )
        print("Message sent successfully via Telegram API.")
        return True
    except telegram.error.InvalidToken:
        print("TELEGRAM ERROR: The provided bot token is invalid. Please check it.")
        return False
    except telegram.error.BadRequest as e:
        print(f"TELEGRAM ERROR: Bad request. This often means the Chat ID '{config.TELEGRAM_CHANNEL_ID}' is incorrect or the bot is not a member. Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while sending Telegram message: {e}")
        return False

# --- Main Test Block ---
async def main():
    """Main function for testing the Telegram handler."""
    print("--- Testing Telegram Handler ---")
    test_message = "*Test Message*\n\nThis is a test message from the Khtab Binance Bot."
    success = await send_telegram_message(test_message)
    if success:
        print("Test concluded successfully.")
    else:
        print("Test failed. Please check the error messages above.")

if __name__ == '__main__':
    asyncio.run(main())
