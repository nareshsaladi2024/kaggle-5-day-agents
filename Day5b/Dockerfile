FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY WeatherAssistant/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for API server
RUN pip install --no-cache-dir fastapi uvicorn python-multipart python-dotenv

# Copy agent files
COPY WeatherAssistant/ ./WeatherAssistant/

# Copy API server
COPY weather-assistant-api.py .

# Note: utility/ is optional - agent handles ImportError gracefully
# If you need utility, copy it from parent directory or include it in Day5b

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run the API server
CMD ["python", "weather-assistant-api.py"]
