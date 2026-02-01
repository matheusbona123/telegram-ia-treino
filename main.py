import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

# 🔹 DICIONÁRIO DE TREINOS
treinos = {
    "fullbody": [
        "Agachamento livre",
        "Supino reto",
        "Remada curvada",
        "Desenvolvimento com halteres",
        "Abdominal prancha"
    ],
    "a": [
        "Supino reto",
        "Supino inclinado",
        "Crucifixo",
        "Tríceps testa",
        "Tríceps corda"
    ],
    "b": [
        "Puxada frontal",
        "Remada baixa",
        "Remada unilateral",
        "Rosca direta",
        "Rosca alternada"
    ],
    "c": [
        "Agachamento",
        "Leg press",
        "Mesa flexora",
        "Cadeira extensora",
        "Panturrilha em pé"
    ]
}

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

    # comando para resetar a conversa
    if text == "/reset":
        users[chat_id] = {"step": "objetivo", "objetivo": None, "peso": None, "dias": None}
        send_message(chat_id, "Conversa reiniciada. Qual é seu objetivo? (hipertrofia, emagrecimento ou condicionamento)")
        return {"ok": True}

    # se usuário não existe, cria
    if chat_id not in users:
        users[chat_id] = {"step": "objetivo", "objetivo": None, "peso": None, "dias": None}
        send_message(chat_id, "Qual é seu objetivo? (hipertrofia, emagrecimento ou condicionamento)")
        return {"ok": True}

    user = users[chat_id]

    # passo 1: objetivo
    if user["step"] == "objetivo":
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual é seu peso atual (em kg)?")
        return {"ok": True}

    # passo 2: peso
    elif user["step"] == "peso":
        user["peso"] = text
        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return {"ok": True}

    # passo 3: dias
    elif user["step"] == "dias":
        try:
            user["dias"] = int(text)
        except ValueError:
            send_message(chat_id, "Por favor, digite apenas números para os dias de treino.")
            return {"ok": True}

        objetivo = user["objetivo"]

        # definir divisão
        if user["dias"] <= 2:
            divisao = "Full Body"
            exercicios = treinos["fullbody"]
        else:
            divisao = "ABC"
            exercicios = treinos["a"] + treinos["b"] + treinos["c"]

        # definir repetições
        if objetivo == "hipertrofia":
            reps = "3x 8–12"
        elif objetivo == "emagrecimento":
            reps = "3x 12–15"
        else:
            reps = "3x 15+"

        treino_texto = f"🏋️ Treino sugerido ({divisao})\n"
        for ex in exercicios:
            treino_texto += f"- {ex}: {reps}\n"

        send_message(chat_id, treino_texto)
        user["step"] = "final"
        return {"ok": True}

    # caso o usuário já tenha completado o fluxo
    elif user["step"] == "final":
        send_message(chat_id, "Você já completou o fluxo. Digite /reset para começar novamente.")
        return {"ok": True}
