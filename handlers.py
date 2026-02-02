import os
import json
import random
from groq import Groq
from bot import send_message

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def send_long_message(chat_id, text):
    chunk_size = 4000
    for i in range(0, len(text), chunk_size):
        send_message(chat_id, text[i:i+chunk_size])

def escolher_tipo_treino(dias):
    return random.choice(["ABC", "Full Body"]) if dias <= 4 else random.choice(["Push/Pull/Legs", "Upper/Lower"])

EXERCICIOS_VALIDOS = [
    "Supino Reto", "Supino Inclinado", "Agachamento", "Remada Curvada",
    "Puxada de Cabos", "Flexão de Braço", "Extensão de Perna",
    "Cadeira Abdutora", "Levantamento Terra", "Rosca Direta",
    "Tríceps Testa", "Elevação Lateral", "Leg Press"
]

async def process_message(chat_id: int, text: str, user: dict):
    # Se for o início ou o bot resetado
    if text == "/start" or user.get("step") == "objetivo":
        keyboard = {
            "inline_keyboard": [
                [{"text": "💪 Hipertrofia", "callback_data": "hipertrofia"}],
                [{"text": "🏃 Emagrecimento", "callback_data": "emagrecimento"}],
                [{"text": "🧘 Condicionamento", "callback_data": "condicionamento"}]
            ]
        }
        send_message(chat_id, "🎯 Qual é seu objetivo?", reply_markup=json.dumps(keyboard))
        user["step"] = "objetivo_resposta"
        return

    if user["step"] == "objetivo_resposta":
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "⚖️ Qual seu peso atual (em kg)?\nEx: 80")
        return

    if user["step"] == "peso":
        try:
            user["peso"] = float(text.replace(",", "."))
            user["step"] = "dias"
            send_message(chat_id, "📅 Quantos dias por semana você treina? (3 a 6)")
        except:
            send_message(chat_id, "❌ Informe apenas números. Ex: 80")
        return

    if user["step"] == "dias":
        try:
            dias = int(text)
            if 3 <= dias <= 6:
                user["dias"] = dias
                user["step"] = "nivel"
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "Iniciante", "callback_data": "1"}],
                        [{"text": "Intermediário", "callback_data": "2"}],
                        [{"text": "Avançado", "callback_data": "3"}]
                    ]
                }
                send_message(chat_id, "🏋️ Qual seu nível?", reply_markup=json.dumps(keyboard))
            else: raise ValueError
        except:
            send_message(chat_id, "❌ Informe um número entre 3 e 6.")
        return

    if user["step"] == "nivel":
        niveis = {"1": "Iniciante", "2": "Intermediário", "3": "Avançado"}
        user["nivel"] = niveis.get(text, "Iniciante")
        user["step"] = "tempo"
        keyboard = {
            "inline_keyboard": [
                [{"text": "40 min", "callback_data": "40"}, {"text": "60 min", "callback_data": "60"}, {"text": "90 min", "callback_data": "90"}]
            ]
        }
        send_message(chat_id, "⏱️ Tempo por treino?", reply_markup=json.dumps(keyboard))
        return

    if user["step"] == "tempo":
        user["tempo"] = text
        send_message(chat_id, "⏳ Gerando seu treino... aguarde.")
        
        tipo_treino = escolher_tipo_treino(user["dias"])
        exercicios_str = ", ".join(EXERCICIOS_VALIDOS)
        
        prompt = f"Você é um PERSONAL TRAINER. Crie um treino {tipo_treino} para objetivo {user['objetivo']}, nível {user['nivel']}, {user['tempo']} min. Use apenas: {exercicios_str}."

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            treino = response.choices[0].message.content.strip()
            send_long_message(chat_id, treino)
            send_message(chat_id, "✅ Treino finalizado! Digite /start para criar um novo.")
        except:
            send_message(chat_id, "⚠️ Erro ao gerar. Tente novamente.")
        
        # Reset
        user.clear()
        user["step"] = "objetivo"
