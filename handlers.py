import os
import re
from bot import send_message
import openai

# 🔐 OpenAI Key
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY não definido!")

openai.api_key = OPENAI_KEY


async def process_message(chat_id, text, user):
    step = user["step"]
    text = text.lower().strip()

    # 🔹 PASSO 1 — OBJETIVO
    if step == "objetivo":
        if text not in ["hipertrofia", "emagrecimento", "condicionamento"]:
            send_message(
                chat_id,
                "❌ Objetivo inválido.\nEscolha: hipertrofia, emagrecimento ou condicionamento."
            )
            return

        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual é seu peso atual (em kg)?")
        return

    # 🔹 PASSO 2 — PESO
    if step == "peso":
        peso_texto = text.replace(",", ".")
        if not peso_texto.replace(".", "", 1).isdigit():
            send_message(chat_id, "❌ Digite um peso válido (ex: 72 ou 72.5).")
            return

        user["peso"] = float(peso_texto)
        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return

    # 🔹 PASSO 3 — DIAS
    if step == "dias":
        numeros = re.findall(r"\d+", text)

        if not numeros:
            send_message(
                chat_id,
                "❌ Não entendi.\nDigite apenas o número de dias (ex: 3, 4 ou 5)."
            )
            return

        dias = int(numeros[0])

        if dias < 1 or dias > 7:
            send_message(chat_id, "❌ Escolha entre 1 e 7 dias por semana.")
            return

        user["dias"] = dias

        # 🤖 GERAR TREINO COM IA
        treino_texto = gerar_treino_ia(
            user["objetivo"],
            user["peso"],
            user["dias"]
        )

        send_message(chat_id, treino_texto)
        user["step"] = "final"
        return


def gerar_treino_ia(objetivo, peso, dias):
    """
    Gera treino detalhado usando OpenAI
    """
    prompt = f"""
Você é um personal trainer profissional.

Crie um treino completo e bem estruturado para um aluno com os seguintes dados:
- Objetivo: {objetivo}
- Peso corporal: {peso} kg
- Dias de treino por semana: {dias}

Regras:
- Escolha a divisão de treino ideal (Full Body, ABC, Upper/Lower, etc.)
- Inclua aquecimento
- Liste exercícios com séries e repetições
- Ajuste volume e intensidade ao objetivo
- Linguagem clara, direta e organizada
- Formato adequado para envio no Telegram
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=650
    )

    treino = response.choices[0].message.content.strip()

    return f"🏋️ **Treino Personalizado**\n\n{treino}"
