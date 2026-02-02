from fastapi import FastAPI, Request
from bot import send_message
from handlers import process_message

app = FastAPI()

# memória simples em runtime
users = {}

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    chat_id = None
    text = ""
    is_callback = False

    # 1. Verifica se é uma mensagem de texto
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").lower().strip()
    
    # 2. Verifica se é um clique em botão (callback_query)
    elif "callback_query" in data:
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        text = data["callback_query"]["data"].lower().strip()
        is_callback = True

    # Se não for nenhum dos dois, ignora
    if not chat_id:
        return {"ok": True}

    # 3. Gerenciamento de estado do usuário
    if chat_id not in users:
        users[chat_id] = {
            "step": "objetivo",
            "objetivo": None,
            "peso": None,
            "dias": None
        }
        # Em vez de esperar um "oi", já inicia o fluxo
        await process_message(chat_id, "/start", users[chat_id])
        return {"ok": True}

    user = users[chat_id]

    try:
        # Processa a entrada (seja texto ou dado do botão)
        await process_message(chat_id, text, user)

    except ValueError as e:
        send_message(chat_id, f"⚠️ {str(e)}")

    except Exception as e:
        print("Erro geral:", e)
        send_message(chat_id, "⚠️ Ocorreu um erro inesperado. Tente novamente.")

    return {"ok": True}
