FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsqlite3-dev \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/prod.txt .

RUN pip install -U pip && \
    pip install -r prod.txt

COPY . .

WORKDIR /app/ore_warehouse
