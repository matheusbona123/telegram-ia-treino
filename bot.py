import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN não definido!")

URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text, reply_markup=None):
    """Envia mensagem para o usuário via Telegram, agora com suporte a botões"""
    payload = {
        "chat_id": chat_id, 
        "text": text
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup

    requests.post(f"{URL}/sendMessage", json=payload)
