# DevEx Ambient Agent - Production Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Build stage with uv
FROM python:3.11-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Stage 2: Production stage
FROM python:3.11-slim as production

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    # Required for enhanced analysis tools
    git \
    # Required for some Python packages
    gcc \
    # Required for Neo4j driver (optional)
    libssl-dev \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install analysis tools for enhanced code analysis
RUN pip install --no-cache-dir \
    bandit \
    safety \
    semgrep \
    pylint \
    flake8 \
    mypy \
    radon \
    vulture

# Create non-root user for security
RUN groupadd -g 1000 devex && \
    useradd -r -u 1000 -g devex devex

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=devex:devex . .

# Create necessary directories
RUN mkdir -p /app/data/vector_store /app/logs /app/config && \
    chown -R devex:devex /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Production environment variables
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO
ENV WORKERS=4

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Switch to non-root user
USER devex

# Default command
CMD ["python", "-m", "uvicorn", "devex_agent.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info", \
     "--access-log", \
     "--use-colors"] 