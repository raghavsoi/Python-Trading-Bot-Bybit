Crypto Trading Bot for Bybit (With Heiken Ashi, Pattern Recognition, and False Breakout Detection)

This is an advanced Python-based crypto trading bot designed for Bybit’s unified trading API. It uses technical indicators, Heiken Ashi candles, pattern recognition (e.g., wedges, double bottoms, head and shoulders), and a robust false breakout detection mechanism to make automated trades on the derivatives market.

Features

	•	Pattern Recognition: Detects various chart patterns like rising wedge, double bottom, symmetrical triangle, and more. Trades are executed based on pattern breakouts.
	•	Heiken Ashi Integration: Filters out noise and confirms trends to avoid entering trades in the wrong direction.
	•	False Breakout Detection: Uses indicators such as MACD, Bollinger Bands, Volume, and RSI Divergence to confirm the legitimacy of a breakout, reducing false signals.
	•	Customizable Trading Strategy: Supports dynamic take-profit (TP) and stop-loss (SL) levels based on pattern targets, customizable leverage, and order quantity.
	•	Enhanced Logging: Provides detailed logs of all actions, including pattern detections, trade execution, and API connection issues.

Requirements

Make sure to install the following dependencies before running the bot:

pip install pybit pandas ta-lib numpy

You will also need a Bybit account and API keys to connect the bot to Bybit’s trading environment.

Configuration

	1.	API Keys: Set your API keys in the keys.py file in the format:

api = "YOUR API KEY"
secret = "YOUR SECRET KEY"


	2.	Trading Configurations: Inside the main script, you can configure the following settings:
	•	leverage: Leverage used for trading.
	•	qty: Amount of USDT for one order.
	•	timeframe: Timeframe for candle data (default: 15 minutes).
	•	max_pos: Maximum number of open positions at any given time.
	•	pattern_target_pct: Fraction of the pattern target to take profit before completion.

Key Functions

Trading Logic

	•	Pattern Recognition: Detects chart patterns such as wedges, double bottoms, head and shoulders, and symmetrical triangles.
	•	Heiken Ashi Trend Confirmation: After a pattern is detected, Heiken Ashi candles are used to confirm the trend (bullish or bearish).
	•	False Breakout Detection: Before placing any order, the bot checks several indicators to detect potential false breakouts.

Trading Execution

	•	place_order_on_breakout(symbol, side, pattern_target): This function places a market order and calculates take profit and stop loss based on the breakout pattern target.

Indicators Used

	•	Heiken Ashi Candles: For trend detection.
	•	MACD: Confirms the momentum of the trend.
	•	Bollinger Bands: Detects breakouts outside the upper or lower bands.
	•	RSI Divergence: Identifies potential divergence for trend reversals.
	•	Volume: Confirms breakouts with high volume.

Example Workflow

	1.	The bot fetches data from Bybit and looks for chart patterns in the price action.
	2.	If a pattern is detected, it checks for a valid breakout using indicators (e.g., MACD, Bollinger Bands, RSI).
	3.	After confirming the trend with Heiken Ashi candles, the bot places a buy or sell order.
	4.	The bot sets the take profit (TP) before the pattern completes to lock in profits.
	5.	Stop loss (SL) is dynamically adjusted to protect against major losses.

How to Run the Bot

	1.	Clone the repository to your local machine:

git clone https://github.com/yourusername/crypto-trading-bot.git
cd crypto-trading-bot

	2.	Install the required dependencies:

pip install -r requirements.txt


	3.	Edit keys.py to include your Bybit API key and secret.
	4.	Run the bot:

python trading_bot.py


Notes

	•	Risk Disclaimer: Trading cryptocurrencies involves significant risk. Ensure that you understand the risks involved before using this bot.
	•	For Educational Use Only: This bot is provided as-is for educational purposes. The authors are not responsible for any financial losses incurred through its use.
