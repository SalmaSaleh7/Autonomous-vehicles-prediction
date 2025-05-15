# Use official ultralytics image with dependencies pre-installed
FROM ultralytics/ultralytics:latest

# Environment variables to prevent Python buffering and pycache creation
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install extra system dependencies for image processing
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application files
COPY . .

# Create upload directory
RUN mkdir -p static/uploads

# Expose port 8080 (you can change to 5000 if you prefer)
EXPOSE 8080

# Use PORT environment variable from Railway or default to 8080
ENV PORT 8080

# Run your app binding to 0.0.0.0 and using the Railway port environment variable
CMD ["sh", "-c", "python app.py --host=0.0.0.0 --port=$PORT"]
