FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY samples/ ./samples/

EXPOSE 7860 8000

# Default: Gradio demo (best for interview)
# Override for API: docker run ... uvicorn app.api:app --host 0.0.0.0 --port 8000
CMD ["python", "-m", "app.web_demo"]
