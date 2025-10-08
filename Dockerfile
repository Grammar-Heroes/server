FROM python:3.11-slim

# ---- Environment Configuration ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/var/cache/huggingface \
    TRANSFORMERS_CACHE=/var/cache/huggingface \
    LANGTOOL_HOME=/var/cache/languagetool

# ---- System Dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Application Setup ----
WORKDIR /app
COPY requirements.txt ./

# Install Python dependencies
# Includes fallback for CPU-only PyTorch builds
RUN pip install --upgrade pip && \
    pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt && \
    python -m spacy download en_core_web_sm

# ---- Optional Prewarm (can skip if slow build times) ----
# RUN python - << 'PY'
# import language_tool_python
# language_tool_python.LanguageTool('en-US').close()
# try:
#     from transformers import pipeline
#     pipeline("text-classification", model="textattack/roberta-base-CoLA")
#     pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
# except Exception as e:
#     print("Model prewarm skipped:", e)
# PY

# ---- Finalize ----
COPY . .
EXPOSE 8000

# Keep workers=1 for heavy ML models to prevent OOM
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
