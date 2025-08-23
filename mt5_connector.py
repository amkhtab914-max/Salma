import MetaTrader5 as mt5
import json
import os

def initialize_mt5():
    """
    Reads config, connects to MT5, and logs in.
    Returns True on success, False on failure.
    """
    # Check if MT5 is initialized
    if mt5.terminal_info() is None:
        if not mt5.initialize():
            error_code, error_message = mt5.last_error()
            print(f"initialize() failed, error code = {error_code}")
            if error_code == -10005: # IPC timeout
                print("\n--- MT5 Connection Help ---")
                print("This 'IPC timeout' error usually means the script could not communicate with the MT5 Terminal.")
                print("Please check the following:")
                print("1. Is your MetaTrader 5 terminal running?")
                print("2. Is the 'Algo Trading' button in the toolbar of your MT5 terminal enabled (it should be green)?")
                print("3. Are you running the Python script and the MT5 terminal as the same user?")
                print("4. Is a firewall or antivirus blocking the connection?")
                print("-" * 25)
            return False
        print("MetaTrader5 package initialized")

    # Load config
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found.")
        return False

    with open(config_path, 'r') as f:
        config = json.load(f)

    mt5_config = config.get('mt5')
    if not mt5_config:
        print("Error: 'mt5' configuration not found in config.json")
        return False

    # Attempt to log in
    authorized = mt5.login(
        login=mt5_config['login'],
        password=mt5_config['password'],
        server=mt5_config['server']
    )

    if authorized:
        print("Connected to account #{}".format(mt5_config['login']))
        return True
    else:
        print("Failed to connect to account #{}, error code: {}".format(
            mt5_config['login'], mt5.last_error()
        ))
        return False

def get_symbol_price(symbol="EURUSD"):
    """
    Fetches the last tick for a given symbol.
    Returns a dictionary with bid and ask prices or None on failure.
    """
    tick = mt5.symbol_info_tick(symbol)
    if tick is not None:
        price = {
            'symbol': symbol,
            'bid': tick.bid,
            'ask': tick.ask
        }
        print(f"Price for {symbol}: Bid={tick.bid}, Ask={tick.ask}")
        return price
    else:
        print(f"Failed to get tick for {symbol}, error code: {mt5.last_error()}")
        return None

def shutdown_mt5():
    """Shuts down the connection to the terminal."""
    print("Shutting down MT5 connection.")
    mt5.shutdown()

def get_historical_data(symbol="EURUSD", count=100, timeframe=mt5.TIMEFRAME_D1):
    """
    Fetches historical data and returns it as a pandas DataFrame.
    """
    import pandas as pd

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

    if rates is None:
        print(f"Failed to get historical data for {symbol}, error code: {mt5.last_error()}")
        return None

    # Convert the structured numpy array to a pandas DataFrame
    df = pd.DataFrame(rates)
    # Convert timestamp to datetime
    if not df.empty:
        df['time'] = pd.to_datetime(df['time'], unit='s')

    print(f"Successfully fetched {len(df)} bars of historical data for {symbol}.")
    return df

if __name__ == '__main__':
    # Example usage for testing
    if initialize_mt5():
        get_symbol_price("EURUSD")
        print("-" * 20)
        # Test historical data fetching
        historical_data = get_historical_data("EURUSD", count=5)
        if historical_data is not None:
            print("Historical data sample:")
            print(historical_data.head())
        shutdown_mt5()
