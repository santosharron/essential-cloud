# Start with a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy everything from your local directory into the container's /app directory
COPY . /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Tell Docker that the container will listen on port 5000
EXPOSE 5000

# The command to run when the container starts
CMD ["python", "app.py"]
