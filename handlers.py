import os
from groq import Groq
from bot import send_message

# inicializa cliente Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY não definida")

client = Groq(api_key=GROQ_API_KEY)


async def process_message(chat_id: int, text: str, user: dict):

    # ETAPA 1 - OBJETIVO
    if user["step"] == "objetivo":
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual seu peso atual (em kg)?")
        return

    # ETAPA 2 - PESO
    if user["step"] == "peso":
        try:
            user["peso"] = float(text.replace(",", "."))
        except ValueError:
            raise ValueError("Informe o peso apenas com números (ex: 80)")

        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return

    # ETAPA 3 - DIAS
    if user["step"] == "dias":
        try:
            dias = int(text)
            if dias < 1 or dias > 6:
                raise ValueError
            user["dias"] = dias
        except ValueError:
            raise ValueError("Informe um número de dias válido (1 a 6)")

        send_message(chat_id, "⏳ Gerando seu treino personalizado...")

        prompt = f"""
Você é um personal trainer experiente.

Crie um treino de musculação seguro e eficiente com:
- Objetivo: {user['objetivo']}
- Peso: {user['peso']} kg
- Dias de treino por semana: {user['dias']}

Separe por dias da semana.
Inclua aquecimento, exercícios, séries e repetições.
Use linguagem clara para WhatsApp/Telegram.
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Você é um personal trainer profissional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=700
            )

            if not response.choices:
                raise RuntimeError("Resposta vazia da IA")

            treino = response.choices[0].message.content.strip()

            send_message(chat_id, f"🏋️‍♂️ **Treino Personalizado**\n\n{treino}")

            # reset do fluxo
            user["step"] = "objetivo"

        except Exception as e:
            print("Erro Groq:", e)
            send_message(chat_id, "⚠️ Ocorreu um erro ao gerar o treino. Tente novamente.")
            user["step"] = "objetivo"
