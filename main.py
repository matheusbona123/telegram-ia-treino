from fastapi import FastAPI, Request
from handlers import process_message
from bot import send_message

app = FastAPI()

users = {}

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    if chat_id not in users:
        users[chat_id] = {
            "step": "inicio",
            "objetivo": None,
            "peso": None,
            "dias": None
        }
        # força a primeira pergunta
        await process_message(chat_id, "", users[chat_id])
        return {"ok": True}

    try:
        await process_message(chat_id, text, users[chat_id])
    except Exception as e:
        print("Erro geral:", e)
        send_message(chat_id, "⚠️ Ocorreu um erro. Tente novamente.")

    return {"ok": True}
