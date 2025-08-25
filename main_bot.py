import asyncio
import time
import json

# Import project modules
import config
import binance_client
import analysis_engine
import telegram_handler

# --- Configuration ---
SYMBOLS_TO_ANALYZE = ['BTCUSDT', 'ETHUSDT', 'PAXGUSDT']
LOOP_INTERVAL_SECONDS = 4 * 60 * 60  # 4 hours
CONFIDENCE_THRESHOLD = 70  # Send alert if confidence is over this percentage

def format_recommendation_message(symbol, recommendation):
    """Formats the recommendation data into a readable string for Telegram."""

    decision = recommendation.get('decision', 'N/A')
    confidence = recommendation.get('confidence', 0)

    # Simple emoji for the decision
    emoji = "🟢" if decision == 'BUY' else ("🔴" if decision == 'SELL' else "⚪️")

    message = f"*{symbol} Analysis Complete* {emoji}\n\n"
    message += f"*Decision:* `{decision}`\n"
    message += f"*Confidence:* `{confidence:.2f}%`\n\n"
    message += "*Strategy Breakdown:*\n"

    scores = recommendation.get('individual_scores', {})
    for strategy, result in scores.items():
        score_percent = result.get('score', 0) * 100
        message += f"- `{strategy}`: {score_percent:.0f}%\n"

    return message

async def main():
    """
    The main logic loop for the bot.
    """
    print("--- Khtab Binance Analysis Bot Starting ---")

    while True:
        print(f"\n--- Starting New Analysis Cycle at {time.ctime()} ---")

        for symbol in SYMBOLS_TO_ANALYZE:
            print(f"\nAnalyzing {symbol}...")

            # 1. Fetch Data
            # Using 4-hour candles for a mid-term analysis
            market_data = binance_client.get_historical_data(
                symbol=symbol,
                interval=binance_client.Client.KLINE_INTERVAL_4HOUR,
                lookback="20 day ago UTC"
            )

            if market_data is None:
                print(f"Could not fetch data for {symbol}. Skipping.")
                continue

            # 2. Run Analysis
            recommendation = analysis_engine.run_analysis_engine(market_data)

            if recommendation is None:
                print(f"Analysis failed for {symbol}. Skipping.")
                continue

            print(f"Analysis for {symbol} complete. Decision: {recommendation['decision']}, Confidence: {recommendation['confidence']:.2f}%")

            # 3. Send Alert if needed
            if recommendation['confidence'] >= CONFIDENCE_THRESHOLD and recommendation['decision'] != 'HOLD':
                print(f"High confidence signal found for {symbol}! Sending Telegram alert...")
                message = format_recommendation_message(symbol, recommendation)
                await telegram_handler.send_telegram_message(message)
            else:
                print(f"Signal for {symbol} is not strong enough to send an alert.")

        print(f"\n--- Analysis Cycle Complete. Sleeping for {LOOP_INTERVAL_SECONDS / 3600:.1f} hours. ---")
        await asyncio.sleep(LOOP_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"\nAn unexpected critical error occurred: {e}")
