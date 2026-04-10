FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required by chromadb / hnswlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements_server.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements_server.txt

# Copy application code
COPY . .

# HF Spaces runs as a non-root user (UID 1000)
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
