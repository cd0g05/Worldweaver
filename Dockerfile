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

# Expose port (Railway uses PORT env var)
EXPOSE $PORT

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "main.py"]