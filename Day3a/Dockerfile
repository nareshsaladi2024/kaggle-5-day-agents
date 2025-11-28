FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agents/ ./agents/
COPY run_*.py ./

# Copy utility from parent directory (if available)
# Note: When building from Day3a directory, copy from ../utility
COPY ../utility/ ./utility/ || true

# Set environment variables
ENV APP_NAME=session_app
ENV USER_ID=default
ENV AGENT_MODEL=gemini-2.5-flash-lite
ENV SESSION_SERVICE_TYPE=database
ENV DB_URL=sqlite:///session_data.db

# Expose port (if running as web service)
EXPOSE 8000

# Default command: run the interactive agent
CMD ["python", "run_session_agent.py"]
