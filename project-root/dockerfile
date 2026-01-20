FROM python:3.11-slim

# Estä pyc + bufferointi
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Työhakemisto
WORKDIR /app

# Riippuvuudet
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopioi botin koodi
COPY . .

# Käynnistä botti
CMD ["python", "bot/main.py"]
