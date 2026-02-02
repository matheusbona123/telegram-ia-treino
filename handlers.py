import os
from groq import Groq
from bot import send_message

# inicializa cliente Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
            user["dias"] = int(text)
        except ValueError:
            raise ValueError("Informe apenas o número de dias (ex: 4)")

        send_message(chat_id, "⏳ Gerando seu treino personalizado...")

        prompt = f"""
        Crie um treino de musculação detalhado para uma pessoa com:
        - Objetivo: {user['objetivo']}
        - Peso: {user['peso']} kg
        - Dias de treino por semana: {user['dias']}

        Separe por dias, com exercícios, séries e repetições.
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Você é um personal trainer experiente."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            treino = response.choices[0].message.content
            send_message(chat_id, treino)

            # reset do usuário
            user["step"] = "objetivo"

        except Exception as e:
            print("Erro Groq:", e)
            send_message(chat_id, "⚠️ Ocorreu um erro ao gerar o treino. Tente novamente.")
