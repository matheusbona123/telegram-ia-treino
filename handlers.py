import os
from groq import Groq
from bot import send_message

# ===============================
# CONFIGURAÇÃO GROQ
# ===============================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY não definida")

client = Groq(api_key=GROQ_API_KEY)


# ===============================
# PROCESSAMENTO DE MENSAGENS
# ===============================
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
        send_message(chat_id, "Quantos dias por semana você treina? (1 a 6)")
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

        # ===============================
        # PROMPT PROFISSIONAL
        # ===============================
        prompt = f"""
Você é um personal trainer brasileiro, experiente e técnico.

Crie um treino de musculação:
- Objetivo: {user['objetivo']}
- Peso: {user['peso']} kg
- Dias de treino por semana: {user['dias']}

REGRAS OBRIGATÓRIAS:
- Use SOMENTE nomes de exercícios comuns no Brasil
- Não invente exercícios
- Não traduza nomes de forma errada
- Use divisão clássica (ABC, ABCD ou Push/Pull/Legs)
- Não use dias da semana (use Treino A, B, C...)
- Linguagem simples, direta e profissional
- Formatação clara para Telegram

FORMATO EXATO:

🏋️ Treino A – (músculos trabalhados)
Aquecimento:
- descrição curta

Exercícios:
1. Nome do exercício – X séries x Y repetições
2. Nome do exercício – X séries x Y repetições

Descanso:
- Entre séries: X segundos

Repita para todos os treinos.
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Você é um personal trainer profissional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )

            if not response.choices:
                raise RuntimeError("Resposta vazia da IA")

            treino = response.choices[0].message.content.strip()

            send_message(chat_id, f"🏋️‍♂️ *Treino Personalizado*\n\n{treino}")

            # reset do fluxo
            user["step"] = "objetivo"

        except Exception as e:
            print("Erro Groq:", e)
            send_message(chat_id, "⚠️ Ocorreu um erro ao gerar o treino. Tente novamente.")
            user["step"] = "objetivo"
