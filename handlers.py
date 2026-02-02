import os
import random
from groq import Groq
from bot import send_message

# ======================
# CONFIGURAÇÃO GROQ
# ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY não definida")

client = Groq(api_key=GROQ_API_KEY)

# ======================
# FUNÇÃO PARA ENVIAR MENSAGENS LONGAS
# ======================
def send_long_message(chat_id, text):
    chunk_size = 4000  # Telegram corta acima de 4096
    for i in range(0, len(text), chunk_size):
        send_message(chat_id, text[i:i+chunk_size])


# ======================
# FUNÇÃO PARA ESCOLHER TIPO DE TREINO
# ======================
def escolher_tipo_treino(dias):
    """
    Retorna tipo de treino baseado na quantidade de dias:
    - 3 a 4 dias: Full Body ou ABC
    - 5 a 6 dias: Push/Pull/Legs ou Upper/Lower
    """
    if dias <= 4:
        return random.choice(["ABC", "Full Body"])
    else:
        return random.choice(["Push/Pull/Legs", "Upper/Lower"])


# ======================
# HANDLER PRINCIPAL
# ======================
async def process_message(chat_id: int, text: str, user: dict):

    text = text.strip().lower()
    user.setdefault("step", "objetivo")

    # ======================
    # ETAPA 1 — OBJETIVO
    # ======================
    if user["step"] == "objetivo":
        send_message(
            chat_id,
            "🎯 Qual é seu objetivo?\n\n"
            "- Hipertrofia\n"
            "- Emagrecimento\n"
            "- Definição\n"
            "- Condicionamento físico"
        )
        user["step"] = "objetivo_resposta"
        return

    if user["step"] == "objetivo_resposta":
        user["objetivo"] = text
        user["step"] = "peso"
        send_message(chat_id, "⚖️ Qual seu peso atual (em kg)?\nEx: 80")
        return

    # ======================
    # ETAPA 2 — PESO
    # ======================
    if user["step"] == "peso":
        try:
            user["peso"] = float(text.replace(",", "."))
        except ValueError:
            send_message(chat_id, "❌ Informe apenas números.\nEx: 80")
            return

        user["step"] = "dias"
        send_message(chat_id, "📅 Quantos dias por semana você treina?\n(3 a 6)")
        return

    # ======================
    # ETAPA 3 — DIAS
    # ======================
    if user["step"] == "dias":
        try:
            dias = int(text)
            if dias < 3 or dias > 6:
                raise ValueError
            user["dias"] = dias
        except ValueError:
            send_message(chat_id, "❌ Informe um número válido entre 3 e 6 dias.")
            return

        user["step"] = "nivel"
        send_message(
            chat_id,
            "🏋️ Qual seu nível de treino?\n\n"
            "1️⃣ Iniciante\n"
            "2️⃣ Intermediário\n"
            "3️⃣ Avançado"
        )
        return

    # ======================
    # ETAPA 4 — NÍVEL
    # ======================
    if user["step"] == "nivel":
        niveis = {"1": "Iniciante", "2": "Intermediário", "3": "Avançado"}
        if text not in niveis:
            send_message(chat_id, "❌ Responda com 1, 2 ou 3.")
            return

        user["nivel"] = niveis[text]
        user["step"] = "tempo"
        send_message(
            chat_id,
            "⏱️ Quanto tempo por treino?\n\n"
            "40 minutos\n"
            "60 minutos\n"
            "90 minutos"
        )
        return

    # ======================
    # ETAPA 5 — TEMPO
    # ======================
    if user["step"] == "tempo":
        if text not in ["40", "60", "90"]:
            send_message(chat_id, "❌ Informe 40, 60 ou 90 minutos.")
            return

        user["tempo"] = text
        send_message(chat_id, "⏳ Gerando seu treino personalizado...")
        user["step"] = "gerando"

        # ======================
        # ESCOLHER TIPO DE TREINO
        # ======================
        tipo_treino = escolher_tipo_treino(user["dias"])

        prompt = f"""
Você é um PERSONAL TRAINER PROFISSIONAL brasileiro.

Crie um TREINO DE MUSCULAÇÃO realista, seguro e bem estruturado do tipo: {tipo_treino}

Dados do aluno:
- Objetivo: {user['objetivo']}
- Peso: {user['peso']} kg
- Dias por semana: {user['dias']}
- Nível: {user['nivel']}
- Tempo por treino: {user['tempo']} minutos

REGRAS OBRIGATÓRIAS:
- Use APENAS nomes corretos em português do Brasil
- NÃO invente exercícios
- NÃO use termos em espanhol ou inglês
- NÃO repita exercícios no mesmo treino
- Separe claramente os treinos (A, B, C… ou Full Body)
- Inclua:
  • Aquecimento curto
  • Exercícios com séries x repetições
  • Descanso entre séries
- Linguagem clara para Telegram
- Sem texto introdutório longo

⚠️ No final, inclua uma dica curta de progressão.
"""

        try:
            # ======================
            # CHAMADA AO GROQ COM MAIS TOKENS
            # ======================
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Você é um personal trainer experiente."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2500  # aumenta para treinos completos
            )

            treino = response.choices[0].message.content.strip()

            # ======================
            # ENVIO AUTOMÁTICO EM BLOCO
            # ======================
            # Se houver múltiplos treinos no texto (A, B, C ou Full Body), separa por linha dupla
            blocos = treino.split("\n\n🏋️‍♂️")
            for i, bloco in enumerate(blocos):
                if i > 0:
                    bloco = "🏋️‍♂️" + bloco  # adiciona título novamente
                send_long_message(chat_id, f"*Treino ({tipo_treino})*\n\n{bloco}")

        except Exception as e:
            print("Erro Groq:", e)
            send_message(chat_id, "⚠️ Erro ao gerar o treino. Tente novamente.")

        # ======================
        # RESET SEGURO DO FLUXO
        # ======================
        user_keys = ["objetivo", "peso", "dias", "nivel", "tempo"]
        for k in user_keys:
            user.pop(k, None)

        user["step"] = "objetivo"
        return
