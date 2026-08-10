FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Regenerate hashed static files + manifest so WhiteNoise's
# CompressedManifestStaticFilesStorage serves the current CSS/JS, not
# whatever was baked into a previous image.
RUN python manage.py collectstatic --noinput

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]