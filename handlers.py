import os
from bot import send_message
import openai

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY não definido!")
openai.api_key = OPENAI_KEY

async def process_message(chat_id, text, user):
    step = user["step"]

    if step == "objetivo":
        if text not in ["hipertrofia", "emagrecimento", "condicionamento"]:
            raise ValueError("Escolha um objetivo válido: hipertrofia, emagrecimento ou condicionamento.")
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual é seu peso atual (em kg)?")
        return

    if step == "peso":
        if not text.replace('.', '', 1).isdigit():
            raise ValueError("Digite um peso válido em números.")
        user["peso"] = float(text)
        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return

    if step == "dias":
        if not text.isdigit():
            raise ValueError("Digite um número válido de dias.")
        user["dias"] = int(text)
        treino_texto = gerar_treino_ia(user["objetivo"], user["peso"], user["dias"])
        send_message(chat_id, treino_texto)
        user["step"] = "final"
        return

def gerar_treino_ia(objetivo, peso, dias):
    """Gera treino detalhado via OpenAI"""
    prompt = f"""
Você é um personal trainer. Crie um treino completo para uma pessoa com os seguintes dados:
- Objetivo: {objetivo}
- Peso: {peso}kg
- Dias de treino por semana: {dias}
Inclua aquecimento, exercícios principais, séries, repetições e dicas.
Varie os exercícios conforme o objetivo e torne o treino seguro e eficiente.
Escreva de forma clara e organizada para enviar no Telegram.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )
    treino_texto = response.choices[0].message.content.strip()
    return f"🏋️ **Treino Personalizado**\n\n{treino_texto}"
