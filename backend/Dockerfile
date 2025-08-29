# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput || echo 'collectstatic skipped'

EXPOSE 8000
CMD ["gunicorn", "novabot_backend.wsgi", "--bind", "0.0.0.0:8000", "--log-file", "-", "--access-logfile", "-"]