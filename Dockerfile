# Production Dockerfile for DGDA Backend (Coolify Ready)
FROM python:3.11-slim

WORKDIR /app

# Prevent python from buffering stdout/stderr and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose the application port
EXPOSE 8000

# Health check to let Coolify verify container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch Uvicorn server in production mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
