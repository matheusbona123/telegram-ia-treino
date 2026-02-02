import os
import json
import random
from groq import Groq
from bot import send_message

# ======================
# CONFIGURAÇÃO GROQ
# ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def send_long_message(chat_id, text):
    chunk_size = 4000
    for i in range(0, len(text), chunk_size):
        send_message(chat_id, text[i:i+chunk_size])

def escolher_tipo_treino(dias):
    if dias == 3:
        return "Full Body (Todo o corpo em uma sessão)"
    elif dias == 4:
        return "Upper/Lower (Divisão Superior e Inferior)"
    else:
        return "Push/Pull/Legs (Divisão Empurrar, Puxar e Pernas)"

EXERCICIOS_VALIDOS = [
    "Supino Reto", "Supino Inclinado", "Agachamento", "Remada Curvada",
    "Puxada de Cabos", "Flexão de Braço", "Extensão de Perna",
    "Cadeira Abdutora", "Levantamento Terra", "Rosca Direta",
    "Tríceps Testa", "Elevação Lateral", "Leg Press"
]

async def process_message(chat_id: int, text: str, user: dict):
    
    # Início ou Reset
    if text == "/start" or user.get("step") == "objetivo":
        keyboard = {
            "inline_keyboard": [
                [{"text": "💪 Hipertrofia", "callback_data": "Hipertrofia"}],
                [{"text": "🏃 Emagrecimento", "callback_data": "Emagrecimento"}],
                [{"text": "🎯 Definição", "callback_data": "Definição"}]
            ]
        }
        send_message(chat_id, "🎯 **Qual é o teu objetivo?**", reply_markup=json.dumps(keyboard))
        user["step"] = "objetivo_resposta"
        return

    if user["step"] == "objetivo_resposta":
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "⚖️ **Qual o teu peso atual (kg)?**")
        return

    if user["step"] == "peso":
        try:
            user["peso"] = float(text.replace(",", "."))
            user["step"] = "dias"
            send_message(chat_id, "📅 **Quantos dias vais treinar? (3-6)**")
        except:
            send_message(chat_id, "❌ Indica apenas o número.")
        return

    if user["step"] == "dias":
        try:
            dias = int(text)
            if 3 <= dias <= 6:
                user["dias"] = dias
                user["step"] = "nivel"
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "Iniciante", "callback_data": "Iniciante"}],
                        [{"text": "Intermediário", "callback_data": "Intermediário"}],
                        [{"text": "Avançado", "callback_data": "Avançado"}]
                    ]
                }
                send_message(chat_id, "🏋️ **Qual o teu nível?**", reply_markup=json.dumps(keyboard))
            else: raise ValueError
        except:
            send_message(chat_id, "❌ Escolha entre 3 e 6.")
        return

    if user["step"] == "nivel":
        user["nivel"] = text
        user["step"] = "tempo"
        keyboard = {
            "inline_keyboard": [
                [{"text": "40 min", "callback_data": "40"}, {"text": "60 min", "callback_data": "60"}, {"text": "90 min", "callback_data": "90"}]
            ]
        }
        send_message(chat_id, "⏱️ **Duração do treino?**", reply_markup=json.dumps(keyboard))
        return

    if user["step"] == "tempo":
        user["tempo"] = text
        send_message(chat_id, "⏳ **Gerando sua ficha de exercícios...**")
        
        tipo_treino = escolher_tipo_treino(user["dias"])
        ex_str = ", ".join(EXERCICIOS_VALIDOS)
        
        prompt = f"Gere um treino para nível {user['nivel']} com foco em {user['objetivo']}. Divisão: {tipo_treino}. Use APENAS estes exercícios: {ex_str}. Regras: Sem dicas técnicas, sem combinar exercícios, liste 6 exercícios por treino. Formato: 📍 **Nome** | 🔄 `3x12` | ⏳ `60s`."

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Você é um personal trainer que gera apenas listas diretas em Markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            treino = response.choices[0].message.content.strip()
            send_long_message(chat_id, treino)
            send_message(chat_id, "✅ **Treino pronto!** /start para recomeçar.")
            
        except Exception as e:
            print(f"Erro na Groq: {e}")
            send_message(chat_id, "⚠️ Erro ao gerar treino.")

        user.clear()
        user["step"] = "objetivo"
