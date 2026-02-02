import os
import re
from bot import send_message
import openai


async def process_message(chat_id, text, user):
    step = user["step"]
    text = text.lower().strip()

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

    if step == "peso":
        peso_texto = text.replace(",", ".")
        if not peso_texto.replace(".", "", 1).isdigit():
            send_message(chat_id, "❌ Digite um peso válido (ex: 72 ou 72.5).")
            return

        user["peso"] = float(peso_texto)
        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina?")
        return

    if step == "dias":
        numeros = re.findall(r"\d+", text)

        if not numeros:
            send_message(chat_id, "❌ Digite apenas o número de dias (ex: 3, 4 ou 5).")
            return

        dias = int(numeros[0])

        if dias < 1 or dias > 7:
            send_message(chat_id, "❌ Escolha entre 1 e 7 dias por semana.")
            return

        user["dias"] = dias

        try:
            treino_texto = gerar_treino_ia(
                user["objetivo"],
                user["peso"],
                user["dias"]
            )
            send_message(chat_id, treino_texto)
            user["step"] = "final"

        except Exception as e:
            send_message(
                chat_id,
                "⚠️ Ocorreu um erro ao gerar o treino. Tente novamente em instantes."
            )
            print("Erro IA:", e)

        return


def gerar_treino_ia(objetivo, peso, dias):
    # 🔐 Só valida a chave AQUI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não configurada no ambiente.")

    openai.api_key = api_key

    prompt = f"""
Você é um personal trainer profissional.

Crie um treino completo para:
- Objetivo: {objetivo}
- Peso: {peso} kg
- Dias de treino por semana: {dias}

Inclua:
- Divisão correta do treino
- Aquecimento
- Exercícios com séries e repetições
- Linguagem clara para Telegram
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=650
    )

    treino = response.choices[0].message.content.strip()
    return f"🏋️ **Treino Personalizado**\n\n{treino}"
