# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files to the container
COPY . .

# Expose the port that the app will run on
EXPOSE 5000

# Specify the command to run the application
# Using gunicorn to serve the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
