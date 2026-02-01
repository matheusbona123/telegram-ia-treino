import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN não definido!")
URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    """
    Envia mensagem para o Telegram
    """
    requests.post(
        f"{URL}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )
