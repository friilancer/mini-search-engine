# ---- Stage 1: Builder ----
FROM rust:1.72-slim AS builder
WORKDIR /app

# Install build essentials, python3-venv, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-venv \
    python3-pip

# Copy project
COPY . /app

# Create a virtual environment
RUN python3 -m venv /app/venv

# Activate and install
RUN /app/venv/bin/pip install --upgrade pip
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Final Runtime Image ----
FROM python:3.13-slim
WORKDIR /app

# Copy from builder
COPY --from=builder /app /app

# If you need the venv in the final image to run the app:
ENV PATH="/app/venv/bin:$PATH"

EXPOSE 5000
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000"]
