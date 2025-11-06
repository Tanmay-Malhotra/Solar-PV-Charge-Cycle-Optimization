import requests

TELEGRAM_BOT_TOKEN = 

TELEGRAM_CHAT_ID = 

TELEGRAM_CHAT_IDS = 

# Add multiple chat IDs to notify more users
"""
def send_telegram_message(message):
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram notification failed: {e}")

"""
def send_telegram_message(message, chat_ids=TELEGRAM_CHAT_IDS):
    """
    Send a message to multiple Telegram chat IDs.
    
    Args:
        message (str): The message to send.
        chat_ids (list): List of chat IDs to send the message to. Defaults to TELEGRAM_CHAT_IDS.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for chat_id in chat_ids:
        try:
            payload = {"chat_id": chat_id, "text": message}
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            print(f"Message sent successfully to {chat_id}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send message to {chat_id}: {e}")
        except Exception as e:
            print(f"Unexpected error for {chat_id}: {e}")

if __name__ == "__main__":
    send_telegram_message("Test message from system.")

