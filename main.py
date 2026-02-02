from fastapi import FastAPI, Request
from bot import send_message
from handlers import process_message

app = FastAPI()

# memória simples em runtime
users = {}

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    # proteção básica
    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").lower().strip()

    # cria usuário novo e INICIA conversa
    if chat_id not in users:
        users[chat_id] = {
            "step": "objetivo",
            "objetivo": None,
            "peso": None,
            "dias": None
        }

        send_message(
            chat_id,
            "🏋️‍♂️ Olá! Vamos montar seu treino personalizado.\n\n"
            
        )
        return {"ok": True}

    user = users[chat_id]

    try:
        await process_message(chat_id, text, user)

    except ValueError as e:
        send_message(chat_id, f"⚠️ {str(e)}")

    except Exception as e:
        print("Erro geral:", e)
        send_message(chat_id, "⚠️ Ocorreu um erro inesperado. Tente novamente.")

    return {"ok": True}
