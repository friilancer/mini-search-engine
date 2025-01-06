# Use an official Python runtime
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies, including Rust
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libffi-dev \
    libssl-dev \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && export PATH="/root/.cargo/bin:$PATH" \
    && rustc --version \
    && cargo --version \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files to the container
COPY . .

# Expose the port that the app will run on
EXPOSE 5000

# Specify the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
