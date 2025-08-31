# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
# We copy requirements.txt from the root directory (the context)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the common library code
# The path is now relative to the context (project root)
COPY ipdr_analyzer/common ./ipdr_analyzer/common

# Copy the application code for this specific service
# Note: This command is slightly different for each Dockerfile
# SEE BELOW

# Set the python path to allow for package imports
ENV PYTHONPATH=/app

# Command to run the application
COPY ipdr_analyzer/processor ./ipdr_analyzer/processor
CMD ["python", "-u", "ipdr_analyzer/processor/main.py"]
