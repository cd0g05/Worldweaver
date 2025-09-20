# Use Python 3.11 slim image
FROM python:3.11-slim

# Install Node.js for building React frontend
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend package.json and install Node dependencies
COPY frontend/planner/package*.json ./frontend/planner/
RUN cd frontend/planner && npm ci

# Copy the entire application
COPY . .

# Build the React frontend
RUN cd frontend/planner && npm run build

# Create necessary directories
RUN mkdir -p /app/backend/scripts && \
    mkdir -p /app/frontend/templates && \
    mkdir -p /app/frontend/static && \
    mkdir -p /app/backend/logs

# Ensure React build files are in the right place for nginx
RUN if [ -d "/app/frontend/static/planning-dist" ]; then \
        echo "React build files found in planning-dist"; \
    else \
        echo "Warning: React build files not found in expected location"; \
        ls -la /app/frontend/static/ || echo "static directory not found"; \
    fi

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV DEV_MODE=0
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Expose port from environment variable (Railway sets this)
EXPOSE ${PORT:-5000}

# Add health check using PORT environment variable
HEALTHCHECK --interval=300s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Run the application with error output
CMD ["python", "-u", "main.py"]