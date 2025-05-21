FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y gcc libpq-dev curl && \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN adduser --disabled-password --no-create-home appuser
USER appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

RUN python manage.py collectstatic --noinput
