import threading
import time
import sys
import atexit
import asyncio
import requests
import json

try:
    import mt5_connector
except ImportError:
    print("Could not import mt5_connector. Is MetaTrader5 installed? The application will not be able to run the analysis engine.", file=sys.stderr)
    mt5_connector = None

import analysis_engine
from news_handler import get_latest_news, NEWS_CHANNEL

# --- Shared Data and Control (for internal threads) ---
# This script no longer shares data with the web app via memory.
shared_data = {
    "latest_news": [],
    "lock": threading.Lock()
}

stop_event = threading.Event()
WEB_APP_URL = "http://127.0.0.1:8080/api/internal/update_recommendation"

def cleanup():
    print("--- Shutting down backend script ---")
    if not stop_event.is_set():
        stop_event.set()
    print("Shutdown signal sent to threads.")

atexit.register(cleanup)


# --- Thread Target Functions ---

def analysis_thread_func():
    print("[Analysis Thread] Started.")
    if not mt5_connector:
        print("[Analysis Thread] MT5 connector not available. Thread is exiting.", file=sys.stderr)
        return

    if not mt5_connector.initialize_mt5():
        print("[Analysis Thread] CRITICAL: Failed to initialize MT5. Thread is exiting.", file=sys.stderr)
        return

    while not stop_event.is_set():
        try:
            print("[Analysis Thread] Running periodic analysis...")
            market_data = mt5_connector.get_historical_data("EURUSD", count=200, timeframe=mt5_connector.mt5.TIMEFRAME_H1)

            with shared_data["lock"]:
                current_news = shared_data["latest_news"]

            if market_data is not None and not market_data.empty:
                recommendation = analysis_engine.run_analysis_engine(market_data, news_texts=current_news)

                # --- Push data to the web server ---
                try:
                    print(f"[Analysis Thread] Pushing recommendation to web server at {WEB_APP_URL}...")
                    requests.post(WEB_APP_URL, json=recommendation, timeout=5)
                    print("[Analysis Thread] Successfully pushed recommendation.")
                except requests.exceptions.RequestException as e:
                    print(f"[Analysis Thread] ERROR: Could not connect to the web server to push update: {e}", file=sys.stderr)
            else:
                print("[Analysis Thread] Could not fetch market data for analysis.")

            stop_event.wait(300)

        except Exception as e:
            print(f"[Analysis Thread] An unexpected error occurred: {e}", file=sys.stderr)
            stop_event.wait(60)

    mt5_connector.shutdown_mt5()
    print("[Analysis Thread] Finished.")

def news_thread_func():
    print("[News Thread] Started.")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while not stop_event.is_set():
        try:
            print("[News Thread] Fetching latest news...")
            news_items = loop.run_until_complete(get_latest_news(NEWS_CHANNEL, limit=5))

            if news_items is not None:
                with shared_data["lock"]:
                    shared_data["latest_news"] = news_items
                print(f"[News Thread] Fetched {len(news_items)} news items.")
            else:
                print("[News Thread] Failed to fetch news. This may be due to login requirements (run generate_session.py).")

            stop_event.wait(900)
        except Exception as e:
            print(f"[News Thread] An error occurred: {e}", file=sys.stderr)
            stop_event.wait(60)

    loop.close()
    print("[News Thread] Finished.")


# --- Main Execution ---

def main():
    print("--- Starting Khtab Backend Analysis Script ---")
    print("This script will run the analysis and news fetching threads.")
    print("Please run web_app.py and telegram_handler.py in separate terminals.")

    threads = [
        threading.Thread(target=analysis_thread_func, name="AnalysisThread"),
        threading.Thread(target=news_thread_func, name="NewsThread")
    ]

    for t in threads:
        t.start()

    print("--- Backend services are running. Press Ctrl+C to exit. ---")

    try:
        for t in threads:
            t.join() # Wait for threads to complete
    except KeyboardInterrupt:
        print("\n[Main Thread] KeyboardInterrupt received.")
        sys.exit(0)

if __name__ == "__main__":
    main()
