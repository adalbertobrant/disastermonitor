# src/utils.py
import logging
import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

def send_telegram_alert(message: str):
    """Sends an alert message via Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram Bot Token or Chat ID not set. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        logger.info("Telegram alert sent successfully.")
    except requests.RequestException as e:
        logger.error(f"Error sending Telegram message: {e}", exc_info=True)
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error sending Telegram message: {e}", exc_info=True)
