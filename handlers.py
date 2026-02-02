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

# Lógica de treino baseada em ciência esportiva
def escolher_tipo_treino(dias):
    if dias == 3:
        return "Full Body (Corpo Inteiro)"
    elif dias == 4:
        return "Upper/Lower (Membros Superiores e Inferiores)"
    else:
        return "Push/Pull/Legs (Empurrar, Puxar e Pernas)"

EXERCICIOS_VALIDOS = [
    "Supino Reto", "Supino Inclinado", "Agachamento", "Remada Curvada",
    "Puxada de Cabos", "Flexão de Braço", "Extensão de Perna",
    "Cadeira Abdutora", "Levantamento Terra", "Rosca Direta",
    "Tríceps Testa", "Elevação Lateral", "Leg Press"
]

async def process_message(chat_id: int, text: str, user: dict):
    
    # Início do Fluxo ou comando /start
    if text == "/start" or user.get("step") == "objetivo":
        keyboard = {
            "inline_keyboard": [
                [{"text": "💪 Hipertrofia", "callback_data": "Hipertrofia"}],
                [{"text": "🏃 Emagrecimento", "callback_data": "Emagrecimento"}],
                [{"text": "🎯 Definição", "callback_data": "Definição"}]
            ]
        }
        send_message(chat_id, "🎯 **Qual é seu objetivo principal?**", reply_markup=json.dumps(keyboard))
        user["step"] = "objetivo_resposta"
        return

    if user["step"] == "objetivo_resposta":
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "⚖️ **Qual seu peso atual (em kg)?**\nEx: 80")
        return

    if user["step"] == "peso":
        try:
            user["peso"] = float(text.replace(",", "."))
            user["step"] = "dias"
            send_message(chat_id, "📅 **Quantos dias por semana você vai treinar?**\n(Responda de 3 a 6)")
        except:
            send_message(chat_id, "❌ Por favor, mande apenas o número do seu peso.")
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
                send_message(chat_id, "🏋️ **Qual seu nível atual de experiência?**", reply_markup=json.dumps(keyboard))
            else:
                send_message(chat_id, "❌ Escolha entre 3 e 6 dias.")
        except:
            send_message(chat_id, "❌ Digite um número de 3 a 6.")
        return

    if user["step"] == "nivel":
        user["nivel"] = text
        user["step"] = "tempo"
        keyboard = {
            "inline_keyboard": [
                [{"text": "40 min", "callback_data": "40"}, {"text": "60 min", "callback_data": "60"}, {"text": "90 min", "callback_data": "90"}]
            ]
        }
        send_message(chat_id, "⏱️ **Quanto tempo você tem para cada treino?**", reply_markup=json.dumps(keyboard))
        return

    if user["step"] == "tempo":
        user["tempo"] = text
        send_message(chat_id, "⏳ **Estou montando seu cronograma...**")
        
        tipo_treino = escolher_tipo_treino(user["dias"])
        exercicios_str = ", ".join(EXERCICIOS_VALIDOS)
        
        prompt = f"""
Você é um Personal Trainer profissional. Gere um treino técnico para um aluno {user['nivel']}.
Objetivo: {user['objetivo']} | Peso: {user['peso']}kg | Duração: {user['tempo']}min.

ESTRUTURA OBRIGATÓRIA:
1. Divisão: {tipo_treino}.
2. Use APENAS estes exercícios: {exercicios_str}.
3. Para cada exercício, coloque: Nome, Séries x Repetições, Descanso e uma DICA TÉCNICA REAL.
4. PROIBIDO dizer "costas arqueadas" para tudo. Seja específico (ex: "coluna neutra no Terra", "cotovelos 45° no Supino").
5. Formate com **Negritos** para títulos.

No final, mande uma frase motivacional curta.
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "Você é um personal experiente que usa Markdown."},
                          {"role": "user", "content": prompt}],
                temperature=0.6
            )
            treino = response.choices[0].message.content.strip()
            
            # Envia o treino formatado
            send_long_message(chat_id, treino)
            send_message(chat_id, "✅ **Treino finalizado!**\nSe quiser mudar algo, use o comando /start.")
            
        except Exception as e:
            print(f"Erro: {e}")
            send_message(chat_id, "⚠️ Erro ao gerar treino. Tente novamente.")

        # Reset limpo do usuário
        user.clear()
        user["step"] = "objetivo"
