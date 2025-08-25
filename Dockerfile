# Enhanced version of your current Dockerfile for local development
FROM python:3.11-slim

# Metadata
LABEL maintainer="your-email@example.com"
LABEL description="Network Automation Dashboard - Development Version"
LABEL version="1.0.0"
LABEL environment="development"

# Set working directory
WORKDIR /app

# Set environment variables for development
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=main.py \
    FLASK_ENV=development \
    FLASK_DEBUG=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install comprehensive system dependencies for development
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libxml2-dev \
        libxslt-dev \
        libffi-dev \
        libssl-dev \
        curl \
        netcat-traditional \
        openssh-client \
        telnet \
        iputils-ping \
        git \
        vim \
        nano \
        htop \
        tcpdump \
        net-tools \
        iproute2 \
        traceroute \
        nmap \
        wireshark-common \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install all dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
        ipython \
        pytest \
        pytest-cov \
        black \
        flake8

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash netdashboard \
    && chown -R netdashboard:netdashboard /app \
    && usermod -aG sudo netdashboard
USER netdashboard

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Development server with auto-reload
CMD ["python", "main.py"]