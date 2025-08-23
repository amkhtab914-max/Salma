import threading
import time
import sys
import atexit
import asyncio

try:
    import mt5_connector
except ImportError:
    print("Could not import mt5_connector. Is MetaTrader5 installed? The application will not be able to run the analysis engine.", file=sys.stderr)
    mt5_connector = None

import analysis_engine
from telegram_handler import run_bot
from web_app import run_web_server
from news_handler import get_latest_news, NEWS_CHANNEL

# --- Shared Data and Control ---

shared_data = {
    "latest_recommendation": None,
    "latest_news": [],
    "lock": threading.Lock()
}

stop_event = threading.Event()

def cleanup():
    print("--- Initiating graceful shutdown ---")
    if not stop_event.is_set():
        stop_event.set()
    print("Shutdown signal sent to all threads.")

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

            # Get the latest news from shared data
            with shared_data["lock"]:
                current_news = shared_data["latest_news"]

            if market_data is not None and not market_data.empty:
                recommendation = analysis_engine.run_analysis_engine(market_data, news_texts=current_news)

                with shared_data["lock"]:
                    shared_data["latest_recommendation"] = recommendation
                print("[Analysis Thread] Shared recommendation updated.")
            else:
                print("[Analysis Thread] Could not fetch market data for analysis.")

            # Wait for 5 minutes
            stop_event.wait(300)

        except Exception as e:
            print(f"[Analysis Thread] An error occurred: {e}", file=sys.stderr)
            stop_event.wait(60)

    mt5_connector.shutdown_mt5()
    print("[Analysis Thread] Finished.")

def news_thread_func():
    """
    Periodically fetches news from the specified Telegram channel.
    """
    print("[News Thread] Started.")

    # We need to run the async function in a way that works within a thread.
    # We can create a new event loop for this thread.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while not stop_event.is_set():
        try:
            print("[News Thread] Fetching latest news...")
            # This is an async function, so we run it in the thread's event loop.
            news_items = loop.run_until_complete(get_latest_news(NEWS_CHANNEL, limit=5))

            if news_items is not None:
                with shared_data["lock"]:
                    shared_data["latest_news"] = news_items
                print(f"[News Thread] Fetched {len(news_items)} news items.")
            else:
                print("[News Thread] Failed to fetch news. This may be due to login requirements.")

            # Wait for 15 minutes before fetching again
            stop_event.wait(900)
        except Exception as e:
            print(f"[News Thread] An error occurred: {e}", file=sys.stderr)
            stop_event.wait(60)

    loop.close()
    print("[News Thread] Finished.")


def telegram_thread_func():
    print("[Telegram Thread] Started.")
    try:
        run_bot()
    except Exception as e:
        print(f"[Telegram Thread] An error occurred: {e}", file=sys.stderr)
    print("[Telegram Thread] Finished.")

def web_thread_func():
    print("[Web Server Thread] Started.")
    try:
        run_web_server(shared_data)
    except Exception as e:
        print(f"[Web Server Thread] An error occurred: {e}", file=sys.stderr)
    print("[Web Server Thread] Finished.")


# --- Main Execution ---

def main():
    print("--- Starting All Khtab Recommendation Bot Services ---")

    threads = [
        threading.Thread(target=analysis_thread_func, name="AnalysisThread"),
        threading.Thread(target=telegram_thread_func, name="TelegramThread"),
        threading.Thread(target=web_thread_func, name="WebThread"),
        threading.Thread(target=news_thread_func, name="NewsThread")
    ]

    for t in threads:
        t.start()

    print("--- All services are running. Press Ctrl+C to exit. ---")

    try:
        # Keep main thread alive
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main Thread] KeyboardInterrupt received.")
        sys.exit(0)

if __name__ == "__main__":
    main()
