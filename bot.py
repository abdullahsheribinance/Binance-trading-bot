import ccxt
import time
import telegram
import pandas as pd
import numpy as np
from datetime import datetime
import talib


# Set your API keys here
BINANCE_API_KEY = 'your-binance-api-key'
BINANCE_API_SECRET = 'your-binance-api-secret'
TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'
TELEGRAM_CHAT_ID = 'your-telegram-chat-id'


# Initialize Binance API
binance = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
})


# Initialize Telegram bot
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


# Strategy Functions


def get_binance_data(symbol, timeframe='1m', limit=500):
    """Fetch historical OHLCV data from Binance."""
    ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit=limit)
    return pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])


def rsi_strategy(df, period=14):
    """Calculate RSI and return buy/sell signal."""
    df['rsi'] = talib.RSI(df['close'], timeperiod=period)
    if df['rsi'].iloc[-1] < 30:
        return 'buy'
    elif df['rsi'].iloc[-1] > 70:
        return 'sell'
    return 'hold'


def macd_strategy(df):
    """Calculate MACD and return buy/sell signal."""
    df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    if df['macd'].iloc[-1] > df['macdsignal'].iloc[-1]:
        return 'buy'
    elif df['macd'].iloc[-1] < df['macdsignal'].iloc[-1]:
        return 'sell'
    return 'hold'


def ema_strategy(df):
    """Calculate EMA and return buy/sell signal."""
    df['ema_short'] = talib.EMA(df['close'], timeperiod=9)
    df['ema_long'] = talib.EMA(df['close'], timeperiod=21)
    if df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1]:
        return 'buy'
    elif df['ema_short'].iloc[-1] < df['ema_long'].iloc[-1]:
        return 'sell'
    return 'hold'


# Get Best Signal
def get_signal(symbol):
    df = get_binance_data(symbol)
    rsi_signal = rsi_strategy(df)
    macd_signal = macd_strategy(df)
    ema_signal = ema_strategy(df)


    # Combine signals (considering RSI, MACD, EMA for highest accuracy)
    signals = [rsi_signal, macd_signal, ema_signal]
    if signals.count('buy') > 1:
        return 'buy'
    elif signals.count('sell') > 1:
        return 'sell'
    return 'hold'


def send_telegram_message(message):
    """Send a message to the specified Telegram chat."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


# Main loop for trading signals
def main():
    while True:
        signal = get_signal('BTC/USDT')  # Example pair
        if signal != 'hold':
            message = f"Trade signal: {signal} BTC/USDT at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            send_telegram_message(message)
        time.sleep(600)  # Wait for 10 minutes before next signal


if __name__ == "__main__":
    main()