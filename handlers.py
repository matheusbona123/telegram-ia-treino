import os
from bot import send_message
from openai import OpenAI

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY não definido!")

async def process_message(chat_id, text, user):
    step = user["step"]

    if step == "objetivo":
        if text not in ["hipertrofia", "emagrecimento", "condicionamento"]:
            send_message(chat_id, "Escolha um objetivo válido: hipertrofia, emagrecimento ou condicionamento.")
            return

        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual é seu peso atual (em kg)?")
        return

    if step == "peso":
        if not text.replace('.', '', 1).isdigit():
            send_message(chat_id, "Digite um peso válido em números.")
            return

        user["peso"] = float(text)
        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return

    if step == "dias":
        if not text.isdigit():
            send_message(chat_id, "Digite um número válido de dias.")
            return

        user["dias"] = int(text)

        treino_texto = gerar_treino_ia(
            user["objetivo"],
            user["peso"],
            user["dias"]
        )

        send_message(chat_id, treino_texto)
        user["step"] = "final"
        return


def gerar_treino_ia(objetivo, peso, dias):
    prompt = f"""
Você é um personal trainer profissional.
Crie um treino completo para uma pessoa com:

Objetivo: {objetivo}
Peso: {peso} kg
Dias de treino por semana: {dias}

Inclua:
- Aquecimento
- Exercícios principais
- Séries e repetições
- Observações de segurança

Escreva de forma clara e organizada para envio via Telegram.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um personal trainer experiente."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600
    )

    treino_texto = response.choices[0].message.content.strip()
    return f"🏋️ *Treino Personalizado*\n\n{treino_texto}"
