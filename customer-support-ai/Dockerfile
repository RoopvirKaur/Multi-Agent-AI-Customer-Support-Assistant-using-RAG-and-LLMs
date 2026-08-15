# ============================================================
# Multi-Agent AI Customer Support Assistant — Backend Dockerfile
# Optimized for Render Web Services & Containerized Deployments
# ============================================================

FROM python:3.11-slim

# Set environment flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install system build dependencies and curl for health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for caching efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend ./backend
COPY knowledge_base ./knowledge_base
COPY datasets ./datasets
COPY vectorstore ./vectorstore
COPY .env.example .env.example
COPY start.sh .

# Ensure start script has execution permissions
RUN chmod +x start.sh

# Expose default port
EXPOSE 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Launch container via entrypoint
CMD ["./start.sh"]
