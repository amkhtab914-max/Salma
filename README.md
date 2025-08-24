# Tawsiat Khtab (توصيات خطاب) - Trading Bot

This project is a multi-service application that provides trading recommendations based on a series of analytical strategies. It includes a backend analysis engine, a web dashboard, and a Telegram bot.

## Running the Application

This application is composed of several services that should be run in separate terminals.

### Step 1: One-Time Setup

1.  **Install Dependencies:** Open a terminal or command prompt in the project folder and run:
    ```
    pip install -r requirements.txt
    ```
    *(Note: For the MT5 connection, you must be on a Windows machine with the MetaTrader 5 terminal installed.)*

2.  **Generate Telegram Session:** To allow the script to read the news channel, you must first log in to your personal Telegram account. Run the following command and follow the on-screen instructions to enter your phone code and 2FA password. This only needs to be done once.
    ```
    python generate_session.py
    ```

### Step 2: Running the Services

You will need to open **three separate terminals** or command prompts in the project directory.

**In Terminal 1 - Start the Web Server:**
```
python web_app.py
```
You should see output indicating the Flask server is running. You can now access the website at `http://127.0.0.1:8080`.

**In Terminal 2 - Start the Backend Analysis Script:**
```
python run.py
```
This will start the MT5 connection, analysis, and news-gathering threads. It will periodically send the latest recommendation to the web server. Make sure your MT5 terminal is running with "Algo Trading" enabled (the button should be green).

**In Terminal 3 - Start the Telegram Bot:**
```
python telegram_handler.py
```
This will start the Telegram recommendation bot.

By running these three components simultaneously in separate terminals, the entire system will be operational.
