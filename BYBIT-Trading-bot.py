from keys import api, secret
from pybit.unified_trading import HTTP
import pandas as pd
import ta
from time import sleep
import numpy as np

session = HTTP(
    api_key=api,
    api_secret=secret
)

# Config:
leverage = 10
qty = 50    # Amount of USDT for one order
timeframe = 15  # 15 minutes
max_pos = 50    # Max current orders
pattern_target_pct = 0.8  # Exit before the pattern completes fully

# Enhanced console printing
def log(message, symbol=None):
    if symbol:
        print(f"[{symbol}] {message}")
    else:
        print(message)

# Fetch candlestick data (klines) for a given symbol
def klines(symbol):
    try:
        resp = session.get_kline(
            category='linear',
            symbol=symbol,
            interval=timeframe,
            limit=500
        )['result']['list']
        df = pd.DataFrame(resp)
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        df.set_index('Time', inplace=True)
        df = df.astype(float)
        return df[::-1]
    except Exception as err:
        log(f"Error fetching klines for {symbol}: {err}")

# Calculate Heiken Ashi candles
def heiken_ashi(df):
    ha_df = pd.DataFrame(index=df.index)
    ha_df['Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    ha_df['Open'] = (df['Open'].shift(1) + df['Close'].shift(1)) / 2
    ha_df['High'] = df[['Open', 'Close', 'High']].max(axis=1)
    ha_df['Low'] = df[['Open', 'Close', 'Low']].min(axis=1)
    return ha_df

# Volume confirmation: Check if volume spikes on breakout
def volume_confirmation(df):
    avg_volume = df['Volume'].rolling(window=20).mean()
    return df['Volume'].iloc[-1] > avg_volume.iloc[-1]

# MACD confirmation: Check MACD trend alignment
def macd_confirmation(df):
    macd = ta.trend.MACD(df['Close'])
    return macd.macd_diff().iloc[-1] > 0  # Positive MACD difference confirms bullish trend

# Bollinger Band confirmation: Check for breakout outside Bollinger Bands
def bollinger_band_confirmation(df):
    bollinger = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    upper_band = bollinger.bollinger_hband().iloc[-1]
    lower_band = bollinger.bollinger_lband().iloc[-1]
    close = df['Close'].iloc[-1]
    return (close > upper_band or close < lower_band)

# RSI Divergence confirmation: Check for divergence
def rsi_divergence(df):
    rsi = ta.momentum.RSIIndicator(df['Close']).rsi()
    return rsi.iloc[-1] < 70 and rsi.iloc[-1] > 30  # Avoid overbought/oversold conditions

# Check trend using Heiken Ashi candles
def heiken_ashi_trend(ha_df):
    ha_close = ha_df['Close']
    ha_open = ha_df['Open']
    if ha_close.iloc[-1] > ha_open.iloc[-1]:
        return 'bullish'
    elif ha_close.iloc[-1] < ha_open.iloc[-1]:
        return 'bearish'
    return 'neutral'

# Pattern detection functions (e.g., wedges, double bottom, etc.) from earlier

# False breakout detection
def false_breakout_detection(df):
    return volume_confirmation(df) and macd_confirmation(df) and bollinger_band_confirmation(df) and rsi_divergence(df)

# General pattern detection (adds all detection functions)
def detect_patterns(symbol):
    df = klines(symbol)
    ha_df = heiken_ashi(df)
    
    patterns = {
        'wedge': detect_wedge(df),
        'double_bottom_top': detect_double_bottom_top(df),
        'head_and_shoulders': detect_head_and_shoulders(df),
        'symmetrical_triangle': detect_symmetrical_triangle(df)
    }
    
    for pattern, signal in patterns.items():
        if signal != 'none':
            log(f"{pattern} detected for {symbol}. Signal: {signal}")
            
            # Check for false breakout
            if not false_breakout_detection(df):
                log(f"False breakout detected for {symbol}. Ignoring the signal.")
                return 'none'
            
            # Check Heiken Ashi trend
            ha_trend = heiken_ashi_trend(ha_df)
            if ha_trend == 'bullish' and signal == 'buy':
                log(f"Bullish trend confirmed by Heiken Ashi for {symbol}")
                return 'buy'
            elif ha_trend == 'bearish' and signal == 'sell':
                log(f"Bearish trend confirmed by Heiken Ashi for {symbol}")
                return 'sell'
            else:
                log(f"Neutral or conflicting trend detected by Heiken Ashi for {symbol}. Ignoring the signal.")
                return 'none'
    
    return 'none'

# Place market order with dynamic SL/TP using pattern target and Heiken Ashi trend
def place_order_on_breakout(symbol, side, pattern_target):
    price_precision, qty_precision = get_precisions(symbol)
    mark_price = float(session.get_tickers(category='linear', symbol=symbol)['result']['list'][0]['markPrice'])
    
    order_qty = round(qty / mark_price, qty_precision)
    
    # Calculate take profit at a fraction of the pattern target
    if side == 'buy':
        tp_price = mark_price + pattern_target * pattern_target_pct
    else:
        tp_price = mark_price - pattern_target * pattern_target_pct

    log(f'Placing {side.upper()} order for {symbol} with target: {tp_price}')
    try:
        resp = session.place_order(
            category='linear',
            symbol=symbol,
            side='Buy' if side == 'buy' else 'Sell',
            orderType='Market',
            qty=order_qty,
            takeProfit=round(tp_price, price_precision),
            stopLoss=round(mark_price, price_precision),  # Set a tight stop loss to protect
            tpTriggerBy='Market',
            slTriggerBy='Market'
        )
        log(f"Order Response: {resp}", symbol)
    except Exception as err:
        log(f"Error placing order: {err}", symbol)

# Main loop for pattern scanning and order placement
symbols = get_tickers()

while True:
    balance = get_balance()
    if balance is None:
        log('Could not retrieve balance. Check API connection.')
    else:
        log(f'Balance: {balance} USDT')
        pos = get_positions()
        log(f'Open positions: {len(pos)}')

        if len(pos) < max_pos:
            for symbol in symbols:
                pos = get_positions()
                if len(pos) >= max_pos:
                    break

                signal = detect_patterns(symbol)

                if signal == 'buy':
                    log(f'BUY signal detected for {symbol}')
                    place_order_on_breakout(symbol, 'buy', pattern_target=0.05)  # Example pattern target
                    sleep(5)
                elif signal == 'sell':
                    log(f'SELL signal detected for {symbol}')
                    place_order_on_breakout(symbol, 'sell', pattern_target=0.05)  # Example pattern target
                    sleep(5)

    log('Waiting 2 minutes before the next check...')
    sleep(120)