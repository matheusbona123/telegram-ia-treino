# Base image
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos necessários
COPY main.py bot.py handlers.py requirements.txt ./

# Instalar dependências
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expõe porta do Railway
EXPOSE 8080

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
