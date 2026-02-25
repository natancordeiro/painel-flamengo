FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# deps do sistema (se precisar de build de libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Flask na porta 5000
EXPOSE 5000

# Gunicorn para produção
CMD ["gunicorn", "-w", "2", "-k", "gthread", "--threads", "8", "-b", "0.0.0.0:5000", "flamengo_api.app:create_app()"]