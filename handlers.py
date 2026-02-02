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
        return "Full Body (Foco em exercícios compostos)"
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
            send_message(chat_id, "📅 **Quantos dias vais treinar por semana? (3-6)**")
        except:
            send_message(chat_id, "❌ Indica apenas o número (ex: 75).")
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
            send_message(chat_id, "❌ Escolhe um número entre 3 e 6.")
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
        send_message(chat_id, "⏳ **Gerando sua ficha técnica...**")
        
        tipo_treino = escolher_tipo_treino(user["dias"])
        exercicios_str = ", ".join(EXERCICIOS_VALIDOS)
        
        prompt = f"""
Você é um Personal Trainer de elite. Gere um treino para um aluno {user['nivel']}.
Foco: {user['objetivo']} | Divisão: {tipo_treino} | Tempo: {user['tempo']}min

ESTRUTURA OBRIGATÓRIA:
- Use APENAS: {exercicios_str}.
- Divida o treino seguindo EXATAMENTE o modelo: {tipo_treino}.
- FORMATO POR EXERCÍCIO:
  📍 **Nome** | 🔄 `3x12` | ⏳ `60s`
  💡 *Dica: [Instrução CURTA e ESPECÍFICA para este movimento]*

REGRAS DE OURO:
1. PROIBIDO repetir a mesma dica técnica.
2. No Levantamento Terra e Agachamento, fale de "coluna neutra" e "base".
3. Nas Roscas e Tríceps, fale de "cotovelos fixos".
4. Vá direto aos treinos, sem introduções longas.
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "Você é um personal trainer direto que usa Markdown e nunca repete conselhos genéricos."},
                          {"role": "user", "content": prompt}],
                temperature=0.3
            )
            treino = response.choices[0].message.content.strip()
            
            send_long_message(chat_id, treino)
            send_message(chat_id, "✅ **Treino atualizado!** Bons ganhos. /start para recomeçar.")
            
        except Exception as e:
            send_message(chat_id, "⚠️ Erro ao gerar treino. Tente novamente.")

    # Reset limpo
    user.clear()
    user["step"] = "objetivo"
