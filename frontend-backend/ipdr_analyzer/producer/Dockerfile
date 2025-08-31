FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements and install
COPY ipdr_analyzer/producer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY ipdr_analyzer/common ./ipdr_analyzer/common
COPY ipdr_analyzer/producer ./ipdr_analyzer/producer

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Run uvicorn via module to avoid PATH issues
CMD ["python", "-m", "uvicorn", "ipdr_analyzer.producer.service:app", "--host", "0.0.0.0", "--port", "5000"]
