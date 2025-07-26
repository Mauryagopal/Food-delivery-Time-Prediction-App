# Use Python 3.10 base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy all project files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask's port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
