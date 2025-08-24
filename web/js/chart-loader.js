/**
 * This script handles the loading of the TradingView Advanced Chart widget.
 */
document.addEventListener('DOMContentLoaded', () => {
    const chartContainer = document.getElementById('tradingview_f1337');
    if (chartContainer) {
        new TradingView.widget({
            "autosize": true,
            "symbol": "FX:EURUSD",
            "interval": "60",
            "timezone": "Etc/UTC",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_f1337"
        });
    }
});
