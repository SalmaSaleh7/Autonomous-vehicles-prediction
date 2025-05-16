FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
    
RUN apt-get update && apt-get install -y libgl1-mesa-glx


COPY . .

RUN mkdir -p static/uploads && chmod -R 777 static/uploads

EXPOSE 8080
ENV PORT=8080
CMD ["python", "app.py"]
