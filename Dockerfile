# syntax=docker/dockerfile:1
FROM python:3.10-slim AS base

# Prevent Python from writing .pyc files & force unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps needed by psycopg (Postgres driver) + gunicorn
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in a dedicated layer (caches better)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Default envs (override in compose or prod)
ENV PORT=5050
ENV FLASK_DEBUG=0

# Expose app port
EXPOSE 5050

# Run with gunicorn (production WSGI server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "main:app"]
