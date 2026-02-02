import os
from bot import send_message
from openai import OpenAI

# cria cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def process_message(chat_id, text, user):
    step = user["step"]

    if step == "objetivo":
        if text not in ["hipertrofia", "emagrecimento", "condicionamento"]:
            send_message(chat_id, "Escolha: hipertrofia, emagrecimento ou condicionamento.")
            return

        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual é seu peso atual (em kg)?")
        return

    if step == "peso":
        try:
            user["peso"] = float(text.replace(",", "."))
        except ValueError:
            send_message(chat_id, "Digite um peso válido. Ex: 80")
            return

        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return

    if step == "dias":
        if not text.isdigit():
            send_message(chat_id, "Digite apenas números. Ex: 3, 4 ou 5")
            return

        user["dias"] = int(text)

        send_message(chat_id, "⏳ Gerando seu treino personalizado...")
        treino = gerar_treino_ia(
            user["objetivo"],
            user["peso"],
            user["dias"]
        )

        send_message(chat_id, treino)
        user["step"] = "final"
        return


def gerar_treino_ia(objetivo, peso, dias):
    prompt = f"""
Você é um personal trainer profissional.

Crie um treino completo para:
- Objetivo: {objetivo}
- Peso: {peso} kg
- Dias de treino por semana: {dias}

Inclua:
• Aquecimento
• Exercícios principais
• Séries e repetições
• Dicas de segurança
• Organização clara para enviar no Telegram
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=700
    )

    texto = response.choices[0].message.content
    return f"🏋️ *Treino Personalizado*\n\n{texto}"
