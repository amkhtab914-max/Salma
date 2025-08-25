"""
Analysis Engine for the Khtab Binance Bot.

This module contains the logic for the 10 trading strategies and the
Composite Engine that combines their scores to generate a trading recommendation.
"""
import random
import json
import pandas as pd
import pandas_ta as ta

# --- Implemented Strategies ---

def strategy_momentum(market_data: pd.DataFrame):
    if market_data.empty or len(market_data) < 35: return {'score': 0, 'rationale': 'Not enough data for MACD.'}
    macd = market_data.ta.macd(fast=12, slow=26, signal=9, append=True)
    if macd is None or macd.empty: return {'score': 0, 'rationale': 'Could not calculate MACD.'}
    last_candle, prev_candle = macd.iloc[-1], macd.iloc[-2]
    if prev_candle['MACD_12_26_9'] < prev_candle['MACDs_12_26_9'] and last_candle['MACD_12_26_9'] > last_candle['MACDs_12_26_9']:
        return {'score': 0.85, 'rationale': 'Recent bullish MACD crossover.'}
    if prev_candle['MACD_12_26_9'] > prev_candle['MACDs_12_26_9'] and last_candle['MACD_12_26_9'] < last_candle['MACDs_12_26_9']:
        return {'score': 0.85, 'rationale': 'Recent bearish MACD crossover.'}
    return {'score': 0.3, 'rationale': 'No recent MACD crossover.'}

def strategy_atr_filter(market_data: pd.DataFrame):
    if market_data.empty or len(market_data) < 15: return {'score': 0, 'rationale': 'Not enough data for ATR.'}
    atr = market_data.ta.atr(length=14); last_atr = atr.iloc[-1] if atr is not None else 0
    last_close = market_data['Close'].iloc[-1]
    if last_close > 0 and (last_atr / last_close) > 0.05: # Using 5% for more volatile crypto
        return {'score': 0.1, 'rationale': f'Veto: High volatility (ATR {last_atr:.4f}).'}
    return {'score': 0.6, 'rationale': 'Acceptable volatility.'}

def strategy_vwap(market_data: pd.DataFrame):
    if 'Volume' not in market_data.columns or market_data.empty: return {'score': 0.5, 'rationale': 'VWAP requires volume data.'}
    vwap = market_data.ta.vwap(); last_vwap = vwap.iloc[-1] if vwap is not None else 0
    last_price = market_data['Close'].iloc[-1]
    if last_price > last_vwap: return {'score': 0.65, 'rationale': f'Price is above VWAP, bullish.'}
    else: return {'score': 0.65, 'rationale': f'Price is below VWAP, bearish.'}

def strategy_volatility_squeeze(market_data: pd.DataFrame):
    if len(market_data) < 20: return {'score': 0, 'rationale': 'Not enough data for Squeeze.'}
    squeeze_data = market_data.ta.squeeze(lazy=True)
    if squeeze_data is None or squeeze_data.empty: return {'score': 0.5, 'rationale': 'Could not calculate Squeeze.'}
    if squeeze_data.iloc[-1]['SQZ_ON']: return {'score': 0.8, 'rationale': 'Volatility squeeze is on.'}
    if squeeze_data.iloc[-1]['SQZ_OFF']: return {'score': 0.6, 'rationale': 'Squeeze recently fired.'}
    return {'score': 0.4, 'rationale': 'No squeeze detected.'}

def strategy_vsa(market_data: pd.DataFrame):
    if 'Volume' not in market_data.columns or len(market_data) < 20: return {'score': 0.5, 'rationale': 'VSA requires volume data.'}
    last_bar = market_data.iloc[-1]
    avg_volume = market_data['Volume'].rolling(20).mean().iloc[-1]
    bar_spread = last_bar['High'] - last_bar['Low']
    if bar_spread == 0: return {'score': 0.5, 'rationale': 'VSA: Zero spread bar.'}
    is_high_volume = last_bar['Volume'] > avg_volume * 2
    closes_near_low = (last_bar['Close'] - last_bar['Low']) / bar_spread < 0.33
    if is_high_volume and closes_near_low: return {'score': 0.8, 'rationale': 'VSA: High-volume up-thrust detected (weakness).'}
    return {'score': 0.5, 'rationale': 'VSA: No specific pattern.'}

# --- Placeholder Strategies ---

def strategy_smc(market_data: pd.DataFrame):
    return {'score': 0.5, 'rationale': 'SMC analysis is a placeholder.'}
def strategy_ict(market_data: pd.DataFrame):
    return {'score': 0.5, 'rationale': 'ICT analysis is a placeholder.'}
def strategy_insider(market_data):
    return {'score': 0.5, 'rationale': 'Insider/COT analysis is a placeholder.'}
def strategy_market_profile(market_data: pd.DataFrame):
    return {'score': 0.5, 'rationale': 'Market Profile analysis is a placeholder.'}
def strategy_order_flow(market_data: pd.DataFrame):
    return {'score': 0.5, 'rationale': 'Order Flow analysis is a placeholder.'}

# --- Composite Engine ---

STRATEGIES = { "SMC": strategy_smc, "ICT": strategy_ict, "Insider": strategy_insider, "VWAP": strategy_vwap, "Momentum": strategy_momentum, "ATR_Filter": strategy_atr_filter, "Volatility_Squeeze": strategy_volatility_squeeze, "Market_Profile": strategy_market_profile, "Order_Flow": strategy_order_flow, "VSA": strategy_vsa }

def run_analysis_engine(market_data: pd.DataFrame):
    if market_data is None or market_data.empty: return None
    all_results = {name: func(market_data) for name, func in STRATEGIES.items()}
    total_score = sum(res['score'] for res in all_results.values())
    average_score = total_score / len(all_results) if all_results else 0
    confidence = average_score * 100
    decision = 'BUY' if confidence > 65 else ('SELL' if confidence < 45 else 'HOLD')

    return {
        'confidence': confidence,
        'decision': decision,
        'individual_scores': all_results
    }

if __name__ == '__main__':
    # This test block requires a working binance_client.
    # It will fail in the current environment due to geo-restrictions.
    print("--- Testing Analysis Engine ---")
    try:
        import binance_client
        # Fetch data for BTCUSDT to test the engine
        test_data = binance_client.get_historical_data("BTCUSDT", "1h", "10 day ago UTC")
        if test_data is not None:
            final_recommendation = run_analysis_engine(test_data)
            print("\n--- Final Recommendation Object ---")
            print(json.dumps(final_recommendation, indent=2))
        else:
            print("Could not fetch test data from Binance.")
    except Exception as e:
        print(f"An error occurred during the test run: {e}")
