FROM python:3.13-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 and build tools
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project structure
COPY . .
RUN mkdir -p logs

# Expose the port
EXPOSE 8000

# Set environment variables for Python path
ENV PYTHONPATH=/app

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
