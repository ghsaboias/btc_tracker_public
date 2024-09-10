import websocket
import json
import requests
import os
import time
import logging
from dotenv import load_dotenv
from collections import deque

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

PRICE_CHANGE_THRESHOLD = 0.001
PERIODIC_UPDATE_INTERVAL = 600

price_history = deque(maxlen=PERIODIC_UPDATE_INTERVAL)

last_price_update_time = time.time()
last_periodic_update_time = time.time()

class NotificationTracker:
    def __init__(self):
        self.total_notifications = 0
        self.notifications_past_minute = deque(maxlen=60)

    def add_notification(self, notification_type):
        self.total_notifications += 1
        current_time = time.time()
        self.notifications_past_minute.append(current_time)
        
        while self.notifications_past_minute and current_time - self.notifications_past_minute[0] > 60:
            self.notifications_past_minute.popleft()

    def get_notifications_past_minute(self):
        return len(self.notifications_past_minute)

notification_tracker = NotificationTracker()

def setup_logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def log_price_update(current_price, price_change):
    logging.info(f"Price: ${current_price:.2f} | Change: {price_change:+.4f}%")

def log_notification(notification_type):
    notification_tracker.add_notification(notification_type)
    logging.info(f"NOTIFICATION: {notification_type} | Total: {notification_tracker.total_notifications} | Past minute: {notification_tracker.get_notifications_past_minute()}")

def on_message(ws, message):
    global last_price_update_time, last_periodic_update_time
    current_time = time.time()
    
    try:
        data = json.loads(message)
        new_price = float(data['p'])
        
        if not price_history:
            send_telegram_message(f"🚀 Bitcoin Price Tracker started. Current price: ${new_price:.2f}")
        
        
        if current_time - last_price_update_time >= 1:
            price_history.append((current_time, new_price))
            if len(price_history) > 1:
                current_price = price_history[-1][1]
                previous_price = price_history[-2][1]
                price_change = ((current_price - previous_price) / previous_price) * 100
                log_price_update(current_price, price_change)
                
                if abs(price_change) >= PRICE_CHANGE_THRESHOLD * 100:
                    send_alert_message(previous_price, current_price, price_change)
                    log_notification("PRICE_ALERT")
            
            last_price_update_time = current_time
    
        if current_time - last_periodic_update_time >= PERIODIC_UPDATE_INTERVAL:
            old_price = price_history[0][1]
            current_price = price_history[-1][1]
            send_periodic_update(old_price, current_price)
            log_notification("PERIODIC_UPDATE")
            last_periodic_update_time = current_time
    
    except Exception as e:
        logging.error(f"Error processing message: {e}")

def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    logging.warning(f"WebSocket connection closed. Status code: {close_status_code}, Message: {close_msg}")

def on_open(ws):
    logging.info("WebSocket connection opened")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logging.error(f"Failed to send Telegram message. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
        else:
            logging.info("Telegram message sent successfully")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")

def send_alert_message(old_price, new_price, price_change):
    message = f"🚨 BTC {price_change:.2f}% 1s change\n"
    message += f"Previous: ${old_price:.2f}\n"
    message += f"Current: ${new_price:.2f}"
    send_telegram_message(message)

def send_periodic_update(old_price, new_price):
    price_change = ((new_price - old_price) / old_price) * 100
    message = f"🔊 BTC {price_change:.2f}% 10min change\n"
    message += f"Previous: ${old_price:.2f}\n"
    message += f"Current: ${new_price:.2f}"
    send_telegram_message(message)

def run_websocket():
    logging.info("Initializing WebSocket...")
    ws = websocket.WebSocketApp(BINANCE_WS_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    
    logging.info("Starting WebSocket...")
    ws.run_forever()

if __name__ == "__main__":
    setup_logger()
    logging.info("Script started")
    while True:
        try:
            run_websocket()
        except Exception as e:
            logging.error(f"An error occurred in the main loop: {e}")
            logging.info("Attempting to reconnect in 60 seconds...")
            time.sleep(60)