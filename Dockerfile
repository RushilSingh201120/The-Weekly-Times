# Use the official Python image.
FROM python:3.14-slim

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory.
WORKDIR /code

# Install system dependencies required by mysqlclient.
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies.
COPY requirements.txt /code/

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the Django project.
COPY . /code/

# Expose Django's port.
EXPOSE 8000

# Start the Django development server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]