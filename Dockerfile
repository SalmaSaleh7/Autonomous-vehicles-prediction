FROM python:3.10-slim


# Avoid pycache & buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system deps
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip packages
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app files
COPY . .

# Create static/uploads
RUN mkdir -p static/uploads && chmod -R 777 static/uploads

EXPOSE 8080
ENV PORT=8080
CMD ["sh", "-c", "python app.py --host=0.0.0.0 --port=$PORT"]
