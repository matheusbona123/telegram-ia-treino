import os
from bot import send_message
import openai

async def process_message(chat_id, text, user):
    step = user["step"]

    if step == "objetivo":
        if text not in ["hipertrofia", "emagrecimento", "condicionamento"]:
            raise ValueError(
                "Escolha um objetivo válido:\n"
                "👉 hipertrofia\n"
                "👉 emagrecimento\n"
                "👉 condicionamento"
            )
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual é seu peso atual (em kg)?")
        return

    if step == "peso":
        if not text.replace('.', '', 1).isdigit():
            raise ValueError("Digite um peso válido (ex: 72 ou 72.5).")
        user["peso"] = float(text)
        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return

    if step == "dias":
        if not text.isdigit():
            raise ValueError("Digite apenas o número de dias (ex: 3, 4 ou 5).")

        user["dias"] = int(text)

        try:
            treino_texto = gerar_treino_ia(
                user["objetivo"],
                user["peso"],
                user["dias"]
            )
            send_message(chat_id, treino_texto)
            user["step"] = "final"

        except Exception as e:
            print("Erro OpenAI:", e)
            send_message(
                chat_id,
                "⚠️ Ocorreu um erro ao gerar o treino. Tente novamente em instantes."
            )

        return


def gerar_treino_ia(objetivo, peso, dias):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise RuntimeError("Chave da OpenAI não configurada.")

    prompt = f"""
Você é um personal trainer profissional.
Crie um treino detalhado com base nos dados abaixo:

Objetivo: {objetivo}
Peso: {peso} kg
Dias de treino por semana: {dias}

Inclua:
- Aquecimento
- Exercícios principais
- Séries e repetições
- Dicas de segurança

Use linguagem clara e organizada.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )

    treino = response.choices[0].message.content.strip()
    return f"🏋️ Treino Personalizado\n\n{treino}"
