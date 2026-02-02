import os
from groq import Groq
from bot import send_message

# Cliente Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY não definida")

client = Groq(api_key=GROQ_API_KEY)


async def process_message(chat_id: int, text: str, user: dict):

    # ETAPA 1 — OBJETIVO
    if user["step"] == "objetivo":
        if text not in ["hipertrofia", "emagrecimento", "condicionamento"]:
            raise ValueError(
                "Digite um objetivo válido:\n"
                "• hipertrofia\n"
                "• emagrecimento\n"
                "• condicionamento"
            )

        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "Qual é o seu peso atual (em kg)?")
        return

    # ETAPA 2 — PESO
    if user["step"] == "peso":
        try:
            user["peso"] = float(text.replace(",", "."))
        except ValueError:
            raise ValueError("Informe apenas números. Ex: 80")

        user["step"] = "dias"
        send_message(chat_id, "Quantos dias por semana você treina? (1 a 6)")
        return

    # ETAPA 3 — DIAS
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
Você é um PERSONAL TRAINER experiente.

Crie um treino de musculação REALISTA e PROFISSIONAL seguindo as regras abaixo:

REGRAS IMPORTANTES:
- Use SOMENTE nomes corretos de exercícios de academia no Brasil
- NÃO invente exercícios
- NÃO use termos como "barra fixa" para tudo
- NÃO repita exercícios iguais em dias diferentes
- NÃO escreva introduções longas
- NÃO corte o treino no final
- Organize bem para leitura no Telegram

DADOS DO ALUNO:
Objetivo: {user['objetivo']}
Peso: {user['peso']} kg
Dias por semana: {user['dias']}

ESTRUTURA OBRIGATÓRIA:
- Divida os treinos como Treino A, B, C (e D se necessário)
- Para cada treino, informe:
  • Grupos musculares
  • Aquecimento curto
  • Exercícios (com séries e repetições)
  • Tempo de descanso

EXEMPLOS DE EXERCÍCIOS VÁLIDOS:
Supino reto, supino inclinado, crucifixo, desenvolvimento com halteres,
elevação lateral, puxada frontal, remada curvada, agachamento livre,
leg press, cadeira extensora, mesa flexora, rosca direta, tríceps pulley,
panturrilha em pé, prancha abdominal.

FORMATAÇÃO:
- Use títulos claros
- Use listas numeradas
- Linguagem objetiva e profissional
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Você é um personal trainer profissional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=900
            )

            treino = response.choices[0].message.content.strip()

            send_message(chat_id, f"🏋️‍♂️ *Treino Personalizado*\n\n{treino}")

            # reinicia fluxo
            user["step"] = "objetivo"

        except Exception as e:
            print("Erro Groq:", e)
            send_message(chat_id, "⚠️ Ocorreu um erro ao gerar o treino. Tente novamente.")
            user["step"] = "objetivo"
