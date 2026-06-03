# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ .
RUN ./node_modules/.bin/vite build

# Stage 2: Python backend
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY main.py .

COPY --from=frontend-build /frontend/dist frontend/dist

RUN mkdir -p data/uploads data/chromadb data/sample

COPY data/sample/ data/sample/

EXPOSE 8000

CMD ["python", "main.py"]
