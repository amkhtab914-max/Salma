"""
This module handles the connection to a personal Telegram account using Telethon
to read messages from a specified news channel.
"""

import json
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import pytesseract
from PIL import Image
import io

# --- Configuration ---
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    PERSONAL_CONFIG = config.get('personal_number')
    NEWS_CHANNEL = config.get('channels', {}).get('news_channel')
except FileNotFoundError:
    print("CRITICAL: config.json not found. The news handler cannot operate.")
    PERSONAL_CONFIG = None
    NEWS_CHANNEL = None

SESSION_FILE = f"{PERSONAL_CONFIG.get('session_name', 'telethon_session')}.session" if PERSONAL_CONFIG else "telethon_session.session"

# --- Telethon Client ---

# Create the client instance. The session file will be created automatically.
# It's defined globally so it can be used by other functions.
client = TelegramClient(
    SESSION_FILE,
    PERSONAL_CONFIG['api_id'],
    PERSONAL_CONFIG['api_hash']
) if PERSONAL_CONFIG else None

async def get_latest_news(channel_url: str, limit=5):
    """
    Connects the Telethon client, fetches the latest messages from a channel,
    and performs OCR on any images found.

    Returns:
        A list of combined message texts (caption + OCR), or None on failure.
    """
    # NOTE: This function requires the user to have the Tesseract OCR engine
    # installed on their system. `pytesseract` is just a Python wrapper for it.
    if not client:
        print("Telethon client not configured.")
        return None

    print(f"Attempting to connect with session file: {SESSION_FILE}")

    try:
        if not client.is_connected():
            await client.connect()

        if not await client.is_user_authorized():
            print("User is not authorized. Please run generate_session.py script once manually to log in.")
            # We no longer send the code here, the dedicated script handles it.
            return None

        me = await client.get_me()
        print(f"Successfully connected as {me.first_name}")
        print(f"Fetching last {limit} messages from {channel_url} for news and OCR...")

        messages = await client.get_messages(channel_url, limit=limit)

        if not messages:
            print("No messages found in the channel.")
            return []

        processed_messages = []
        for msg in messages:
            full_text = msg.text or ""

            if msg.photo:
                print(f"  - Photo found in message {msg.id}. Performing OCR...")
                try:
                    buffer = io.BytesIO()
                    await msg.download_media(file=buffer)
                    buffer.seek(0)
                    image = Image.open(buffer)
                    ocr_text = pytesseract.image_to_string(image)

                    if ocr_text:
                        print("    - OCR successful, text extracted.")
                        full_text += "\n\n--- OCR Text ---\n" + ocr_text
                    else:
                        print("    - OCR complete, no text found.")
                except Exception as e:
                    print(f"    - OCR failed for message {msg.id}: {e}")

            if full_text:
                processed_messages.append(full_text.strip())

        return processed_messages

    except SessionPasswordNeededError:
        print("2FA Password needed. Please run this script manually to log in.")
        # In a real app, you would prompt for the password here.
        return None
    except Exception as e:
        print(f"An error occurred in Telethon client: {e}")
        return None
    finally:
        # In the main run.py loop, we want the client to stay connected.
        # The connection will be terminated when the main script exits.
        print("News fetch cycle complete.")

async def main():
    """Main function for testing the news handler."""
    print("--- Testing News Handler ---")
    if not NEWS_CHANNEL:
        print("News channel URL not found in config.json.")
        return

    latest_messages = await get_latest_news(NEWS_CHANNEL, limit=3)

    if latest_messages:
        print("\n--- Latest Messages ---")
        for i, text in enumerate(latest_messages):
            print(f"Message {i+1}:\n---\n{text}\n---")
    else:
        print("\nCould not retrieve messages. This may be expected on the first run.")
        print("Please run the script in an interactive terminal to complete the login process.")

if __name__ == "__main__":
    # asyncio.run() is the modern way to run an async main function.
    if client:
        # This is a more robust way to run the async code from a sync context
        with client:
            client.loop.run_until_complete(main())
    else:
        print("Client could not be configured. Exiting test.")
