"""
This script is a one-time utility to generate a Telethon .session file.

Run this script directly from your terminal: python generate_session.py

It will ask for your phone number, a code sent to your Telegram account,
and your 2FA password if you have one enabled.

Once successfully run, it will create a .session file (e.g., Khtab_Demo.session)
in this directory. The main application (run.py) will use this file for all
subsequent non-interactive logins.
"""

import asyncio
import json
from telethon import TelegramClient

async def main():
    """The main function to handle the interactive login."""

    print("--- Telethon Session Generator ---")

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        personal_config = config.get('personal_number')
        if not personal_config:
            print("Error: 'personal_number' section not found in config.json.")
            return
    except FileNotFoundError:
        print("Error: config.json not found.")
        return

    api_id = personal_config['api_id']
    api_hash = personal_config['api_hash']
    session_name = personal_config.get('session_name', 'telethon_session')
    phone = personal_config['phone']

    # We pass the phone number directly to the start() method
    # so the user doesn't have to type it again.
    client = TelegramClient(session_name, api_id, api_hash)

    print(f"\nAttempting to create session file: '{session_name}.session'")
    print("Telethon will now ask for your credentials.")
    print("Please enter the code sent to your Telegram account when prompted.")
    print("If you have 2-Factor Authentication, you will also be asked for your password.")
    print("-" * 30)

    try:
        # Connect and log in
        await client.start(phone=phone)

        print("\n" + "-" * 30)
        print("Login successful!")
        me = await client.get_me()
        print(f"Session file '{session_name}.session' has been created for user: {me.first_name}")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Disconnect after we're done.
        if client.is_connected():
            await client.disconnect()
        print("Client disconnected.")


if __name__ == "__main__":
    asyncio.run(main())
