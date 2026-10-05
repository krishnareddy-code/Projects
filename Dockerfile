# Step 1: Base image
# Debian Linux + Python 3.12, minimal size.
FROM python:3.12-slim

# Step 2: Metadata
LABEL maintainer="dexops trainee"
LABEL description="Flask login web app for DevOps training"

# Step 3: Set working directory inside the container
WORKDIR /app

# Step 4: Install system packages
# mysql-connector-python is pure Python, so no system deps required.
# We add curl so the HEALTHCHECK below can hit /health.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Copy requirements FIRST (for layer caching)
# Note: The destination dot (.) represents the current WORKDIR (/app)
COPY requirements.txt .

# Step 6: Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Step 7: Copy the rest of the app code
COPY app.py .
COPY templates/ ./templates/

# Step 8: Document the port the app listens on
EXPOSE 5000

# Step 9: Healthcheck so Docker knows if the app is healthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fs http://localhost:5000/health || exit 1

# Step 10: The command to start the app
CMD ["python", "app.py"]
