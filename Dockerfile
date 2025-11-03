# Dockerfile
FROM python:3.11-slim

# Install system deps + AWS CLI
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    awscli \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run download script → then Streamlit
ENTRYPOINT ["sh", "-c", "python rag/download_vectorstore.py && exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]