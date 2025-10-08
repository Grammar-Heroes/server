FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/var/cache/huggingface \
    TRANSFORMERS_CACHE=/var/cache/huggingface \
    LANGTOOL_HOME=/var/cache/languagetool

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
# If torch build fails, see Step 14 for CPU wheel fallback
RUN pip install --upgrade pip && pip install -r requirements.txt

# Optional: prewarm small spaCy model if used by your code
# RUN python -m spacy download en_core_web_sm || true

# Optional (speeds first request): pre-download LanguageTool + HF models
# RUN python - << 'PY'
# import language_tool_python; language_tool_python.LanguageTool('en-US').close()
# try:
#   from transformers import pipeline
#   pipeline("text-classification", model="textattack/roberta-base-CoLA")
#   pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
# except Exception as e:
#   print("Model prewarm skipped:", e)
# PY

COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
