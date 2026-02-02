from fastapi import FastAPI, Request
from bot import send_message
from handlers import process_message

app = FastAPI()

# memória simples dos usuários
users = {}

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    # extrair informações do Telegram
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"].lower()

    # cria usuário se não existir
    if chat_id not in users:
        users[chat_id] = {"step": "objetivo", "objetivo": None, "peso": None, "dias": None}

    user = users[chat_id]

    try:
        await process_message(chat_id, text, user)
    except ValueError as e:
        send_message(chat_id, str(e))
    except Exception as e:
        send_message(chat_id, "Ocorreu um erro, tente novamente.")
        print(f"Erro: {e}")

    return {"ok": True}
