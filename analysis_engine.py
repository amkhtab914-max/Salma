"""
Analysis Engine for the Khtab Recommendation Bot.

This module contains the logic for the trading strategies and the
Composite Engine that combines their scores to generate a trading recommendation.
"""
import random
import json
import pandas as pd
import pandas_ta as ta

# --- Strategy Implementations ---

def strategy_momentum(market_data: pd.DataFrame):
    """
    Calculates MACD and looks for a recent bullish or bearish crossover.
    Score is higher for a more recent crossover.
    """
    if market_data.empty or len(market_data) < 35: # MACD requires a certain amount of data
        return {'score': 0, 'rationale': 'Not enough data for MACD.'}

    # Calculate MACD
    macd = market_data.ta.macd(fast=12, slow=26, signal=9, append=True)
    if macd is None or macd.empty: return {'score': 0, 'rationale': 'Could not calculate MACD.'}

    last_candle = macd.iloc[-1]
    prev_candle = macd.iloc[-2]

    # Bullish crossover: MACD crosses ABOVE signal
    if prev_candle['MACD_12_26_9'] < prev_candle['MACDs_12_26_9'] and last_candle['MACD_12_26_9'] > last_candle['MACDs_12_26_9']:
        return {'score': 0.85, 'rationale': 'Recent bullish MACD crossover detected.'}

    # Bearish crossover: MACD crosses BELOW signal
    if prev_candle['MACD_12_26_9'] > prev_candle['MACDs_12_26_9'] and last_candle['MACD_12_26_9'] < last_candle['MACDs_12_26_9']:
        return {'score': 0.85, 'rationale': 'Recent bearish MACD crossover detected.'}

    return {'score': 0.3, 'rationale': 'No recent MACD crossover.'}


def strategy_atr_filter(market_data: pd.DataFrame):
    """
    Acts as a volatility filter. If volatility is too high, it returns a low
    score to veto trades. Otherwise, returns a neutral score.
    """
    if market_data.empty or len(market_data) < 15:
        return {'score': 0, 'rationale': 'Not enough data for ATR.'}

    atr = market_data.ta.atr(length=14)
    if atr is None or atr.empty: return {'score': 0, 'rationale': 'Could not calculate ATR.'}

    last_atr = atr.iloc[-1]
    last_close = market_data['close'].iloc[-1]

    if last_atr / last_close > 0.02:
        return {'score': 0.1, 'rationale': f'Veto: High volatility detected (ATR is {last_atr:.4f}).'}
    if last_atr / last_close < 0.002:
         return {'score': 0.1, 'rationale': f'Veto: Low volatility detected (ATR is {last_atr:.4f}).'}

    return {'score': 0.6, 'rationale': 'Volatility is within acceptable limits.'}

def strategy_vwap(market_data: pd.DataFrame):
    """
    Checks if the price is above or below the VWAP.
    """
    if 'tick_volume' not in market_data.columns or market_data.empty:
        return {'score': 0.5, 'rationale': 'VWAP requires volume data, which is unavailable.'}

    vwap = market_data.ta.vwap()
    if vwap is None or vwap.empty: return {'score': 0.5, 'rationale': 'Could not calculate VWAP.'}

    last_price = market_data['close'].iloc[-1]
    last_vwap = vwap.iloc[-1]

    if last_price > last_vwap:
        return {'score': 0.65, 'rationale': f'Price ({last_price:.4f}) is above VWAP ({last_vwap:.4f}), suggesting bullish sentiment.'}
    else:
        return {'score': 0.65, 'rationale': f'Price ({last_price:.4f}) is below VWAP ({last_vwap:.4f}), suggesting bearish sentiment.'}

def strategy_volatility_squeeze(market_data: pd.DataFrame):
    """
    Checks for a volatility squeeze using Bollinger Bands and Keltner Channels.
    A squeeze is on when Bollinger Bands are inside the Keltner Channels.
    """
    if len(market_data) < 20: return {'score': 0, 'rationale': 'Not enough data for Squeeze.'}

    squeeze_data = market_data.ta.squeeze(lazy=True)
    if squeeze_data is None or squeeze_data.empty: return {'score': 0.5, 'rationale': 'Could not calculate Squeeze.'}

    last_squeeze = squeeze_data.iloc[-1]
    if last_squeeze['SQZ_ON']:
        return {'score': 0.8, 'rationale': 'Volatility squeeze is on, indicating potential for a big move.'}
    if last_squeeze['SQZ_OFF']:
        return {'score': 0.6, 'rationale': 'Squeeze has recently fired, indicating a breakout is in progress.'}

    return {'score': 0.4, 'rationale': 'No volatility squeeze detected.'}

def strategy_vsa(market_data: pd.DataFrame):
    """
    Simplified Volume Spread Analysis. Looks for an up-thrust bar.
    An up-thrust is a bar with a high spread, closing near the low, on high volume.
    """
    if 'tick_volume' not in market_data.columns or len(market_data) < 20:
        return {'score': 0.5, 'rationale': 'VSA requires volume data.'}

    last_bar = market_data.iloc[-1]
    avg_volume = market_data['tick_volume'].rolling(20).mean().iloc[-1]
    avg_spread = (market_data['high'] - market_data['low']).rolling(20).mean().iloc[-1]

    bar_spread = last_bar['high'] - last_bar['low']
    bar_volume = last_bar['tick_volume']

    # Check for up-thrust (a sign of weakness)
    is_high_volume = bar_volume > avg_volume * 1.5
    is_wide_spread = bar_spread > avg_spread * 1.5
    closes_near_low = (last_bar['close'] - last_bar['low']) / bar_spread < 0.33

    if is_high_volume and is_wide_spread and closes_near_low:
        return {'score': 0.8, 'rationale': 'VSA: High-volume up-thrust bar detected, indicating weakness.'}

    return {'score': 0.5, 'rationale': 'VSA: No specific pattern detected.'}


# --- Placeholder Strategy Functions ---

def strategy_smc(market_data: pd.DataFrame):
    """
    Placeholder for Smart Money Concepts (SMC) strategy.
    SMC focuses on identifying where institutional players ('smart money') are placing orders.
    """
    # --- Full Implementation Steps ---
    # 1. Identify Market Structure: Find recent swing highs and lows to determine the trend.
    # 2. Find Order Blocks: Locate significant up or down candles just before a strong move that breaks market structure.
    # 3. Look for Liquidity Grabs: Identify where price has moved above/below a previous high/low to take out stop losses.
    # 4. Check for Imbalance (Fair Value Gaps): Look for large, inefficient price moves creating gaps.
    # 5. Entry Condition: Price returns to an order block or fills an imbalance.
    #
    # This requires a sophisticated pattern recognition algorithm.
    return {'score': 0.5, 'rationale': 'SMC analysis is a placeholder.'}

def strategy_ict(market_data: pd.DataFrame):
    """
    Placeholder for Inner Circle Trader (ICT) strategy.
    ICT is a collection of concepts focusing on liquidity and market inefficiencies.
    """
    # --- Full Implementation Steps ---
    # 1. Identify Liquidity Pools: Locate obvious swing highs and lows where stop orders are likely placed.
    # 2. Look for 'Judas Swing': A false move during the London session to trap traders.
    # 3. Identify Silver Bullet setups: Time-based setups that occur during specific windows (e.g., 10-11 AM NY time).
    # 4. Find Fair Value Gaps (FVG): Similar to SMC, look for price inefficiencies.
    # 5. Entry Condition: Price sweeps a liquidity pool and then reverses, often into an FVG.
    #
    # This is highly conceptual and requires time-of-day analysis.
    return {'score': 0.5, 'rationale': 'ICT analysis is a placeholder.'}

def strategy_insider(market_data):
    """Placeholder for Insider/COT analysis."""
    # --- Full Implementation Steps ---
    # 1. Fetch Commitment of Traders (COT) data from an external source (e.g., CFTC website or an API).
    # 2. Parse the data for the relevant currency (e.g., EUR futures).
    # 3. Analyze the net positions of 'Non-Commercial' traders (speculators/hedge funds).
    # 4. Generate a score based on extreme positioning (e.g., net long/short positions at multi-month highs/lows).
    #
    # This requires an external data feed and is not based on chart data alone.
    return {'score': 0.5, 'rationale': 'Insider/COT analysis requires an external data source and is a placeholder.'}

def strategy_market_profile(market_data: pd.DataFrame):
    """
    Placeholder for Market Profile strategy.
    This technique organizes price and volume data to identify key reference points.
    """
    # --- Full Implementation Steps ---
    # 1. Build a Market Profile: This typically requires tick data or 1-min data to build Time Price Opportunities (TPOs).
    #    This is not easily done with standard OHLC bars.
    # 2. Identify Key Levels:
    #    - Point of Control (POC): The price level with the most traded volume.
    #    - Value Area (VA): The range where ~70% of the volume was traded.
    #    - Value Area High/Low (VAH/VAL).
    # 3. Entry Condition: Price interacts with one of these key levels (e.g., rejection from POC, acceptance into value).
    #
    # Requires specialized libraries (e.g., market-profile) or complex custom code.
    return {'score': 0.5, 'rationale': 'Market Profile analysis is a placeholder.'}
def strategy_order_flow(market_data: pd.DataFrame):
    """
    Placeholder for Order Flow analysis.
    This strategy analyzes the flow of buy and sell orders to anticipate price moves.
    """
    # --- Full Implementation Steps ---
    # 1. Obtain Level 2 Data: This is the critical prerequisite. It requires a data feed that provides
    #    the Depth of Market (DOM), showing buy/sell orders at different price levels. The standard
    #    MT5 connector does not provide historical Level 2 data easily.
    # 2. Analyze the Tape: Look for patterns in executed trades (e.g., large volume trades at a single price).
    # 3. Look for Absorption: Identify areas where large market orders are being absorbed by passive limit orders,
    #    preventing the price from moving further. This often signals a reversal.
    # 4. Identify Order Book Imbalances: Look for a significantly larger number of buy vs. sell orders (or vice-versa)
    #    in the order book.
    #
    # This is one of the most data-intensive forms of analysis and requires a specialized data provider.
    return {'score': 0.5, 'rationale': 'Order Flow analysis requires a Level 2 data feed and is a placeholder.'}


# --- Composite Engine ---

STRATEGIES = {
    "SMC": strategy_smc,
    "ICT": strategy_ict,
    "Insider": strategy_insider,
    "VWAP": strategy_vwap,
    "Momentum": strategy_momentum,
    "ATR_Filter": strategy_atr_filter,
    "Volatility_Squeeze": strategy_volatility_squeeze,
    "Market_Profile": strategy_market_profile,
    "Order_Flow": strategy_order_flow,
    "VSA": strategy_vsa,
}

def strategy_sentiment_analysis(news_texts: list):
    """
    Performs basic sentiment analysis on a list of news headlines/texts.
    """
    if not news_texts:
        return {'score': 0.5, 'rationale': 'No news text to analyze.'}

    bullish_keywords = ['strong', 'hike', 'bullish', 'up', 'rally', 'growth']
    bearish_keywords = ['weak', 'cut', 'bearish', 'down', 'recession', 'slump']

    sentiment_score = 0.5
    bull_count = 0
    bear_count = 0

    combined_text = " ".join(news_texts).lower()

    for word in bullish_keywords:
        bull_count += combined_text.count(word)
    for word in bearish_keywords:
        bear_count += combined_text.count(word)

    if bull_count > bear_count:
        sentiment_score = 0.7
        rationale = f'News sentiment appears bullish ({bull_count} bullish vs {bear_count} bearish keywords).'
    elif bear_count > bull_count:
        sentiment_score = 0.3
        rationale = f'News sentiment appears bearish ({bear_count} bearish vs {bull_count} bullish keywords).'
    else:
        rationale = 'News sentiment appears neutral.'

    return {'score': sentiment_score, 'rationale': rationale}

def run_analysis_engine(market_data: pd.DataFrame, news_texts: list = None):
    """
    Runs all registered strategies on the given market data and news text.
    """
    if market_data is None or market_data.empty:
        print("Analysis engine received no market data.")
        return None

    print("--- Running Analysis Engine ---")
    all_results = {}
    # Run market data strategies
    for name, strategy_func in STRATEGIES.items():
        result = strategy_func(market_data)
        all_results[name] = result
        print(f"  - Strategy '{name}': Score={result['score']:.2f}, Rationale: {result['rationale']}")

    # Run news sentiment strategy
    sentiment_result = strategy_sentiment_analysis(news_texts)
    all_results['Sentiment'] = sentiment_result
    print(f"  - Strategy 'Sentiment': Score={sentiment_result['score']:.2f}, Rationale: {sentiment_result['rationale']}")

    total_score = sum(res['score'] for res in all_results.values())
    average_score = total_score / len(all_results) if all_results else 0
    confidence = average_score * 100

    print(f"--- Composite Engine Result ---")
    print(f"  - Final Confidence: {confidence:.2f}%")

    recommendation = {
        'confidence': confidence,
        'individual_scores': all_results
    }

    if confidence >= 60:
        recommendation['decision'] = 'BUY' # Dummy value
        recommendation['scenario'] = 'High-probability setup based on multiple confluences.'
    else:
        recommendation['decision'] = 'HOLD'
        recommendation['scenario'] = 'Not enough confluence for a high-probability trade.'

    print(f"  - Decision: {recommendation['decision']}")
    return recommendation

if __name__ == '__main__':
    # This test block now uses the mt5_connector to get real (mocked) data
    try:
        # This is a bit of a hack to make the test run from the root directory
        import mt5_connector
        if mt5_connector.initialize_mt5():
            test_data = mt5_connector.get_historical_data("EURUSD", count=100, timeframe=mt5_connector.mt5.TIMEFRAME_H1)
            if test_data is not None:
                final_recommendation = run_analysis_engine(test_data)
                print("\n--- Final Recommendation Object ---")
                print(json.dumps(final_recommendation, indent=2))
            mt5_connector.shutdown_mt5()
    except ImportError:
        print("Could not import mt5_connector. Run this from the project root.")
    except Exception as e:
        print(f"An error occurred during the test run: {e}")
