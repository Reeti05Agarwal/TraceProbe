# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
# We copy requirements.txt from the root directory
COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the common library code
COPY ../common ./ipdr_analyzer/common

# Copy the application code for this specific service
# The first '.' is the service directory (e.g., 'producer'), the second '.' is the WORKDIR in the container
COPY . .

# Set the python path to allow for package imports
ENV PYTHONPATH=/app

# Command to run the application
CMD ["python", "-u", "main.py"]
