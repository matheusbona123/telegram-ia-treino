import os
from bot import send_message
from openai import OpenAI

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não definido no ambiente")
    return OpenAI(api_key=api_key)

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
            user["peso"] = float(text)
        except ValueError:
            send_message(chat_id, "Digite um peso válido.")
            return

        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return

    if step == "dias":
        if not text.isdigit():
            send_message(chat_id, "Digite apenas números.")
            return

        user["dias"] = int(text)
        treino = gerar_treino_ia(user)
        send_message(chat_id, treino)
        user["step"] = "final"
        return


def gerar_treino_ia(user):
    client = get_client()

    prompt = f"""
Você é um personal trainer profissional.

Crie um treino completo com:
- Objetivo: {user['objetivo']}
- Peso: {user['peso']} kg
- Dias por semana: {user['dias']}

Inclua:
• Aquecimento
• Exercícios principais
• Séries e repetições
• Observações de segurança

Formato claro para Telegram.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700
    )

    texto = response.choices[0].message.content
    return f"🏋️ *Treino Personalizado*\n\n{texto}"
