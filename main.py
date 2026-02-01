import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

# memória simples
users = {}

def send_message(chat_id, text):
    requests.post(
        f"{URL}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"].lower()

    # se usuário não existe, cria
    if chat_id not in users:
        users[chat_id] = {
            "step": "objetivo",
            "objetivo": None,
            "peso": None,
            "dias": None
        }
        send_message(chat_id, "Qual é seu objetivo? (hipertrofia, emagrecimento ou condicionamento)")
        return {"ok": True}

    user = users[chat_id]

    # passo 1
    if user["step"] == "objetivo":
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual é seu peso atual (em kg)?")
        return {"ok": True}

    # passo 2
    if user["step"] == "peso":
        user["peso"] = text
        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return {"ok": True}

    # passo 3
    if user["step"] == "dias":
        user["dias"] = text
        user["step"] = "final"
        send_message(
            chat_id,
            f"Perfeito! Objetivo: {user['objetivo']}, Peso: {user['peso']}kg, Dias: {user['dias']}x/semana."
        )
        return {"ok": True}

    return {"ok": True}
