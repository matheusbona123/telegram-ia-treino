import os
import re
import traceback
from openai import OpenAI

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY não definido!")

client = OpenAI()

user_states = {}

def extract_number(text):
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


async def process_message(user_id: str, message: str):
    message = message.strip()
    state = user_states.get(user_id, {"step": "ask_days"})
    step = state.get("step")

    try:
        # 1️⃣ Dias de treino
        if step == "ask_days":
            days = extract_number(message)

            if not days or days < 1 or days > 7:
                return "Quantos dias por semana você treina? (1 a 7)"

            state.update({
                "days": days,
                "step": "ask_goal"
            })
            user_states[user_id] = state

            return f"Perfeito 💪 Você treina {days} dias. Qual é o seu objetivo?"

        # 2️⃣ Objetivo
        if step == "ask_goal":
            if len(message) < 3:
                return "Me diga melhor seu objetivo 🙂"

            state.update({
                "goal": message,
                "step": "generate"
            })
            user_states[user_id] = state

        # 3️⃣ Gerar treino
        if state.get("step") == "generate":
            days = state.get("days")
            goal = state.get("goal")

            if not days or not goal:
                raise ValueError("Estado incompleto para gerar treino")

            prompt = f"""
            Monte um treino de musculação para:
            - Dias por semana: {days}
            - Objetivo: {goal}

            Seja claro, organizado e prático.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um personal trainer experiente."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            treino = response.choices[0].message.content

            state["step"] = "done"
            user_states[user_id] = state

            return treino

        return "Vamos recomeçar 🙂 Quantos dias por semana você treina?"

    except Exception as e:
        print("❌ ERRO AO GERAR TREINO")
        print(traceback.format_exc())

        return "⚠️ Ocorreu um erro ao gerar o treino. Tente novamente em instantes."
