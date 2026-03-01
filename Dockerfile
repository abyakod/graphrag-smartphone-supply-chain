FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pymgclient
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command (overridden by docker-compose)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
