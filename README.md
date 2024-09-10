# Bitcoin Price Tracker

A real-time Bitcoin price tracker that monitors the BTC/USDT pair on Binance and sends alerts via Telegram.

## Features

- Real-time price monitoring using Binance WebSocket
- Price change alerts for significant short-term movements
- Periodic updates every 10 minutes
- Telegram notifications for alerts and updates
- Logging of price changes and notifications

## Requirements

- Python 3.7+
- Required packages: websocket-client, requests, python-dotenv

## Setup

1. Install required packages: `pip install websocket-client requests python-dotenv`
2. Create a `.env` file with your Telegram bot token and chat ID:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```
3. Run the script: `python main.py`

## Configuration

Adjust these variables in the script to customize behavior:

- `PRICE_CHANGE_THRESHOLD`: Minimum price change percentage for alerts
- `PERIODIC_UPDATE_INTERVAL`: Time between periodic updates (in seconds)

## Note

Ensure stable internet connection for continuous operation. The script will attempt to reconnect if the WebSocket connection is lost.
