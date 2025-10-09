FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/var/cache/huggingface \
    TRANSFORMERS_CACHE=/var/cache/huggingface \
    LANGTOOL_HOME=/var/cache/languagetool

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}