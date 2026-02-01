from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
SEND_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

@app.get("/")
def home():
    return {"status": "online"}

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")

    if chat_id:
        requests.post(SEND_URL, json={
            "chat_id": chat_id,
            "text": f"Você disse: {text}"
        })

    return {"ok": True}
