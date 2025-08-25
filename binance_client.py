import pandas as pd
from binance.client import Client
import config

# --- Initialize Binance Client ---
client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)

def get_historical_data(symbol, interval=Client.KLINE_INTERVAL_1HOUR, lookback="10 day ago UTC"):
    """
    Fetches historical k-line data from Binance and returns it as a pandas DataFrame.

    :param symbol: The symbol to fetch data for (e.g., 'BTCUSDT').
    :param interval: The k-line interval (e.g., Client.KLINE_INTERVAL_1HOUR).
    :param lookback: A string describing the lookback period (e.g., "10 day ago UTC").
    :return: A pandas DataFrame with OHLCV data, or None if an error occurs.
    """
    try:
        print(f"Fetching historical data for {symbol} with interval {interval}...")
        klines = client.get_historical_klines(symbol, interval, lookback)

        if not klines:
            print(f"No data found for {symbol}.")
            return None

        # Define column names as per Binance API documentation
        columns = [
            'Open_time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close_time', 'Quote_asset_volume', 'Number_of_trades',
            'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'Ignore'
        ]

        df = pd.DataFrame(klines, columns=columns)

        # --- Data Cleaning and Formatting ---
        # Convert timestamp columns to datetime objects
        df['Open_time'] = pd.to_datetime(df['Open_time'], unit='ms')
        df['Close_time'] = pd.to_datetime(df['Close_time'], unit='ms')

        # Convert numeric columns to appropriate types
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote_asset_volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Keep only the most useful columns
        df = df[['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume']]

        # Set the time as the index
        df.set_index('Open_time', inplace=True)

        print(f"Successfully fetched {len(df)} k-lines for {symbol}.")
        return df

    except Exception as e:
        print(f"An error occurred while fetching data from Binance: {e}")
        return None

# --- Main Test Block ---
if __name__ == '__main__':
    print("--- Testing Binance Client ---")

    # Test with BTC/USDT
    btc_data = get_historical_data('BTCUSDT', Client.KLINE_INTERVAL_4HOUR, "30 day ago UTC")
    if btc_data is not None:
        print("\n--- BTC/USDT Data Sample ---")
        print(btc_data.head())
        print(btc_data.tail())

    print("\n" + "="*30 + "\n")

    # Test with PAX Gold (PAXG/USDT)
    gold_data = get_historical_data('PAXGUSDT', Client.KLINE_INTERVAL_1DAY, "90 day ago UTC")
    if gold_data is not None:
        print("\n--- PAXG/USDT (Gold) Data Sample ---")
        print(gold_data.head())
        print(gold_data.tail())
