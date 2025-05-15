FROM ultralytics/ultralytics:latest

# Prevent Python buffering and pycache
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system deps first (cached unless changed)
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy ONLY requirements.txt first (for layer caching)
COPY requirements.txt .

# Install Python deps with pinned versions and no cache
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app (changes here won't trigger pip reinstall)
COPY . .

# Create uploads dir (avoid permission issues)
RUN mkdir -p static/uploads && chmod -R 777 static/uploads

# Runtime settings
EXPOSE 8080
ENV PORT=8080
CMD ["sh", "-c", "python app.py --host=0.0.0.0 --port=$PORT"]