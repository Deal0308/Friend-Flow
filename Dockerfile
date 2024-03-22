# Use an official Python runtime as a parent image
FROM python:3.8

# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd && apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Copy .env file
COPY .env /app/

# Run the application on port 8000
EXPOSE 8000

# Start Gunicorn with 3 worker processes
CMD ["gunicorn", "--workers=3", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
