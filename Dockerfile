FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional requirements from subdirectories if they exist
RUN if [ -f Day3a/requirements.txt ]; then pip install --no-cache-dir -r Day3a/requirements.txt; fi
RUN if [ -f Day3b/requirements.txt ]; then pip install --no-cache-dir -r Day3b/requirements.txt; fi

# Copy all project files (excluding .dockerignore patterns)
COPY . .

# Ensure .env files exist (create from template if needed)
RUN for dir in Day1a Day1b Day2a Day2b Day3a Day3b Day4a Day4b Day5a Day5b; do \
    if [ ! -f "$dir/.env" ] && [ -f "$dir/env.template" ]; then \
        cp "$dir/env.template" "$dir/.env"; \
    fi; \
    done || true

# Set environment variables from .env file (will be overridden by docker-compose)
ENV GOOGLE_CLOUD_PROJECT=aiagent-capstoneproject
ENV GOOGLE_CLOUD_LOCATION=us-central1
ENV ADK_LOG_LEVEL=DEBUG

# Expose port for ADK web server
EXPOSE 8080

# Default command: run ADK web server with recursive discovery
CMD ["adk", "web", ".", "--port", "8080", "--host", "0.0.0.0", "--log_level", "DEBUG"]

