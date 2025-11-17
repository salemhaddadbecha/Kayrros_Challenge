FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml for dependency installation
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

ENV PYTHONPATH="/app:${PYTHONPATH}"

# Run FastAPI with Uvicorn
CMD ["uvicorn", "api_launch:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
