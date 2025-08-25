"""
This module handles sending messages to Telegram.
"""
import telegram
import asyncio
import config

# Initialize the Bot object
bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)

async def send_telegram_message(message_text: str):
    """
    Sends a formatted message to the specified Telegram channel.

    :param message_text: The text of the message to send.
    :return: True if successful, False otherwise.
    """
    try:
        print(f"Sending message to Telegram channel {config.TELEGRAM_CHANNEL_ID}...")
        await bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=message_text,
            parse_mode='Markdown'
        )
        print("Message sent successfully.")
        return True
    except Exception as e:
        print(f"An error occurred while sending Telegram message: {e}")
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
        print("Test failed.")

if __name__ == '__main__':
    asyncio.run(main())
